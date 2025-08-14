# setup.py

from setuptools import setup, find_packages
import os

# Read the contents of your README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="crowd_vision",
    version="0.1.1",
    author="Shobhit Shah",  # Replace with your name
    author_email="shobhitchamp21@gmail.com",  # Replace with your email
    description="An advanced library for crowd detection, tracking, and analysis in videos.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/crowd_vision",  # Optional: Link to your GitHub repo
    packages=find_packages(),
    # This is the most important part!
    # It lists all the libraries your code depends on.
    install_requires=[
        "numpy",
        "scipy",
        "scikit-learn",
        "torch",
        "torchvision",
        "opencv-python>=4.5",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Image Recognition",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
)
