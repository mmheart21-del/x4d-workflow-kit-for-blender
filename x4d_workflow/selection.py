"""Keep the attribute manager aligned with Outliner selection, in this workspace only."""
import bpy
_owner=object()
_last={}
_materials={}

def focus():
    manager=getattr(bpy.context,'window_manager',None)
    if not manager:return
    for window in manager.windows:
        if window.workspace.name!='X4D':continue
        from . import source_visibility
        source_visibility.sync(window)
        from . import material_dock
        materials=material_dock.highlighted(window)
        if _materials.get(window.as_pointer())!=materials:
            _materials[window.as_pointer()]=materials
            for area in window.screen.areas:
                if material_dock.is_dock(area):area.tag_redraw()
        obj=window.view_layer.objects.active
        if obj and obj.is_editable:
            from .object_lists import prepare_sources,sync_tags
            prepare_sources(obj)
            sync_tags(obj)
        token=(obj.as_pointer() if obj else 0,window.scene.as_pointer())
        # RNA context changes can be deferred while the first object is linked
        # into an empty scene. Retry TOOL -> CONSTRAINT after Blender refreshes.
        pending=obj is not None and any(a.type=='PROPERTIES' and a.spaces.active.context=='TOOL' for a in window.screen.areas)
        if _last.get(window.as_pointer())==token and not pending:continue
        _last[window.as_pointer()]=token
        context='CONSTRAINT' if obj else 'TOOL'
        for area in window.screen.areas:
            from .material_dock import is_dock
            if area.type=='PROPERTIES' and not is_dock(area):
                try:
                    if isinstance(area.spaces.active.pin_id,bpy.types.Material):
                        area.spaces.active.use_pin_id=False;area.spaces.active.pin_id=None
                        area.spaces.active.context='TOOL'
                    area.spaces.active.context=context
                except TypeError:pass
                area.tag_redraw()

def subscribe():
    _last.clear();_materials.clear()
    bpy.msgbus.clear_by_owner(_owner)
    bpy.msgbus.subscribe_rna(key=(bpy.types.LayerObjects,'active'),owner=_owner,args=(),notify=focus,options={'PERSISTENT'})
    bpy.msgbus.subscribe_rna(key=(bpy.types.Window,'scene'),owner=_owner,args=(),notify=focus,options={'PERSISTENT'})
    if not bpy.app.background and not bpy.app.timers.is_registered(tick):bpy.app.timers.register(tick,first_interval=.25,persistent=True)

def tick():
    focus()
    return .25

def stop():
    if bpy.app.timers.is_registered(tick):bpy.app.timers.unregister(tick)
    bpy.msgbus.clear_by_owner(_owner);_last.clear();_materials.clear()

