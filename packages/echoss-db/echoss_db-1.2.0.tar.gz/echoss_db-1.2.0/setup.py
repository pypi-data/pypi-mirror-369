from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

package_name = "echoss-db"

setup(
    name='echoss-db',
    version='1.2.0',
    author='ckkim',
    author_email='ckkim@12cm.co.kr',
    url='https://github.com/12cmlab/echoss-query',
    install_requires=[
        'pandas>=1.5.3',
        'pymongo>=4.3.3',
        'sqlalchemy>=2.0.0',
        'PyMySQL>=1.0.2',
        'PyYAML>=6.0',
        'opensearch-py>=2.2.0',
        'echoss-fileformat>=1.1.2',
    ],
    description='echoss AI Bigdata Solution - Database Query Package',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='Apache License 2.0',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    include_package_data=True,
    python_requires= '>3.7',
)
