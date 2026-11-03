import bpy,sys,os
root=os.path.dirname(os.path.dirname(__file__));sys.path.insert(0,root)
import x4d_workflow as kit
kit.register()
def show():
    bpy.ops.cw.primitive(kind='CUBE')
    for name,color in [('Blue',(.03,.3,.7,1)),('Purple',(.35,.02,.65,1)),('Red',(.65,.02,.02,1)),('Green',(.02,.65,.25,1)),('White',(.8,.8,.8,1))]:
        bpy.ops.cw.material_new();mat=bpy.context.window_manager.cw_material;mat.name=name;mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=color
    area=next(a for a in bpy.context.screen.areas if a.type=='VIEW_3D');region=next(r for r in area.regions if r.type=='WINDOW')
    with bpy.context.temp_override(area=area,region=region):bpy.ops.cw.materials('INVOKE_DEFAULT')
    bpy.app.timers.register(done,first_interval=2)
    return None
def done():
    assert kit.material_dock.is_open(bpy.context.window)
    assert len([a for a in bpy.context.screen.areas if a.type=='PROPERTIES'])==2
    bpy.ops.screen.screenshot(filepath=os.path.join(root,'artifacts','materials-v062.png'))
    bpy.ops.cw.material_pick(material='Blue')
    assert bpy.context.window_manager.cw_material.name=='Blue'
    bpy.ops.cw.materials()
    bpy.app.timers.register(reopen,first_interval=.5)
    return None

def reopen():
    assert not kit.material_dock.is_open(bpy.context.window)
    assert len([a for a in bpy.context.screen.areas if a.type=='PROPERTIES'])==1
    bpy.ops.cw.materials()
    bpy.app.timers.register(cleanup,first_interval=.6)
    return None

def cleanup():
    assert kit.material_dock.is_open(bpy.context.window)
    kit.unregister()
    assert not kit.material_dock._draws
    print('X4D_MATERIAL_GUI_OK');bpy.ops.wm.quit_blender();return None
bpy.app.timers.register(show,first_interval=6)
