from setuptools import setup, find_packages

setup(
    name="healthylife-staff-scheduler",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "pulp>=2.0.0",
        "pandas>=1.3.0",
        "numpy>=1.20.0",
        "matplotlib>=3.5.0",
        "seaborn>=0.11.0",
        "streamlit>=1.0.0",
    ],
)
