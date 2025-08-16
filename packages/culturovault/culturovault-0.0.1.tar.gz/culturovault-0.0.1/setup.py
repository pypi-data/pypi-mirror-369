from setuptools import setup, find_packages

setup(
    name="culturovaultapi",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "selenium",
        "requests",
        "beautifulsoup4"
    ],
    entry_points={
        "console_scripts": [
            "culturovaultapi=culturovaultapi.cli:main",
        ],
    },
    author="D. Saahishnu Ram",
    description="CLI tool to upload and view CulturoVault entries",
    url="https://culturovaultignicion.pythonanywhere.com/",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
