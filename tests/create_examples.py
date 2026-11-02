import sys,os
sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))
import bpy
import x4d_workflow as kit
kit.register()
root=os.path.dirname(os.path.dirname(__file__))
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.mesh.primitive_cube_add();obj=bpy.context.object
obj.name='01 Modeling — rounded industrial block'
bpy.ops.cw.action(action='SUBSURF');obj.modifiers[-1].levels=2
bpy.ops.cw.action(action='MATERIAL')
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(root,'examples','01_modeling.blend'))
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.mesh.primitive_cylinder_add(vertices=32,depth=8)
obj=bpy.context.object;obj.name='02 Native bend workflow'
bpy.ops.cw.action(action='BEND');bpy.ops.cw.action(action='GROUP')
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(root,'examples','02_deformer.blend'))
print('CW_EXAMPLES_OK')
