# X4D modeling shortcuts / 建模快捷键

Press and release the first key, then press the second key. `M → T` means two successive presses, not holding M and T together. Esc or right-click cancels; an incomplete sequence times out after four seconds. Clicking elsewhere cancels the sequence and passes the click through.

连续按键需要依次按下并松开，例如 `M → T`，不是同时按住。Esc 或右键取消，4 秒未完成会自动退出。点击其他位置会退出连续命令。

These bindings apply only to the X4D workspace’s 3D viewport in Object or Mesh Edit mode. Modeling commands require point/edge/polygon mode and suitable geometry. Text editors, material/node editors and other workspaces retain their normal bindings. Blender’s native operators, tool options, F9 adjustments and transform confirmation rules still apply.

快捷键仅接管 X4D 工作区三维视口的对象/网格编辑模式。建模命令需要点、边或面模式以及适用的选择。参数输入框、文字编辑器、材质/节点编辑器和其他工作区使用原有输入规则。

## General / 基础

| Key | Action / 操作 |
| --- | --- |
| E / R / T | Move / Rotate / Scale 移动、旋转、缩放工具 |
| Ctrl+A / Ctrl+Shift+A | Select all / Deselect all 全选、取消全选 |
| H / S | Frame all / Frame selected 框显全部、选中项 |
| C | Make editable in Object mode 对象模式转为可编辑 |
| Alt+G | Group 空对象分组 |
| F1–F5 | Perspective / Top / Right / Front / Quad views |
| Alt+mouse or 1/2/3 + left drag | View navigation 视图导航 |
| Ctrl+B | Render Settings 渲染设置 |
| Ctrl+R / Shift+R | Render current view 渲染当前视图 |
| Alt+Backspace / Alt+Delete | Dissolve in mesh edit mode 融解 |
| Ctrl+Backspace / Ctrl+Delete | Delete components in mesh edit mode 消除组件 |

**Correction:** U → A recalculates normals; it is not Select All. Use Ctrl+A for Select All.

**修正：** U → A 为对齐法线，不再错误地执行全选。全选使用 Ctrl+A。

## Modeling / 建模

| Keys | Command | 命令 | Blender behavior |
| --- | --- | --- | --- |
| M → E | Poly Build | 多边形画笔 | Blender Poly Build tool |
| M → A | Create Point | 创建点 | Add a vertex at the 3D cursor |
| M → D | Close Polygon Hole | 封闭多边形孔洞 | Fill selected boundary loops |
| M → S | Bevel | 倒角 | Bevel selected edges or vertices |
| M → T  /  D | Extrude | 挤压 | Extrude and move the selection |
| M → B  /  B | Bridge | 桥接 | Bridge selected edge loops |
| M → R | Subdivision Weight | 细分曲面权重 | Edit Blender edge or vertex crease |
| M → Q | Weld | 焊接 | Merge selected vertices at their center |
| M → P | Stitch | 缝合 | Merge selected vertices by distance |
| U → C | Collapse | 坍塌 | Collapse selected edges |
| U → Z | Dissolve | 融解 | Dissolve selected components |
| M → N | Delete | 消除 | Delete the selected component type |
| U → O | Optimize | 优化 | Merge selected coincident vertices and remove degenerate edges |
| U → D | Disconnect | 断开连接 | Split selection from neighboring geometry |
| U → P | Split to Object | 分裂 | Separate selected geometry into another object |
| M → H | Symmetrize | 对称化 | Blender symmetrize; default -X to +X |
| K → K  /  M → K | Line Cut | 线性切割 | Blender Knife tool; Enter confirms, Esc cancels |
| K → J  /  M → J | Plane Cut | 平面切割 | Blender Bisect tool |
| K → L  /  M → L | Loop Cut | 循环/路径切割 | Blender Loop Cut and Slide |
| M → F  /  U → S | Subdivide | 切割边 / 细分 | Subdivide selected geometry |
| M → M | Connect Points / Edges | 连接点/边 | Connect selected vertices across faces |
| M → G | Smooth | 熨烫 | Smooth selected vertex positions |
| M → C | Smooth Brush | 平滑笔刷 | Blender mesh Smooth tool |
| M → I | Proportional Editing | 磁铁 | Toggle proportional editing for mesh transforms |
| M → U | Set Point Values | 设置点值 | Set enabled local coordinate components of selected vertices |
| M → O | Slide | 滑动 | Blender vertex slide or edge slide |
| M → V | Rotate Edge | 旋转边 | Rotate selected edges counterclockwise |
| M → W | Inset | 内挤压 / 嵌入 | Inset selected faces |
| M → Z | Move Along Normals | 沿法线移动 | Blender Shrink/Fatten |
| U → A | Align Normals | 对齐法线 | Recalculate selected normals outside |
| U → R | Reverse Normals | 翻转法线 | Reverse selected face normals |
| U → U | Untriangulate | 反三角化 | Join selected triangles into quads |
| U → I | Invert Selection | 反选 | Invert objects or mesh components |
| U → W | Select Connected | 选择连接 | Select linked mesh geometry |
| U → Y | Grow Selection | 扩展选区 | Grow mesh selection |
| U → K | Shrink Selection | 收缩选区 | Shrink mesh selection |
| U → L | Loop Selection | 循环选择 | Expand selected edges to loops |
| U → B | Ring Selection | 环状选择 | Expand selected edges to rings |
| U → Q | Boundary Selection | 轮廓选择 | Convert a face region to its boundary edges |

## Differences / 差异

- These are explicit Blender equivalents, not identical implementations of another application’s tools. The key reference was checked against a locally running 2027 command table and the supplied screenshot; personal shortcut overrides may differ.
- Poly Build uses Blender’s tool; Create Point adds one vertex at the 3D cursor. Weld merges at the selected vertices’ center. Stitch and Optimize use a 0.0001 Blender-unit distance; adjust in the native operator redo panel where available.
- Cut, Plane Cut, Loop Cut and Smooth Brush activate Blender’s corresponding tools. Make the cut with the mouse afterwards. A plain K starts a sequence; use K → K for the knife tool.
- Split to Object separates geometry from the original object. It does not duplicate and retain the same faces in both objects.
- Symmetrize defaults to -X to +X in Blender local coordinates. Set Point Values also uses Blender local coordinates. Subdivision Weight edits Blender’s crease attributes. Proportional Editing is a transform falloff toggle, not a separate magnet brush.
- Shift variants for opening another application's settings dialog are not replicated. Use native tool settings or the redo panel instead. Commands without keys in the supplied menu are not automatically assigned new keys.
- The material browser's blue outline shows all non-empty material slots of the active, selected object. It does not select those materials, assign a material, or switch the selected shader node tree. No selected object or no material slots means no outlines. The selected material still has its separate pressed name button.

材质球的蓝色边框仅表示当前活动且已选中的物体使用了此材质（包括非空材质槽）；不会更改材质选择、材质分配或当前节点窗口。物体没有材质或没有选择物体时，边框全部消失。材质名称按钮的按下状态仍代表当前选中的材质。

## Access / 入口

Tools → Shortcut Reference opens an in-app reference. In mesh edit mode, the viewport Modeling menu lists the same commands and keys.

工具 → 快捷键速查；网格编辑模式下，视口顶部“建模”菜单列出相同命令与快捷键。

Minimum compatibility target: Blender 4.5. Actual runtime tests: Windows / Blender 5.2.3 LTS. Loop/ring selection uses capability-based operator names for version compatibility. Other versions are not claimed as runtime-tested.
