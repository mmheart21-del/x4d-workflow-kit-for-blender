import bpy,sys,os
sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))
import x4d_workflow as kit
kit.register()
bpy.ops.cw.primitive(kind='CUBE');obj=bpy.context.object
obj.cw_size=(2,4,6)
assert tuple(obj.cw_primitive.size)==(2,6,4)
assert tuple(obj.cw_size)==(2,4,6)
bpy.ops.cw.create(kind='FIELD');field=bpy.context.object
assert field.empty_display_size==field.cw.radius
field.cw.radius=7;assert field.empty_display_size==7
field.cw.field_type='BOX';assert field.empty_display_type=='CUBE'
field.cw.field_type='SPHERE';assert field.empty_display_type=='SPHERE'
kit.unregister()
assert not hasattr(bpy.types.Object,'cw_size')
print('CW_ATTRIBUTES_OK')
