"""Editable lists for object tags and procedural sources."""
import bpy
from .catalog import label

VOLUMES={'VOLUME_BUILDER','VOLUME_MESHER','SDF_SMOOTH','FOG_SMOOTH'}
TAGS={
    'MATERIAL':('材质','Material','MATERIAL'),
    'SMOOTH':('平滑着色','Smooth Shading','MOD_SMOOTH'),
    'VERTEX':('点选集','Point Set','VERTEXSEL'),
    'EDGE':('线选集','Edge Set','EDGESEL'),
    'FACE':('面选集','Face Set','FACESEL'),
    'POINT':('顶点贴图','Vertex Map','GROUP_VERTEX'),
    'TARGET':('目标约束','Target Constraint','CONSTRAINT'),
}

class CWObjectTag(bpy.types.PropertyGroup):
    name:bpy.props.StringProperty()
    kind:bpy.props.StringProperty()
    reference:bpy.props.StringProperty()
    material:bpy.props.PointerProperty(type=bpy.types.Material)

def source_list(obj):
    if obj.cw.kind=='CLONER':return 'sources'
    if obj.cw.kind=='EXTRA' and obj.cw_extra.kind in VOLUMES:return 'inputs'
    return None

def prepare_sources(obj):
    name=source_list(obj)
    if not name or obj.cw.sources_list_ready:return
    settings=obj.cw
    rows=getattr(settings,name)
    old=settings.source if name=='sources' else obj.cw_extra.source
    existing={row.target for row in rows}
    if old and old not in existing:
        rows.add().target=old
        rows.move(len(rows)-1,0)
        existing.add(old)
    if name=='inputs':
        for child in obj.children:
            if child.type=='MESH' and child not in existing:rows.add().target=child
    settings.sources_list_ready=True

def sync_volume_sources(obj,scene):
    if source_list(obj)!='inputs' or not obj.cw.sources_list_ready:return
    from .generators import hide_source,sync
    desired={row.target for row in obj.cw.inputs if row.target and row.target.type=='MESH'
             and row.target!=obj and obj not in row.target.children_recursive}
    for child in list(obj.children):
        if child.get('cw_generator_owner')==obj and child not in desired:
            world=child.matrix_world.copy()
            child.parent=child.get('x4d_volume_previous_parent')
            if 'x4d_volume_previous_parent' in child:del child['x4d_volume_previous_parent']
            child.matrix_world=world
    for child in desired:
        owner=child.get('cw_generator_owner') or child.get('x4d_clone_owner')
        if child.library or (owner and owner!=obj):continue
        if child.parent!=obj:
            world=child.matrix_world.copy()
            if child.parent:child['x4d_volume_previous_parent']=child.parent
            child.parent=obj
            child.matrix_world=world
            hide_source(child,obj)
    sync(scene)

def sync_tags(obj):
    from .mesh_tags import PREFIX
    entries=obj.cw.tags
    existing={(item.kind,item.reference) for item in entries}
    def add(kind,reference='',material=None):
        if (kind,reference) in existing:return
        item=entries.add()
        item.name=label(*TAGS[kind][:2])
        item.kind=kind;item.reference=reference;item.material=material
        existing.add((kind,reference))
    for slot in obj.material_slots:
        if slot.material:
            item=next((entry for entry in entries if entry.kind=='MATERIAL' and entry.material==slot.material),None)
            if item:
                if item.reference!=slot.material.name:item.reference=slot.material.name
                existing.add(('MATERIAL',item.reference))
            else:add('MATERIAL',slot.material.name,slot.material)
    for constraint in obj.constraints:
        if constraint.type=='TRACK_TO':add('TARGET',constraint.name)
    if obj.type!='MESH':return
    if obj.mode=='EDIT':
        import bmesh
        mesh=bmesh.from_edit_mesh(obj.data)
        layers=[('EDGE',mesh.edges.layers.int.keys()),('FACE',mesh.faces.layers.int.keys())]
    else:layers=[(domain,[a.name for a in obj.data.attributes if a.domain==domain and a.data_type=='INT']) for domain in PREFIX]
    for domain,names in layers:
        for name in names:
            if name.startswith(PREFIX[domain]):add(domain,name)
    for group in obj.vertex_groups:
        if group.name.startswith(('Selection','Vertex Map','顶点贴图')):add('VERTEX' if group.name.startswith('Selection') else 'POINT',group.name)

def smooth_tag(obj,enable):
    import bmesh
    editing=obj.mode=='EDIT'
    mesh=bmesh.from_edit_mesh(obj.data) if editing else bmesh.new()
    if not editing:mesh.from_mesh(obj.data)
    try:
        layers=mesh.faces.layers.int
        layer=layers.get('X4D Previous Smooth')
        if enable and layer is None:
            layer=layers.new('X4D Previous Smooth')
            for face in mesh.faces:
                face[layer]=2 if face.smooth else 1
                face.smooth=True
        elif not enable and layer is not None:
            for face in mesh.faces:
                if face[layer]:face.smooth=face[layer]==2
            layers.remove(layer)
        if editing:bmesh.update_edit_mesh(obj.data,loop_triangles=False,destructive=False)
        else:mesh.to_mesh(obj.data)
    finally:
        if not editing:mesh.free()

class CW_UL_sources(bpy.types.UIList):
    def draw_item(self,context,layout,data,item,icon,active_data,active_propname,index=0):
        row=layout.row(align=True)
        row.prop(item,'enabled',text='')
        row.prop(item,'target',text='',icon='OBJECT_DATA')

class CW_UL_tags(bpy.types.UIList):
    def draw_item(self,context,layout,data,item,icon,active_data,active_propname,index=0):
        layout.prop(item,'name',text='',emboss=False,icon=TAGS[item.kind][2])

class CW_OT_source_list(bpy.types.Operator):
    bl_idname='cw.source_list'
    bl_label='Manage Sources'
    bl_options={'UNDO'}
    action:bpy.props.StringProperty()
    @classmethod
    def poll(cls,context):return context.object is not None and source_list(context.object) is not None
    def execute(self,context):
        from . import engine,extras
        obj=context.object
        prepare_sources(obj)
        name=source_list(obj);s=obj.cw;rows=getattr(s,name)
        index=s.source_index
        if self.action=='SELECTED':
            existing={row.target for row in rows}
            for source in context.selected_objects:
                if source==obj or source in existing or obj in source.children_recursive:continue
                if source.cw.kind in {'CLONER','FIELD','EFFECTOR'} or (name=='inputs' and source.type!='MESH'):continue
                rows.add().target=source
            index=len(rows)-1
        elif self.action=='ADD':
            rows.add();index=len(rows)-1
        elif 0<=index<len(rows):
            if self.action=='REMOVE':
                rows.remove(index)
            else:
                new=max(0,min(len(rows)-1,index+(-1 if self.action=='UP' else 1)))
                rows.move(index,new);index=new
        s.source_index=max(0,min(index,len(rows)-1))
        sync_volume_sources(obj,context.scene)
        extras._CACHE.clear();extras.update(context.scene);engine.rebuild_all(context.scene)
        return {'FINISHED'}

class CW_OT_tag_add(bpy.types.Operator):
    bl_idname='cw.tag_add'
    bl_label='Add Tag'
    bl_options={'UNDO'}
    kind:bpy.props.StringProperty()
    def execute(self,context):
        obj=context.object
        if not obj:return {'CANCELLED'}
        sync_tags(obj)
        before=len(obj.cw.tags)
        if self.kind in {'EDGE','FACE','POINT','VERTEX'}:
            result=bpy.ops.cw.mesh_tag(domain=self.kind)
        elif self.kind=='TARGET':
            constraint=obj.constraints.new('TRACK_TO')
            constraint.track_axis='TRACK_NEGATIVE_Z';constraint.up_axis='UP_Y'
            constraint.target=next((o for o in context.selected_objects if o!=obj),None)
            result={'FINISHED'}
        elif self.kind=='SMOOTH':
            if obj.type!='MESH' or any(tag.kind=='SMOOTH' for tag in obj.cw.tags):return {'CANCELLED'}
            smooth_tag(obj,True)
            result={'FINISHED'}
        else:
            result=bpy.ops.cw.action(action='SELECTION' if self.kind=='VERTEX' else self.kind)
        if 'FINISHED' not in result:return {'CANCELLED'}
        sync_tags(obj)
        if self.kind=='SMOOTH':
            tag=obj.cw.tags.add();tag.kind='SMOOTH';tag.name=label(*TAGS['SMOOTH'][:2])
        if len(obj.cw.tags)>before:obj.cw.tag_index=len(obj.cw.tags)-1
        return {'FINISHED'}

class CW_MT_tag_add(bpy.types.Menu):
    bl_label='Add Tag'
    def draw(self,context):
        for kind,(cn,en,icon) in TAGS.items():
            if context.object.type=='MESH' or kind in {'MATERIAL','TARGET'}:
                self.layout.operator('cw.tag_add',text=label(cn,en),icon=icon).kind=kind

class CW_OT_tag_list(bpy.types.Operator):
    bl_idname='cw.tag_list'
    bl_label='Manage Tags'
    bl_options={'UNDO'}
    action:bpy.props.StringProperty()
    def execute(self,context):
        obj=context.object
        if not obj:return {'CANCELLED'}
        rows=obj.cw.tags;index=obj.cw.tag_index
        if not 0<=index<len(rows):return {'CANCELLED'}
        item=rows[index];kind=item.kind
        if self.action=='REMOVE':
            if kind in {'EDGE','FACE'}:bpy.ops.cw.mesh_tag(domain=kind,operation='REMOVE',tag=item.reference)
            elif kind in {'VERTEX','POINT'}:
                group=obj.vertex_groups.get(item.reference)
                if group:obj.vertex_groups.remove(group)
            elif kind=='TARGET':
                constraint=obj.constraints.get(item.reference)
                if constraint:obj.constraints.remove(constraint)
            elif kind=='MATERIAL':
                for i,slot in enumerate(obj.material_slots):
                    if slot.material==item.material:obj.data.materials.pop(index=i);break
            elif kind=='SMOOTH':smooth_tag(obj,False)
            rows.remove(index)
        else:
            new=max(0,min(len(rows)-1,index+(-1 if self.action=='UP' else 1)))
            rows.move(index,new);index=new
        obj.cw.tag_index=max(0,min(index,len(rows)-1))
        return {'FINISHED'}

def buttons(layout,operator):
    for action,icon in [('REMOVE','REMOVE'),('UP','TRIA_UP'),('DOWN','TRIA_DOWN')]:
        layout.operator(operator,text='',icon=icon).action=action

def draw_sources(layout,obj):
    name=source_list(obj);s=obj.cw
    row=layout.row(align=True)
    row.label(text=label('源对象','Sources'))
    row.operator('cw.source_list',text='',icon='ADD').action='ADD'
    row.operator('cw.source_list',text=label('添加选中','Add Selected')).action='SELECTED'
    row=layout.row()
    row.template_list('CW_UL_sources',name,s,name,s,'source_index',rows=3)
    buttons(row.column(align=True),'cw.source_list')

def draw_tags(layout,obj):
    s=obj.cw
    layout.menu('CW_MT_tag_add',text=label('添加标签','Add Tag'),icon='ADD')
    row=layout.row()
    row.template_list('CW_UL_tags','tags',s,'tags',s,'tag_index',rows=4)
    buttons(row.column(align=True),'cw.tag_list')
    if not 0<=s.tag_index<len(s.tags):return
    item=s.tags[s.tag_index];kind=item.kind
    if kind in {'EDGE','FACE'}:
        row=layout.row(align=True)
        for action,names in [('RECALL',('恢复选择','Recall Selection')),('UPDATE',('更新选集','Update Set'))]:
            op=row.operator('cw.mesh_tag',text=label(*names));op.domain=kind;op.operation=action;op.tag=item.reference
    elif kind in {'VERTEX','POINT'}:
        group=obj.vertex_groups.get(item.reference)
        if group:
            op=layout.operator('object.vertex_group_set_active',text=group.name)
            op.group=group.name
        if obj.mode=='EDIT' and obj.vertex_groups.active and obj.vertex_groups.active.name==item.reference:
            row=layout.row(align=True)
            row.prop(bpy.context.scene.tool_settings,'vertex_group_weight',text=label('权重','Weight'))
            row.operator('object.vertex_group_assign',text=label('分配','Assign'))
            row.operator('object.vertex_group_select',text=label('选择','Select'))
    elif kind=='TARGET':
        constraint=obj.constraints.get(item.reference)
        if constraint:
            layout.prop(constraint,'target');layout.prop(constraint,'influence')
    elif kind=='MATERIAL' and item.material:
        for slot in obj.material_slots:
            if slot.material==item.material:layout.prop(slot,'material');break

classes=[CWObjectTag,CW_UL_sources,CW_UL_tags,CW_OT_source_list,CW_OT_tag_add,CW_MT_tag_add,CW_OT_tag_list]
