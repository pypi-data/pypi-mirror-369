from setuptools import setup, find_packages

setup(
    name="epsilonq", 
    version="0.1.0",
    author="Krish Makhija",
    author_email="krish.makhija2@gmail.com",
    description="Lightweight RL utilities: epsilon-greedy and Q-learning update",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://pypi.org/project/epsilonq/",
    packages=find_packages(),
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
