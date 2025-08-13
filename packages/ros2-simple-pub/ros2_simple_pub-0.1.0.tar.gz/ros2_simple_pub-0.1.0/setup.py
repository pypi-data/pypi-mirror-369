from setuptools import setup, find_packages

setup(
    name="ros2_simple_pub",
    version="0.1.0",
    author="Akshay",
    author_email="akshayfusion1@gmail.com",
    description="A simple configurable ROS2 publisher",
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.7",
)
