"""Keep the attribute manager aligned with Outliner selection, in this workspace only."""
import bpy
_owner=object()
_last={}

def focus():
    manager=getattr(bpy.context,'window_manager',None)
    if not manager:return
    for window in manager.windows:
        if window.workspace.name!='X4D':continue
        obj=window.view_layer.objects.active
        token=(obj.as_pointer() if obj else 0,window.scene.as_pointer())
        # RNA context changes can be deferred while the first object is linked
        # into an empty scene. Retry TOOL -> CONSTRAINT after Blender refreshes.
        pending=obj is not None and any(a.type=='PROPERTIES' and a.spaces.active.context=='TOOL' for a in window.screen.areas)
        if _last.get(window.as_pointer())==token and not pending:continue
        _last[window.as_pointer()]=token
        context='CONSTRAINT' if obj else 'TOOL'
        for area in window.screen.areas:
            if area.type=='PROPERTIES':
                try:area.spaces.active.context=context
                except TypeError:pass
                area.tag_redraw()

def subscribe():
    _last.clear()
    bpy.msgbus.clear_by_owner(_owner)
    bpy.msgbus.subscribe_rna(key=(bpy.types.LayerObjects,'active'),owner=_owner,args=(),notify=focus,options={'PERSISTENT'})
    bpy.msgbus.subscribe_rna(key=(bpy.types.Window,'scene'),owner=_owner,args=(),notify=focus,options={'PERSISTENT'})
    if not bpy.app.background and not bpy.app.timers.is_registered(tick):bpy.app.timers.register(tick,first_interval=.25,persistent=True)

def tick():
    focus()
    return .25

def stop():
    if bpy.app.timers.is_registered(tick):bpy.app.timers.unregister(tick)
    bpy.msgbus.clear_by_owner(_owner);_last.clear()

