from setuptools import find_packages, setup

setup(
    name='src',
    packages=find_packages(),
    version='0.1.0',
    description='A production-grade MLOps capstone project demonstrating the complete machine learning lifecycle—from data versioning with DVC, experiment tracking with MLflow/DagsHub, containerization with Docker, to deployment on AWS EKS with CI/CD pipelines and observability using Prometheus & Grafana.',
    author='kernel crush',
    license='Apache License 2.0',
)
