#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import find_packages, setup

with open("README.md") as readme_file:
    readme = readme_file.read()

setup_requirements = [
    "pytest-runner>=5.2",
]

test_requirements = [
    "black>=19.10b0",
    "codecov==2.1.12",
    "flake8>=3.8.3",
    "flake8-debugger>=3.2.1",
    "isort>=5.7.0",
    "mypy>=0.790",
    "pytest>=5.4.3",
    "pytest-cov>=2.9.0",
    "pytest-raises>=0.11",
    "tox>=3.15.2",
]

dev_requirements = [
    *setup_requirements,
    *test_requirements,
    "bump2version>=1.0.1",
    "coverage>=5.4",
    "ipython>=7.15.0",
    "m2r2>=0.2.7",
    "pytest-runner>=5.2",
    "Sphinx>=3.4.3",
    "sphinx_rtd_theme>=0.5.1",
    "twine>=3.1.1",
    "wheel>=0.34.2",
]

requirements = [
    "axe_selenium_python==2.1.6",
    "dataclasses-json==0.5.6",
    "pandas==1.3.4",
    "requests==2.26.0",
    "scrapy==2.5.1",
    "scrapy-selenium==0.0.7",
    "selenium==3.141.0",
    "textstat==0.7.2",
    "tldextract==3.1.2",
    "tqdm>=4.62,<5",
    "w3lib",  # no pin, pulled in with scrapy
]

extra_requirements = {
    "setup": setup_requirements,
    "test": test_requirements,
    "dev": dev_requirements,
    "all": [
        *requirements,
        *dev_requirements,
    ],
}

setup(
    author="BITS-Research",
    author_email="nmweber@uw.edu, jmxbrown@uw.edu",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    description=(
        "Digital material accessibility evaluation tools for political campaigns."
    ),
    entry_points={
        "console_scripts": [
            (
                "process-access-eval-results="
                "access_eval.bin.post_process_access_eval:main",
                "generate-access-eval-2021-dataset="
                "access_eval.bin.generate_access_eval_2021_dataset:main",
            ),
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme,
    long_description_content_type="text/markdown",
    include_package_data=True,
    keywords="civic technology, web accessibility, political campaigns",
    name="access-eval",
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*"]),
    python_requires=">=3.9",
    setup_requires=setup_requirements,
    test_suite="access_eval/tests",
    tests_require=test_requirements,
    extras_require=extra_requirements,
    url="https://github.com/BITS-Research/campaign-access-eval",
    # Do not edit this string manually, always use bump2version
    # Details in CONTRIBUTING.rst
    version="0.0.0",
    zip_safe=False,
)
