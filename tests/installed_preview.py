"""Only load the extension installed by Blender's install-file command."""
import bpy,sys,os,importlib,addon_utils,traceback,json
root=os.path.dirname(os.path.dirname(__file__))
name='bl_ext.x4d_test.x4d_workflow'
kit=sys.modules.get(name)
if kit is None or not getattr(kit,'__addon_enabled__',False):kit=addon_utils.enable(name,default_set=False)
assert kit is not None
assert os.path.commonpath([os.path.abspath(kit.__file__),os.path.join(root,'artifacts','install-profile')])==os.path.join(root,'artifacts','install-profile'),kit.__file__
import tomllib
with open(os.path.join(os.path.dirname(kit.__file__),'blender_manifest.toml'),'rb') as f:assert tomllib.load(f)['version']=='0.6.1'
assert len(kit.icons._preview)==131
print('CW_INSTALLED_ENABLED',kit.__file__)
if not bpy.app.background:
    bpy.context.preferences.view.language='zh_HANS'
    bpy.context.preferences.view.use_translate_interface=True
    def field():
        bpy.ops.cw.create(kind='FIELD')
        bpy.app.timers.register(finish,first_interval=.75)
        return None
    def finish():
        try:
            assert bpy.context.workspace.name=='X4D'
            props=next(a for a in bpy.context.screen.areas if a.type=='PROPERTIES')
            assert props.spaces.active.context=='CONSTRAINT',props.spaces.active.context
            assert kit.ui.CW_PT_manager.poll(bpy.context)
            bpy.ops.screen.screenshot(filepath=os.path.join(root,'artifacts','installed-v060-field.png'))
            bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
            bpy.ops.cw.primitive(kind='CUBE')
            bpy.context.object.cw_size=(2,4,2)
            bpy.context.object.cw_primitive.subdivisions=4
            bpy.ops.cw.generator(kind='SUBSURF')
            assert bpy.context.object.cw.kind=='GENERATOR' and len(bpy.context.object.data.vertices)>8
            bpy.app.timers.register(generator_shot,first_interval=.75)
            print('CW_INSTALLED_GUI_OK')
        except Exception:
            traceback.print_exc();bpy.ops.wm.quit_blender()
        return None
    def generator_shot():
        bpy.ops.screen.screenshot(filepath=os.path.join(root,'artifacts','installed-v060-generator.png'))
        print('CW_INSTALLED_GENERATOR_GUI_OK')
        bpy.ops.wm.quit_blender();return None
    bpy.app.timers.register(field,first_interval=5)
else:
    addon_utils.disable(name,default_set=False)
    assert not hasattr(bpy.types.Object,'cw')
    assert addon_utils.enable(name,default_set=False) is not None
    print('CW_INSTALLED_REENABLE_OK')





