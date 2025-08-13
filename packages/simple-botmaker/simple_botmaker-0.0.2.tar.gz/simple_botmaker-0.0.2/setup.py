#!/usr/bin/env python3
"""Setup script for simple-botmaker package."""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ''

# Read requirements from requirements.txt
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name='simple-botmaker',
    version='1.0.0',
    author='Simple Botmaker Team',
    author_email='',
    description='A package that simplifies the creation of bots that react to the screen in real time',
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/simple-botmaker',  # Update with actual repository URL
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Games/Entertainment',
        'Topic :: Multimedia :: Graphics :: Capture :: Screen Capture',
        'Topic :: Scientific/Engineering :: Image Recognition',
    ],
    python_requires='>=3.7',
    install_requires=read_requirements(),
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-cov',
            'black',
            'flake8',
            'mypy',
        ],
    },
    entry_points={
        'console_scripts': [
            'simple-botmaker-interpreter=simple_botmaker.custom_interpreter.interpreter:main',
        ],
    },
    keywords=['automation', 'bot', 'screen-capture', 'ocr', 'image-recognition', 'windows'],
    project_urls={
        'Bug Reports': 'https://github.com/yourusername/simple-botmaker/issues',
        'Source': 'https://github.com/yourusername/simple-botmaker',
        'Documentation': 'https://github.com/yourusername/simple-botmaker#readme',
    },
    include_package_data=True,
    zip_safe=False,
    platforms=['win32'],
)
