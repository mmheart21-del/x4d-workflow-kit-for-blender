import bpy
from bpy.props import StringProperty
from .catalog import label
class CW_OT_materials(bpy.types.Operator):
    bl_idname='cw.materials';bl_label='Materials / 材质管理'
    bl_description='Browse material previews and inspect the objects using each material'
    def invoke(self,context,event):return self.execute(context)
    def execute(self,context):
        from .material_dock import toggle
        return toggle(context)
class CW_OT_material_new(bpy.types.Operator):
    bl_idname='cw.material_new';bl_label='New Material';bl_options={'REGISTER','UNDO'}
    def execute(self,context):
        mat=bpy.data.materials.new('Material');mat.use_nodes=True
        from . import material_previews
        material_previews.request()
        context.window_manager.cw_material=mat
        result=bpy.ops.cw.material_assign(material=mat.name)
        from . import material_editors
        material_editors.select(context,mat)
        return result
class CW_OT_material_assign(bpy.types.Operator):
    bl_idname='cw.material_assign';bl_label='Assign Material';bl_options={'REGISTER','UNDO'}
    material:StringProperty()
    def execute(self,context):
        mat=bpy.data.materials.get(self.material)
        if not mat:return {'CANCELLED'}
        for obj in [o for o in context.view_layer.objects if o.select_get()]:
            if hasattr(obj.data,'materials'):
                if mat.name not in obj.data.materials:obj.data.materials.append(mat)
                index=list(obj.data.materials).index(mat);obj.active_material_index=index
                if obj.type=='MESH':
                    for face in obj.data.polygons:face.material_index=index
        return {'FINISHED'}
class CW_OT_material_user(bpy.types.Operator):
    bl_idname='cw.material_user';bl_label='Select Material User';bl_options={'UNDO'}
    object:StringProperty()
    def execute(self,context):
        obj=context.scene.objects.get(self.object)
        if not obj:return {'CANCELLED'}
        for item in context.selected_objects:item.select_set(False)
        obj.hide_set(False);obj.select_set(True);context.view_layer.objects.active=obj
        return {'FINISHED'}
class CW_PT_object_materials(bpy.types.Panel):
    bl_label='Object Materials / 对象材质';bl_space_type='OUTLINER';bl_region_type='HEADER'
    def draw(self,context):
        for obj in context.scene.objects:
            if not obj.material_slots:continue
            row=self.layout.row();row.label(text=obj.name,icon='OBJECT_DATA')
            for slot in obj.material_slots:
                if slot.material:
                    slot.material.preview_ensure()
                    row.template_icon(icon_value=slot.material.preview.icon_id,scale=2)
                    row.label(text=slot.material.name)

def outliner_header(self,context):
    if context.workspace and context.workspace.name=='X4D':self.layout.popover(panel='CW_PT_object_materials',text='',icon='MATERIAL')

class CW_OT_material_delete(bpy.types.Operator):
    bl_idname='cw.material_delete';bl_label='Delete Material / 删除材质';bl_options={'REGISTER'}
    material:StringProperty()
    def execute(self,context):
        mat=bpy.data.materials.get(self.material) if self.material else context.window_manager.cw_material
        if mat is None:return {'CANCELLED'}
        undo=not bpy.app.background and context.preferences.edit.use_global_undo
        if undo:bpy.ops.ed.undo_push(message='Before Delete Material')
        from . import material_editors
        names=[m.name for m in bpy.data.materials if not getattr(m,'is_grease_pencil',False)]
        index=names.index(mat.name);names.remove(mat.name)
        material_editors.before_remove(context,mat)
        bpy.data.materials.remove(mat,do_unlink=True)
        if names:material_editors.select(context,bpy.data.materials.get(names[min(index,len(names)-1)]))
        if undo:bpy.ops.ed.undo_push(message='Delete Material')
        for area in context.screen.areas:area.tag_redraw()
        return {'FINISHED'}

classes=[CW_OT_materials,CW_OT_material_new,CW_OT_material_assign,CW_OT_material_user,CW_PT_object_materials,CW_OT_material_delete]
