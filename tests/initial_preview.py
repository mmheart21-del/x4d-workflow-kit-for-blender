import bpy,sys,os,traceback
root=os.path.dirname(os.path.dirname(__file__));sys.path.insert(0,root)
import x4d_workflow as kit
kit.register()
bpy.context.preferences.view.language='zh_HANS'
bpy.context.preferences.view.use_translate_interface=True

def view_context():
    area=next(a for a in bpy.context.screen.areas if a.type=='VIEW_3D')
    region=next(r for r in area.regions if r.type=='WINDOW')
    return bpy.context.temp_override(area=area,region=region)
def quad():
    with view_context():bpy.ops.cw.view(view='QUAD')
    bpy.app.timers.register(single,first_interval=.5)
    return None
def single():
    with view_context():bpy.ops.cw.view(view='PERSP')
    bpy.ops.cw.new_scene()
    bpy.app.timers.register(finish,first_interval=.75)
    return None
def finish():
    try:
        assert not kit.layout._errors,kit.layout._errors
        assert not bpy.context.scene.objects
        assert len(bpy.context.screen.areas)==4
        bpy.ops.screen.screenshot(filepath=os.path.join(root,'artifacts',f'initial-v030-{bpy.context.window.width}.png'))
        print('CW_INITIAL_QUAD_OK')
    except Exception:traceback.print_exc()
    bpy.ops.wm.quit_blender();return None
bpy.app.timers.register(quad,first_interval=5)
