from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="purechainlib",
    version="2.1.2",
    author="PureChain Team",
    author_email="dev@purechain.network",
    description="Python SDK for PureChain EVM network - Zero gas cost blockchain development",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://pypi.org/project/purechainlib/",
    project_urls={
        "Documentation": "https://docs.purechain.network",
        "PyPI": "https://pypi.org/project/purechainlib/",
        "NPM Package": "https://www.npmjs.com/package/purechainlib",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: System :: Distributed Computing",
        "Topic :: Office/Business :: Financial",
        "Topic :: Security :: Cryptography",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    keywords=[
        "blockchain", "ethereum", "web3", "smart-contracts", 
        "zero-gas", "purechain", "evm", "solidity", "defi",
        "cryptocurrency", "web3py", "ethereum-development"
    ],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'purechain-security-setup=purechainlib.security_setup:main',
        ],
    },
)