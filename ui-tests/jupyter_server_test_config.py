"""Server configuration for integration tests.

!! Never use this configuration in production because it
opens the server to the world and provide access to JupyterLab
JavaScript objects through the global window variable.
"""
try:
    # Available from JupyterLab 4 and later
    from jupyterlab.galata import configure_jupyter_server

    configure_jupyter_server(c)

    # Option specific for notebook v7+
    import jupyterlab
    from pathlib import Path
    c.JupyterNotebookApp.expose_app_in_browser = True
    c.LabServerApp.extra_labextensions_path = str(Path(jupyterlab.__file__).parent / "galata")

except ImportError:
    from tempfile import mkdtemp

    c.ServerApp.port = 8888
    c.ServerApp.port_retries = 0
    c.ServerApp.open_browser = False

    c.ServerApp.root_dir = mkdtemp(prefix='galata-test-')
    c.ServerApp.token = ""
    c.ServerApp.password = ""
    c.ServerApp.disable_check_xsrf = True
    c.LabApp.expose_app_in_browser = True

# Uncomment to set server log level to debug level
# c.ServerApp.log_level = "DEBUG"
