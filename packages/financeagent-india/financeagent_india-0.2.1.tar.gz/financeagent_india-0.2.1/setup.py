from setuptools import setup, find_packages
import pathlib

from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="financeagent-india",  
    version="0.2.1",    # Prep for PyPI publish validation
    description="Lightweight India NSE stock quotes (MoneyControl) - pruned & optimized.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author="FinanceAgent Contributors",
    author_email="arushsinghal98@gmail.com",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
    ],
    keywords="finance stock nse india moneycontrol quotes",
    packages=find_packages(where="src"),
    package_dir={'': 'src'},
    install_requires=[
        'requests>=2.25.0',
        'beautifulsoup4>=4.9.0'
    ],
    python_requires=">=3.4",
    project_urls={
        "Homepage": "https://pypi.org/project/financeagent-india/",
    },
)
