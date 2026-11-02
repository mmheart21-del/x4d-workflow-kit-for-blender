import bpy,sys,os
root=os.path.dirname(os.path.dirname(__file__));sys.path.insert(0,root)
import x4d_workflow as kit
from x4d_workflow import generators
kit.register()
# Every generator can be created in an empty scene.
for kind in generators.NAMES:
    bpy.ops.object.select_all(action='DESELECT');bpy.context.view_layer.objects.active=None
    assert 'FINISHED' in bpy.ops.cw.generator(kind=kind)
    assert bpy.context.object.cw.status,kind
# Parent, evaluate, change source dimensions, and restore source visibility.
bpy.ops.cw.primitive(kind='CUBE');source=bpy.context.object
bpy.ops.cw.generator(kind='SUBSURF');host=bpy.context.object
assert source.parent==host and source.hide_get()
assert len(host.data.vertices)==8 and not host.cw.status,host.cw.status
source.cw_size=(4,6,8);generators.sync(bpy.context.scene)
assert max(v.co.x for v in host.data.vertices)==2
context=bpy.context;context.view_layer.update()
mesh=host.evaluated_get(context.evaluated_depsgraph_get()).to_mesh()
assert len(mesh.vertices)>8
host.evaluated_get(context.evaluated_depsgraph_get()).to_mesh_clear()
source.parent=None;generators.sync(context.scene)
assert not source.hide_get() and not source.hide_render
assert len(host.data.vertices)==0
# Curve extrusion and rotation accept editable spline children.
bpy.ops.cw.catalog(command='SPLINE:CIRCLE');curve=bpy.context.object
bpy.ops.cw.generator(kind='EXTRUDE');extrude=bpy.context.object
assert curve.parent==extrude and len(extrude.data.splines)==1 and extrude.data.extrude>.0
assert not extrude.cw.status,extrude.cw.status
bpy.ops.cw.catalog(command='SPLINE:ARC');arc=bpy.context.object
bpy.ops.cw.generator(kind='LATHE');lathe=bpy.context.object
assert len(lathe.data.edges)>0 and not lathe.cw.status,lathe.cw.status
# Sweep input order is explicit, independent of object-name sorting.
bpy.ops.cw.catalog(command='SPLINE:HELIX');path=bpy.context.object
bpy.ops.cw.catalog(command='SPLINE:CIRCLE');profile=bpy.context.object
path.select_set(True);context.view_layer.objects.active=path
bpy.ops.cw.generator(kind='SWEEP');sweep=bpy.context.object
assert sweep.data.bevel_object==profile and not sweep.cw.status,sweep.cw.status
# Repeated restore/re-entry must invalidate old modal rail handlers.
before=kit.rail._generation;kit.rail.stop();assert kit.rail._generation==before+1 and not kit.rail._running
kit.unregister()
print('CW_GENERATORS_OK')
