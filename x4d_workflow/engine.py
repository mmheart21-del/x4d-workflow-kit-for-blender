import bpy
import random
import math
from mathutils import Vector, Euler
from bpy.app.handlers import persistent
from bpy.props import (StringProperty, EnumProperty, FloatProperty, IntProperty, BoolProperty, FloatVectorProperty, IntVectorProperty, PointerProperty, CollectionProperty)
from .object_lists import CWObjectTag
from .core import positions, field_weight, blend_weight

_busy = False
_EFFECTOR_LABELS=dict(PLAIN='简易',RANDOM='随机',STEP='步幅',DELAY='延迟',FORMULA='公式',SHADER='着色',SOUND='声音',TIME='时间',TARGET='目标',SPLINE='样条',PYTHON='Python')
_FIELD_LABELS=dict(LINEAR='线性',SPHERE='球体',BOX='盒形',RANDOM='随机',CYLINDER='圆柱体',CONE='圆锥体',CAPSULE='胶囊体',TORUS='圆环体',SHADER='着色器',SOUND='声音',FORMULA='公式',GROUP='组域')


def localized_items(names):
    variants=[
        [(key,key.title(),'',i) for i,key in enumerate(names)],
        [(key,value,'',i) for i,(key,value) in enumerate(names.items())],
    ]
    def items(self,context):
        return variants[int(bpy.context.preferences.view.language.startswith('zh'))]
    return items

effector_items=localized_items(_EFFECTOR_LABELS)
field_items=localized_items(_FIELD_LABELS)

def changed(self, context):
    if getattr(self,'kind','')=='FIELD':
        obj=self.id_data
        obj.empty_display_size=min(self.radius,.15)
        obj.empty_display_type='PLAIN_AXES'
    if context and not _busy:
        if isinstance(self,CWLink) and '.inputs[' in self.path_from_id():
            from .object_lists import sync_volume_sources
            sync_volume_sources(self.id_data,context.scene)
        if getattr(self,'kind','')=='DEFORMER':
            from . import deformers
            deformers.sync(context.scene)
        from . import extras
        extras._CACHE.clear();extras.update(context.scene)
        rebuild_all(context.scene)

def field_target(self,obj):
    return obj.cw.kind=='FIELD'

def link_target(self,obj):
    path=self.path_from_id()
    if '.effectors[' in path:return obj.cw.kind=='EFFECTOR'
    if '.sources[' in path:return obj!=self.id_data and obj.cw.kind not in {'CLONER','FIELD','EFFECTOR'} and self.id_data not in obj.children_recursive
    if '.inputs[' in path and self.id_data.cw_extra.kind in {'VOLUME_BUILDER','VOLUME_MESHER','SDF_SMOOTH','FOG_SMOOTH'}:
        return obj.type=='MESH' and obj!=self.id_data and self.id_data not in obj.children_recursive
    return True

class CWField(bpy.types.PropertyGroup):
    target: PointerProperty(type=bpy.types.Object, poll=field_target, update=changed)
    mode: EnumProperty(items=[(x,x.title(),'') for x in ['ADD','MULTIPLY','MAX','MIN','SUBTRACT']],default='ADD',update=changed)
    invert: BoolProperty(update=changed)
    low: FloatProperty(default=0,min=0,max=1,update=changed)
    high: FloatProperty(default=1,min=0,max=1,update=changed)

class CWLink(bpy.types.PropertyGroup):
    enabled: BoolProperty(default=True,update=changed)
    target: PointerProperty(type=bpy.types.Object, poll=link_target, update=changed)

class CWSettings(bpy.types.PropertyGroup):
    kind: StringProperty()
    deform_target: PointerProperty(type=bpy.types.Object,update=changed)
    deform_type: StringProperty(default='BEND')
    deform_angle: FloatProperty(default=.5,subtype='ANGLE',update=changed)
    deform_factor: FloatProperty(default=.25,update=changed)
    deform_axis: EnumProperty(items=[(v,v,'') for v in 'XYZ'],default='Y',update=changed)
    generator: StringProperty()
    inputs: CollectionProperty(type=CWLink)
    mode: EnumProperty(items=[(x,x.title(),'') for x in ['LINEAR','RADIAL','GRID','SURFACE']],default='GRID',update=changed)
    count: IntVectorProperty(size=3,default=(3,3,1),min=1,max=1000,update=changed)
    spacing: FloatVectorProperty(size=3,default=(3,3,3),update=changed)
    inner_range: FloatProperty(name='Inner Range',default=0,min=0,max=.99,subtype='FACTOR',update=changed)
    radius: FloatProperty(default=5,min=.001,update=changed)
    source: PointerProperty(type=bpy.types.Object,update=changed)
    surface: PointerProperty(type=bpy.types.Object,update=changed)
    tags: CollectionProperty(type=CWObjectTag)
    tag_index: IntProperty(min=0)
    source_index: IntProperty(min=0)
    sources_list_ready: BoolProperty()
    sources: CollectionProperty(type=CWLink)
    effectors: CollectionProperty(type=CWLink)
    fields: CollectionProperty(type=CWField)
    effector: EnumProperty(items=effector_items,update=changed)
    field_type: EnumProperty(items=field_items,default=1,update=changed)
    strength: FloatProperty(default=1,update=changed)
    move: FloatVectorProperty(size=3,default=(0,0,2),update=changed)
    rotate: FloatVectorProperty(size=3,subtype='EULER',update=changed)
    scale: FloatVectorProperty(size=3,default=(0,0,0),update=changed)
    seed: IntProperty(default=42,update=changed)
    status: StringProperty()

def node(tree, kind, x=0,y=0):
    n=tree.nodes.new(kind); n.location=(x,y); return n

def clone_sources(obj):
    return list(dict.fromkeys(source for source in
        ([] if obj.cw.sources_list_ready else [obj.cw.source])+[link.target for link in obj.cw.sources if link.enabled]
        if source is not None))

def ensure_graph(obj):
    mod=next((m for m in obj.modifiers if m.type=='NODES' and m.name=='CW Instances'),None)
    if mod and mod.node_group and not mod.node_group.get('x4d_multi_source'):
        obj.modifiers.remove(mod)
        mod=None
    if mod and mod.node_group:
        if bool(mod.node_group.get('cw_matrix',False)) == (obj.cw_extra.kind=='MATRIX'):
            if mod.node_group.users>1:mod.node_group=mod.node_group.copy()
            return
        obj.modifiers.remove(mod)
    tree=bpy.data.node_groups.new('CW Instances','GeometryNodeTree')
    tree['x4d_multi_source']=True
    tree['cw_matrix']=obj.cw_extra.kind=='MATRIX'
    tree.interface.new_socket(name='Geometry',in_out='INPUT',socket_type='NodeSocketGeometry')
    tree.interface.new_socket(name='Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
    inp=node(tree,'NodeGroupInput',-600,0); out=node(tree,'NodeGroupOutput',400,0)
    inst=node(tree,'GeometryNodeInstanceOnPoints',150,0)
    if obj.cw_extra.kind=='MATRIX':
        source=node(tree,'GeometryNodeMeshCube',-600,-200);source.inputs['Size'].default_value=(.1,.1,.1)
    else:
        source=node(tree,'GeometryNodeJoinGeometry',-200,-200)
        source.name='X4D Sources'
        inst.inputs['Pick Instance'].default_value=True
        index=node(tree,'GeometryNodeInputNamedAttribute',-200,-400)
        index.data_type='INT'
        index.inputs['Name'].default_value='cw_source_index'
        tree.links.new(index.outputs['Attribute'],inst.inputs['Instance Index'])
    tree.links.new(inp.outputs['Geometry'],inst.inputs['Points'])
    tree.links.new(source.outputs.get('Geometry') or source.outputs['Mesh'],inst.inputs['Instance'])
    for name,socket in [('cw_rotation','Rotation'),('cw_scale','Scale')]:
        attr=node(tree,'GeometryNodeInputNamedAttribute',-300,-400 if socket=='Scale' else -200)
        attr.data_type='FLOAT_VECTOR'; attr.inputs['Name'].default_value=name
        tree.links.new(attr.outputs['Attribute'],inst.inputs[socket])
    tree.links.new(inst.outputs['Instances'],out.inputs['Geometry'])
    mod=obj.modifiers.new('CW Instances','NODES'); mod.node_group=tree

def rebuild(obj, scene):
    s=obj.cw
    matrix=obj.cw_extra.kind=='MATRIX'
    sources=clone_sources(obj)
    if not sources and not matrix:
        if obj.data.vertices:obj.data.clear_geometry()
        mod=obj.modifiers.get('CW Instances')
        if mod:obj.modifiers.remove(mod)
        s.status='请选择其他对象作为克隆源 / Select a source'; return
    # A source depending on this cloner creates an evaluation cycle.
    for source in sources:
        parent=source
        while parent:
            if parent==obj and source.get('x4d_clone_owner')!=obj:s.status='Cyclic reference';return
            parent=parent.parent
        if source.cw.kind=='CLONER':
            s.status='Nested cloners unsupported';return
    total=math.prod(s.count) if s.mode=='GRID' else s.count[0]
    if total>100000:
        s.status='实例数上限 100000 / Instance limit'; return
    if s.mode=='SURFACE':
        if not s.surface or s.surface.type!='MESH' or s.surface==obj:
            s.status='请选择网格表面 / Select mesh surface'; return
        mesh=s.surface.data; mesh.calc_loop_triangles()
        tris=list(mesh.loop_triangles)
        if not tris: s.status='表面没有三角面 / Empty surface'; return
        rng=random.Random(s.seed); weights=[t.area for t in tris]
        pts=[]
        for i in range(total):
            t=rng.choices(tris,weights=weights,k=1)[0]; u=math.sqrt(rng.random()); v=rng.random()
            a,b,c=[mesh.vertices[j].co for j in t.vertices]
            pts.append(obj.matrix_world.inverted() @ s.surface.matrix_world @ ((1-u)*a+u*(1-v)*b+u*v*c))
    else: pts=[Vector(p) for p in positions(s.mode,s.count,s.spacing,s.radius)]
    result,rotations,scales,warnings=evaluate_clones(obj,pts,scene)
    if obj.data.users>1:obj.data=obj.data.copy()
    obj.data.clear_geometry(); obj.data.from_pydata(result,[],[])
    for name,values in [('cw_rotation',rotations),('cw_scale',scales)]:
        attr=obj.data.attributes.get(name) or obj.data.attributes.new(name,'FLOAT_VECTOR','POINT')
        attr.data.foreach_set('vector',[x for value in values for x in value])
    ensure_graph(obj)
    mod=next(m for m in obj.modifiers if m.name=='CW Instances')
    if not matrix:
        tree=mod.node_group
        source_index=obj.data.attributes.get('cw_source_index') or obj.data.attributes.new('cw_source_index','INT','POINT')
        source_index.data.foreach_set('value',[i%len(sources) for i in range(len(pts))])
        nodes=[n for n in tree.nodes if n.bl_idname=='GeometryNodeObjectInfo']
        if [n.inputs['Object'].default_value for n in nodes]!=sources:
            for n in nodes:tree.nodes.remove(n)
            for i,source in enumerate(sources):
                n=node(tree,'GeometryNodeObjectInfo',-620,-220*i)
                n.inputs['As Instance'].default_value=True
                n.inputs['Object'].default_value=source
                n.transform_space='ORIGINAL'
            nodes=[n for n in tree.nodes if n.bl_idname=='GeometryNodeObjectInfo']
            for n in reversed(nodes):
                tree.links.new(n.outputs['Geometry'],tree.nodes['X4D Sources'].inputs['Geometry'])
    s.status=next(iter(warnings),'')

def evaluate_clones(obj,pts,scene):
    s=obj.cw
    rotations=[]; scales=[]; result=[]; warnings=[]
    for i,point in enumerate(pts):
        p=point.copy(); rot=Vector((0,0,0)); size=Vector((1,1,1))
        for link in s.effectors:
            eff=link.target
            if not eff or eff.cw.kind!='EFFECTOR':
                warnings.append('缺失效果器 / Missing effector'); continue
            e=eff.cw; weight=1.0
            from . import advanced_fx
            if e.fields:
                weight=advanced_fx.layers(e.fields,obj.matrix_world@point,i,scene)
            weight*=e.strength
            rng=random.Random(e.seed+i*104729)
            factors=[rng.uniform(-1,1) for _ in range(9)] if e.effector=='RANDOM' else [i/max(len(pts)-1,1)]*9 if e.effector=='STEP' else advanced_fx.factors(eff,point,i,len(pts),scene)
            p+=Vector([e.move[j]*factors[j]*weight for j in range(3)])
            rot+=Vector([e.rotate[j]*factors[j+3]*weight for j in range(3)])
            size=Vector([size[j]*(1+e.scale[j]*factors[j+6]*weight) for j in range(3)])
            p,rot,size=advanced_fx.post(obj,eff,i,len(pts),p,rot,size,weight,scene)
        result.append(p); rotations.append(rot); scales.append(size)
    return result,rotations,scales,warnings

@persistent
def rebuild_all(scene,*args):
    global _busy
    if _busy:return
    _busy=True
    try:
        from . import clone_ownership
        clone_ownership.sync(scene)
        for obj in scene.objects:
            if obj.cw.kind=='CLONER':
                try: rebuild(obj,scene)
                except Exception as exc: obj.cw.status=str(exc)
    finally: _busy=False

@persistent
def deps_changed(scene,depsgraph):
    if _busy:return
    if any(isinstance(u.id,bpy.types.Object) and u.is_updated_transform for u in depsgraph.updates): rebuild_all(scene)
    else:
        from . import clone_ownership
        clone_ownership.sync(scene)

classes=[CWField,CWLink,CWSettings]









