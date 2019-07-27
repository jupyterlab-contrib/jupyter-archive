import {
  JupyterFrontEnd, JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { IFileBrowserFactory } from '@jupyterlab/filebrowser';
import { ServerConnection } from '@jupyterlab/services';
import { URLExt } from '@jupyterlab/coreutils';

namespace CommandIDs {
  export const download_archive = 'filebrowser:download-archive';
}

function archiveRequest(
  path: string,
): Promise<void> {

  // Generate a random token.
  const rand = () => Math.random().toString(36).substr(2);
  const token = (length: number) => (rand() + rand() + rand() + rand()).substr(0, length);

  const settings = ServerConnection.makeSettings();

  let url = URLExt.join(settings.baseUrl, "/archive-download");
  url += `?archivePath=${path}&archiveToken=${token(20)}&archiveFormat=${'zip'}`;

  const request = { method: 'GET' };

  return ServerConnection.makeRequest(url, request, settings).then(response => {
    if (response.status !== 200) {
      throw new ServerConnection.ResponseError(response);
    }

    // Check the browser is Chrome https://stackoverflow.com/a/9851769
    const chrome = (window as any).chrome;
    const isChrome = !!chrome && (!!chrome.webstore || !!chrome.runtime);
    if (isChrome) {
      // Workaround https://bugs.chromium.org/p/chromium/issues/detail?id=455987
      window.open(response.url);
    } else {
      let element = document.createElement('a');
      document.body.appendChild(element);
      element.setAttribute('href', response.url);
      element.setAttribute('download', '');
      element.click();
      document.body.removeChild(element);

      console.log(response);
    }
  });
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
            archiveRequest(selected_folder.path);
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
