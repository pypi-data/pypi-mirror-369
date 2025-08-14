"""
Django DB Sync - Intelligent Database Synchronization Tool
"""

import os
from setuptools import setup, find_packages

# Import version from package
from django_dbsync import __version__

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Read requirements - only include actual package requirements
with open(os.path.join(this_directory, 'requirements.txt'), encoding='utf-8') as f:
    requirements = []
    for line in f:
        line = line.strip()
        # Skip empty lines and comments
        if line and not line.startswith('#'):
            # Remove inline comments
            if '#' in line:
                line = line.split('#')[0].strip()
            if line:  # Make sure there's still content after removing comments
                requirements.append(line)

setup(
    name='django-dbsync',
    version=__version__,
    author='love dazzell',
    author_email='lovepreetdazzell@gmail.com',
    description='Intelligent database synchronization tool for Django projects',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Lovedazzell/django-dbsync',
    project_urls={
        'Bug Tracker': 'https://github.com/Lovedazzell/django-dbsync/issues',
        'Documentation': 'https://django-dbsync.readthedocs.io/',
        'Source Code': 'https://github.com/Lovedazzell/django-dbsync',
    },
    packages=find_packages(exclude=['tests*']),
    include_package_data=True,
    install_requires=requirements,
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 3.2',
        'Framework :: Django :: 4.0',
        'Framework :: Django :: 4.1',
        'Framework :: Django :: 4.2',
        'Framework :: Django :: 5.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Database',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='django database sync migration schema synchronization',
    license='MIT',
    zip_safe=False,
    platforms=['any'],
    
    # Entry points for command line tools (optional)
    entry_points={
        'console_scripts': [
            'django-dbsync=django_dbsync.cli:main',
        ],
    },
    
    # Package data
    package_data={
        'django_dbsync': [
            'templates/django_dbsync/*.html',
            'static/django_dbsync/css/*.css',
            'static/django_dbsync/js/*.js',
        ],
    },
    
    # Test suite
    test_suite='tests',
    tests_require=[
        'pytest>=6.0',
        'pytest-django>=4.0',
        'pytest-cov>=2.0',
    ],
    
    # Additional metadata
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-django>=4.0',
            'pytest-cov>=2.0',
            'black>=22.0',
            'flake8>=4.0',
            'isort>=5.0',
            'mypy>=0.900',
        ],
        'mysql': ['mysqlclient>=2.0'],
        'postgresql': ['psycopg2-binary>=2.8'],
        'oracle': ['cx_Oracle>=8.0'],
    },
)