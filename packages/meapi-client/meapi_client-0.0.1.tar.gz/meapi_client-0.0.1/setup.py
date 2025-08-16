from setuptools import setup, find_packages

setup(
    name="meapi-client",
    version="0.0.1",
    author="MeAPI Team",
    author_email="dev@meapi.dev",
    description="MeAPI - Personal Intelligence API (Coming Soon)",
    long_description="# MeAPI\n\nPersonal Intelligence API - Coming Soon\n\nVisit https://meapi.dev for more information.",
    long_description_content_type="text/markdown",
    url="https://meapi.dev",
    project_urls={
        "Homepage": "https://meapi.dev",
        "Source": "https://github.com/getmeapi/meapi",
        "Documentation": "https://docs.meapi.dev"
    },
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    packages=find_packages(),
)
