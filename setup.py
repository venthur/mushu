#!/usr/bin/env python


from distutils.core import setup

import libmushu

setup(
    name = 'Mushu',
    version = libmushu.__version__,
    description = 'Brain Computer Interfacing signal acquisition software.',
    long_description = 'A Python library for BCI signal acquisition. It can be used as a stand-alone application or as a library.',
    author = 'Bastian Venthur',
    author_email = 'bastian.venthur@tu-berlin.de',
    url = 'http://venthur.github.io/mushu/',
    download_url = 'http://github.com/venthur/mushu/',
    license = 'GPL2',
    platforms = 'any',
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Healthcare Industry',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Education',
        'Topic :: Scientific/Engineering :: Human Machine Interfaces',
        'Topic :: Scientific/Engineering :: Medical Science Apps.',
        'Topic :: Software Development :: Libraries',
        ],
    packages = ['libmushu', 'libmushu.driver'],
    scripts = ['mushu.py'],
)

