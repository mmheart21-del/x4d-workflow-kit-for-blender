import bpy,sys,os,hashlib
root=os.path.dirname(os.path.dirname(__file__));sys.path.insert(0,root)
import x4d_workflow as kit
kit.register()
assert len(kit.icons._preview)==131
for category,cn,en,icon,color,entries in kit.catalog.CATEGORIES:
    assert min(kit.icons._preview[kit.icons.key(category)].image_size)>0
    for cn,en,cmd in entries:assert kit.icons.key(category,en) in kit.icons._preview
cube=open(os.path.join(kit.icons.ROOT,'mesh_cube.png'),'rb').read()
sphere=open(os.path.join(kit.icons.ROOT,'mesh_sphere.png'),'rb').read()
assert cube!=sphere
area=next(a for a in bpy.context.screen.areas if a.type=='VIEW_3D')
region=next(r for r in area.regions if r.type=='WINDOW')
with bpy.context.temp_override(area=area,region=region):
    for name in ['SELECT','MOVE','ROTATE','SCALE','POINT','EDGE','FACE','OBJECT','AXIS']:
        assert 'FINISHED' in bpy.ops.cw.tool(tool=name),name
    for name in ['TOP','RIGHT','FRONT','PERSP']:
        assert 'FINISHED' in bpy.ops.cw.view(view=name),name
old=bpy.context.scene;old_count=len(old.objects)
bpy.ops.cw.new_scene()
assert len(bpy.context.scene.objects)==0
assert len(old.objects)==old_count
assert bpy.context.scene.frame_end==90 and bpy.context.scene.frame_start==0
assert bpy.context.scene.render.fps==30
assert abs(bpy.context.scene.unit_settings.scale_length-1.0)<1e-6
kit.unregister();kit.register();kit.unregister()
print('CW_V030_TEST_OK')




