from setuptools import setup, find_packages
import os

# Attempt to read the README.md file for the long description
readme_path = 'README.md'
if os.path.exists(readme_path):
    with open(readme_path, 'r') as fh:
        long_description = fh.read()
else:
    long_description = 'Long description not available.'

setup(
    name='pregress',
    version='1.0.8',
    packages=find_packages(include=['pregress', 'pregress.*']),
    install_requires=[
        'matplotlib', 'pandas', 'numpy', 'statsmodels', 'seaborn', 'scikit-learn', 
        'scipy'
    ],
    entry_points={
        'console_scripts': [
            # Define any command-line scripts here, if applicable
        ],
    },
    author="Daniel McGibney",
    author_email="dmcgibney@bus.miami.edu",
    description="Python Regression Analysis.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/danmcgib/pregress",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    include_package_data=True,  # Ensures package data is included
    package_data={
        'pregress': ['data/*.csv'],  # Reference the correct package name
    },
)
