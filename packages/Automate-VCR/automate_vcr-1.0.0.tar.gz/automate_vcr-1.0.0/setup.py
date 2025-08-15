from setuptools import setup, find_packages

setup(
    name='Automate-VCR',  # No spaces in package name
    version='1.0.0',
    author='Raunak Raj',
    author_email='test@gmail.com',
    description='Automate VCR by Raunak Raj',
    packages=find_packages(exclude=["vcr*", "venv*", "tests*"]),  # exclude venv
    install_requires=[
        'selenium',
        'webdriver-manager',
    ],
    python_requires='>=3.8',
)
