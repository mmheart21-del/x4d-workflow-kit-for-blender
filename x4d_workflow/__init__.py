"""X4D Workflow Kit. GPL-3.0-or-later."""
import bpy
from . import object_lists,mesh_tags,quick_menu,drag_tools,loop_preview,translations,field_view,modeling,rendering,materials,material_dock,material_previews,material_editors,material_events,source_visibility
from . import engine,operators,workspace,ui,coordinates,primitives,catalog,rail,icons,selection,generators,skin,deformers,extra_properties,extras,extra_operators,procedural_scripts,advanced_fx,svg_import
bl_info={'name':'X4D Workflow Kit','author':'X4D Workflow contributors','version':(0,7,8),'blender':(4,5,0),'category':'3D View'}
classes=object_lists.classes+mesh_tags.classes+quick_menu.classes+drag_tools.classes+[loop_preview.CW_OT_loop_preview]+field_view.classes+modeling.classes+material_events.classes+material_dock.classes+materials.classes+rendering.classes+svg_import.classes+extra_properties.classes+extra_operators.classes+procedural_scripts.classes+primitives.classes+engine.classes+operators.classes+generators.classes+deformers.classes+catalog.classes+rail.classes+workspace.classes+ui.classes+skin.classes
_registered=[]
_header_added=False

def register():
    global _header_added
    if bpy.app.version<(4,5,0):raise RuntimeError('Blender 4.5 or newer required')
    if _registered:return
    try:
        bpy.app.translations.register(__name__,{'zh_HANS':translations.ZH,'zh_CN':translations.ZH})
        icons.register()
        selection.subscribe()
        for cls in classes:
            bpy.utils.register_class(cls);_registered.append(cls)
        bpy.types.WindowManager.cw_material=bpy.props.PointerProperty(type=bpy.types.Material)
        bpy.types.OUTLINER_HT_header.append(materials.outliner_header)
        bpy.types.Object.cw_extra=bpy.props.PointerProperty(type=extra_properties.CWExtra)
        primitives.register_properties()
        bpy.types.WindowManager.cw_attribute_tab=bpy.props.EnumProperty(items=ui.attribute_tabs)
        coordinates.register()
        bpy.types.Object.cw=bpy.props.PointerProperty(type=engine.CWSettings)
        bpy.types.VIEW3D_HT_header.append(catalog.header);_header_added=True
        skin.install();rendering.install();material_dock.install()
        for handlers,fn in _handlers():
            if fn not in handlers:handlers.append(fn)
        if not bpy.app.background and not bpy.app.timers.is_registered(workspace.first_run):bpy.app.timers.register(workspace.first_run,first_interval=.5)
    except Exception:
        unregister()
        raise

def track_creation(scene, depsgraph):
    materials=[m for m in bpy.data.materials if not m.library]
    latest=max((m.get('x4d_created',0) for m in materials),default=0)
    for mat in sorted((m for m in materials if 'x4d_created' not in m),key=lambda m:m.session_uid):
        latest+=1
        mat['x4d_created']=latest

def _handlers():
    return [(bpy.app.handlers.depsgraph_update_post,track_creation),(bpy.app.handlers.frame_change_post,engine.rebuild_all),(bpy.app.handlers.depsgraph_update_post,engine.deps_changed),(bpy.app.handlers.load_pre,workspace.load_pre),(bpy.app.handlers.load_post,workspace.load_post),(bpy.app.handlers.depsgraph_update_post,generators.sync),(bpy.app.handlers.frame_change_post,generators.sync),(bpy.app.handlers.depsgraph_update_post,deformers.sync),(bpy.app.handlers.frame_change_post,deformers.sync),(bpy.app.handlers.depsgraph_update_post,extras.update),(bpy.app.handlers.frame_change_post,extras.update)]

def unregister():
    global _header_added
    if bpy.app.timers.is_registered(workspace.first_run):bpy.app.timers.unregister(workspace.first_run)
    loop_preview.active.clear();modeling.stop();skin.restore();rendering.stop();material_previews.stop();material_events.stop();material_editors.stop();material_dock.stop()
    if hasattr(bpy.types.Object,'cw'):source_visibility.stop()
    if hasattr(bpy.types.WindowManager,'cw_material'):
        bpy.types.OUTLINER_HT_header.remove(materials.outliner_header)
        del bpy.types.WindowManager.cw_material
        if hasattr(bpy.types.WindowManager,'cw_material_tile'):del bpy.types.WindowManager.cw_material_tile
    generators.stop();extras.stop();advanced_fx.stop();procedural_scripts.stop()
    selection.stop()
    rail.stop();workspace.layout.stop()
    # Registration failure can occur while bpy.context is restricted, before
    # any theme/keymap/image state exists. Restore only state actually applied.
    if workspace.keys or workspace.snapshot:workspace.restore()
    icons.unregister()
    bpy.app.translations.unregister(__name__)
    if _header_added:bpy.types.VIEW3D_HT_header.remove(catalog.header);_header_added=False
    for handlers,fn in _handlers():
        if fn in handlers:handlers.remove(fn)
    for owner,name in [(bpy.types.Object,'cw_extra'),(bpy.types.Object,'cw_primitive'),(bpy.types.Object,'cw_position'),(bpy.types.Object,'cw_rotation'),(bpy.types.Object,'cw_scale'),(bpy.types.Object,'cw_size'),(bpy.types.Object,'cw'),(bpy.types.WindowManager,'cw_attribute_tab')]:
        if hasattr(owner,name):delattr(owner,name)
    for cls in reversed(_registered):bpy.utils.unregister_class(cls)
    _registered.clear()








