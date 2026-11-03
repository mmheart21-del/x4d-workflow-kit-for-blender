import bpy,os,sys
sys.path.insert(0,os.getcwd())
import x4d_workflow as kit
kit.register()
for mat in list(bpy.data.materials):bpy.data.materials.remove(mat,do_unlink=True)
bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object
mat=bpy.data.materials.new('Last Material');mat.use_nodes=True
obj.data.materials.append(mat)
kit.material_editors.select(bpy.context,mat)
assert bpy.ops.cw.material_delete()=={'FINISHED'}
assert len(bpy.data.materials)==0
assert obj.data.materials[0] is None
assert bpy.context.window_manager.cw_material is None
assert bpy.ops.cw.material_delete()=={'CANCELLED'}
kit.unregister()
print('X4D_DELETE_LAST_ASSIGNED_MATERIAL_OK')
