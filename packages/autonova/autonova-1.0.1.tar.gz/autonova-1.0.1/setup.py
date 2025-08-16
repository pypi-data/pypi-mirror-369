from setuptools import setup, find_packages

setup(
    name="autonova",
    version="1.0.1",  # bump version if republishing to PyPI
    author="Sanjay Pal",
    author_email="sanjaypal606060@gmail.com",
    description="An automated machine learning pipeline with all-at-one-click feature.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Sanjaypal1916/ProjectX",
    packages=find_packages(),
    install_requires=[
        "catboost",
        "imbalanced-learn",
        "joblib",
        "lightgbm",
        "numpy",
        "optuna",
        "optuna-integration",
        "pandas",
        "pytest",
        "scikit-learn",
        "xgboost"
    ],
    license="MIT",  # or whatever your license is
    classifiers=[
        "License :: OSI Approved :: MIT License",  # change if using another license
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    include_package_data=True,  # ensures LICENSE and other data files are included
)
