import setuptools
import socket
import base64
import os

setuptools.setup(
    name="titifel-pyip",
    version="6.0.0",
    author="TitifelBro47",
    author_email="you@example.com",
    description="Your package description",
    packages=setuptools.find_packages(),
    install_requires=[
        "dnspython"  # Needed for DNS requests
    ],
    python_requires='>=3.6',
)
