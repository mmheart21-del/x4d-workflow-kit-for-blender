This extension is under development. Many features remain unfinished due to time constraints. I will keep improving it, and contributions are welcome to help complete its functionality.

# X4D Workflow Kit for Blender

![Version](https://img.shields.io/badge/version-v0.6.6-blue)

[简体中文](README_ZH.md) · [Download](https://github.com/mmheart21-del/x4d-workflow-kit-for-blender/releases/tag/v0.6.6) · [Report an issue](https://github.com/mmheart21-del/x4d-workflow-kit-for-blender/issues) · GPL-3.0-or-later · Windows · Blender 4.5+ target

A Blender extension providing a dedicated workspace, compact creation palettes, modeling generators, deformers, MoGraph-style tools, fields and familiar navigation shortcuts. This independent project is under active development.

Prefer to keep your current interface and use only some X4D features? Take a look at [Swift 4D](https://plugins.laoma3d.xyz/p/1).

## What’s new in 0.6.6

- Embedded material browser with Blender-native material thumbnails and clickable objects using the selected material. No custom preview renderer or changes to your CPU/GPU settings; native thumbnails are not a pixel-for-pixel copy of the Properties preview widget.
- Click a material to show its native Material Properties. Double-click to open a reusable shader node window; selecting another material updates that window.
- Press Delete while the pointer is inside the material browser to remove the selected material, including its object assignments. Ctrl+Z restores it.
- Selecting an input object of a Boolean or Volume generator in the Outliner shows an editable wireframe. Deselect it to hide the wireframe; moving it updates the generated result.
- Fixed Boolean input evaluation and Volume Builder updates losing edits to input geometry.
- Fixed the Region Render callback cleanup error when completing or cancelling a region selection.
- Clicking an object, including the already active object, now returns the attribute manager from Material Properties to object controls.

Tested on Windows with Blender **5.2.3 LTS**. Blender **4.5** remains the minimum compatibility target, not an additional tested version.

## Community & contributing

**GitHub is the primary home for X4D discussion, bug reports and development. No separate chat server is required.** Start with the [community guide](https://github.com/mmheart21-del/x4d-workflow-kit-for-blender/discussions/2).

| I want to… | Go to |
| --- | --- |
| Ask about installation or usage | [Q&A](https://github.com/mmheart21-del/x4d-workflow-kit-for-blender/discussions/categories/q-a) |
| Chat about workflows or share experiences | [General](https://github.com/mmheart21-del/x4d-workflow-kit-for-blender/discussions/categories/general) |
| Suggest or explore an idea | [Ideas](https://github.com/mmheart21-del/x4d-workflow-kit-for-blender/discussions/categories/ideas) |
| Share a creation or experiment | [Show and tell](https://github.com/mmheart21-del/x4d-workflow-kit-for-blender/discussions/categories/show-and-tell) |
| Report a reproducible bug or request a specific feature | [Issue forms](https://github.com/mmheart21-del/x4d-workflow-kit-for-blender/issues/new/choose) |
| Help fix, develop, optimize, test or document X4D | [Development collaboration](https://github.com/mmheart21-del/x4d-workflow-kit-for-blender/discussions/1) |
| Submit a code change for review | [Pull Requests](https://github.com/mmheart21-del/x4d-workflow-kit-for-blender/pulls) |
| Follow project updates | [Announcements](https://github.com/mmheart21-del/x4d-workflow-kit-for-blender/discussions/categories/announcements) |

Bug reports should include X4D/Blender versions, OS, steps to reproduce, expected/actual results and screenshots or error output. If unsure whether something is a bug, ask in Q&A first.

To contribute: discuss the approach → open or link an Issue → coordinate the task → submit a PR with test results → maintainer review and merge. Anyone can participate; participation does not automatically grant repository write access. See [CONTRIBUTING](CONTRIBUTING.md).

![Workspace](docs/images/workspace.png)

## Install

Download **x4d_workflow-0.6.6.zip**, then Preferences → Get Extensions → menu → Install from Disk. Enable the extension. Do not install the source archive as the extension.

An untouched factory startup enters a new empty scene. The original scene is preserved; existing edited or saved work is not cleared. Tools → Restore Blender restores managed theme/keymap state and switches back to the previous workspace. The extension never writes your startup file automatically.

The upper-right controls are Region Render, Render Current View and Render Settings. Drag a rectangle for region rendering; Esc cancels selection. Non-camera views use a temporary render camera that is removed when rendering finishes or is cancelled.

## Workflow

E / R / T: move / rotate / scale. H: frame all. S: frame selected. C: make editable. Alt+G: group. Alt+mouse or 1/2/3+left-drag: navigate. F1–F5: perspective/top/right/front/quad. M,T / M,S / U,A / U,I: command sequences. These shortcuts apply in the X4D workspace viewport.

![MoGraph](docs/images/mograph.png)

![Primitives](docs/images/generators.png)

Minimum compatibility target is Blender 4.5. **Actual runtime tested: Windows, Blender 5.2.3 LTS.** Other versions and future releases are not claimed as tested. UI screenshots are from real Blender windows, not mockups.

Known differences include raster planar spline Booleans, mesh-boundary fog smoothing rather than voxel-density convolution, mesh-attribute vector smoothing rather than VDB vector grids, a 32-seed Voronoi limit, PCM WAV RMS rather than full spectral audio analysis, and approximate HPB rotation mapping. See the [Chinese documentation](README_ZH.md) for the complete feature matrix and limitations. No .x4d compatibility, Xpresso, renderer or simulation-system replication is provided.

Public PNG icons are original procedural drawings, reproducible with scripts/build_icons.py. Code and public icons use GPL-3.0-or-later. Blender is a trademark of its respective owner.
