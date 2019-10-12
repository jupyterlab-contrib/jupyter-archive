import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from "@jupyterlab/application";

import { each } from "@phosphor/algorithm";
import { IFileBrowserFactory } from "@jupyterlab/filebrowser";
import { ServerConnection } from "@jupyterlab/services";
import { URLExt, ISettingRegistry } from "@jupyterlab/coreutils";
import { showErrorMessage, showDialog, Dialog } from "@jupyterlab/apputils";
import { Menu } from "@phosphor/widgets";

const DIRECTORIES_URL = "directories";
const EXTRACT_ARCHVE_URL = "extract-archive";

namespace CommandIDs {
  export const downloadArchive = "filebrowser:download-archive";
  export const extractArchive = "filebrowser:extract-archive";
  export const downloadArchiveCurrentFolder =
    "filebrowser:download-archive-current-folder";
}

function downloadArchiveRequest(
  path: string,
  archiveFormat: string
): Promise<void> {
  const settings = ServerConnection.makeSettings();

  let baseUrl = settings.baseUrl;
  let url = URLExt.join(baseUrl, DIRECTORIES_URL, URLExt.encodeParts(path));

  const fullurl = new URL(url);

  // Generate a random token.
  const rand = () =>
    Math.random()
      .toString(36)
      .substr(2);
  const token = (length: number) =>
    (rand() + rand() + rand() + rand()).substr(0, length);

  fullurl.searchParams.append("archiveToken", token(20));
  fullurl.searchParams.append("archiveFormat", archiveFormat);

  const xsrfTokenMatch = document.cookie.match("\\b_xsrf=([^;]*)\\b");
  if (xsrfTokenMatch) {
    fullurl.searchParams.append("_xsrf", xsrfTokenMatch[1]);
  }

  url = fullurl.toString();

  // Check the browser is Chrome https://stackoverflow.com/a/9851769
  const chrome = (window as any).chrome;
  const isChrome = !!chrome && (!!chrome.webstore || !!chrome.runtime);
  if (isChrome) {
    // Workaround https://bugs.chromium.org/p/chromium/issues/detail?id=455987
    window.open(url);
  } else {
    let element = document.createElement("a");
    document.body.appendChild(element);
    element.setAttribute("href", url);
    element.setAttribute("download", "");
    element.click();
    document.body.removeChild(element);
  }

  return void 0;
}

function extractArchiveRequest(path: string): Promise<void> {
  const settings = ServerConnection.makeSettings();

  let baseUrl = settings.baseUrl;
  let url = URLExt.join(baseUrl, EXTRACT_ARCHVE_URL, URLExt.encodeParts(path));

  const fullurl = new URL(url);

  const xsrfTokenMatch = document.cookie.match("\\b_xsrf=([^;]*)\\b");
  if (xsrfTokenMatch) {
    fullurl.searchParams.append("_xsrf", xsrfTokenMatch[1]);
  }

  url = fullurl.toString();
  const request = { method: "GET" };

  return ServerConnection.makeRequest(url, request, settings).then(response => {
    if (response.status !== 200) {
      throw new ServerConnection.ResponseError(response);
    }
  });
}

/**
 * Initialization data for the jupyter-archive extension.
 */
const extension: JupyterFrontEndPlugin<void> = {
  id: "@jupyterlab/archive:archive",
  autoStart: true,

  requires: [IFileBrowserFactory, ISettingRegistry],

  activate: (
    app: JupyterFrontEnd,
    factory: IFileBrowserFactory,
    settingRegistry: ISettingRegistry
  ) => {
    console.log("JupyterLab extension jupyter-archive is activated!");

    const { commands } = app;
    const { tracker } = factory;

    const allowedArchiveExtensions = [
      ".zip",
      ".tgz",
      ".tar.gz",
      ".tbz",
      ".tbz2",
      ".tar.bz",
      ".tar.bz2",
      ".txz",
      ".tar.xz"
    ];
    let archiveFormat: string = "zip";

    // Create submenu
    const archives = new Menu({
      commands
    });
    archives.title.label = "Download As ";
    archives.title.iconClass = "jp-MaterialIcon jp-DownloadIcon";

    ["zip", "tar.bz2", "tar.gz", "tar.xz"].forEach(format =>
      archives.addItem({
        command: CommandIDs.downloadArchive,
        args: { format }
      })
    );

    // Load the settings
    settingRegistry
      .load("@hadim/jupyter-archive:archive")
      .then(settings => {
        settings.changed.connect(settings => {
          const newFormat = settings.get("format").composite as string;
          if (
            newFormat !== archiveFormat &&
            (newFormat === null || archiveFormat === null)
          ) {
            showDialog({
              title: "Information",
              body:
                "You will need to reload the page to apply the new default archive format.",
              buttons: [Dialog.okButton()]
            });
          } else {
            archiveFormat = newFormat;
          }
        });
        archiveFormat = settings.get("format").composite as string;
      })
      .then(() => {
        if (archiveFormat === null) {
          app.contextMenu.addItem({
            selector: selectorOnlyDir,
            rank: 10,
            type: "submenu",
            submenu: archives
          });
        } else {
          app.contextMenu.addItem({
            command: CommandIDs.downloadArchive,
            selector: selectorOnlyDir,
            rank: 10
          });
        }
      })
      .catch(reason => {
        console.error(reason);
        showErrorMessage(
          "Fail to read settings for '@hadim/jupyter-archive:archive'",
          reason
        );
      });

    // matches anywhere on filebrowser
    const selectorContent = ".jp-DirListing-content";

    // matches all filebrowser items
    const selectorOnlyDir = '.jp-DirListing-item[data-isdir="true"]';

    // Add the 'downloadArchive' command to the file's menu.
    commands.addCommand(CommandIDs.downloadArchive, {
      execute: args => {
        const widget = tracker.currentWidget;
        if (widget) {
          each(widget.selectedItems(), item => {
            if (item.type == "directory") {
              const format = args["format"] as string;
              downloadArchiveRequest(
                item.path,
                allowedArchiveExtensions.indexOf("." + format) >= 0
                  ? format
                  : archiveFormat
              );
            }
          });
        }
      },
      iconClass: args =>
        "format" in args ? "" : "jp-MaterialIcon jp-DownloadIcon",
      label: args => {
        const format = (args["format"] as string) || "";
        const label = format.replace(".", " ");
        return label ? `${label} Archive` : "Download as an archive";
      }
    });

    // Add the 'extractArchive' command to the file's menu.
    commands.addCommand(CommandIDs.extractArchive, {
      execute: () => {
        const widget = tracker.currentWidget;
        if (widget) {
          each(widget.selectedItems(), item => {
            extractArchiveRequest(item.path);
          });
        }
      },
      iconClass: "jp-MaterialIcon jp-DownCaretIcon",
      label: "Extract archive"
    });

    // Add a command for each archive extensions
    // TODO: use only one command and accept multiple extensions.
    allowedArchiveExtensions.forEach(extension => {
      const selector = '.jp-DirListing-item[title$="' + extension + '"]';
      app.contextMenu.addItem({
        command: CommandIDs.extractArchive,
        selector: selector,
        rank: 10
      });
    });

    // Add the 'downloadArchiveCurrentFolder' command to file browser content.
    commands.addCommand(CommandIDs.downloadArchiveCurrentFolder, {
      execute: () => {
        const widget = tracker.currentWidget;
        if (widget) {
          downloadArchiveRequest(widget.model.path, archiveFormat);
        }
      },
      iconClass: "jp-MaterialIcon jp-DownloadIcon",
      label: "Download current folder as an archive"
    });

    app.contextMenu.addItem({
      command: CommandIDs.downloadArchiveCurrentFolder,
      selector: selectorContent,
      rank: 3
    });
  }
};

export default extension;
