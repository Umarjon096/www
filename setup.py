import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-starko',
    version='0.2',
    packages=['mc',
              'mc.management',
              'mc.management.commands',
              'mc.migrations',
              'mc.utils',
              'mc.views',
              'mc.templatetags'
              ],
    include_package_data=True,
    license='BSD License',  # example license
    description='Opteo-monitor-control',
    long_description=README,
    url='http://www.starko.ru/',
    author='Sergey Stepanov',
    author_email='imbashamba@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License', # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        # Replace these appropriately if you are stuck on Python 2.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires=[
    'Django>=1.7,<1.8',
    'django-jfu',
    'ecdsa',
    'lorem-ipsum-generator',
    'numpy',
    'paramiko',
    'pillow',
    'pycrypto',
    'pytz',
    'requests',
    'scp',
    'six',
    'transliterate',
    'wifi'
    ]
)