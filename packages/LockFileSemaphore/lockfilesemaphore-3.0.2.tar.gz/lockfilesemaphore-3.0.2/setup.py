from setuptools import setup, find_packages

setup(
    name="LockFileSemaphore",
    version="3.0.2",
    author="Marcin Kowalczyk",
    description="Robust file-based semaphore with stale lock recovery and context manager support.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.10",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
