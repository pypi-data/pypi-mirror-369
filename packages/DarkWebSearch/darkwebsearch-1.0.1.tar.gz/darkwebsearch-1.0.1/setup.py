import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="DarkWebSearch",
    version="1.0.1",
    author="Mohammad Taha Gorji",
    author_email="MohammadTahaGorjiProfile@gmail.com",
    description="A library for search onion links on DarkWeb",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "requests"
    ],
)
