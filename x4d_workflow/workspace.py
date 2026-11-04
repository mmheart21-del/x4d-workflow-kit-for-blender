import bpy
from bpy.app.handlers import persistent
from . import layout

keys=[]
snapshot=[]
_respect_saved=False

def apply_theme():
    if snapshot:return
    theme=bpy.context.preferences.themes[0]
    for owner,attr,value in [(theme.view_3d,'wire',(0.18,.19,.21)),(theme.view_3d,'object_selected',(.25,.55,.95)),(theme.view_3d,'object_active',(.4,.7,1.0))]:
        old=tuple(getattr(owner,attr));setattr(owner,attr,value);snapshot.append((owner,attr,old,tuple(getattr(owner,attr))))

def restore():
    layout.stop()
    from . import rail
    rail.stop()
    for km,kmi in keys:
        try:km.keymap_items.remove(kmi)
        except ReferenceError:pass
    keys.clear()
    for owner,attr,old,applied in snapshot:
        try:
            if tuple(getattr(owner,attr))==applied:setattr(owner,attr,old)
        except ReferenceError:pass
    snapshot.clear()

def keymaps():
    kc=bpy.context.window_manager.keyconfigs.addon
    if not kc or keys:return
    km=kc.keymaps.new(name='3D View',space_type='VIEW_3D')
    for key,op,props,mods in [
        ('E','wm.tool_set_by_id',{'name':'builtin.move'},{}),('R','wm.tool_set_by_id',{'name':'builtin.rotate'},{}),('T','wm.tool_set_by_id',{'name':'builtin.scale'},{}),
        ('V','wm.call_menu_pie',{'name':'CW_MT_v_pie'},{}),
        ('H','view3d.view_all',{},{}),('S','view3d.view_selected',{},{}),('C','cw.action',{'action':'EDITABLE'},{}),
        ('G','cw.action',{'action':'GROUP'},{'alt':True}),('M','cw.sequence',{'prefix':'M'},{}),('U','cw.sequence',{'prefix':'U'},{}),('K','cw.sequence',{'prefix':'K'},{}),
        ('A','cw.select',{'action':'SELECT'},{'ctrl':True}),('A','cw.select',{'action':'DESELECT'},{'ctrl':True,'shift':True}),
        ('B','cw.render',{'mode':'SETTINGS'},{'ctrl':True}),('R','cw.render',{'mode':'RENDER'},{'ctrl':True}),('R','cw.render',{'mode':'RENDER'},{'shift':True}),
        ('F1','cw.view',{'view':'PERSP'},{}),('F2','cw.view',{'view':'TOP'},{}),('F3','cw.view',{'view':'RIGHT'},{}),('F4','cw.view',{'view':'FRONT'},{}),('F5','cw.view',{'view':'QUAD'},{}),
        ('LEFTMOUSE','view3d.move',{}, {'key_modifier':'ONE'}),('LEFTMOUSE','view3d.zoom',{}, {'key_modifier':'TWO'}),('LEFTMOUSE','view3d.rotate',{}, {'key_modifier':'THREE'}),
        ('LEFTMOUSE','view3d.rotate',{}, {'alt':True}),('MIDDLEMOUSE','view3d.move',{}, {'alt':True}),('RIGHTMOUSE','view3d.zoom',{}, {'alt':True})]:
        kmi=km.keymap_items.new('cw.command',key,'PRESS',**mods)
        kmi.properties.command=op
        kmi.properties.argument=str(next(iter(props.values()),''))
        keys.append((km,kmi))
    # Mesh has higher priority than 3D View, so mirror only the intended keys.
    mesh=kc.keymaps.new(name='Mesh',space_type='EMPTY')
    routes=[('E','wm.tool_set_by_id','builtin.move'),('R','wm.tool_set_by_id','builtin.rotate'),('T','wm.tool_set_by_id','builtin.scale'),('H','view3d.view_all',''),('S','view3d.view_selected','')]
    routes += [(key,'cw.sequence',key) for key in ('M','U','K')]
    routes += [('V','wm.call_menu_pie','CW_MT_v_pie')]
    routes += [('D','cw.model','EXTRUDE'),('B','cw.model','BRIDGE')]
    for key,op,arg in routes:
        item=mesh.keymap_items.new('cw.command',key,'PRESS');item.properties.command=op;item.properties.argument=arg;keys.append((mesh,item))
    for key,op,arg,mods in [('A','cw.select','SELECT',{'ctrl':True}),('A','cw.select','DESELECT',{'ctrl':True,'shift':True}),('B','cw.render','SETTINGS',{'ctrl':True}),('R','cw.render','RENDER',{'ctrl':True}),('R','cw.render','RENDER',{'shift':True}),('BACK_SPACE','cw.model','DISSOLVE',{'alt':True}),('DEL','cw.model','DISSOLVE',{'alt':True}),('BACK_SPACE','cw.model','DELETE',{'ctrl':True}),('DEL','cw.model','DELETE',{'ctrl':True})]:
        item=mesh.keymap_items.new('cw.command',key,'PRESS',**mods);item.properties.command=op;item.properties.argument=arg;keys.append((mesh,item))

class CW_OT_workspace(bpy.types.Operator):
    bl_idname='cw.workspace';bl_label='Enter X4D Workspace'
    def execute(self,context):
        window=context.window
        if not window:return {'CANCELLED'}
        # Keep startup contents recoverable; only a pristine unsaved factory scene
        # enters a new empty scene. Never infer this from names alone.
        if not bpy.data.filepath and is_factory_scene(context.scene):
            for material in bpy.data.materials:
                if material.name=='Material' and material.users<=1 and not material.library:
                    material['x4d_factory_material']=True
            bpy.ops.cw.new_scene()
        existing=bpy.data.workspaces.get('X4D')
        if not existing:
            existing=next((w for w in bpy.data.workspaces if w.get('cw_workspace',False)),None)
            if existing:existing.name='X4D'
        if existing:
            window.workspace=existing
            if not bpy.app.background:
                def resume():
                    if window.workspace==existing:
                        from . import rail
                        rail.start(window)
                    return None
                bpy.app.timers.register(resume,first_interval=.3)
        else:
            previous=window.workspace
            before=set(bpy.data.workspaces)
            bpy.ops.workspace.duplicate()
            created=next((w for w in bpy.data.workspaces if w not in before),None)
            if not created:return {'CANCELLED'}
            created.name='X4D'
            created['cw_previous']=previous.name
            created['cw_workspace']=True
            window.workspace=created
            screen=created.screens[0]
            for area in screen.areas:
                if area.type=='PROPERTIES':
                    area.type='PROPERTIES';area.spaces.active.context='CONSTRAINT'
            created['cw_workspace']=True
        apply_theme();keymaps();layout.queue(window);return {'FINISHED'}

class CW_OT_restore(bpy.types.Operator):
    bl_idname='cw.restore';bl_label='Restore Blender'
    def execute(self,context):
        restore()
        cw=bpy.data.workspaces.get('X4D')
        other=bpy.data.workspaces.get(cw.get('cw_previous','Layout')) if cw else None
        if not other:other=next((w for w in bpy.data.workspaces if w.name!='X4D'),None)
        if other:context.window.workspace=other
        return {'FINISHED'}

def first_run():
    if bpy.app.background:return None
    if _respect_saved and bpy.data.filepath and bpy.context.workspace.name!='X4D':return None
    try:
        if bpy.context.window:
            bpy.ops.cw.workspace()
            from . import material_dock,material_events
            if material_dock.is_open(bpy.context.window):material_events.start(bpy.context.window)
    except Exception as exc:print('CW workspace:',exc)
    return None

@persistent
def load_post(_):
    global _respect_saved
    from . import selection,generators,extras,advanced_fx,procedural_scripts
    generators.stop();extras.stop();advanced_fx.stop();procedural_scripts.stop()
    from . import material_previews
    material_previews.stop()
    from . import material_events,material_editors,material_dock
    material_events.stop();material_editors.stop();material_dock._areas.clear()
    selection.subscribe()
    _respect_saved=bool(bpy.data.filepath)
    if not bpy.app.background and not bpy.app.timers.is_registered(first_run):bpy.app.timers.register(first_run,first_interval=.3)

classes=[CW_OT_workspace,CW_OT_restore]

def is_factory_scene(scene):
    objects=list(scene.objects)
    if len(objects)!=3 or set(o.name for o in objects)!={'Cube','Camera','Light'}:return False
    cube=scene.objects.get('Cube');camera=scene.objects.get('Camera');light=scene.objects.get('Light')
    if (cube.type,camera.type,light.type)!=('MESH','CAMERA','LIGHT'):return False
    if cube.cw.kind or cube.cw_primitive.kind or cube.cw_extra.kind:return False
    if len(cube.data.vertices)!=8 or len(cube.data.polygons)!=6 or cube.modifiers or cube.animation_data:return False
    if any(o.parent or o.constraints or o.animation_data for o in objects):return False
    if tuple(cube.location)!=(0.,0.,0.) or tuple(cube.rotation_euler)!=(0.,0.,0.) or tuple(cube.scale)!=(1.,1.,1.):return False
    if any(abs(abs(v.co[i])-1)>1e-6 for v in cube.data.vertices for i in range(3)):return False
    return (camera.location-__import__('mathutils').Vector((7.35889,-6.92579,4.95831))).length<.001 and (light.location-__import__('mathutils').Vector((4.07625,1.00545,5.90386))).length<.001












