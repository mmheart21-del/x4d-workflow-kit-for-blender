# X4D v0.7.6

This release brings together the changes since v0.6.6.

- **Tags and source lists:** Add, rename, reorder and remove object tags. The tag menu includes materials, smooth shading, point/edge/face sets, vertex weights and target constraints. Cloner and volume source lists support adding selected objects, toggling individual inputs and reordering them.
- **Cloning and fields:** Cloners accept multiple sources and cycle through them in list order. Sources are parented and hidden while in use, with their previous state restored on removal. Fields have viewport handles, including inner and outer controls for box, sphere and linear fields.
- **Modeling:** Added contextual point, edge and face toolbars, M/U/K command popups and the eight-direction V menu. U → L and U → B preview loops and rings and stay active after confirmation. Left toolbar extrusion and inset start on drag, confirm on release and offer mode choices on long press.
- **Materials and localization:** Selecting an object outlines its material tiles independently of the active material. Materials appear newest first, and common interface labels and new data names follow the Blender language setting.
- **Viewport:** Improved toolbar icon contrast and kept the creation rail clear of the N sidebar.

## Install

### Remote installation

1. Open the [X4D self-service page](https://plugins.laoma3d.xyz/p/2) and click **免费获取 (Get for Free)** to receive the repository URL and access token.
2. In Blender, go to **Edit → Preferences → Get Extensions → Repositories**. Add a remote repository, enter the URL, and enable and fill in **Access Token**.
3. Refresh the repository, find **X4D Workflow Kit**, and click **Install**. Use the same repository to check for and download updates.

### Install from disk

Download **x4d_workflow-0.7.6.zip**, then use **Preferences → Get Extensions → Install from Disk**.

Minimum compatibility target: Blender 4.5. Runtime tested on Windows with Blender 5.2.3 LTS.
