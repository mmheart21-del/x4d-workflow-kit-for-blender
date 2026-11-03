"""Blender-owned material thumbnails. Device and engine choices remain native."""
import bpy,time
_pending=False;_states={};_changed={}

def signature(mat,seen=None):
    seen=set() if seen is None else seen
    tree=mat.node_tree if isinstance(mat,bpy.types.Material) else mat
    if not tree or tree.as_pointer() in seen:return ()
    seen.add(tree.as_pointer());result=[]
    for node in tree.nodes:
        values=[]
        for socket in list(node.inputs)+list(node.outputs):
            value=getattr(socket,'default_value',None)
            if value is not None and not isinstance(value,(str,int,float,bool)):
                try:value=tuple(value)
                except TypeError:value=str(value)
            values.append((socket.identifier,str(value)))
        ramp=getattr(node,'color_ramp',None);image=getattr(node,'image',None)
        result.append((node.name,node.bl_idname,node.mute,tuple(values),tuple((e.position,tuple(e.color)) for e in ramp.elements) if ramp else (),(image.name,image.filepath,image.is_dirty) if image else None,tuple((k,str(getattr(node,k))) for k in ('operation','blend_type','distribution','noise_dimensions','projection','extension') if hasattr(node,k)),ramp.interpolation if ramp else None,signature(node.node_tree,seen) if getattr(node,'node_tree',None) else ()))
    return tuple(result),tuple((l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier) for l in tree.links)

def key(mat,context):return (context.scene.render.engine,tuple(mat.diffuse_color),mat.preview_render_type,mat.use_preview_world,signature(mat))

def request():
    global _pending
    _pending=True
    if not bpy.app.background and not bpy.app.timers.is_registered(tick):bpy.app.timers.register(tick,first_interval=.25)

def tick():
    global _pending
    mats=[m for m in bpy.data.materials if not getattr(m,'is_grease_pencil',False)]
    now=time.monotonic()
    for mat in mats:
        pointer=mat.as_pointer();current=key(mat,bpy.context)
        if _pending:
            mat.asset_generate_preview();_states[pointer]=current;_changed.pop(pointer,None)
        elif _states.get(pointer)!=current:
            if _changed.get(pointer,(None,))[0]!=current:_changed[pointer]=(current,now)
            elif now-_changed[pointer][1]>1:
                mat.asset_generate_preview();_states[pointer]=current;_changed.pop(pointer,None)
    _pending=False
    live={m.as_pointer() for m in mats}
    for pointer in list(_states):
        if pointer not in live:_states.pop(pointer,None);_changed.pop(pointer,None)
    manager=getattr(bpy.context,'window_manager',None)
    if manager:
        selected=getattr(manager,'cw_material',None)
        if selected:
            from . import material_editors
            material_editors.sync_nodes(bpy.context,selected)
        for window in manager.windows:
            for area in window.screen.areas:
                if area.type=='PROPERTIES':area.tag_redraw()
    return .5

def status():return 'Blender native material previews'
def stop():
    global _pending
    _pending=False;_states.clear();_changed.clear()
    if bpy.app.timers.is_registered(tick):bpy.app.timers.unregister(tick)
