#!/usr/bin/env python


from distutils.core import setup


setup(
    name = 'Mushu',
    version = '0.0',
    description = 'Brain Computer Interfacing signal acquisition software.',
    author = 'Bastian Venthur',
    author_email = 'bastian.venthur@tu-berlin.de',
    url = 'http://github.com/venthur/mushu/',
    packages = ['libmushu', 'libmushu.amps'],
    scripts = ['mushu.py'],
)

