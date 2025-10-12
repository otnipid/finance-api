from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="finance_api",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=requirements,
    python_requires=">=3.8",
    include_package_data=True,
    package_data={
        "": ["*.yaml", "*.json"],
    },
    entry_points={
        "console_scripts": [
            "finance-api=src.main:main",
        ],
    },
)
