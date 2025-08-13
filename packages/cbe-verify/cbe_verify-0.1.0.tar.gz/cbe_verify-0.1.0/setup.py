from setuptools import setup, find_packages

setup(
    name="cbe-verify",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.1",
        "pdfplumber>=0.7.4",
    ],
    author="yohnnes gizaw",
    author_email="yohnnesgizaw777@example.com",
    description="A simple package to verify CBE payment receipts",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yohaboy/cbe_verifier",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)