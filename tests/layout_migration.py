"""Exercise migration from the shipped 0.2.0 layout in an isolated GUI process."""
import bpy,sys,os,zipfile,types,json,traceback
root=os.path.dirname(os.path.dirname(__file__));sys.path.insert(0,root)
import x4d_workflow as kit
kit.register()
if bpy.app.timers.is_registered(kit.workspace.first_run):bpy.app.timers.unregister(kit.workspace.first_run)
bpy.ops.cw.workspace();kit.layout.stop()
legacy=types.ModuleType('x4d_workflow.legacy_layout');legacy.__package__='x4d_workflow'
with zipfile.ZipFile(os.path.join(root,'dist','x4d_workflow-0.2.0.zip')) as z:exec(compile(z.read('layout.py'),'legacy-layout.py','exec'),legacy.__dict__)
def old():legacy.queue(bpy.context.window);return None
def migrate():
    try:
        if legacy._pending:return .5
        assert any(a.type=='IMAGE_EDITOR' for a in bpy.context.screen.areas)
        assert bpy.context.workspace['cw_layout_revision']==2
        kit.layout.queue(bpy.context.window)
        bpy.app.timers.register(finish,first_interval=2.5)
    except Exception:traceback.print_exc();bpy.ops.wm.quit_blender()
    return None
def finish():
    try:
        if kit.layout._pending:return .5
        areas=list(bpy.context.screen.areas)
        assert len(areas)==4,[(a.type,a.width,a.height) for a in areas]
        assert not any(a.type=='IMAGE_EDITOR' for a in areas)
        assert bpy.context.workspace['cw_layout_revision']==4
        bpy.ops.screen.screenshot(filepath=os.path.join(root,'artifacts','migration-v030.png'))
        print('CW_MIGRATION_OK')
    except Exception:traceback.print_exc()
    bpy.ops.wm.quit_blender();return None
bpy.app.timers.register(old,first_interval=.5)
bpy.app.timers.register(migrate,first_interval=3)


