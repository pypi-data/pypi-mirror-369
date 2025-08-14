from setuptools import setup, find_packages

setup(
    name="DrugAutoML",
    version="0.1.4",  # her yüklemede artır
    author="Your Name",
    author_email="ayca.beyhan@msu.edu.tr",
    description="Automated Machine Learning pipeline for bioactivity prediction using molecular fingerprints",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/aycapmkcu/DrugAutoML",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "pandas",
        "numpy",
        "scikit-learn",
        "matplotlib",
        "seaborn",
        "optuna",
        "xgboost",
        "lightgbm",
        "joblib",
        "scipy",
        "rdkit-pypi",
        "shap"
    ],
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
