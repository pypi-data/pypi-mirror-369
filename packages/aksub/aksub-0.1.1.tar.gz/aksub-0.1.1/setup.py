from setuptools import setup, find_packages
import os

# Read README.txt
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, "README.txt"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name='aksub',
    version='0.1.1',
    packages=find_packages(),
    install_requires=[
        'setuptools',
        'cv_bridge'
    ],
    author='akshay',
    author_email='akshayfusion1@gmail.com',
    description='A generic ROS2 subscriber for numbers, strings, images, and video.',
    long_description=long_description,
    long_description_content_type="text/plain",
    python_requires='>=3.6',
)
