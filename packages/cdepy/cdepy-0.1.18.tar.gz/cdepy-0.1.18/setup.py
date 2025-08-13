from setuptools import setup, find_packages
import os

def read_file(filename):
    with open(os.path.join(os.path.dirname(__file__), filename)) as file:
        return file.read()

setup(
    author="Paul de Fusco",
    description="A Python Package for interacting with Cloudera Data Engineering Clusters",
    long_description=read_file("README.md"),
    long_description_content_type="text/markdown",
    name="cdepy",
    version="0.1.18",
    packages=find_packages(include=["cdepy", "cdepy.*"]),
    install_requires=["pyparsing==3.0.9", "requests-toolbelt==1.0.0", "xmltodict==0.13.0"],
    python_requires=">=2.7",
    license="MIT",
    url = "https://github.com/pdefusco/cdepy",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
  ]
)
