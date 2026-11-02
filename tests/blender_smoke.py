import sys, os, time, json
sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))
import bpy
import x4d_workflow as kit
from x4d_workflow import engine
kit.register()
bpy.ops.mesh.primitive_cube_add()
source=bpy.context.object
bpy.ops.cw.create(kind='CLONER');cloner=bpy.context.object
engine._busy=True
cloner.cw.count=(10,10,10)
engine._busy=False
start=time.perf_counter();engine.rebuild_all(bpy.context.scene)
assert len(cloner.data.vertices)==1000,cloner.cw.status
assert len(cloner.modifiers)==1
bpy.ops.cw.create(kind='FIELD');field=bpy.context.object
bpy.ops.cw.create(kind='EFFECTOR');eff=bpy.context.object
engine._busy=True
eff.cw.fields.add().target=field
cloner.cw.effectors.add().target=eff
engine._busy=False
engine.rebuild_all(bpy.context.scene)
assert not cloner.cw.status,cloner.cw.status
bpy.context.view_layer.update()
graph=bpy.context.evaluated_depsgraph_get()
evaluated=cloner.evaluated_get(graph)
instances=sum(1 for i in graph.object_instances if i.is_instance and i.parent and i.parent.original==cloner)
assert instances==1000,instances
results={'1000_instances':instances,'seconds':time.perf_counter()-start}
engine._busy=True;cloner.cw.count=(100,100,1);engine._busy=False
start=time.perf_counter();engine.rebuild_all(bpy.context.scene);results['10000_seconds']=time.perf_counter()-start
assert len(cloner.data.vertices)==10000
engine._busy=True;cloner.cw.count=(5,5,1);engine._busy=False;engine.rebuild_all(bpy.context.scene)
root=os.path.dirname(os.path.dirname(__file__))
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(root,'examples','03_mograph.blend'))
bpy.ops.wm.open_mainfile(filepath=os.path.join(root,'examples','03_mograph.blend'))
cloner=next(o for o in bpy.context.scene.objects if o.cw.kind=='CLONER')
assert len(cloner.cw.effectors)==1 and cloner.cw.effectors[0].target
engine.rebuild_all(bpy.context.scene);assert len(cloner.data.vertices)==25
print('CW_TEST_RESULTS',json.dumps(results))
kit.unregister();kit.register();kit.unregister()
print('CW_TEST_OK')
