"""Server configuration for integration tests.

!! Never use this configuration in production because it
opens the server to the world and provide access to JupyterLab
JavaScript objects through the global window variable.
"""
from jupyterlab.galata import configure_jupyter_server

configure_jupyter_server(c)

# Option specific for notebook v7+
import jupyterlab
from pathlib import Path
c.JupyterNotebookApp.expose_app_in_browser = True
c.LabServerApp.extra_labextensions_path = str(Path(jupyterlab.__file__).parent / "galata")

# Uncomment to set server log level to debug level
# c.ServerApp.log_level = "DEBUG"
