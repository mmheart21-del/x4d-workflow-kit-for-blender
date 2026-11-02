"""Create extended tools with real editable parameters and geometry handlers."""
import bpy,os
from bpy.props import StringProperty
from . import extras,extra_properties,procedural_scripts
CURVES={'FORMULA_SPLINE','PROFILE','LOFT_CURVE','MOSPLINE','TRACER','SPLINE_MASK'}
CONTROLLERS={'COLLISION','FORMULA_DEFORM','MELT'}
NAMES={'CAPSULE':'胶囊','OIL_TANK':'油罐','TUBE':'管道','FIGURE':'人形对象','LANDSCAPE':'地形','RELIEF':'浮雕','BACKGROUND':'背景','FORMULA_SPLINE':'公式样条','PROFILE':'轮廓','LOFT':'放样','SPLINE_MASK':'样条布尔','LOD':'LOD','PYTHON_GENERATOR':'Python 生成器','VOLUME_BUILDER':'体积生成','VOLUME_MESHER':'体积网格','SDF_SMOOTH':'SDF 平滑','FOG_SMOOTH':'雾平滑','VECTOR_SMOOTH':'矢量平滑','MATRIX':'矩阵','SCATTER':'散布','FRACTURE':'分裂','VORONOI':'Voronoi 破碎','TRACER':'追踪对象','MOSPLINE':'运动样条','MOEXTRUDE':'运动挤压','COLLISION':'碰撞','FORMULA_DEFORM':'公式变形','MELT':'融解','IES':'IES 灯'}

class CW_OT_extra(bpy.types.Operator):
    bl_idname='cw.extra';bl_label='创建 / Create';bl_options={'REGISTER','UNDO'}
    kind:StringProperty()
    def execute(self,context):
        kind=self.kind
        if kind not in NAMES:self.report({'ERROR'},'Unknown tool '+kind);return {'CANCELLED'}
        if context.object and context.object.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
        selected=list(context.selected_objects)
        if context.object in selected:selected.remove(context.object);selected.insert(0,context.object)
        curve_inputs={'LOFT','SPLINE_MASK','MOSPLINE'}
        mesh_inputs={'VOLUME_BUILDER','VOLUME_MESHER','SDF_SMOOTH','FOG_SMOOTH','VECTOR_SMOOTH','FRACTURE','VORONOI','MOEXTRUDE','LOD','COLLISION','FORMULA_DEFORM','MELT'}
        if kind in curve_inputs:selected=[o for o in selected if o.type=='CURVE']
        elif kind in mesh_inputs:selected=[o for o in selected if o.type=='MESH']
        source=selected[0] if selected else None
        extra_properties._busy=True
        try:
            if kind in {'MATRIX','SCATTER'}:
                bpy.ops.cw.create(kind='CLONER');obj=context.object;obj.cw_extra.kind=kind
                if kind=='MATRIX':obj.cw.source=None
                else:
                    obj.cw.mode='SURFACE';obj.cw.count=(100,1,1);obj.cw.source=source
                    obj.cw.surface=next((o for o in selected[1:] if o.type=='MESH'),None)
            else:
                if kind in CURVES:data=bpy.data.curves.new(NAMES[kind],'CURVE');data.dimensions='3D'
                elif kind in CONTROLLERS:data=None
                elif kind=='IES':data=bpy.data.lights.new(NAMES[kind],'POINT')
                else:data=bpy.data.meshes.new(NAMES[kind])
                obj=bpy.data.objects.new(NAMES[kind],data);(context.collection or context.scene.collection).objects.link(obj)
                obj.cw.kind='EXTRA';obj.cw_extra.kind=kind
                if source:obj.cw_extra.source=source
                if kind in CONTROLLERS:obj.empty_display_type='CUBE';obj.empty_display_size=2
                if source and kind in {'LOFT','SPLINE_MASK','FRACTURE','VORONOI','MOEXTRUDE','VOLUME_BUILDER','VOLUME_MESHER','SDF_SMOOTH','FOG_SMOOTH','LOD'}:
                    obj.matrix_world=source.matrix_world.copy()
                    for child in selected:
                        obj.cw.inputs.add().target=child
                        matrix=child.matrix_world.copy();child.parent=obj;child.matrix_world=matrix
                        from .generators import hide_source
                        hide_source(child,obj)
                elif kind=='TRACER':
                    if len(selected)>1:
                        for child in selected:obj.cw.inputs.add().target=child
                if kind=='PYTHON_GENERATOR':procedural_scripts.compile_program(obj)
                if kind=='BACKGROUND' and context.scene.camera:
                    obj.parent=context.scene.camera;obj.location=(0,0,-5);obj.rotation_euler=(0,0,0)
                if kind=='SPLINE_MASK':obj.cw_extra.resolution=64
                if kind=='MELT':obj.cw_extra.amount=.5
                if kind=='FORMULA_DEFORM':obj.cw_extra.formula='sin(x*2+t)'
            for other in context.selected_objects:other.select_set(False)
            obj.select_set(True);context.view_layer.objects.active=obj
        finally:extra_properties._busy=False
        context.view_layer.update();extras.update(context.scene)
        from .engine import rebuild_all
        rebuild_all(context.scene)
        return {'FINISHED'}
classes=[CW_OT_extra]

class CW_OT_new_texture(bpy.types.Operator):
    bl_idname='cw.new_texture';bl_label='新建噪波纹理 / New Noise Texture';bl_options={'UNDO'}
    def execute(self,context):
        if not context.object:return {'CANCELLED'}
        texture=bpy.data.textures.new('CW Noise',type='CLOUDS');context.object.cw_extra.texture=texture
        return {'FINISHED'}
classes.append(CW_OT_new_texture)

from bpy_extras.io_utils import ImportHelper
class CW_OT_load_asset(bpy.types.Operator,ImportHelper):
    bl_idname='cw.load_asset';bl_label='载入资源 / Load Asset';bl_options={'UNDO'}
    filename_ext=''
    filter_glob:StringProperty(default='*.png;*.jpg;*.jpeg;*.tif;*.exr;*.ies;*.wav',options={'HIDDEN'})
    object_name:StringProperty()
    field:StringProperty(default='image')
    def invoke(self,context,event):
        if context.object:self.object_name=context.object.name
        context.window_manager.fileselect_add(self);return {'RUNNING_MODAL'}
    def execute(self,context):
        obj=bpy.data.objects.get(self.object_name)
        if obj is None:self.report({'ERROR'},'Target object no longer exists');return {'CANCELLED'}
        try:
            if self.field=='image':obj.cw_extra.image=bpy.data.images.load(self.filepath,check_existing=True)
            elif self.field in {'ies','audio'}:setattr(obj.cw_extra,self.field,self.filepath)
            else:return {'CANCELLED'}
            return {'FINISHED'}
        except Exception as exc:self.report({'ERROR'},str(exc));return {'CANCELLED'}
classes.append(CW_OT_load_asset)



