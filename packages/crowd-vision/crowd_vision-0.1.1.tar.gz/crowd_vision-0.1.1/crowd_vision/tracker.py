import cv2
import numpy as np
import torch
import torchvision
from torchvision.transforms import functional as F
from torchvision.ops import nms, box_iou
from scipy.optimize import linear_sum_assignment
from collections import defaultdict, deque
import os
import csv

# --------------------------- Utilities ---------------------------
COCO_PERSON_CLASS = 1

def iou_xyxy(a, b):
    """Calculates Intersection over Union (IoU) between two bounding boxes."""
    return box_iou(torch.as_tensor(a)[None,:4], torch.as_tensor(b)[None,:4]).item()

def compute_hist_feature(image, box):
    """Computes a 32-bin color histogram feature for a given box."""
    x1,y1,x2,y2 = [int(v) for v in box]
    h,w = image.shape[:2]
    x1, x2 = max(0, min(w-1, x1)), max(0, min(w-1, x2))
    y1, y2 = max(0, min(h-1, y1)), max(0, min(h-1, y2))
    if x2<=x1 or y2<=y1: return np.zeros(32, dtype=np.float32)
    
    crop = image[y1:y2, x1:x2]
    hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
    feats = [cv2.calcHist([hsv],[ch],None,[8],[0,256]).flatten() for ch in range(3)]
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    feats.append(cv2.calcHist([gray],[0],None,[8],[0,256]).flatten())
    
    vec = np.concatenate(feats).astype(np.float32)
    return vec / (np.sum(vec)+1e-6)

def cosine(a,b):
    """Computes cosine similarity between two vectors."""
    na = np.linalg.norm(a)+1e-6; nb=np.linalg.norm(b)+1e-6
    return float(np.dot(a,b)/(na*nb))

# --------------------------- Kalman & Helpers ---------------------------
def convert_bbox_to_z(bbox):
    """Converts a bounding box from [x1,y1,x2,y2] to [cx,cy,s,r] format."""
    w = bbox[2]-bbox[0]; h = bbox[3]-bbox[1]
    x = bbox[0] + w/2.; y = bbox[1] + h/2.; s = w*h; r = (w/(h+1e-6))
    return np.array([x,y,s,r], dtype=np.float32).reshape((4,1))

def convert_x_to_bbox(x):
    """Converts a state vector [cx,cy,s,r] back to a bounding box [x1,y1,x2,y2]."""
    w = np.sqrt(max(1e-6, x[2]*x[3])); h = max(1e-6, x[2]/(w+1e-6))
    return np.array([x[0]-w/2., x[1]-h/2., x[0]+w/2., x[1]+h/2.], dtype=np.float32).reshape((1,4))

class KalmanBoxTracker:
    """This class represents the internal state of individual tracked objects."""
    count = 0
    def __init__(self, bbox, feat=None):
        self.kf = cv2.KalmanFilter(7,4)
        self.kf.measurementMatrix = np.array([[1,0,0,0,0,0,0],[0,1,0,0,0,0,0],[0,0,1,0,0,0,0],[0,0,0,1,0,0,0]], np.float32)
        self.kf.transitionMatrix = np.array([[1,0,0,0,1,0,0],[0,1,0,0,0,1,0],[0,0,1,0,0,0,1],[0,0,0,1,0,0,0],[0,0,0,0,1,0,0],[0,0,0,0,0,1,0],[0,0,0,0,0,0,1]], np.float32)
        self.kf.processNoiseCov = np.eye(7, dtype=np.float32)*0.05
        self.kf.measurementNoiseCov = np.eye(4, dtype=np.float32)*1.0
        self.kf.errorCovPost = np.eye(7, dtype=np.float32)*1000.0
        self.kf.statePost = np.array([*convert_bbox_to_z(bbox[:4]).flatten(), 0,0,0], dtype=np.float32)
        
        self.time_since_update = 0
        self.id = KalmanBoxTracker.count
        KalmanBoxTracker.count += 1
        self.history = []
        self.hits = 0
        self.hit_streak = 0
        self.age = 0
        self.feat = feat if feat is not None else np.zeros(32, dtype=np.float32)

    def update(self, bbox, feat=None):
        """Updates the state vector with observed bbox and appearance feature."""
        self.time_since_update = 0
        self.history = []
        self.hits += 1
        self.hit_streak += 1
        measurement = convert_bbox_to_z(bbox[:4])
        self.kf.correct(measurement)
        if feat is not None: self.feat = (0.7*self.feat + 0.3*feat)

    def predict(self):
        """Advances the state vector and predicts its future location."""
        if self.kf.statePost[2] + self.kf.statePost[6] <= 0: self.kf.statePost[6] *= 0.0
        self.kf.predict()
        self.age += 1
        if self.time_since_update > 0: self.hit_streak = 0
        self.time_since_update += 1
        bbox = self.get_state()
        if bbox.size>0: self.history.append(bbox[0])
        return bbox

    def get_state(self):
        """Returns the current bounding box estimate."""
        try:
            return convert_x_to_bbox(self.kf.statePost)
        except:
            return np.empty((0,4), dtype=np.float32)

    def get_velocity(self):
        """Returns the current velocity estimate."""
        return self.kf.statePost[4:6].flatten()

# --------------------------- PersonDetector ---------------------------
class PersonDetector:
    """A wrapper for the torchvision Faster R-CNN model to detect people."""
    def __init__(self, model_name="fasterrcnn_resnet50_fpn_v2", conf_thr_high=0.6, conf_thr_low=0.25, nms_thr=0.45):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"Using detector on device: {self.device}")
        self.model = torchvision.models.detection.get_model(model_name, weights='DEFAULT').to(self.device).eval()
        self.conf_high = conf_thr_high
        self.conf_low = conf_thr_low
        self.nms_thr = nms_thr

    @torch.no_grad()
    def infer(self, frame_bgr):
        """Performs inference on a single frame."""
        img_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        t = F.to_tensor(img_rgb).to(self.device)
        
        with torch.amp.autocast('cuda', enabled=self.device.type == 'cuda'):
            preds = self.model([t])[0]

        def to_np(p):
            m = p['labels'] == COCO_PERSON_CLASS
            return p['boxes'][m].cpu().numpy(), p['scores'][m].cpu().numpy()

        all_b, all_s = to_np(preds)
        if len(all_b):
            keep = nms(torch.from_numpy(all_b), torch.from_numpy(all_s), self.nms_thr)
            all_b, all_s = all_b[keep], all_s[keep]

        high_mask = all_s >= self.conf_high
        low_mask = (all_s >= self.conf_low) & ~high_mask
        dets_high = np.column_stack([all_b[high_mask], all_s[high_mask]])
        dets_low = np.column_stack([all_b[low_mask], all_s[low_mask]])
        return dets_high, dets_low

# --------------------------- Hybrid Tracker ---------------------------
class HybridTracker:
    """Manages all active tracks using a hybrid IOU and appearance matching strategy."""
    def __init__(self, max_age=30, min_hits=3, iou_thr=0.3, app_w=0.6):
        self.max_age = max_age
        self.min_hits = min_hits
        self.iou_thr = iou_thr
        self.app_w = app_w
        self.trackers = []
        self.frame_count = 0

    def _iou_cost(self, trks, dets):
        trk_boxes = np.array([t.get_state()[0] for t in trks])
        det_boxes = dets[:,:4]
        iou_matrix = np.zeros((len(trk_boxes), len(det_boxes)))
        for r in range(len(trk_boxes)):
            for c in range(len(det_boxes)):
                iou_matrix[r,c] = iou_xyxy(trk_boxes[r], det_boxes[c])
        return iou_matrix

    def update(self, frame_bgr, dets_high, dets_low):
        """Updates tracks with new detections, manages track lifecycle."""
        self.frame_count += 1
        for trk in self.trackers: trk.predict()

        unmatched_dets_high = np.arange(len(dets_high))
        trk_recent_idx = [i for i, t in enumerate(self.trackers) if t.time_since_update <= 1]
        trk_old_idx = [i for i, t in enumerate(self.trackers) if t.time_since_update > 1]

        # Stage 1: Match recent trackers with high-confidence detections
        if len(trk_recent_idx) > 0 and len(unmatched_dets_high) > 0:
            trks_recent = [self.trackers[i] for i in trk_recent_idx]
            dets = dets_high[unmatched_dets_high]
            feats = [compute_hist_feature(frame_bgr, d[:4]) for d in dets]

            iou_mat = self._iou_cost(trks_recent, dets)
            app_mat = np.array([[cosine(t.feat, f) for f in feats] for t in trks_recent])
            cost = (1.0 - self.app_w) * iou_mat + self.app_w * app_mat
            
            r, c = linear_sum_assignment(-cost)
            matches = []
            for r_i, c_i in zip(r,c):
                if cost[r_i, c_i] > self.iou_thr:
                    matches.append((r_i, c_i))
                    trk_idx = trk_recent_idx[r_i]
                    det_idx = unmatched_dets_high[c_i]
                    self.trackers[trk_idx].update(dets_high[det_idx,:4], feats[c_i])
            
            unmatched_dets_high = np.delete(unmatched_dets_high, [c_i for _, c_i in matches])

        # Stage 2: Match old trackers with remaining high-conf dets (IOU only)
        if len(trk_old_idx) > 0 and len(unmatched_dets_high) > 0:
            trks_old = [self.trackers[i] for i in trk_old_idx]
            dets = dets_high[unmatched_dets_high]
            iou_mat = self._iou_cost(trks_old, dets)
            
            r, c = linear_sum_assignment(-iou_mat)
            matches = []
            for r_i, c_i in zip(r,c):
                if iou_mat[r_i, c_i] > self.iou_thr:
                    matches.append((r_i, c_i))
                    trk_idx = trk_old_idx[r_i]
                    det_idx = unmatched_dets_high[c_i]
                    feat = compute_hist_feature(frame_bgr, dets_high[det_idx,:4])
                    self.trackers[trk_idx].update(dets_high[det_idx,:4], feat)

            unmatched_dets_high = np.delete(unmatched_dets_high, [c_i for _, c_i in matches])

        # Create new trackers for unmatched high-confidence detections
        for det_idx in unmatched_dets_high:
            feat = compute_hist_feature(frame_bgr, dets_high[det_idx, :4])
            self.trackers.append(KalmanBoxTracker(dets_high[det_idx, :4], feat))

        # Prune old trackers
        self.trackers = [t for t in self.trackers if t.time_since_update <= self.max_age]

        # Output active tracks
        out = []
        for trk in self.trackers:
            if (trk.hit_streak >= self.min_hits or self.frame_count <= self.min_hits) and trk.time_since_update < 2:
                out.append(np.concatenate((trk.get_state()[0], [trk.id+1])))

        return np.array(out) if len(out) else np.empty((0,5))

# --------------------------- Enhanced Crowd Detector ---------------------------
class EnhancedCrowdDetector:
    """The main class that orchestrates detection, tracking, and crowd clustering."""
    def __init__(self, **kwargs):
        self.detector = PersonDetector(
            conf_thr_high=kwargs.get("confidence_threshold", 0.6),
            conf_thr_low=kwargs.get("low_conf_threshold", 0.25),
            nms_thr=kwargs.get("nms_threshold", 0.45)
        )
        self.tracker = HybridTracker(
            max_age=kwargs.get("tracking_max_age", 30),
            min_hits=kwargs.get("tracking_min_hits", 3),
            app_w=kwargs.get("app_weight", 0.6)
        )
        self.proximity_base = kwargs.get("proximity_base", 0.5)
        self.motion_weight = kwargs.get("motion_weight", 0.2)
        self.marker_color = kwargs.get("marker_color", (0, 255, 0))
        self.group_color = kwargs.get("group_color", (255, 100, 0))
        self.frame_count = 0

    def _adaptive_eps(self, tracked_objects):
        if len(tracked_objects) == 0: return 60.0
        heights = [abs(t[3]-t[1]) for t in tracked_objects]
        med_h = np.percentile(heights, 75) if len(heights) else 80.0
        return max(30.0, self.proximity_base * med_h)

    def process_frame(self, frame):
        """Processes a single video frame to detect and analyze crowds."""
        self.frame_count += 1
        dets_high, dets_low = self.detector.infer(frame)
        tracked_objects = self.tracker.update(frame, dets_high, dets_low)

        crowd_info = []
        active_track_data = {}
        feature_vectors = []

        for obj in tracked_objects:
            tid = int(obj[4])
            trk_instance = next((t for t in self.tracker.trackers if t.id == tid-1), None)
            if trk_instance:
                x1,y1,x2,y2 = obj[:4]
                cx, cy = (x1+x2)/2, (y1+y2)/2
                vx, vy = trk_instance.get_velocity()
                feature_vectors.append([cx, cy, vx * self.motion_weight, vy * self.motion_weight])
                active_track_data[tid] = {'box': obj[:4], 'center': (cx, cy)}

        if len(feature_vectors) >= 3:
            from sklearn.cluster import DBSCAN
            eps = self._adaptive_eps(tracked_objects)
            clustering_data = np.array(feature_vectors)
            labels = DBSCAN(eps=eps, min_samples=3).fit(clustering_data).labels_
            unique_labels = set(labels) - {-1}
            all_track_ids = list(active_track_data.keys())

            for cid in unique_labels:
                mask = labels == cid
                member_ids = [all_track_ids[i] for i, in_crowd in enumerate(mask) if in_crowd]
                if len(member_ids) < 3: continue

                member_centers = np.array([active_track_data[tid]['center'] for tid in member_ids])
                hull = cv2.convexHull(member_centers.astype(np.int32))
                
                # Draw crowd visualization
                overlay = frame.copy()
                cv2.fillPoly(overlay, [hull], self.group_color)
                frame = cv2.addWeighted(overlay, 0.3, frame, 0.7, 0)
                cv2.drawContours(frame, [hull], 0, self.group_color, 2)
                tx, ty = int(np.mean(hull[:,0,0])) - 40, int(hull.min(axis=0)[0][1]) - 15
                cv2.putText(frame, f"Crowd: {len(member_ids)}", (tx,ty), cv2.FONT_HERSHEY_SIMPLEX, 0.7, self.group_color, 2)

                crowd_info.append({'count': len(member_ids), 'track_ids': member_ids})

        # Draw all tracked boxes
        for tid, data in active_track_data.items():
            x1,y1,x2,y2 = map(int, data['box'])
            cv2.rectangle(frame, (x1,y1), (x2,y2), self.marker_color, 2)
            cv2.putText(frame, f"{tid}", (x1, y1-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.marker_color, 1)

        cv2.putText(frame, f"Frame: {self.frame_count}", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
        return frame, crowd_info

# --------------------------- Main Video Loop Function ---------------------------
def analyze_video(video_path, output_dir, **kwargs):
    """
    High-level function to run the entire analysis pipeline on a video file.
    
    Args:
        video_path (str): Path to the input video file.
        output_dir (str): Directory to save the output video and CSV data.
        **kwargs: Keyword arguments to customize the detector and tracker parameters.
    """
    detector = EnhancedCrowdDetector(**kwargs)
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video {video_path}")
        return

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = max(1, int(cap.get(cv2.CAP_PROP_FPS)))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"📊 Video Stats: {width}x{height} @ {fps} FPS, {total_frames} frames.")

    os.makedirs(output_dir, exist_ok=True)
    csv_path = os.path.join(output_dir, 'crowd_analysis_data.csv')
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Frame','Time_Seconds','Crowd_ID','Person_Count','Track_IDs'])

    out_video_path = os.path.join(output_dir, 'crowd_analysis_output.mp4')
    out = cv2.VideoWriter(out_video_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

    frame_idx = 0
    while True:
        ret, frame = cap.read()
        if not ret: break

        processed_frame, crowd_data = detector.process_frame(frame)
        out.write(processed_frame)

        if crowd_data:
            with open(csv_path, 'a', newline='') as f:
                writer = csv.writer(f)
                for i, crowd in enumerate(crowd_data):
                    writer.writerow([frame_idx, f"{frame_idx/fps:.2f}", i+1, crowd['count'], ';'.join(map(str, crowd['track_ids']))])

        frame_idx += 1
        if frame_idx % (fps * 5) == 0: # Print progress every 5 seconds of video
            print(f"  -> Processing frame {frame_idx}/{total_frames} ({(frame_idx/total_frames)*100:.1f}%)")

    cap.release()
    out.release()
    print(f"\n✅ Processing complete! Analyzed {frame_idx} frames.")
    print(f"📁 Results saved to: {output_dir}")
