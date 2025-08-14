from setuptools import setup, find_packages

setup(
    name='sparams',
    version='1.0.1',
    description='A simple config watcher ',
    author='PAT',
    packages=find_packages(),
    install_requires=[
        'watchdog',
        'pyyaml',
        'opencv-python',
        'numpy',  
    ],
    python_requires='>=3.8',
    long_description = open("README", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
)