from setuptools import setup, find_packages

with open("README.txt", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="robocad-pyd",
    version="0.1.0",
    author="Mark Lays",
    author_email="Studica@gmail.com",
    description="Studica Robotics",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[],
)