# -*- coding: UTF-8 -*-
import sys
import glob
from setuptools import find_packages, setup

if sys.version_info < (3,6):
    print('Python >= 3.6 required. Python %s.%s found' % (sys.version_info[0], sys.version_info[1]))
    sys.exit(1)

try:
    from setuptools import find_packages, setup
except Exception:
    if sys.version_info > (3, 4):
        # maybe /usr/local/lib/pythonX.Y/site-packages is missing?
        import os
        usrlocalpath = "/usr/local/lib/python%u.%u/site-packages" % (sys.version_info[0], sys.version_info[1])
        if os.path.exists(usrlocalpath):
            sys.path.insert(0, usrlocalpath)
            from setuptools import find_packages, setup
        else:
            raise ImportError(usrlocalpath+" does not exist...")

sys.path.insert(0,'src')
from domainmagic import __version__

setup(
    name = 'domainmagic',
    version = __version__,
    description = "Python library for all sorts of domain lookup related stuff (rbl lookups, extractors etc)",
    author = "O. Schacher",
    url='https://gitlab.com/fumail/domainmagic',
    download_url='https://gitlab.com/fumail/domainmagic/-/archive/master/domainmagic-master.tar.bz2',
    author_email = "oli@fuglu.org",
    package_dir={'':'src'},
    packages = find_packages('src'),
    install_requires=[
        'dnspython',
        'geoip2',
    ],
    long_description = """Python library for all sorts of domain lookup related stuff (rbl lookups, extractors etc)""" ,
    data_files=[
        ('/etc/domainmagic',glob.glob('conf/*.dist')),
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: Internet :: Name Service (DNS)',
        'Environment :: No Input/Output (Daemon)',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX',
        'Programming Language :: Python',
    ],
    license='Apache Software License',
) 
