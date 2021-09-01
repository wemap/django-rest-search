# -*- coding: utf-8 -*-

import os.path

from setuptools import setup

root_dir = os.path.abspath(os.path.dirname(__file__))

about = {}
about_file = os.path.join(root_dir, "src", "rest_search", "about.py")
with open(about_file, encoding="utf-8") as fp:
    exec(fp.read(), about)

readme_file = os.path.join(root_dir, "README.rst")
with open(readme_file, encoding="utf-8") as f:
    long_description = f.read()

setup(
    name=about["__title__"],
    version=about["__version__"],
    description=about["__summary__"],
    long_description=long_description,
    url=about["__uri__"],
    author=about["__author__"],
    author_email=about["__email__"],
    license=about["__license__"],
    package_dir={"": "src"},
    packages=["rest_search"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    extras_require={
        'dev': [
            'celery',
            'coreapi',
            'coreschema',
            'django',
            'djangorestframework',
        ]
    },
    install_requires=[
        "aws-requests-auth>=0.3.0",
        "elasticsearch>=6.0.0,<8.0.0",
    ],
)
