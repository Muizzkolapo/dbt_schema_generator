from setuptools import setup, find_packages
import os

# Read the README.md content
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='dbt_schema_generator',
    version='0.1.0a1',  # First alpha release 
    author='Your Name',
    author_email='lateefmuizz@gmail.com',
    description='A command-line tool to generate schema.yml files for specified dbt models',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/Muizzkolapo/dbt_schema_generator.git',
    license='MIT',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
    ],
    entry_points={
        'console_scripts': [
            'dbt_schema_generator=dbt_schema_generator:main',
        ],
    },
    python_requires='>=3.9',
    include_package_data=True, 
)
