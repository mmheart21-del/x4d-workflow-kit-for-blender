"""Armed viewport tools for press-and-drag extrusion."""
import bpy
from .catalog import label

armed={}
choices={}
EXTRUDE={
    'NORMAL':('沿法线','Along Normals'),
    'REGION':('区域挤压','Extrude Region'),
    'INDIVIDUAL':('各面单独挤压','Extrude Individual Faces'),
    'MANIFOLD':('流形挤压','Extrude Manifold'),
}
INSET={'REGION':('保持群组','Inset Region'),'INDIVIDUAL':('各面内挤压','Inset Individual'),'OUTSET':('向外偏移','Outset')}

def run(context,tool):
    from .modeling import selected_mesh
    if not selected_mesh(context):return {'CANCELLED'}
    mode=choices.get((context.window.as_pointer(),tool),'NORMAL' if tool=='EXTRUDE' else 'REGION')
    point,edge,face=context.tool_settings.mesh_select_mode
    confirm={'release_confirm':True}
    if tool=='INSET':
        if not face:return {'CANCELLED'}
        return bpy.ops.mesh.inset('INVOKE_DEFAULT',release_confirm=True,use_individual=mode=='INDIVIDUAL',use_outset=mode=='OUTSET')
    if not face:
        if edge:return bpy.ops.mesh.extrude_edges_move('INVOKE_DEFAULT',TRANSFORM_OT_translate=confirm)
        return bpy.ops.mesh.extrude_vertices_move('INVOKE_DEFAULT',TRANSFORM_OT_translate=confirm)
    if mode=='NORMAL':
        return bpy.ops.mesh.extrude_region_shrink_fatten('INVOKE_DEFAULT',TRANSFORM_OT_shrink_fatten=confirm)
    if mode=='INDIVIDUAL':
        return bpy.ops.mesh.extrude_faces_move('INVOKE_DEFAULT',TRANSFORM_OT_shrink_fatten=confirm)
    if mode=='MANIFOLD':
        return bpy.ops.mesh.extrude_manifold('INVOKE_DEFAULT',TRANSFORM_OT_translate=confirm)
    return bpy.ops.mesh.extrude_region_move('INVOKE_DEFAULT',TRANSFORM_OT_translate=confirm)

class CW_OT_drag_choice(bpy.types.Operator):
    bl_idname='cw.drag_choice'
    bl_label='Choose Drag Tool'
    tool:bpy.props.StringProperty()
    mode:bpy.props.StringProperty()

    def execute(self,context):
        key=context.window.as_pointer()
        choices[key,self.tool]=self.mode
        armed[key]=self.tool
        context.area.tag_redraw()
        return {'FINISHED'}

class CW_MT_extrude_drag(bpy.types.Menu):
    bl_idname='CW_MT_extrude_drag'
    bl_label='Extrude'
    def draw(self,context):
        draw_choices(self.layout,'EXTRUDE',EXTRUDE)

class CW_MT_inset_drag(bpy.types.Menu):
    bl_idname='CW_MT_inset_drag'
    bl_label='Inset'
    def draw(self,context):
        draw_choices(self.layout,'INSET',INSET)

def draw_choices(layout,tool,modes):
    for mode,names in modes.items():
        op=layout.operator('cw.drag_choice',text=label(*names))
        op.tool=tool
        op.mode=mode

classes=[CW_OT_drag_choice,CW_MT_extrude_drag,CW_MT_inset_drag]
