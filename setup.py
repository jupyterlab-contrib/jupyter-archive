from setuptools import setup
from setuptools import find_packages

setup(name='jupyter-archive',
      version='0.3.0',
      author='Hadrien Mary',
      author_email='hadrien.mary@gmail.com',
      url='https://github.com/hadim/jupyter-archive/',
      description='Download folder as archive in Jupyter.',
      long_description_content_type='text/markdown',
      packages=find_packages(),
      classifiers=[
              'Development Status :: 5 - Production/Stable',
              'Intended Audience :: Developers',
              'Natural Language :: English',
              'License :: OSI Approved :: BSD License',
              'Operating System :: OS Independent',
              'Programming Language :: Python',
              'Programming Language :: Python :: 3',
              ])
