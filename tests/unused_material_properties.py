import bpy,sys,os
sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))
import x4d_workflow as kit
kit.register()
def begin():
    assert not bpy.context.scene.objects
    mat=bpy.data.materials.new('Unused Material');mat.use_nodes=True
    kit.material_editors.select(bpy.context,mat)
    bpy.app.timers.register(check,first_interval=1)
    return None
def check():
    props=next(a for a in bpy.context.screen.areas if a.type=='PROPERTIES')
    assert props.spaces.active.context=='MATERIAL',props.spaces.active.context
    assert props.spaces.active.pin_id.name=='Unused Material'
    kit.unregister();print('X4D_UNUSED_MATERIAL_PROPERTIES_OK');bpy.ops.wm.quit_blender();return None
bpy.app.timers.register(begin,first_interval=6)
