from setuptools import setup, find_packages
import os

# Read the README.txt for long description
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, "README.txt"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name='akpub',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'setuptools',
        'cv_bridge'
    ],
    author='akshay',
    author_email='you@example.com',
    description='A generic ROS2 publisher for numbers, strings, images, and video.',
    long_description=long_description,
    long_description_content_type="text/plain",  # Important for .txt
    python_requires='>=3.6',
)
