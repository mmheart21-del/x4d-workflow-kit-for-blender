import bpy,sys,os
from types import SimpleNamespace
root=os.path.dirname(os.path.dirname(__file__));sys.path.insert(0,root)
import x4d_workflow as kit
kit.register()
assert kit.workspace.is_factory_scene(bpy.context.scene)
original=bpy.context.scene
bpy.ops.cw.workspace()
assert len(bpy.context.scene.objects)==0
assert len(original.objects)==3
assert bpy.context.scene.frame_end==90
bpy.context.window.scene=original
bpy.data.objects['Cube'].location.x=1
assert not kit.workspace.is_factory_scene(original)
bpy.ops.cw.workspace()
assert bpy.context.scene==original
area=next(a for a in bpy.context.screen.areas if a.type=='VIEW_3D')
region=next(r for r in area.regions if r.type=='WINDOW')
oldcamera=original.camera
kit.rendering.prepare(original,area.spaces.active,region,(.2,.2,.8,.8))
assert original.camera!=oldcamera and original.render.use_border
original.render.engine='BLENDER_EEVEE';original.render.resolution_x=32;original.render.resolution_y=32;original.render.resolution_percentage=100
bpy.ops.render.render()
assert original.camera==oldcamera and not original.render.use_border
assert not any(o.name.startswith('CW Temporary Render Camera') for o in bpy.data.objects)
for key in ['MOVE','ROTATE','SCALE','OBJECT','POINT','EDGE','FACE','AXIS']:
    text=kit.rail.CW_OT_tool.description(bpy.context,SimpleNamespace(tool=key))
    assert len(text)>10 and 'X4D Tool' not in text
with bpy.context.temp_override(area=area,region=region):assert 'FINISHED' in bpy.ops.cw.render(mode='SETTINGS')
assert next(a for a in bpy.context.screen.areas if a.type=='PROPERTIES').spaces.active.context=='RENDER'
kit.unregister();assert not kit.rendering._jobs
print('CW_V060_STARTUP_RENDER_TOOLTIPS_OK')
