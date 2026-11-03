import bpy,sys,os
sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))
import x4d_workflow as kit
kit.register();bpy.ops.cw.workspace()
def reset():
    for obj in list(bpy.context.scene.objects):bpy.data.objects.remove(obj,do_unlink=True)
    kit.source_visibility._active.clear()
def sources(kind):
    bpy.ops.mesh.primitive_cube_add();a=bpy.context.object
    bpy.ops.mesh.primitive_cube_add(location=(1,0,0));b=bpy.context.object
    a.select_set(True);bpy.context.view_layer.objects.active=a
    if kind=='BOOLEAN':bpy.ops.cw.generator(kind='BOOLEAN')
    else:bpy.ops.cw.extra(kind='VOLUME_BUILDER')
    host=bpy.context.object;kit.source_visibility.sync(bpy.context.window)
    return a,b,host
for kind in ['BOOLEAN','VOLUME']:
    reset();a,b,host=sources(kind);original=a.display_type
    assert a.hide_get() and b.hide_get()
    bpy.context.view_layer.objects.active=a
    kit.source_visibility.sync(bpy.context.window)
    assert not a.hide_get() and a.display_type=='WIRE' and a.show_in_front
    before=tuple(tuple(v.co) for v in host.data.vertices)
    a.location.x+=.4;bpy.context.view_layer.update()
    kit.generators.sync(bpy.context.scene);kit.extras.update(bpy.context.scene)
    after=tuple(tuple(v.co) for v in host.data.vertices)
    assert before!=after,kind
    a.select_set(False);kit.source_visibility.sync(bpy.context.window)
    assert a.hide_get() and a.display_type==original and not a.show_in_front
    bpy.context.view_layer.objects.active=a;kit.source_visibility._active.clear();kit.source_visibility.sync(bpy.context.window)
    a.parent=None;kit.generators.sync(bpy.context.scene);kit.source_visibility.sync(bpy.context.window)
    assert a.display_type==original and not a.hide_get()
    print('X4D_WIRE_SOURCE_OK',kind)
kit.unregister()
