import re

from setuptools import find_packages, setup

with open("framedisplay/js/src/version.js", encoding="utf-8") as fh:
    content = fh.read()
    version = re.search(r"const\s+version\s*=\s*['\"]([^'\"]+)['\"]", content).group(1)

with open("README.md", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements/app.txt", encoding="utf-8") as fh:
    app_dependencies = fh.read().splitlines()

setup(
    name="framedisplay",
    version=version,
    packages=find_packages(include=["framedisplay*"]),
    package_dir={"framedisplay": "framedisplay"},
    package_data={
        "framedisplay": [
            "js/**/*.js",
            "js/**/*.css",
        ]
    },
    include_package_data=True,
    install_requires=app_dependencies,
    python_requires=">=3.7",
    author="Nima Sarang",
    author_email="contact@nimasarang.com",
    description="Enhanced DataFrame Display",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nsarang/framedisplay",
    project_urls={
        "Homepage": "https://github.com/nsarang/framedisplay",
        "Issues": "https://github.com/nsarang/framedisplay/issues",
        "Documentation": "https://github.com/nsarang/framedisplay#readme",
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Text Processing :: Markup :: HTML",
    ],
    keywords="dataframe display pandas jupyter notebook",
)
