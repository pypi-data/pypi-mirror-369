from setuptools import setup, find_packages

setup(
    name="plutus-sdk",  # Replace with your package name
    version="1.0.0",  # Replace with your version
    description="A Python SDK for Plutus API integration",
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/sdk",  # Replace with your repo URL
    packages=find_packages(),  # Automatically find all packages
    install_requires=[
        "requests",  # Add dependencies here
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)