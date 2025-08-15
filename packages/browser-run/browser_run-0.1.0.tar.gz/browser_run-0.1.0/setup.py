from setuptools import setup, find_packages

setup(
    name="browser-run",                 # your package name
    version="0.1.0",                    # start with 0.1.0
    description="Run browser tasks and add SSH keys",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your_email@example.com",
    url="https://github.com/yourusername/browser-run",  # optional
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.31.0"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
