import bpy,sys,os,time,traceback
root=os.path.dirname(os.path.dirname(__file__));sys.path.insert(0,root)
import x4d_workflow as kit
kit.register();state={'start':time.monotonic()}
def digest(mat):
    if not mat.preview:return None
    values=list(mat.preview.image_pixels_float)
    if not values or not any(values[::53]):return None
    return hash(tuple(round(v,4) for v in values))
def begin():
    try:
        state['prefs']=(bpy.context.preferences.addons['cycles'].preferences.compute_device_type,bpy.context.scene.render.engine,bpy.context.scene.cycles.device)
        bpy.ops.cw.primitive(kind='CUBE');bpy.ops.cw.material_new();mat=bpy.context.window_manager.cw_material;mat.name='Sync Test'
        state['mat']=mat;mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.8,.01,.01,1)
        bpy.ops.cw.materials();bpy.app.timers.register(wait_red,first_interval=2)
    except Exception:traceback.print_exc();bpy.ops.wm.quit_blender()
    return None
def wait_red():
    mat=state['mat'];value=digest(mat)
    if not value or bpy.app.is_job_running('RENDER_PREVIEW'):
        if time.monotonic()-state['start']>100:raise RuntimeError('Native preview timed out')
        return 2
    state['old']=value
    mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.01,.03,.8,1)
    bpy.app.timers.register(wait_blue,first_interval=2);return None
def wait_blue():
    mat=state['mat'];value=digest(mat)
    if value is None or value==state['old'] or bpy.app.is_job_running('RENDER_PREVIEW'):
        if time.monotonic()-state['start']>150:raise RuntimeError('Native preview failed to synchronize')
        return 2
    prefs=(bpy.context.preferences.addons['cycles'].preferences.compute_device_type,bpy.context.scene.render.engine,bpy.context.scene.cycles.device)
    assert prefs==state['prefs'],(prefs,state['prefs'])
    assert not hasattr(kit.material_previews,'subprocess')
    bpy.app.timers.register(finish,first_interval=1);return None
def finish():
    bpy.ops.screen.screenshot(filepath=os.path.join(root,'artifacts','native-preview-sync.png'))
    kit.unregister();print('X4D_NATIVE_PREVIEW_SYNC_AND_DEVICE_PRESERVATION_OK');bpy.ops.wm.quit_blender();return None
bpy.app.timers.register(begin,first_interval=6)
