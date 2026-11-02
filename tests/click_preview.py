import bpy,sys,os
root=os.path.dirname(os.path.dirname(__file__));sys.path.insert(0,root)
import x4d_workflow as kit
kit.register()
bpy.context.preferences.view.language='zh_HANS';bpy.context.preferences.view.use_translate_interface=True
bpy.context.object.cw_primitive.kind='CUBE'
def ready():
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(root,'artifacts','cw-click-test.blend'))
    bpy.ops.screen.screenshot(filepath=os.path.join(root,'artifacts','workspace-v040.png'))
    print('CW_CLICK_READY',flush=True)
    return None
def finish():
    bpy.ops.screen.screenshot(filepath=os.path.join(root,'artifacts','clicked-v040.png'))
    print('CW_CLICK_OBJECTS',[o.name for o in bpy.context.scene.objects],flush=True)
    bpy.ops.wm.quit_blender();return None
bpy.app.timers.register(ready,first_interval=4)
bpy.app.timers.register(finish,first_interval=90)
