from setuptools import setup, find_packages
import os

# Read the contents of README.md
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='autotrend',
    version='0.2.4',
    author='Chotanansub Sophaken',
    author_email='chotanansub.s@gmail.com',
    description='Local Linear Trend Extraction for Time Series',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/chotanansub/autotrend',
    packages=find_packages(exclude=['demo', 'demo.*', 'output', 'output.*']),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: Mathematics',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    python_requires='>=3.8',
    install_requires=[
        'numpy>=1.20.0',
        'scikit-learn>=1.0.0',
        'matplotlib>=3.3.0',
        'seaborn>=0.11.0',
        'scipy>=1.7.0',
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=3.0.0',
            'black>=22.0.0',
            'flake8>=4.0.0',
            'mypy>=0.950',
        ],
    },
    keywords='time-series trend-extraction linear-regression segmentation decomposition',
    project_urls={
        'Bug Reports': 'https://github.com/chotanansub/autotrend/issues',
        'Source': 'https://github.com/chotanansub/autotrend',
        'Documentation': 'https://github.com/chotanansub/autotrend#readme',
    },
)