"""Render controls with temporary viewport cameras and non-destructive settings."""
import bpy
from bpy.props import EnumProperty
from .catalog import label
_jobs={}
_borders={}

def prepare(scene,space,region,border=None):
    if scene.as_pointer() in _jobs:raise RuntimeError('已有渲染任务 / A render is already running')
    old=(scene.camera,scene.render.use_border,scene.render.use_crop_to_border,scene.render.border_min_x,scene.render.border_max_x,scene.render.border_min_y,scene.render.border_max_y)
    temp=None
    if not scene.camera or space.region_3d.view_perspective!='CAMERA':
        data=bpy.data.cameras.new('CW Temporary Render Camera');temp=bpy.data.objects.new('CW Temporary Render Camera',data);scene.collection.objects.link(temp)
        temp.matrix_world=space.region_3d.view_matrix.inverted();data.lens=space.lens
        data.type='ORTHO' if space.region_3d.view_perspective=='ORTHO' else 'PERSP'
        data.ortho_scale=space.region_3d.view_distance*2
        data.sensor_fit='HORIZONTAL' if region.width>=region.height else 'VERTICAL'
        scene.camera=temp
    scene.render.use_border=border is not None;scene.render.use_crop_to_border=False
    if border:
        scene.render.border_min_x,scene.render.border_min_y,scene.render.border_max_x,scene.render.border_max_y=border
    _jobs[scene.as_pointer()]=(scene,old,temp)

def finish(scene,*args):
    job=_jobs.pop(scene.as_pointer(),None)
    if not job:return
    _,old,temp=job
    scene.camera=old[0]
    for name,value in zip(('use_border','use_crop_to_border','border_min_x','border_max_x','border_min_y','border_max_y'),old[1:]):setattr(scene.render,name,value)
    if temp:
        data=temp.data;bpy.data.objects.remove(temp,do_unlink=True)
        if not data.users:bpy.data.cameras.remove(data)

def stop():
    for operator,context in list(_borders.values()):operator.cleanup(context)
    for scene,_,_ in list(_jobs.values()):finish(scene)
    for handlers in (bpy.app.handlers.render_complete,bpy.app.handlers.render_cancel):
        if finish in handlers:handlers.remove(finish)

def install():
    for handlers in (bpy.app.handlers.render_complete,bpy.app.handlers.render_cancel):
        if finish not in handlers:handlers.append(finish)

class CW_OT_render(bpy.types.Operator):
    bl_idname='cw.render';bl_label='Render'
    mode:EnumProperty(items=[('REGION','区域渲染',''),('RENDER','渲染',''),('SETTINGS','渲染设置','')])
    @classmethod
    def description(cls,context,properties):
        return label(*{'REGION':('区域渲染：拖出矩形后渲染当前视图，Esc 取消','Render Region: drag a rectangle in the viewport; Esc cancels'), 'RENDER':('渲染：渲染当前视图；摄像机视图使用场景摄像机','Render the current view; use the scene camera in camera view'), 'SETTINGS':('渲染设置：打开渲染器、采样与输出参数','Render Settings: open engine, sampling and output controls')}[properties.mode])
    def invoke(self,context,event):
        if self.mode!='REGION':return self.execute(context)
        area=context.area
        region=next((r for r in area.regions if r.type=='WINDOW'),None) if area and area.type=='VIEW_3D' else None
        if not region:return {'CANCELLED'}
        self.area=area;self.region=region;self.start=None;self.end=None
        context.window.cursor_modal_set('CROSSHAIR');area.header_text_set(label('拖出渲染区域，Esc 取消','Drag a render region; Esc cancels'))
        self.handle=bpy.types.SpaceView3D.draw_handler_add(self.draw_region,(),'WINDOW','POST_PIXEL')
        _borders[self.as_pointer()]=(self,context.copy())
        context.window_manager.modal_handler_add(self);return {'RUNNING_MODAL'}
    def draw_region(self):
        if not self.start or not self.end or bpy.context.area!=self.area:return
        import gpu
        from gpu_extras.batch import batch_for_shader
        x,y=self.start;u,v=self.end;shader=gpu.shader.from_builtin('UNIFORM_COLOR');shader.bind();shader.uniform_float('color',(.5,.7,1,1))
        batch_for_shader(shader,'LINE_STRIP',{'pos':[(x,y),(u,y),(u,v),(x,v),(x,y)]}).draw(shader)
    def cleanup(self,context):
        if _borders.pop(self.as_pointer(),None) is None:return
        handle=getattr(self,'handle',None);self.handle=None
        if handle is not None:
            try:bpy.types.SpaceView3D.draw_handler_remove(handle,'WINDOW')
            except (ValueError,ReferenceError):pass
        window=context.get('window') if isinstance(context,dict) else context.window
        try:
            window.cursor_modal_restore();self.area.header_text_set(None);self.area.tag_redraw()
        except (ReferenceError,RuntimeError):pass
    def cancel(self,context):self.cleanup(context)
    def modal(self,context,event):
        if self.as_pointer() not in _borders:return {'CANCELLED'}
        if event.type in {'ESC','RIGHTMOUSE'}:self.cleanup(context);return {'CANCELLED'}
        point=(max(0,min(self.region.width,event.mouse_x-self.region.x)),max(0,min(self.region.height,event.mouse_y-self.region.y)))
        if event.type=='LEFTMOUSE' and event.value=='PRESS':self.start=point
        if self.start:self.end=point;self.area.tag_redraw()
        if event.type=='LEFTMOUSE' and event.value=='RELEASE' and self.start:
            x,y=self.start;u,v=point;self.cleanup(context)
            if abs(u-x)<3 or abs(v-y)<3:return {'CANCELLED'}
            border=(min(x,u)/self.region.width,min(y,v)/self.region.height,max(x,u)/self.region.width,max(y,v)/self.region.height)
            return self.run_render(context,self.area,self.region,border)
        return {'RUNNING_MODAL'}
    def execute(self,context):
        if self.mode=='SETTINGS':
            from .material_dock import is_dock
            area=next((a for a in context.screen.areas if a.type=='PROPERTIES' and not is_dock(a)),None)
            if area:
                space=area.spaces.active
                if space.use_pin_id:
                    space.use_pin_id=False;space.pin_id=None;space.context='TOOL'
                space.context='RENDER';area.tag_redraw();return {'FINISHED'}
            self.report({'WARNING'},label('当前窗口没有属性编辑器','No Properties editor in this window'));return {'CANCELLED'}
        area=context.area if context.area and context.area.type=='VIEW_3D' else next((a for a in context.screen.areas if a.type=='VIEW_3D'),None)
        if not area:return {'CANCELLED'}
        return self.run_render(context,area,next(r for r in area.regions if r.type=='WINDOW'))
    def run_render(self,context,area,region,border=None):
        try:
            prepare(context.scene,area.spaces.active,region,border)
            with context.temp_override(area=area,region=region):result=bpy.ops.render.render('INVOKE_DEFAULT')
            if 'CANCELLED' in result:finish(context.scene)
            return {'CANCELLED'} if 'CANCELLED' in result else {'FINISHED'}
        except Exception as exc:
            finish(context.scene);self.report({'ERROR'},str(exc));return {'CANCELLED'}
class CW_PT_render_output(bpy.types.Panel):
    bl_label='Render Settings'
    bl_space_type='PROPERTIES';bl_region_type='WINDOW';bl_context='render'
    bl_order=-100
    @classmethod
    def poll(cls,context):return context.workspace is not None and context.workspace.name=='X4D'
    def draw(self,context):
        layout=self.layout;render=context.scene.render
        layout.prop(render,'engine',text=label('渲染器','Engine'))
        row=layout.row(align=True);row.prop(render,'resolution_x',text='X');row.prop(render,'resolution_y',text='Y')
        layout.prop(render,'resolution_percentage',text=label('分辨率比例','Resolution Scale'))
        layout.prop(render,'fps',text=label('帧率','Frame Rate'))
        layout.prop(render.image_settings,'file_format',text=label('文件格式','File Format'))
        layout.prop(render,'filepath',text=label('输出路径','Output Path'))

classes=[CW_OT_render,CW_PT_render_output]
