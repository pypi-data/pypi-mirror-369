from setuptools import setup, find_packages

setup(
    name="ros2_simple_sub",
    version="0.1.0",
    author="Your Name",
    author_email="you@example.com",
    description="A simple configurable ROS2 subscriber",
    long_description=open("README.txt", "r").read(),
    long_description_content_type="text/plain",
    packages=find_packages(),
    python_requires=">=3.7",
)
