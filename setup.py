# Inside setup.py
from setuptools import setup, find_packages

setup(
    name='docsible',
    version='0.4.4',
    packages=find_packages(),
    include_package_data=True,
    author='Lucian BLETAN',
    author_email='neuraluc@gmail.com',
    url='https://github.com/exaluc/docsible/',
    description='Doc generator for ansible role',
    long_description="",
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Click',
        'PyYAML',
        'Jinja2'
    ],
    entry_points='''
        [console_scripts]
        docsible=docsible.cli:doc_the_role
    ''',
    
    classifiers=[
        # As from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        # 'Development Status :: 1 - Planning',
        # 'Development Status :: 2 - Pre-Alpha',
        # 'Development Status :: 3 - Alpha',
        'Development Status :: 4 - Beta',
        # 'Development Status :: 5 - Production/Stable',
        # 'Development Status :: 6 - Mature',
        # 'Development Status :: 7 - Inactive',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Operating System :: MacOS',
        'Operating System :: Unix',
        'Programming Language :: Python',
        #'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
