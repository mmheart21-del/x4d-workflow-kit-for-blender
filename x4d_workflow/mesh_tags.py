"""Persistent mesh selection tags and native vertex weights."""
import bpy
import bmesh
from .catalog import label

PREFIX={'EDGE':'X4D Edge Set','FACE':'X4D Face Set'}

class CW_OT_mesh_tag(bpy.types.Operator):
    bl_idname='cw.mesh_tag'
    bl_label='Mesh Tag'
    bl_options={'REGISTER','UNDO'}
    domain:bpy.props.EnumProperty(items=[('EDGE','Edge',''),('FACE','Face',''),('POINT','Point',''),('VERTEX','Point Set','')])
    tag:bpy.props.StringProperty()
    operation:bpy.props.EnumProperty(items=[(x,x.title(),'') for x in ('ADD','RECALL','UPDATE','REMOVE')])
    weight:bpy.props.FloatProperty(name='Weight',default=1,min=0,max=1)

    @classmethod
    def poll(cls,context):
        return context.object is not None and context.object.type=='MESH' and context.mode in {'OBJECT','EDIT_MESH'}

    def execute(self,context):
        obj=context.object
        if self.domain in {'POINT','VERTEX'}:
            group=obj.vertex_groups.new(name='Selection' if self.domain=='VERTEX' else label('顶点贴图','Vertex Map'))
            if obj.mode=='EDIT':
                mesh=bmesh.from_edit_mesh(obj.data)
                deform=mesh.verts.layers.deform.verify()
                for vertex in mesh.verts:
                    if vertex.select:vertex[deform][group.index]=self.weight
                bmesh.update_edit_mesh(obj.data,loop_triangles=False,destructive=False)
            else:group.add(list(range(len(obj.data.vertices))),self.weight,'REPLACE')
            obj.vertex_groups.active_index=group.index
            return {'FINISHED'}
        if self.operation in {'RECALL','UPDATE'} and obj.mode!='EDIT':
            bpy.ops.object.mode_set(mode='EDIT')
        editing=obj.mode=='EDIT'
        mesh=bmesh.from_edit_mesh(obj.data) if editing else bmesh.new()
        if not editing:mesh.from_mesh(obj.data)
        try:
            elements=mesh.edges if self.domain=='EDGE' else mesh.faces
            layers=elements.layers.int
            layer=layers.new(PREFIX[self.domain]) if self.operation=='ADD' else layers.get(self.tag)
            if layer is None:return {'CANCELLED'}
            if self.operation in {'ADD','UPDATE'}:
                for element in elements:element[layer]=int(element.select)
            elif self.operation=='REMOVE':layers.remove(layer)
            else:
                for sequence in (mesh.faces,mesh.edges,mesh.verts):
                    for element in sequence:element.select_set(False)
                bpy.ops.mesh.select_mode(type=self.domain)
                for element in elements:
                    if element[layer] and not element.hide:element.select_set(True)
                mesh.select_flush_mode()
            if editing:bmesh.update_edit_mesh(obj.data,loop_triangles=False,destructive=False)
            else:mesh.to_mesh(obj.data)
        finally:
            if not editing:mesh.free()
        return {'FINISHED'}

def draw(layout,obj):
    row=layout.row(align=True)
    for domain,names in [('EDGE',('边选集','Edge Set')),('FACE',('面选集','Face Set')),('POINT',('顶点贴图','Vertex Map'))]:
        op=row.operator('cw.mesh_tag',text=label(*names));op.domain=domain
    mesh=bmesh.from_edit_mesh(obj.data) if obj.mode=='EDIT' else None
    for domain,prefix in PREFIX.items():
        if mesh:
            names=(mesh.edges if domain=='EDGE' else mesh.faces).layers.int.keys()
        else:names=[attr.name for attr in obj.data.attributes if attr.domain==domain and attr.data_type=='INT']
        for name in names:
            if not name.startswith(prefix):continue
            row=layout.row(align=True)
            title=label('边选集','Edge Set') if domain=='EDGE' else label('面选集','Face Set')
            suffix=name[len(prefix):]
            for operation,text,icon in [('RECALL',title+suffix,'RESTRICT_SELECT_OFF'),('UPDATE','','FILE_REFRESH'),('REMOVE','','X')]:
                op=row.operator('cw.mesh_tag',text=text,icon=icon);op.domain=domain;op.tag=name;op.operation=operation
    if obj.vertex_groups:
        layout.template_list('MESH_UL_vgroups','x4d_maps',obj,'vertex_groups',obj.vertex_groups,'active_index',rows=2)
        if obj.mode=='EDIT':
            row=layout.row(align=True)
            row.prop(bpy.context.scene.tool_settings,'vertex_group_weight',text=label('权重','Weight'))
            row.operator('object.vertex_group_assign',text=label('分配','Assign'))
            row.operator('object.vertex_group_select',text=label('选择','Select'))

classes=[CW_OT_mesh_tag]
