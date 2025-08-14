from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="precisiondoc",
    version="0.1.1rc1",
    author="Kay Chiao",
    author_email="kaychiao216@gmail.com",
    description="Document processing and evidence extraction package for precision oncology",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kaychiao/precisiondoc",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "PyMuPDF==1.26.3",
        "openai==1.96.1",
        "requests==2.31.0",
        "pandas==2.3.1",
        "python-dotenv==1.0.0",
        "python-docx==1.2.0",
        "openpyxl>=3.1.5",
        "numpy>=2.3.1",
        "tqdm>=4.67.1",
        "pillow>=8.2.0",
    ],
    entry_points={
        "console_scripts": [
            "precisiondoc=precisiondoc.main:main",
        ],
    },
    include_package_data=True,
)
