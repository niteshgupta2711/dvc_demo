from setuptools import setup,find_packages
AUTHOR='Nitesh'
AUTHOR_EMAIL='guptanitesh2711@gmail.com'
setup(author=AUTHOR,
author_email=AUTHOR_EMAIL,
description='demo for dvc',
name='demo',packages=find_packages(),# any any foler with __init__.py init,
install_requires=['numpy','sklearn'])