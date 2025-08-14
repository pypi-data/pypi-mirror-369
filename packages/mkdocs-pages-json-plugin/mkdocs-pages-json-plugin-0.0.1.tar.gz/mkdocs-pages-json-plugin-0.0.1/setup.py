from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="mkdocs-pages-json-plugin",
    version="0.0.1",
    description="An MkDocs plugin that generates a pages.json file with page metadata.",
    long_description="An MkDocs plugin that generates a pages.json file at the root of the site, containing the title, URL, last modified date, and a custom review date for all pages.",
    keywords="mkdocs python json plugin",
    author="Bradley Stannard",
    author_email="opensource@breadnet.co.uk",
    license="MIT",
    python_requires=">=3.6",
    install_requires=[
        "mkdocs>=1.0.4"
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    packages=find_packages(),
    entry_points={
        "mkdocs.plugins": [
            "pages-json = mkdocs_pages_json_plugin.plugin:PagesJsonPlugin",
        ]
    }
)
