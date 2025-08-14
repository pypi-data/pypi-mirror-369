import setuptools
import os

# Get the directory where setup.py is located
here = os.path.abspath(os.path.dirname(__file__))

# Get the long description from the README file
with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Get the dependencies from the requirements file
with open(os.path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    install_requires = f.read().splitlines()

setuptools.setup(name="librespot-spotizerr",
                 version="0.3.0",
                 description="Spotizerr's python librespot implementation",
                 long_description=long_description,
                 long_description_content_type="text/markdown",
                 author="Xoconoch",
                 url="https://github.com/Xoconoch/librespot-spotizerr",
                 license="Apache-2.0", # SPDX identifier
                 packages=setuptools.find_packages("."),
                 install_requires=install_requires,
                 classifiers=[
                     "Development Status :: 1 - Planning",
                     # "License :: OSI Approved :: Apache Software License", # Removed
                     "Topic :: Multimedia :: Sound/Audio"
                 ])
