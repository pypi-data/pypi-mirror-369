from setuptools import setup, find_packages

setup(
    name="elempysdk",
    version="2.0.0",
    author="elemem.tech",
    author_email="support@elemem.tech",
    description="A Python SDK for elem",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
#    url="https://github.com/yourusername/elem-py-sdk",
    packages=find_packages(),
    install_requires=[
        'grpcio==1.73.0',
        'grpcio-tools==1.73.0',
        'numpy==1.26.4',
        'tqdm==4.67.1',
        'h5py==3.14.0',
        'protobuf==6.31.1',

    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
