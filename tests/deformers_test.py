import bpy,sys,os
sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))
import x4d_workflow as kit
kit.register()
bpy.ops.object.select_all(action='DESELECT');bpy.context.view_layer.objects.active=None
for kind in ['BEND','TWIST','TAPER']:
    bpy.ops.object.select_all(action='DESELECT');bpy.context.view_layer.objects.active=None
    bpy.ops.cw.catalog(command='ACTION:'+kind)
    controller=bpy.context.object
    assert controller.cw.kind=='DEFORMER' and controller.cw.status
    bpy.ops.cw.primitive(kind='CUBE');target=bpy.context.object
    controller.cw.deform_target=target
    assert len(target.modifiers)==1 and target.modifiers[0].origin==controller
    controller.cw.deform_axis='X';assert target.modifiers[0].deform_axis=='X'
    controller.cw.deform_axis='Y';assert target.modifiers[0].deform_axis=='Z'
    controller.cw.deform_angle=1.0
    controller.cw.deform_factor=.7
    modifier=target.modifiers[0]
    assert abs((modifier.factor if kind=='TAPER' else modifier.angle)-(.7 if kind=='TAPER' else 1))<1e-6
    bpy.context.view_layer.update()
    evaluated=target.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=evaluated.to_mesh();assert len(mesh.vertices)==8;evaluated.to_mesh_clear()
    controller.cw.deform_target=None;assert not target.modifiers
    controller.cw.deform_target=target;assert len(target.modifiers)==1
    bpy.data.objects.remove(controller,do_unlink=True)
    kit.deformers.sync(bpy.context.scene);assert not target.modifiers
kit.unregister()
print('CW_DEFORMERS_OK')

