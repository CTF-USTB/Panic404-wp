from setuptools import setup, find_packages

setup(
    name="author_from_json",
    version="0.1",
    packages=find_packages(),
    entry_points={
        "mkdocs.plugins": [
            "author_from_json = plugins.author_from_json:AuthorFromJSONPlugin",
        ]
    },
)