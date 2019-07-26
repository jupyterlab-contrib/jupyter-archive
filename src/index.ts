import {
  JupyterFrontEnd, JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { IFileBrowserFactory } from '@jupyterlab/filebrowser';
import { ServerConnection } from '@jupyterlab/services';
import { URLExt } from '@jupyterlab/coreutils';

namespace CommandIDs {
  export const download_archive = 'filebrowser:download-archive';
}

/** Makes a HTTP request, sending a git command to the backend */
function httpRequest(
  url: string,
  method: string,
  request: Object
): Promise<Response> {
  let fullRequest = {
    method: method,
    body: JSON.stringify(request)
  };

  let setting = ServerConnection.makeSettings();
  let fullUrl = URLExt.join(setting.baseUrl, url);
  return ServerConnection.makeRequest(fullUrl, fullRequest, setting);
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
    factory: IFileBrowserFactory, ) => {
    console.log('JupyterLab extension jupyter-archive is activated!');

    const { commands } = app;
    const { tracker } = factory;

    commands.addCommand(CommandIDs.download_archive, {
      execute: () => {
        const widget = tracker.currentWidget;
        if (widget) {
          var selected_folder = widget.selectedItems().next();
          if (selected_folder) {
            console.log('Download the archive!!!!');

            // Generate a random token.
            const rand = () => Math.random().toString(36).substr(2);
            const token = (length: number) => (rand() + rand() + rand() + rand()).substr(0, length);

            let body = Object();
            body.archivePath = selected_folder.path;
            body.archiveToken = token(20);
            body.archiveFormat = 'zip';

            try {
              httpRequest('/archive-download/', 'GET', body);
            } catch (err) {
              throw ServerConnection.NetworkError;
            }
          }
        }
      },
      iconClass: 'jp-MaterialIcon jp-DownloadIcon',
      label: 'Download as an archive'
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
