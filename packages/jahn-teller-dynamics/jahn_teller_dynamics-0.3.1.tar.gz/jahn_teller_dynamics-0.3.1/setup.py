#!/usr/bin/env python3
"""
Setup script for Jahn-Teller Dynamics package.
"""

from setuptools import setup, find_packages
import os

# Read requirements from requirements.txt
def read_requirements():
    """Read requirements from requirements.txt file."""
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

# Read README for long description
def read_readme():
    """Read README.md file for long description."""
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')

    with open(readme_path, 'r', encoding='utf-16le', errors='ignore') as f:
        return f.read() 
    
setup(
    name='jahn_teller_dynamics',
    version='0.3.1',
    author='Balázs Tóth',
    author_email='toth.balazs@wigner.hun-ren.hu',
    description='A comprehensive Python package for Jahn-Teller effect calculations and dynamics',
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    
    # Package discovery - this is the key part
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    
    # Python version requirements
    python_requires='>=3.8',
    
    # Dependencies
    install_requires=read_requirements(),
    
    # Optional dependencies for development
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-cov>=2.0',
            'black>=21.0',
            'flake8>=3.8',
        ],
        'docs': [
            'sphinx>=4.0',
            'sphinx-rtd-theme>=1.0',
        ],
    },
    
    # Classifiers for PyPI
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Physics',
        'Topic :: Scientific/Engineering :: Chemistry',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Operating System :: OS Independent',
    ],
    
    # Keywords for PyPI search
    keywords=[
        'jahn-teller',
        'quantum-physics',
        'solid-state-physics',
        'vasp',
        'dft',
        'quantum-mechanics',
        'crystal-field-theory',
        'electron-phonon-coupling',
        'spin-orbit-coupling',
        'defect-physics',
        'point-defects',
        'color-centers',
    ],
    
    # License
    license='GPL-3.0',
    license_files=(),  # Explicitly disable license file inclusion
    
    # Include non-Python files
    include_package_data=True,
    
    # Entry points for command-line tools (optional)
    entry_points={
        'console_scripts': [
            'Exe=jahn_teller_dynamics.Exe:main',
        ],
    },
    
    # Additional metadata
    zip_safe=False,
    platforms=['any'],
    
    # URLs (update these with your actual URLs)
    url='https://github.com/yourusername/Jahn-Teller-Dynamics',
    project_urls={
        'Homepage': 'https://github.com/yourusername/Jahn-Teller-Dynamics',
        'Documentation': 'https://github.com/yourusername/Jahn-Teller-Dynamics#readme',
        'Repository': 'https://github.com/yourusername/Jahn-Teller-Dynamics.git',
        'Bug Tracker': 'https://github.com/yourusername/Jahn-Teller-Dynamics/issues',
    },
)