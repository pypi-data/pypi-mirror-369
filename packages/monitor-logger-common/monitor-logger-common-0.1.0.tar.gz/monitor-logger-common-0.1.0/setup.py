from setuptools import setup, find_packages

setup(
    name="logger",
    version="0.1.0",
    description="Logger custom use structlog",
    author="Ricardo",
    packages=find_packages(),
    install_requires=[
        "structlog>=24.1.0"  # Asegúrate de usar una versión compatible
    ],
    python_requires=">=3.7",
)