from setuptools import setup, find_packages

setup(
    name="sqladmin-whiteleads",
    version="0.21.0",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.7",
    install_requires=[
        "sqlalchemy>=1.4",
        "fastapi>=0.68.0",
        "jinja2>=2.11.0",
    ],
    include_package_data=True,
)