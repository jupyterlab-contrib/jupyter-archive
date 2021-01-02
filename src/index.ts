import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin,
} from "@jupyterlab/application";
import { showErrorMessage } from "@jupyterlab/apputils";
import { URLExt, PathExt } from "@jupyterlab/coreutils";
import { ISettingRegistry } from "@jupyterlab/settingregistry";
import { IFileBrowserFactory } from "@jupyterlab/filebrowser";
import { ServerConnection } from "@jupyterlab/services";
import { each } from "@lumino/algorithm";
import { IDisposable } from "@lumino/disposable";
import { Menu } from "@lumino/widgets";
import { archiveIcon, unarchiveIcon } from "./icon";

const DIRECTORIES_URL = "directories";
const EXTRACT_ARCHVE_URL = "extract-archive";
type ArchiveFormat =
  | null
  | "zip"
  | "tgz"
  | "tar.gz"
  | "tbz"
  | "tbz2"
  | "tar.bz"
  | "tar.bz2"
  | "txz"
  | "tar.xz";

namespace CommandIDs {
  export const downloadArchive = "filebrowser:download-archive";
  export const extractArchive = "filebrowser:extract-archive";
  export const downloadArchiveCurrentFolder =
    "filebrowser:download-archive-current-folder";
}

function downloadArchiveRequest(
  path: string,
  archiveFormat: ArchiveFormat,
  followSymlinks: string,
  downloadHidden: string
): Promise<void> {
  const settings = ServerConnection.makeSettings();

  let baseUrl = settings.baseUrl;
  let url = URLExt.join(baseUrl, DIRECTORIES_URL, URLExt.encodeParts(path));

  const fullurl = new URL(url);

  // Generate a random token.
  const rand = () => Math.random().toString(36).substr(2);
  const token = (length: number) =>
    (rand() + rand() + rand() + rand()).substr(0, length);

  fullurl.searchParams.append("archiveToken", token(20));
  fullurl.searchParams.append("archiveFormat", archiveFormat);
  fullurl.searchParams.append("followSymlinks", followSymlinks);
  fullurl.searchParams.append("downloadHidden", downloadHidden);

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

  return ServerConnection.makeRequest(url, request, settings).then(
    (response) => {
      if (response.status !== 200) {
        throw new ServerConnection.ResponseError(response);
      }
    }
  );
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
      ".tar.xz",
    ];
    let archiveFormat: ArchiveFormat; // Default value read from settings
    let followSymlinks: string; // Default value read from settings
    let downloadHidden: string; // Default value read from settings

    // matches anywhere on filebrowser
    const selectorContent = ".jp-DirListing-content";

    // matches directory filebrowser items
    const selectorOnlyDir = '.jp-DirListing-item[data-isdir="true"]';

    // matches file filebrowser items
    const selectorNotDir = '.jp-DirListing-item[data-isdir="false"]';

    // Create submenus
    const archiveFolder = new Menu({
      commands,
    });
    archiveFolder.title.label = "Download As";
    archiveFolder.title.icon = archiveIcon;
    const archiveCurrentFolder = new Menu({
      commands,
    });
    archiveCurrentFolder.title.label = "Download Current Folder As";
    archiveCurrentFolder.title.icon = archiveIcon;

    ["zip", "tar.bz2", "tar.gz", "tar.xz"].forEach((format) => {
      archiveFolder.addItem({
        command: CommandIDs.downloadArchive,
        args: { format },
      });
      archiveCurrentFolder.addItem({
        command: CommandIDs.downloadArchiveCurrentFolder,
        args: { format },
      });
    });

    // Reference to menu items
    let archiveFolderItem: IDisposable;
    let archiveCurrentFolderItem: IDisposable;

    function updateFormat(newFormat: ArchiveFormat, oldFormat: ArchiveFormat) {
      if (newFormat !== oldFormat) {
        if (
          newFormat === null ||
          oldFormat === null ||
          oldFormat === undefined
        ) {
          if (oldFormat !== undefined) {
            archiveFolderItem.dispose();
            archiveCurrentFolderItem.dispose();
          }

          if (newFormat === null) {
            archiveFolderItem = app.contextMenu.addItem({
              selector: selectorOnlyDir,
              rank: 10,
              type: "submenu",
              submenu: archiveFolder,
            });

            archiveCurrentFolderItem = app.contextMenu.addItem({
              selector: selectorContent,
              rank: 3,
              type: "submenu",
              submenu: archiveCurrentFolder,
            });
          } else {
            archiveFolderItem = app.contextMenu.addItem({
              command: CommandIDs.downloadArchive,
              selector: selectorOnlyDir,
              rank: 10,
            });

            archiveCurrentFolderItem = app.contextMenu.addItem({
              command: CommandIDs.downloadArchiveCurrentFolder,
              selector: selectorContent,
              rank: 3,
            });
          }
        }

        archiveFormat = newFormat;
      }
    }

    // Load the settings
    settingRegistry
      .load("@hadim/jupyter-archive:archive")
      .then((settings) => {
        settings.changed.connect((settings) => {
          const newFormat = settings.get("format").composite as ArchiveFormat;
          updateFormat(newFormat, archiveFormat);
          followSymlinks = settings.get("followSymlinks").composite as string;
          downloadHidden = settings.get("downloadHidden").composite as string;
        });

        const newFormat = settings.get("format").composite as ArchiveFormat;
        updateFormat(newFormat, archiveFormat);
        followSymlinks = settings.get("followSymlinks").composite as string;
        downloadHidden = settings.get("downloadHidden").composite as string;
      })
      .catch((reason) => {
        console.error(reason);
        showErrorMessage(
          "Fail to read settings for '@hadim/jupyter-archive:archive'",
          reason
        );
      });

    // Add the 'downloadArchive' command to the file's menu.
    commands.addCommand(CommandIDs.downloadArchive, {
      execute: (args) => {
        const widget = tracker.currentWidget;
        if (widget) {
          each(widget.selectedItems(), (item) => {
            if (item.type == "directory") {
              const format = args["format"] as ArchiveFormat;
              downloadArchiveRequest(
                item.path,
                allowedArchiveExtensions.indexOf("." + format) >= 0
                  ? format
                  : archiveFormat,
                followSymlinks,
                downloadHidden
              );
            }
          });
        }
      },
      icon: (args) => ("format" in args ? "" : archiveIcon),
      label: (args) => {
        const format = (args["format"] as ArchiveFormat) || "";
        const label = format.replace(".", " ").toLocaleUpperCase();
        return label ? `${label} Archive` : "Download as an Archive";
      },
    });

    // Add the 'extractArchive' command to the file's menu.
    commands.addCommand(CommandIDs.extractArchive, {
      execute: () => {
        const widget = tracker.currentWidget;
        if (widget) {
          each(widget.selectedItems(), (item) => {
            extractArchiveRequest(item.path);
          });
        }
      },
      icon: unarchiveIcon,
      isVisible: () => {
        const widget = tracker.currentWidget;
        let visible = false;
        if (widget) {
          const firstItem = widget.selectedItems().next();
          const basename = PathExt.basename(firstItem.path);
          const splitName = basename.split(".");
          let lastTwoParts = "";
          if (splitName.length >= 2) {
            lastTwoParts =
              "." + splitName.splice(splitName.length - 2, 2).join(".");
          }
          visible =
            allowedArchiveExtensions.indexOf(PathExt.extname(basename)) >= 0 ||
            allowedArchiveExtensions.indexOf(lastTwoParts) >= 0;
        }
        return visible;
      },
      label: "Extract Archive",
    });

    app.contextMenu.addItem({
      command: CommandIDs.extractArchive,
      selector: selectorNotDir,
      rank: 10,
    });

    // Add the 'downloadArchiveCurrentFolder' command to file browser content.
    commands.addCommand(CommandIDs.downloadArchiveCurrentFolder, {
      execute: (args) => {
        const widget = tracker.currentWidget;
        if (widget) {
          const format = args["format"] as ArchiveFormat;
          downloadArchiveRequest(
            widget.model.path,
            allowedArchiveExtensions.indexOf("." + format) >= 0
              ? format
              : archiveFormat,
            followSymlinks,
            downloadHidden
          );
        }
      },
      icon: (args) => ("format" in args ? "" : archiveIcon),
      label: (args) => {
        const format = (args["format"] as ArchiveFormat) || "";
        const label = format.replace(".", " ").toLocaleUpperCase();
        return label
          ? `${label} Archive`
          : "Download Current Folder as an Archive";
      },
    });
  },
};

export default extension;
