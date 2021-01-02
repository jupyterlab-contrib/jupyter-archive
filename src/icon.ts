import { LabIcon } from "@jupyterlab/ui-components";

// icon svg import statements
import archiveSvg from "../style/icons/archive.svg";
import unarchiveSvg from "../style/icons/unarchive.svg";

export const archiveIcon = new LabIcon({
  name: "jupyter-archive:archive",
  svgstr: archiveSvg,
});
export const unarchiveIcon = new LabIcon({
  name: "jupyter-archive:unarchive",
  svgstr: unarchiveSvg,
});
