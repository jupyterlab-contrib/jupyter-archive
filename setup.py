"""
jupyter-archive setup
"""
import json
import pathlib

from jupyter_packaging import create_cmdclass, install_npm, ensure_targets, combine_commands, skip_if_exists
import setuptools

HERE = pathlib.Path(__file__).parent.resolve()

# The name of the project
name = "jupyter_archive"

# Get our version
with (HERE / "package.json").open() as f:
    version = json.load(f)["version"]

lab_path = HERE / name / "labextension"

# Representative files that should exist after a successful build
jstargets = [
    str(lab_path / "package.json"),
]

package_data_spec = {name: ["*"]}

labext_name = "@hadim/jupyter-archive"

data_files_spec = [
    ("share/jupyter/labextensions/%s" % labext_name, str(lab_path), "**"),
    ("share/jupyter/labextensions/%s" % labext_name, str(HERE), "install.json"),
    ("etc/jupyter/jupyter_notebook_config.d", "jupyter-config", "jupyter-archive-nb.json"),
    ("etc/jupyter/jupyter_server_config.d", "jupyter-config", "jupyter-archive.json"),
]

cmdclass = create_cmdclass("jsdeps", package_data_spec=package_data_spec, data_files_spec=data_files_spec)

js_command = combine_commands(
    install_npm(HERE, build_cmd="build:prod", npm=["jlpm"]),
    ensure_targets(jstargets),
)

is_repo = (HERE / ".git").exists()
if is_repo:
    cmdclass["jsdeps"] = js_command
else:
    cmdclass["jsdeps"] = skip_if_exists(jstargets, js_command)

long_description = (HERE / "README.md").read_text()

setup_args = dict(
    name=name.replace("_", "-"),
    version=version,
    author="Hadrien Mary, Frederic Collonval",
    author_email="hadrien.mary@gmail.com, fcollonval@gmail.com",
    url="https://github.com/jupyterlab-contrib/jupyter-archive/",
    description="A Jupyterlab extension to make, download and extract archive files.",
    long_description=(pathlib.Path(HERE) / "README.md").read_text(),
    long_description_content_type="text/markdown",
    cmdclass=cmdclass,
    packages=setuptools.find_packages(),
    install_requires=[
        "jupyterlab>=3.0.0rc13,==3.*",
    ],
    extra_requires={"test": ["pytest", "pytest-tornasync"]},
    zip_safe=False,
    include_package_data=True,
    python_requires=">=3.6,<4",
    license="BSD-3-Clause",
    platforms="Linux, Mac OS X, Windows",
    keywords=["Jupyter", "JupyterLab", "JupyterLab3"],
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Framework :: Jupyter",
    ],
)


if __name__ == "__main__":
    setuptools.setup(**setup_args)
