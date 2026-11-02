import bpy,sys,os,traceback
root=os.path.dirname(os.path.dirname(__file__));sys.path.insert(0,root)
import x4d_workflow as kit
kit.register()
bpy.context.preferences.view.language='en_US';bpy.context.preferences.view.use_translate_interface=False
out=os.path.join(root,'docs','images');os.makedirs(out,exist_ok=True)
def initial():
    assert bpy.context.workspace.name=='X4D'
    assert len(bpy.context.scene.objects)==0
    bpy.context.scene.name='Untitled'
    bpy.app.timers.register(capture_initial,first_interval=.75)
    return None

def capture_initial():
    try:
        assert bpy.context.workspace.name=='X4D'
        assert len(bpy.context.scene.objects)==0
        bpy.context.scene.name='Untitled'
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP',iterations=2)
        bpy.ops.screen.screenshot(filepath=os.path.join(out,'workspace.png'))
        bpy.ops.cw.primitive(kind='CUBE');bpy.context.object.cw_size=(1,1,1);bpy.context.object.name='Cube'
        bpy.ops.cw.create(kind='CLONER');cloner=bpy.context.object;cloner.name='Cloner';cloner.cw.count=(8,8,1);cloner.cw.spacing=(1.4,1.4,1.4)
        bpy.ops.cw.create(kind='EFFECTOR');eff=bpy.context.object;eff.name='Plain Effector';eff.cw.move=(0,0,5)
        cloner.cw.effectors.add().target=eff
        bpy.ops.cw.create(kind='FIELD');field=bpy.context.object;field.name='Spherical Field';field.cw.radius=7
        eff.cw.fields.add().target=field
        kit.engine.rebuild_all(bpy.context.scene)
        for obj in bpy.context.selected_objects:obj.select_set(False)
        cloner.select_set(True);bpy.context.view_layer.objects.active=cloner
        area=next(a for a in bpy.context.screen.areas if a.type=='VIEW_3D');region=next(r for r in area.regions if r.type=='WINDOW')
        with bpy.context.temp_override(area=area,region=region):bpy.ops.view3d.view_all(center=False)
        bpy.app.timers.register(mograph,first_interval=1.5)
    except Exception:traceback.print_exc();bpy.ops.wm.quit_blender()
    return None
def mograph():
    for obj in bpy.context.selected_objects:obj.select_set(False)
    bpy.context.view_layer.objects.active=None
    kit.selection._last.clear();kit.selection.focus()
    bpy.app.timers.register(capture_mograph,first_interval=.75)
    return None

def capture_mograph():
    bpy.ops.screen.screenshot(filepath=os.path.join(out,'mograph.png'))
    for obj in list(bpy.context.scene.objects):bpy.data.objects.remove(obj,do_unlink=True)
    kit.selection._last.clear();kit.selection.focus()
    bpy.app.timers.register(capture_empty,first_interval=1)
    return None

def capture_empty():
    bpy.ops.screen.screenshot(filepath=os.path.join(out,'workspace.png'))
    print('X4D_ENGLISH_SCREENSHOTS_OK');bpy.ops.wm.quit_blender()
    return None
bpy.app.timers.register(initial,first_interval=6)
