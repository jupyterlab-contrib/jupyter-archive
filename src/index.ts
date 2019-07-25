import {
  JupyterFrontEnd, JupyterFrontEndPlugin
} from '@jupyterlab/application';


/**
 * Initialization data for the jupyter-archive extension.
 */
const extension: JupyterFrontEndPlugin<void> = {
  id: 'jupyter-archive',
  autoStart: true,
  activate: (app: JupyterFrontEnd) => {
    console.log('JupyterLab extension jupyter-archive is activated!');
  }
};

export default extension;
