import os
from setuptools import setup, find_packages

base_directory = os.path.dirname(__file__)

with open(os.path.join(base_directory, 'README.md')) as file:
  long_description = file.read()

setup(
  name='sanitipy',
  description='Sanitipy is a user-friendly Python library designed for data cleaning and preprocessing. It provides essential utilities to streamline the process of preparing datasets for analysis or modeling. With features such as duplicate removal, handling missing values, and automatic data type inference, sanitipy simplifies the data cleaning workflow, making it a useful tool for data scientists and analysts.',
  long_description=long_description,
  long_description_content_type='text/markdown',
  author='Adam Ben-Aamr',
  author_email='adambenaamr@gmail.com',

  # Note: Always update the version number
  version='1.1.0',
  packages=find_packages(),
  license='MIT',
  install_requires=[
    # Add dependencies here.
    'pandas',
    'missingno',
  ],
  url='https://github.com/yestab335/sanitipy',
  download_url='',
  keywords=[
    'data',
    'data cleaning',
    'missing data',
    'data science',
    'pandas',
    'python'
  ],
  classifiers=[
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    # 'Programming Language :: Python 3.7',
    # 'Programming Language :: Python 3.8',
    # 'Programming Language :: Python 3.9',
  ],
)
