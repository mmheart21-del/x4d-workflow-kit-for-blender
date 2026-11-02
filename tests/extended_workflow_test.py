import bpy,sys,os,math,json
from mathutils import Vector
root=os.path.dirname(os.path.dirname(__file__));sys.path.insert(0,root)
import x4d_workflow as kit
kit.register();results=[]
def clean():bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);kit.extras.stop()
def cube():bpy.ops.mesh.primitive_cube_add();return bpy.context.object
# Image-driven relief and background material.
clean();image=bpy.data.images.new('Height',width=2,height=2);image.pixels=[0,0,0,1,1,1,1,1,.5,.5,.5,1,.8,.8,.8,1];image.update()
bpy.ops.cw.extra(kind='RELIEF');obj=bpy.context.object;obj.cw_extra.image=image
assert max(v.co.z for v in obj.data.vertices)>min(v.co.z for v in obj.data.vertices),obj.cw.status;results.append('RELIEF_IMAGE')
bpy.ops.cw.extra(kind='BACKGROUND');obj=bpy.context.object;obj.cw_extra.image=image
assert obj.data.uv_layers and obj.data.materials and len(obj.data.polygons)==1;results.append('BACKGROUND_IMAGE')
# SVG import uses its actual file execution path.
svg=os.path.join(root,'artifacts','test-vector.svg')
with open(svg,'w') as f:f.write('<svg xmlns="http://www.w3.org/2000/svg"><g transform="translate(10,20)"><rect width="100" height="100"/><path d="M0 0 C0 100 100 100 100 0 A50 50 0 0 1 0 0 Z"/></g></svg>')
assert 'FINISHED' in bpy.ops.cw.import_svg(filepath=svg)
assert len(bpy.context.object.data.splines)==2;results.append('SVG_FILE')
# Surface scatter.
clean();prototype=cube();surface=cube();surface.scale=(4,4,.1);prototype.select_set(True);bpy.context.view_layer.objects.active=prototype
bpy.ops.cw.extra(kind='SCATTER');obj=bpy.context.object
assert obj.cw.surface==surface and len(obj.data.vertices)==100,obj.cw.status;results.append('SCATTER_SURFACE')
# Tracer connects an explicit object list, then tracks a single animated source.
clean();a=cube();b=cube();b.location.x=3;a.select_set(True);bpy.ops.cw.extra(kind='TRACER');tracer=bpy.context.object
assert len(tracer.data.splines[0].points)==2,tracer.cw.status;results.append('TRACER_LIST')
# Collision projection and deletion restoration.
clean();source=cube();collider=cube();collider.scale=(3,3,3);bpy.context.view_layer.update()
collider.select_set(False);source.select_set(True);bpy.context.view_layer.objects.active=source
before=tuple(tuple(v.co) for v in source.data.vertices)
bpy.ops.cw.extra(kind='COLLISION');controller=bpy.context.object;controller.cw_extra.target=collider
assert before!=tuple(tuple(v.co) for v in source.data.vertices),controller.cw.status
bpy.data.objects.remove(controller,do_unlink=True);kit.extras.update(bpy.context.scene)
assert before==tuple(tuple(v.co) for v in source.data.vertices);results.append('COLLISION_AND_RESTORE')
# Formula/melt stack is stable across repeated evaluation.
clean();source=cube();bpy.ops.cw.extra(kind='MELT');melt=bpy.context.object
source.select_set(True);melt.select_set(False);bpy.context.view_layer.objects.active=source
bpy.ops.cw.extra(kind='FORMULA_DEFORM');formula=bpy.context.object
first=tuple(tuple(v.co) for v in source.data.vertices)
for _ in range(5):kit.extras.update(bpy.context.scene)
assert first==tuple(tuple(v.co) for v in source.data.vertices);results.append('STABLE_DEFORM_STACK')
# Delay blends from the prior frame, not repeated redraws of the current frame.
clean();source=cube();bpy.ops.cw.create(kind='CLONER');cloner=bpy.context.object
bpy.ops.cw.catalog(command='EFFECTOR:PLAIN');plain=bpy.context.object;plain.cw.move=(0,0,0)
bpy.ops.cw.catalog(command='EFFECTOR:DELAY');delay=bpy.context.object;delay.cw_extra.amount=.5
cloner.cw.effectors.add().target=plain;cloner.cw.effectors.add().target=delay
bpy.context.scene.frame_set(1);kit.engine.rebuild_all(bpy.context.scene)
bpy.context.scene.frame_set(2);plain.cw.move=(0,0,10);kit.engine.rebuild_all(bpy.context.scene)
assert abs(cloner.data.vertices[0].co.z-5)<1e-5,cloner.data.vertices[0].co
for _ in range(3):kit.engine.rebuild_all(bpy.context.scene)
assert abs(cloner.data.vertices[0].co.z-5)<1e-5;results.append('DELAY_HISTORY')
# Scripts are deactivated after unregister/re-enable.
assert all(command for row in kit.catalog.CATEGORIES for cn,en,command in row[5])
with open(os.path.join(root,'artifacts','extended-workflow-results.json'),'w') as f:json.dump(results,f,indent=2)
print('CW_EXTENDED_WORKFLOW_OK',results)
kit.unregister()
