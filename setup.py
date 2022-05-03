from setuptools import setup, find_packages

# FIXME: Remove this and keep all requirements in this setup file
with open("requirements.txt") as f:
    required = f.read().splitlines()

setup(
    name="cport",
    license="Apache License 2.0",
    version="0.1.0",
    author="",
    description="",
    author_email="",
    include_package_data=True,
    packages=find_packages("src"),
    package_dir={"": "src"},
    classifiers=[],
    python_requires=">=3.6, <4",
    install_requires=required,
    entry_points={"console_scripts": ["cport=cport.cli:maincli",],},
)
