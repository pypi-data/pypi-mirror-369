import os
from setuptools import setup

def package_files(directory):
    paths = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            cur_file = os.path.join('..', root, file)
            if any(exclude in cur_file for exclude in ['/tests/', '/docs/', '/.git', '__pycache__', '.html']):
                continue
            paths.append(cur_file)
    return paths

# 0.1 version from OpenWebMath: https://github.com/keirp/OpenWebMath
# OpenWebMath is made available under an ODC-By 1.0 license; users should also abide by the CommonCrawl ToU: https://commoncrawl.org/terms-of-use/. We do not alter the license of any of the underlying data.
setup(
    name="haruka_parser",
    version="1.0.8",
    description="A simple HTML Parser",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="papersnake",
    author_email="prnake@gmail.com",
    url="https://github.com/prnake/haruka-parser",
    packages=["haruka_parser"],
    package_data={"": package_files("haruka_parser")},
    install_requires=[
        "py_asciimath",
        "inscriptis",
        "tabulate",
        "numpy",
        "resiliparse",
        "ftfy",
        "faust-cchardet",
        "lxml",
        "lxml_html_clean",
        "courlan",
        "charset_normalizer",
        "trafilatura",
        "tldextract",
        "pyahocorasick",
        "nltk",
        "uniseg",
        "pyyaml"
    ],
    extras_require={
        "dev": ["fasttext"],
    },
    include_package_data=True,
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Text Processing",
        "Topic :: Text Processing :: Markup :: HTML",
        "Topic :: Utilities",
    ),
)
