from os.path import join as pjoin
from setuptools import find_packages, setup

from setupbase import (
    create_cmdclass, install_npm, ensure_targets,
    find_packages, combine_commands, ensure_python,
    get_version, HERE
)

# The name of the project
name='jupyter_archive'

# Ensure a valid python version
ensure_python('>=3.5')

# Get our version
version = get_version(pjoin(name, '_version.py'))

lab_path = pjoin(HERE, name, 'labextension')

# Representative files that should exist after a successful build
jstargets = [
    pjoin(HERE, 'lib', 'index.js'),
]

package_data_spec = {
    name: [
        '*'
    ]
}

data_files_spec = [
    ('share/jupyter/lab/extensions', lab_path, '*.tgz'),
    ('etc/jupyter/jupyter_notebook_config.d',
     'jupyter-config/jupyter_notebook_config.d', 'jupyter_archive.json'),
]

cmdclass = create_cmdclass('jsdeps',
    package_data_spec=package_data_spec,
    data_files_spec=data_files_spec
)

cmdclass['jsdeps'] = combine_commands(
    install_npm(HERE, build_cmd='build:all'),
    ensure_targets(jstargets),
)

setup(name=name.replace('_', '-'),
      version=version,
      author='Hadrien Mary',
      author_email='hadrien.mary@gmail.com',
      url='https://github.com/hadim/jupyter-archive/',
      description='Make, download and extract archive files.',
      long_description_content_type='text/markdown',
      cmdclass=cmdclass,
      packages=find_packages(),
      classifiers=[
              'Development Status :: 5 - Production/Stable',
              'Intended Audience :: Developers',
              'Natural Language :: English',
              'License :: OSI Approved :: BSD License',
              'Operating System :: OS Independent',
              'Programming Language :: Python',
              'Programming Language :: Python :: 3',
              ],
      include_package_data = True,
      install_requires=[
            'notebook'
      ],
      extras_require={
            "test": ["jupyterlab", "pytest"]
      }
)
