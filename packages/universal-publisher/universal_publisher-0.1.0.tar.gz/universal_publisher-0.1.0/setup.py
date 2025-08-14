from setuptools import setup, find_packages

setup(
    name="universal-publisher",
    version="0.1.0",
    author="Akshay",
    description="A universal ROS2 publisher for text, numbers, booleans, images, videos, and multi-float arrays.",
    packages=find_packages(),
    install_requires=[
        "cv_bridge",
        "opencv-python"
    ],
    python_requires=">=3.6",
)
