#!/user/bin/env python

from setuptools import setup

setup(
    name='catbot',
    version='0.1.0',
    author='Bryan Wyatt',
    author_email='brwyatt@gmail.com',
    description=('IRC bot'),
    license='GPLv3',
    keywords='irc bot',
    url='https://github.com/brwyatt/catbot',
    packages=['catbot', 'catbot.plugins'],
    package_dir={'': 'src'},
    include_package_data=False,
    entry_points={
        'console_scripts': [
            'catbot = irc3:run'
        ],
    },
    install_requires=[
        'irc3==1.0.3'
    ]
)
