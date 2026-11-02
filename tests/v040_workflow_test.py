import bpy,sys,os
sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))
import x4d_workflow as kit
kit.register()
bpy.ops.cw.primitive(kind='CUBE');source=bpy.context.object
source.cw_primitive.subdivisions=4
assert len(source.data.polygons)==96
bpy.ops.cw.catalog(command='ACTION:SUBSURF');original=bpy.context.object
bpy.ops.cw.action(action='STATE');copy=bpy.context.object
assert original!=copy and copy.cw.kind=='' and original.cw.kind=='GENERATOR'
assert len(copy.data.vertices)>8
bpy.context.view_layer.objects.active=original;copy.select_set(False);original.select_set(True)
bpy.ops.cw.action(action='EDITABLE');assert original.cw.kind=='' and len(original.data.vertices)>8
bpy.ops.cw.primitive(kind='CUBE');target=bpy.context.object
bpy.ops.cw.catalog(command='LATTICE:CREATE');cage=bpy.context.object
assert cage.type=='LATTICE' and target.modifiers[-1].object==cage
area=next(a for a in bpy.context.screen.areas if a.type=='VIEW_3D');region=next(r for r in area.regions if r.type=='WINDOW')
with bpy.context.temp_override(area=area,region=region):
    bpy.ops.cw.tool(tool='POINT');assert cage.mode=='EDIT'
    bpy.ops.cw.tool(tool='OBJECT');assert cage.mode=='OBJECT'
bpy.ops.cw.primitive(kind='CUBE');left=bpy.context.object
bpy.ops.cw.primitive(kind='CUBE');right=bpy.context.object;right.location.x=4
left.select_set(True);bpy.context.view_layer.objects.active=left
bpy.ops.cw.generator(kind='WELD');connected=bpy.context.object
assert len(connected.data.vertices)==16 and len(connected.data.polygons)==12
# Built-in menu targets must actually exist.
for name in ['TOPBAR_MT_file','TOPBAR_MT_edit','TOPBAR_MT_render','TOPBAR_MT_window','TOPBAR_MT_help']:assert hasattr(bpy.types,name),name
kit.unregister()
print('CW_V040_WORKFLOW_OK')

