import bpy,sys,os
sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))
import x4d_workflow as kit
kit.register()
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.mesh.primitive_cube_add();a=bpy.context.object
bpy.ops.mesh.primitive_cube_add(location=(1,0,0));b=bpy.context.object
a.select_set(True);bpy.context.view_layer.objects.active=a
bpy.ops.cw.generator(kind='BOOLEAN');host=bpy.context.object
bpy.context.view_layer.update();mesh=host.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh()
assert len(mesh.polygons)>0
assert max(v.co.x for v in mesh.vertices)<.01,[(tuple(v.co)) for v in mesh.vertices]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.mesh.primitive_cube_add();a=bpy.context.object
bpy.ops.mesh.primitive_cube_add(location=(3,0,0));b=bpy.context.object
a.select_set(True);bpy.context.view_layer.objects.active=a
bpy.ops.cw.extra(kind='VOLUME_BUILDER');vol=bpy.context.object
assert len(vol.data.vertices)==16,len(vol.data.vertices)
b.data.vertices[0].co.x-=2;kit.extras.update(bpy.context.scene)
assert len(vol.data.vertices)==16
bpy.ops.cw.material_new();assert len(vol.data.materials)==1
kit.unregister();print('X4D_FIXES_OK')
