from setuptools import setup, find_packages

setup(
    name="easy-rl-env",
    version="0.1.0",
    author="Your Name",
    author_email="you@example.com",
    description="Easily create custom RL environments for Gymnasium",
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/easy-rl-env",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "gymnasium"
    ],
    python_requires='>=3.7',
)
