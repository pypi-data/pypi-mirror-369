from setuptools import setup, find_packages

setup(
    name="DrugAutoML",
    version="0.1.0",
    author="Your Name",
    author_email="ayca.beyhan@msu.edu.tr",
    description="Automated Machine Learning pipeline for bioactivity prediction using molecular fingerprints",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/DrugAutoML",
    packages=find_packages(),
    install_requires=open("requirements.txt").read().splitlines(),
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
