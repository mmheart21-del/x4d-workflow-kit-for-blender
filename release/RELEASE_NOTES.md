# X4D v0.7.6

This release brings together the changes since v0.6.6.

- **Tags and source lists:** Add, rename, reorder and remove object tags. The tag menu includes materials, smooth shading, point/edge/face sets, vertex weights and target constraints. Cloner and volume source lists support adding selected objects, toggling individual inputs and reordering them.
- **Cloning and fields:** Cloners accept multiple sources and cycle through them in list order. Sources are parented and hidden while in use, with their previous state restored on removal. Fields have viewport handles, including inner and outer controls for box, sphere and linear fields.
- **Modeling:** Added contextual point, edge and face toolbars, M/U/K command popups and the eight-direction V menu. U → L and U → B preview loops and rings and stay active after confirmation. Left toolbar extrusion and inset start on drag, confirm on release and offer mode choices on long press.
- **Materials and localization:** Selecting an object outlines its material tiles independently of the active material. Materials appear newest first, and common interface labels and new data names follow the Blender language setting.
- **Viewport:** Improved toolbar icon contrast and kept the creation rail clear of the N sidebar.

## 中文更新

- 对象标签、克隆源与体积源采用列表管理，支持添加、排序和移除。标签可重命名，源对象可逐项启停。
- 克隆支持多源轮换、自动收纳与隐藏原件。域新增视口手柄，盒形、球形和线性域可调整内外范围。
- 新增点、边、面工具栏、M/U/K 连续快捷键弹窗和 V 八方向菜单。循环与环状预览可连续选择。左栏挤压、内挤压改为拖动操作，长按按钮可选方式。
- 材质面板支持物体关联高亮与新旧排序。改进中英文命名、工具栏图标和 N 面板共存。

## Install

Download **x4d_workflow-0.7.6.zip** for Install from Disk, or follow the remote repository instructions on the project homepage.

Minimum compatibility target: Blender 4.5. Runtime tested on Windows with Blender 5.2.3 LTS.
