import bpy
from bpy.props import StringProperty, IntProperty
from . import engine

class CW_OT_create(bpy.types.Operator):
    bl_idname='cw.create'; bl_label='创建 / Create'; bl_options={'REGISTER','UNDO'}
    kind: StringProperty(default='CLONER')
    def execute(self,context):
        source=context.active_object
        if self.kind=='CLONER':
            mesh=bpy.data.meshes.new('Cloner Points'); obj=bpy.data.objects.new('克隆 / Cloner',mesh)
        else:
            obj=bpy.data.objects.new('域 / Field' if self.kind=='FIELD' else '效果器 / Effector',None)
            obj.empty_display_type='SPHERE' if self.kind=='FIELD' else 'ARROWS'
        context.collection.objects.link(obj)
        engine._busy=True
        obj.cw.kind=self.kind
        if self.kind=='CLONER':obj.cw.source=source
        engine._busy=False
        if self.kind=='FIELD':
            obj.empty_display_size=obj.cw.radius
            obj.color=(.75,.4,.8,1)
        for o in context.selected_objects:o.select_set(False)
        obj.select_set(True); context.view_layer.objects.active=obj
        engine.rebuild_all(context.scene)
        return {'FINISHED'}

class CW_OT_list(bpy.types.Operator):
    bl_idname='cw.list_edit'; bl_label='列表 / List'; bl_options={'UNDO'}
    action: StringProperty(default='ADD')
    collection: StringProperty(default='effectors')
    index: IntProperty(default=0)
    def execute(self,context):
        items=getattr(context.object.cw,self.collection)
        if self.action=='ADD': items.add()
        elif 0<=self.index<len(items):
            if self.action=='REMOVE':items.remove(self.index)
            else:items.move(self.index,max(0,min(len(items)-1,self.index+(-1 if self.action=='UP' else 1))))
        engine.rebuild_all(context.scene);return {'FINISHED'}

class CW_OT_action(bpy.types.Operator):
    bl_idname='cw.action'; bl_label='操作 / Action'; bl_options={'REGISTER','UNDO'}
    action: StringProperty()
    @classmethod
    def poll(cls,context):return context.scene is not None
    def execute(self,context):
        obj=context.object; a=self.action
        if a!='GROUP' and obj is None:self.report({'WARNING'},'请先选择对象 / Select an object first');return {'CANCELLED'}
        if a in {'EDITABLE','STATE'} and obj.type not in {'MESH','CURVE','FONT','SURFACE'}:self.report({'WARNING'},'此对象不能转换为网格 / This object cannot be converted to a mesh');return {'CANCELLED'}
        if a=='GROUP':
            selected=list(context.selected_objects); group=bpy.data.objects.new('空对象 / Null',None); context.collection.objects.link(group)
            for child in selected:
                mat=child.matrix_world.copy();child.parent=group;child.matrix_world=mat
            context.view_layer.objects.active=group;group.select_set(True)
        elif a in {'EDITABLE','STATE'}:
            if a=='STATE':
                copy=obj.copy();copy.data=obj.data.copy() if obj.data else None;copy.cw.kind='';context.collection.objects.link(copy)
                for child in context.selected_objects:child.select_set(False)
                copy.select_set(True);context.view_layer.objects.active=copy;obj=copy
            if obj.type in {'MESH','CURVE','FONT','SURFACE'}:
                if obj.cw.kind=='GENERATOR':
                    from . import generators
                    generators.sync(context.scene);obj.cw.kind=''
                engine.rebuild_all(context.scene)
                # Realize instances before conversion.
                for m in obj.modifiers:
                    if m.type=='NODES' and m.node_group:
                        m.node_group=m.node_group.copy();t=m.node_group;out=next(n for n in t.nodes if n.type=='GROUP_OUTPUT')
                        if out.inputs['Geometry'].links:
                            sock=out.inputs['Geometry'].links[0].from_socket
                            real=t.nodes.new('GeometryNodeRealizeInstances');t.links.new(sock,real.inputs['Geometry']);t.links.new(real.outputs[0],out.inputs['Geometry'])
                bpy.ops.object.convert(target='MESH');context.object.cw.kind='';context.object.cw_primitive.kind=''
        elif a in {'BEND','TWIST','TAPER'}:
            m=obj.modifiers.new(a,'SIMPLE_DEFORM');m.deform_method=a;m.angle=.5;m.deform_axis='Z'
        elif a=='SUBSURF':obj.modifiers.new('细分 / Subdivision','SUBSURF')
        elif a=='BOOLEAN':
            others=[o for o in context.selected_objects if o!=obj and o.type=='MESH']
            if not others:self.report({'ERROR'},'请选择两个网格 / Select two meshes');return {'CANCELLED'}
            m=obj.modifiers.new('布尔 / Boolean','BOOLEAN');m.object=others[0];m.operation='DIFFERENCE'
        elif a=='EXTRUDE':
            if obj.type!='CURVE':self.report({'ERROR'},'需要曲线 / Curve required');return {'CANCELLED'}
            obj.data.dimensions='2D';obj.data.extrude=.5
        elif a=='LATHE':obj.modifiers.new('旋转 / Lathe','SCREW')
        elif a=='SWEEP':
            curves=[o for o in context.selected_objects if o!=obj and o.type=='CURVE']
            if obj.type!='CURVE' or not curves:self.report({'ERROR'},'选择路径和轮廓曲线 / Select path and profile');return {'CANCELLED'}
            obj.data.bevel_mode='OBJECT';obj.data.bevel_object=curves[0]
        elif a=='SMOOTH':
            if obj.type=='MESH':
                for p in obj.data.polygons:p.use_smooth=True
        elif a=='MATERIAL':
            if not obj.data or not hasattr(obj.data,'materials'):return {'CANCELLED'}
            mat=bpy.data.materials.new('材质 / Material');mat.use_nodes=True;obj.data.materials.append(mat)
        elif a=='SELECTION':
            if obj.type!='MESH':return {'CANCELLED'}
            if obj.mode=='EDIT':obj.update_from_editmode()
            group=obj.vertex_groups.new(name='选择集 / Selection')
            ids=[v.index for v in obj.data.vertices if v.select]
            if obj.mode=='EDIT':bpy.ops.object.mode_set(mode='OBJECT')
            if ids:group.add(ids,1,'REPLACE')
        elif a=='TARGET':
            target=next((o for o in context.selected_objects if o!=obj),None)
            if not target:self.report({'ERROR'},'请选择目标 / Select target');return {'CANCELLED'}
            c=obj.constraints.new('TRACK_TO');c.target=target;c.track_axis='TRACK_NEGATIVE_Z';c.up_axis='UP_Y'
        return {'FINISHED'}

class CW_OT_sequence(bpy.types.Operator):
    bl_idname='cw.sequence';bl_label='连续命令 / Sequential command'
    prefix: StringProperty(default='M')
    def invoke(self,context,event):
        if context.area.type!='VIEW_3D':return {'CANCELLED'}
        context.workspace.status_text_set(self.prefix+' → … (Esc)');context.window_manager.modal_handler_add(self);return {'RUNNING_MODAL'}
    def modal(self,context,event):
        if event.value!='PRESS':return {'RUNNING_MODAL'}
        context.workspace.status_text_set(None)
        if event.type=='ESC':return {'CANCELLED'}
        if self.prefix=='M' and event.type=='T' and context.mode=='EDIT_MESH':bpy.ops.mesh.extrude_region_move('INVOKE_DEFAULT')
        elif self.prefix=='M' and event.type=='S' and context.mode=='EDIT_MESH':bpy.ops.mesh.bevel('INVOKE_DEFAULT')
        elif self.prefix=='U' and event.type=='A':bpy.ops.mesh.select_all(action='SELECT') if context.mode=='EDIT_MESH' else bpy.ops.object.select_all(action='SELECT')
        elif self.prefix=='U' and event.type=='I':bpy.ops.mesh.select_all(action='INVERT') if context.mode=='EDIT_MESH' else bpy.ops.object.select_all(action='INVERT')
        else:return {'CANCELLED'}
        return {'FINISHED'}

classes=[CW_OT_create,CW_OT_list,CW_OT_action,CW_OT_sequence]

class CW_OT_command(bpy.types.Operator):
    bl_idname='cw.command';bl_label='X4D Command'
    command: StringProperty()
    argument: StringProperty()
    @classmethod
    def poll(cls,context):
        return context.area is not None and context.area.type=='VIEW_3D' and context.region is not None and context.region.type=='WINDOW' and context.workspace.name=='X4D'
    def invoke(self,context,event):
        target=self.command
        args={}
        if target=='wm.tool_set_by_id':args['name']=self.argument
        elif target=='cw.action':args['action']=self.argument
        elif target=='cw.sequence':args['prefix']=self.argument
        elif target=='view3d.view_axis':args['type']=self.argument
        elif target=='cw.view':args['view']=self.argument
        elif target=='view3d.view_all':args['center']=False
        module,name=target.split('.')
        try:return getattr(getattr(bpy.ops,module),name)('INVOKE_DEFAULT',**args)
        except RuntimeError as exc:self.report({'WARNING'},str(exc));return {'CANCELLED'}

classes.append(CW_OT_command)


class CW_OT_view(bpy.types.Operator):
    bl_idname='cw.view';bl_label='X4D View'
    view:StringProperty(default='PERSP')
    @classmethod
    def poll(cls,context):return context.area is not None and context.area.type=='VIEW_3D'
    def execute(self,context):
        space=context.space_data
        if self.view=='QUAD':
            if bpy.app.background:self.report({'WARNING'},'Quad View requires an interactive window');return {'CANCELLED'}
            bpy.ops.screen.region_quadview();return {'FINISHED'}
        if space.region_quadviews:bpy.ops.screen.region_quadview()
        if self.view=='PERSP':
            import math
            from mathutils import Euler
            space.region_3d.view_perspective='PERSP'
            space.region_3d.view_rotation=Euler((math.radians(68),0,math.radians(35)),'XYZ').to_quaternion()
        else:bpy.ops.view3d.view_axis(type=self.view)
        return {'FINISHED'}
classes.append(CW_OT_view)


class CW_OT_new_scene(bpy.types.Operator):
    bl_idname='cw.new_scene';bl_label='新建 X4D 场景 / New X4D Scene'
    bl_description='Create an empty scene with 0–90 frames, 30 fps and centimeters; preserve the current scene'
    bl_options={'REGISTER','UNDO'}
    def execute(self,context):
        scene=bpy.data.scenes.new('未标题 / Untitled')
        scene.frame_start=0;scene.frame_end=90;scene.frame_set(0)
        scene.render.fps=30;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1.0;scene.unit_settings.length_unit='CENTIMETERS'
        context.window.scene=scene
        return {'FINISHED'}
classes.append(CW_OT_new_scene)




