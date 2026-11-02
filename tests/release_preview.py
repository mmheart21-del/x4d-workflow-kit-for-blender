import bpy,sys,os,traceback
root=os.path.dirname(os.path.dirname(__file__));sys.path.insert(0,root)
import x4d_workflow as kit
kit.register()
bpy.context.preferences.view.language='zh_HANS';bpy.context.preferences.view.use_translate_interface=True
out=os.path.join(root,'docs','images');os.makedirs(out,exist_ok=True)
def initial():
    try:
        assert bpy.context.workspace.name=='X4D'
        assert len(bpy.context.scene.objects)==0
        bpy.ops.screen.screenshot(filepath=os.path.join(out,'workspace.png'))
        bpy.ops.cw.primitive(kind='CUBE');bpy.context.object.cw_size=(1,1,1)
        bpy.ops.cw.create(kind='CLONER');cloner=bpy.context.object;cloner.cw.count=(8,8,1);cloner.cw.spacing=(1.4,1.4,1.4)
        bpy.ops.cw.create(kind='EFFECTOR');eff=bpy.context.object;eff.cw.move=(0,0,5)
        cloner.cw.effectors.add().target=eff
        bpy.ops.cw.create(kind='FIELD');field=bpy.context.object;field.cw.radius=7
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
    bpy.ops.screen.screenshot(filepath=os.path.join(out,'mograph.png'))
    area=next(a for a in bpy.context.screen.areas if a.type=='VIEW_3D');region=next(r for r in area.regions if r.type=='WINDOW')
    with bpy.context.temp_override(area=area,region=region):bpy.ops.cw.palette('INVOKE_DEFAULT',category='GENERATOR')
    bpy.app.timers.register(menu,first_interval=1)
    return None
def menu():
    bpy.ops.screen.screenshot(filepath=os.path.join(out,'generators.png'))
    print('CW_PUBLIC_SCREENSHOTS_OK');bpy.ops.wm.quit_blender();return None
bpy.app.timers.register(initial,first_interval=6)
