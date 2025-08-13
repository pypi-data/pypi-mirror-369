from setuptools import setup, find_packages
import os

setup(
    name="oip-dataset-client",
    version=os.environ["OIP_DATASET_CLIENT_VERSION"],
    author="Rachid Belmeskine",
    author_email="rachid.belmeskine@gmail.com",
    description="This is the API client of Open Innovation MLOps Platform - Dataset",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    # url='https://github.com/...',
    python_requires=">=3.7",
    packages=find_packages(),
    install_requires=[
        "typeguard==2.13.3",
        "requests>=2.27.1",
        "six==1.16.0",
        "psutil==5.9.8",
        "tqdm>=4.66.1",
        "boto3>=1.26.20",
        "PyYAML==6.0.1",
        "attrs==23.2.0",
        "python-dotenv==1.0.1",
        "pandas==2.3.1"
    ],
    license="PRIVATE LICENSE",
    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        "console_scripts": [
            "oip-dataset-client-init = oip_dataset_client.cli.config.__main__:main",
        ],
    },
)
