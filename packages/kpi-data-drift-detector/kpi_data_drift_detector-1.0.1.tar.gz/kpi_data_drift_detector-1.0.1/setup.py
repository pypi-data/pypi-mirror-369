from setuptools import setup, find_packages

setup(
    name="kpi-data-drift-detector",
    version="1.0.1",
    author="Daria Yurchenko",
    packages=find_packages(),
    install_requires=[
        "pandas >= 1.5.0",
        "scikit-learn >= 1.0",
        "pytest >= 7.0.0"
    ],
    python_requires=">=3.6",
)