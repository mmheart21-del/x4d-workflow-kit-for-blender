import bpy,sys,os,json,math,wave,struct
root=os.path.dirname(os.path.dirname(__file__));sys.path.insert(0,root)
import x4d_workflow as kit
from x4d_workflow import extras,advanced_fx
kit.register();results=[]
def clean():
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);extras.stop()
def cube():bpy.ops.mesh.primitive_cube_add();return bpy.context.object
def check(obj):
    assert not any(s in obj.cw.status for s in ['Unknown','attribute','Traceback','NoneType','enum','not found','Error']),obj.cw.status
    return obj
for kind in ['CAPSULE','OIL_TANK','TUBE','FIGURE','LANDSCAPE']:
    clean();bpy.ops.cw.extra(kind=kind);obj=check(bpy.context.object);assert len(obj.data.vertices)>20,(kind,obj.cw.status);results.append(kind)
for kind in ['FORMULA_SPLINE','PROFILE','MOSPLINE']:
    clean();bpy.ops.cw.extra(kind=kind);obj=check(bpy.context.object);assert obj.data.splines and len(obj.data.splines[0].points)>2,(kind,obj.cw.status);results.append(kind)
clean();bpy.ops.cw.catalog(command='SPLINE:CIRCLE');a=bpy.context.object
bpy.ops.cw.catalog(command='SPLINE:CIRCLE');b=bpy.context.object;b.location.z=2;a.select_set(True)
bpy.ops.cw.extra(kind='LOFT');obj=check(bpy.context.object);assert len(obj.data.polygons)>10,obj.cw.status;results.append('LOFT')
clean();bpy.ops.cw.catalog(command='SPLINE:CIRCLE');a=bpy.context.object
bpy.ops.cw.catalog(command='SPLINE:CIRCLE');b=bpy.context.object;b.location.x=.7;a.select_set(True)
bpy.ops.cw.extra(kind='SPLINE_MASK');obj=check(bpy.context.object);assert obj.data.splines,obj.cw.status;results.append('SPLINE_MASK')
for kind in ['VOLUME_BUILDER','VOLUME_MESHER','SDF_SMOOTH','FOG_SMOOTH','FRACTURE','VORONOI','MOEXTRUDE','LOD']:
    clean();source=cube();bpy.ops.cw.extra(kind=kind);obj=check(bpy.context.object)
    assert obj.cw.status=='' or 'camera' in obj.cw.status.lower(),(kind,obj.cw.status)
    assert len(obj.data.vertices)>0,(kind,obj.cw.status)
    if kind in {'VOLUME_MESHER','SDF_SMOOTH'}:
        bpy.context.view_layer.update();evaluated=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=evaluated.to_mesh();assert len(mesh.vertices)>0,(kind,'empty evaluated volume mesh');evaluated.to_mesh_clear()
    if kind=='VORONOI':assert len(set(v.value for v in obj.data.attributes['cw_piece'].data))>1
    if kind=='MOEXTRUDE':assert len(obj.data.polygons)>6
    results.append(kind)
clean();source=cube();attr=source.data.attributes.new('velocity','FLOAT_VECTOR','POINT');attr.data[0].vector=(4,0,0)
bpy.ops.cw.extra(kind='VECTOR_SMOOTH');obj=check(bpy.context.object);assert obj.data.attributes.get('cw_velocity'),obj.cw.status;assert obj.data.attributes['cw_velocity'].data[0].vector.x<4;results.append('VECTOR_SMOOTH')
for kind in ['FORMULA_DEFORM','MELT']:
    clean();source=cube();before=[tuple(v.co) for v in source.data.vertices];bpy.ops.cw.extra(kind=kind);obj=check(bpy.context.object);assert before!=[tuple(v.co) for v in source.data.vertices],(kind,obj.cw.status);results.append(kind)
clean();bpy.ops.cw.extra(kind='PYTHON_GENERATOR');obj=bpy.context.object;assert obj.data.vertices
bpy.ops.cw.run_python();assert len(obj.data.polygons)==5,obj.cw.status;results.append('PYTHON_GENERATOR')
clean();bpy.ops.cw.extra(kind='MATRIX');obj=check(bpy.context.object);assert len(obj.data.vertices)==9,obj.cw.status;assert len(obj.modifiers)==1;results.append('MATRIX')
clean();source=cube();bpy.ops.cw.extra(kind='IES');obj=check(bpy.context.object);assert obj.type=='LIGHT' and any(n.bl_idname=='ShaderNodeTexIES' for n in obj.data.node_tree.nodes),obj.cw.status;results.append('IES')
# All catalog entries now have actual command routes; import has its own file test.
assert all(command for category in kit.catalog.CATEGORIES for cn,en,command in category[5])
with open(os.path.join(root,'artifacts','extended-test-results.json'),'w') as f:json.dump(results,f,indent=2)
print('CW_EXTENDED_GEOMETRY_OK',len(results),results)
kit.unregister()

