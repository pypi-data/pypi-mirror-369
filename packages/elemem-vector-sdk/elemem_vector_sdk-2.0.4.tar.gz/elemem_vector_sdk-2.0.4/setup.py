import setuptools 
import subprocess
import os

class BuildProtoCommand(setuptools.Command):
    user_options = []

    def initialize_options(self): pass
    def finalize_options(self): pass

    def run(self):
        subprocess.check_call([
            'python3', '-m', 'grpc_tools.protoc',
            '-I../../proto',
            '--python_out=elemem_sdk/proto',
            '--grpc_python_out=elemem_sdk/proto',
            '../../proto/sdk.proto',
        ])
        grpc_file = "elemem_sdk/proto/sdk_pb2_grpc.py"
        if os.path.exists(grpc_file):
            with open(grpc_file, "r") as f:
                content = f.read()
            content = content.replace(
                "import sdk_pb2",
                "from . import sdk_pb2"
            )
            with open(grpc_file, "w") as f:
                f.write(content)


setuptools.setup(
    name="elemem_vector_sdk",
    version="2.0.4",
    author="elemem.tech",
    author_email="support@elemem.tech",
    description="A Python SDK for elem",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    py_modules=['hilbert_client', 'hilbert_cli'],
    entry_points={
        'console_scripts': [
            'hilbert-cli = hilbert_cli:main',
        ],
    },
    packages=setuptools.find_packages(),
    package_dir={'': '.'},
    package_data={
        'elemem_sdk': ['proto/*.py'],
    },
    install_requires=[
        'grpcio==1.74.0',
        'grpcio-tools==1.74.0',
        'numpy==1.26.4',
        'tqdm==4.67.1',
        'h5py==3.14.0',
        'protobuf==6.31.1'
    ],
    cmdclass={
        'build_proto': BuildProtoCommand
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
