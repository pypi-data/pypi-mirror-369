from setuptools import setup, find_packages

setup(
    name="meapi-core",
    version="0.0.1",
    author="MeAPI Team",
    author_email="dev@meapi.dev",
    description="MeAPI Core - Official Python SDK",
    long_description="# MeAPI Core\n\nOfficial MeAPI Python SDK\n\nVisit https://meapi.dev",
    long_description_content_type="text/markdown",
    url="https://meapi.dev",
    project_urls={
        "Homepage": "https://meapi.dev",
        "Source": "https://github.com/getmeapi/meapi",
    },
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
    python_requires=">=3.8",
    packages=find_packages(),
)
