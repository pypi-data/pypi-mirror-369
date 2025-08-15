

# my_package/setup.py

from setuptools import setup, find_packages
with open('README.md', 'r') as f:
    description = f.read()
setup(
    name='my_package_bhavya_choksey',
    version='0.2',  # <-- Update version
    packages=find_packages(),
    install_requires=[],
    long_description=description,
    long_description_content_type='text/markdown'
)


    