# X4D v0.6.6

This extension is under development. Many features remain unfinished due to time constraints. I will keep improving it, and contributions are welcome to help complete its functionality.

## What’s new in 0.6.6

- Embedded material browser with Blender-native material thumbnails and clickable objects using the selected material. No custom preview renderer or changes to your CPU/GPU settings; native thumbnails are not a pixel-for-pixel copy of the Properties preview widget.
- Click a material to show its native Material Properties. Double-click to open a reusable shader node window; selecting another material updates that window.
- Press Delete while the pointer is inside the material browser to remove the selected material, including its object assignments. Ctrl+Z restores it.
- Selecting an input object of a Boolean or Volume generator in the Outliner shows an editable wireframe. Deselect it to hide the wireframe; moving it updates the generated result.
- Fixed Boolean input evaluation and Volume Builder updates losing edits to input geometry.
- Fixed the Region Render callback cleanup error when completing or cancelling a region selection.
- Clicking an object, including the already active object, now returns the attribute manager from Material Properties to object controls.

Tested on Windows with Blender **5.2.3 LTS**. Blender **4.5** remains the minimum compatibility target, not an additional tested version.

## Install / 安装

Download **x4d_workflow-0.6.6.zip** and install it using Blender Preferences → Get Extensions → Install from Disk. Disable the previous version before updating, then enable the new version. Do not install the source archive as an extension.

下载 **x4d_workflow-0.6.6.zip**，在 Blender 偏好设置 → 获取扩展 → 从磁盘安装。更新前先停用旧版，安装后启用新版。源码包不是插件安装包。

## 中文更新说明

- 新增内嵌材质浏览器、原生缩略图与材质使用对象列表。
- 单击显示材质属性；双击打开可复用并随所选材质同步的节点窗口。
- 材质面板内按 Del 删除所选材质，Ctrl+Z 恢复。
- 布尔、体积输入对象选中时显示可编辑线框，取消选择后隐藏。
- 修复布尔求值、体积输入编辑更新、区域渲染回调清理报错，以及点击对象后属性仍停留在材质页的问题。

Minimum compatibility target: Blender 4.5. Actual runtime tests: Windows / Blender 5.2.3 LTS. Other versions are not claimed as tested.
