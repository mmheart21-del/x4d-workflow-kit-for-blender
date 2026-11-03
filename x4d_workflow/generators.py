"""Child-driven generator objects, keeping source objects editable."""
import bpy
from bpy.app.handlers import persistent
from bpy.props import StringProperty
_busy=False
_signatures={}
NAMES={'SUBSURF':'细分曲面','BOOLEAN':'布尔','EXTRUDE':'挤压','LATHE':'旋转','SWEEP':'扫描','MIRROR':'对称','ARRAY':'阵列','WIREFRAME':'晶格','DECIMATE':'减面','SOLIDIFY':'布料曲面','WELD':'连接'}
MODIFIERS={'SUBSURF':'SUBSURF','MIRROR':'MIRROR','ARRAY':'ARRAY','WIREFRAME':'WIREFRAME','DECIMATE':'DECIMATE','SOLIDIFY':'SOLIDIFY','WELD':'WELD','BOOLEAN':'BOOLEAN','LATHE':'SCREW'}

def status(obj,message):
    if obj.cw.status!=message:obj.cw.status=message

def hide_source(child,host):
    if 'cw_generator_owner' not in child:
        child['cw_generator_visibility']=[int(child.hide_get()),int(child.hide_render)]
    if child.get('cw_generator_owner')!=host:child['cw_generator_owner']=host
    from .source_visibility import apply
    apply(child)
    if not child.hide_render:child.hide_render=True

def sync_one(obj):
    kind=obj.cw.generator
    actual=[o for o in obj.children if o.cw.kind not in {'EFFECTOR','FIELD'}]
    children=[link.target for link in obj.cw.inputs if link.target in actual]
    children+= [o for o in actual if o not in children]
    if not children:
        if obj.type=='MESH' and len(obj.data.vertices):obj.data.clear_geometry()
        if obj.type=='CURVE' and len(obj.data.splines):obj.data.splines.clear()
        _signatures.pop(obj.as_pointer(),None)
        status(obj,'将源对象拖入此生成器下面 / Parent a source object here');return
    for child in children:hide_source(child,obj)
    source=children[0]
    for child in children:
        if child.type=='MESH' and child.mode=='EDIT':child.update_from_editmode()
    if kind in {'EXTRUDE','SWEEP'}:
        if source.type!='CURVE':status(obj,'首个子对象需要是样条 / First child must be a curve');return
        if obj.type!='CURVE':status(obj,'生成器类型不匹配 / Generator type mismatch');return
        sig=(source.as_pointer(),tuple(v for row in source.matrix_local for v in row),tuple((tuple(p.co) for s in source.data.splines for p in s.points)),tuple((tuple(p.co) for s in source.data.splines for p in s.bezier_points)))
        if _signatures.get(obj.as_pointer())!=sig:
            previous=obj.data
            result=source.data.copy();result.name=obj.name+' Geometry'
            result.extrude=previous.extrude;result.bevel_depth=previous.bevel_depth
            result.transform(source.matrix_local)
            obj.data=result
            if previous.users==0:bpy.data.curves.remove(previous)
            _signatures[obj.as_pointer()]=sig
        if kind=='SWEEP':
            profile=next((o for o in children[1:] if o.type=='CURVE'),None)
            if not profile:status(obj,'第二个子对象需要是轮廓样条 / Add a profile curve as second child');return
            obj.data.bevel_mode='OBJECT';obj.data.bevel_object=profile
        status(obj,'');return
    if kind=='LATHE' and source.type=='CURVE':
        vertices=[];edges=[];polygons=[]
        for spline in source.data.splines:
            offset=len(vertices)
            points=spline.bezier_points if spline.type=='BEZIER' else spline.points
            vertices.extend(tuple(source.matrix_local @ p.co.to_3d()) for p in points)
            edges.extend((offset+i,offset+i+1) for i in range(len(points)-1))
            if spline.use_cyclic_u and len(points)>2:edges.append((len(vertices)-1,offset))
    elif source.type=='MESH':
        vertices=[];polygons=[];edges=[]
        meshes=[c for c in children if c.type=='MESH'] if kind=='WELD' else [source]
        for child in meshes:
            offset=len(vertices)
            vertices.extend(tuple(child.matrix_local @ v.co) for v in child.data.vertices)
            polygons.extend(tuple(i+offset for i in p.vertices) for p in child.data.polygons)
            edges.extend(tuple(i+offset for i in e.vertices) for e in child.data.edges)
    else:status(obj,'首个子对象需要是网格 / First child must be a mesh');return
    sig=(source.as_pointer(),hash(tuple(vertices)),hash(tuple(polygons)),hash(tuple(edges)))
    if _signatures.get(obj.as_pointer())!=sig:
        if obj.data.users>1:obj.data=obj.data.copy()
        obj.data.clear_geometry();obj.data.from_pydata(vertices,edges,polygons);obj.data.update()
        obj.data.materials.clear()
        for mat in source.data.materials:
            if mat:obj.data.materials.append(mat)
        if source.type=='MESH':
            for a,b in zip(obj.data.polygons,source.data.polygons):a.material_index=b.material_index;a.use_smooth=b.use_smooth
        _signatures[obj.as_pointer()]=sig
    if kind=='BOOLEAN':
        other=next((c for c in children[1:] if c.type=='MESH'),None)
        modifier=next((m for m in obj.modifiers if m.type=='BOOLEAN'),None)
        if modifier:
            modifier.object=other
            modifier.solver='EXACT'
        if not other:status(obj,'添加第二个网格子对象作为布尔工具 / Add a second mesh child');return
    status(obj,'')

@persistent
def sync(scene,*args):
    global _busy
    if _busy:return
    _busy=True
    try:
        for child in scene.objects:
            if 'cw_generator_owner' in child and (not child.get('cw_generator_owner') or child.parent!=child.get('cw_generator_owner')):
                hidden,render=child.get('cw_generator_visibility',[0,0])
                child.hide_set(bool(hidden));child.hide_render=bool(render)
                del child['cw_generator_owner'];del child['cw_generator_visibility']
        for obj in scene.objects:
            if obj.cw.kind=='GENERATOR':
                try:sync_one(obj)
                except Exception as exc:status(obj,str(exc))
    finally:_busy=False

def stop():_signatures.clear()

class CW_OT_generator(bpy.types.Operator):
    bl_idname='cw.generator';bl_label='创建生成器 / Create Generator';bl_options={'REGISTER','UNDO'}
    kind:StringProperty(default='SUBSURF')
    def execute(self,context):
        if self.kind not in NAMES:return {'CANCELLED'}
        selected=list(context.selected_objects)
        if context.active_object in selected:selected.remove(context.active_object);selected.insert(0,context.active_object)
        if context.object and context.object.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
        data=bpy.data.curves.new(NAMES[self.kind],'CURVE') if self.kind in {'EXTRUDE','SWEEP'} else bpy.data.meshes.new(NAMES[self.kind])
        if isinstance(data,bpy.types.Curve):data.dimensions='2D';data.extrude=.5 if self.kind=='EXTRUDE' else 0
        host=bpy.data.objects.new(NAMES[self.kind],data);context.collection.objects.link(host)
        host.cw.kind='GENERATOR';host.cw.generator=self.kind
        if selected:host.matrix_world=selected[0].matrix_world.copy()
        for child in selected:
            host.cw.inputs.add().target=child
            matrix=child.matrix_world.copy();child.parent=host;child.matrix_world=matrix
            hide_source(child,host);child.select_set(False)
        if self.kind in MODIFIERS:
            m=host.modifiers.new(NAMES[self.kind],MODIFIERS[self.kind])
            if m.type=='SUBSURF':m.levels=2
            elif m.type=='BOOLEAN':m.operation='DIFFERENCE'
        context.view_layer.objects.active=host;host.select_set(True)
        context.view_layer.update();sync(context.scene)
        return {'FINISHED'}
classes=[CW_OT_generator]



