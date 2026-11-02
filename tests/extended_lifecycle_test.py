import bpy,sys,os
root=os.path.dirname(os.path.dirname(__file__));sys.path.insert(0,root)
import x4d_workflow as kit
kit.register()
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.cw.primitive(kind='CUBE');target=bpy.context.object;target.name='Target'
bpy.ops.cw.extra(kind='FORMULA_DEFORM');controller=bpy.context.object;controller.name='Formula'
kit.extras.update(bpy.context.scene)
expected=[tuple(v.co) for v in target.data.vertices]
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(root,'artifacts','extended-lifecycle.blend'))
bpy.ops.wm.open_mainfile(filepath=os.path.join(root,'artifacts','extended-lifecycle.blend'))
kit.extras.update(bpy.context.scene)
target=bpy.data.objects['Target'];controller=bpy.data.objects['Formula']
assert controller.cw_extra.source==target
assert max(abs(v.co[i]-p[i]) for v,p in zip(target.data.vertices,expected) for i in range(3))<1e-5
controller.cw_extra.amount=0
kit.extras.update(bpy.context.scene)
assert max(abs(v.co.z) for v in target.data.vertices)<1.01
bpy.ops.cw.extra(kind='LANDSCAPE');original=bpy.context.object
copy=original.copy();copy.data=original.data.copy();bpy.context.collection.objects.link(copy)
copy.cw_extra.size=(20,20,5);kit.extras.update(bpy.context.scene)
assert original.data!=copy.data
assert abs(max(v.co.x for v in original.data.vertices)-5)<.001
assert abs(max(v.co.x for v in copy.data.vertices)-10)<.001
print('CW_EXTENDED_LIFECYCLE_OK')
kit.unregister()
