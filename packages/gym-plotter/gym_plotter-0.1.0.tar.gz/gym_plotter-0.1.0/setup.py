from setuptools import setup, find_packages

setup(
    name="gym-plotter",
    version="0.1.0",
    author="Yashvi Shah",
    author_email="yashviimpstme@gmail.com",
    description="Live plotting utility for RL environments (Gym, Stable-Baselines, etc.)",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yashviiishah/gym-plotter",
    packages=find_packages(),
    install_requires=[
        "matplotlib>=3.0.0",
        "numpy>=1.18.0"
    ],
    python_requires=">=3.6",
    license="MIT",
)
