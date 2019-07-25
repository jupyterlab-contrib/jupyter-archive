import {
  JupyterFrontEnd, JupyterFrontEndPlugin
} from '@jupyterlab/application';

import {
  IFileBrowserFactory
} from '@jupyterlab/filebrowser';

namespace CommandIDs {
  export const download_archive = 'filebrowser:download-archive';
}

/**
 * Initialization data for the jupyter-archive extension.
 */
const extension: JupyterFrontEndPlugin<void> = {
  id: 'jupyter-archive',
  autoStart: true,

  requires: [
    IFileBrowserFactory,
  ],

  activate: (app: JupyterFrontEnd,
             factory: IFileBrowserFactory,) => {
    console.log('JupyterLab extension jupyter-archive is activated!');

    const { commands } = app;
    const { tracker } = factory;

    commands.addCommand(CommandIDs.download_archive, {
      execute: () => {
        const widget = tracker.currentWidget;
        if (widget) {
          console.log('Download the archive!!!!');
        }
      },
      iconClass: 'jp-MaterialIcon jp-DownloadIcon',
      label: 'Download as an Archive'
    });

    const selectorOnlyDir = '.jp-DirListing-item[data-isdir="true"]';
    app.contextMenu.addItem({
      command: CommandIDs.download_archive,
      selector: selectorOnlyDir,
      rank: 10
    });

  }
};

export default extension;
