"""Viewport V menu using Blender's native eight-direction pie."""
import bpy
from .catalog import label
recent=[]

def remember(operator,value):
    item=(operator,value)
    if item in recent:recent.remove(item)
    recent.insert(0,item)
    del recent[8:]

def tool(layout,name,title):
    layout.operator('wm.tool_set_by_id',text=title).name=name

class CW_MT_v_view(bpy.types.Menu):
    bl_label='View'
    def draw(self,context):
        l=self.layout
        l.prop(context.space_data.shading,'type',expand=True)
        l.prop(context.space_data.overlay,'show_wireframes',text=label('线框叠加','Wire Overlay'))
        l.prop(context.space_data.overlay,'show_face_normals',text=label('多边形法线','Face Normals'))
        l.prop(context.space_data.shading,'show_backface_culling',text=label('背面忽略','Backface Culling'))
        l.prop(context.space_data.overlay,'show_overlays',text=label('叠加层','Overlays'))

class CW_MT_v_modes(bpy.types.Menu):
    bl_label='Modes'
    def draw(self,context):
        for key,names in [('OBJECT',('对象','Object')),('POINT',('点','Points')),('EDGE',('边','Edges')),('FACE',('面','Faces'))]:
            self.layout.operator('cw.tool',text=label(*names)).tool=key
        self.layout.operator('view3d.localview',text=label('切换视窗独显','Toggle Local View'))

class CW_MT_v_select(bpy.types.Menu):
    bl_label='Select'
    def draw(self,context):
        l=self.layout
        for name,names in [('builtin.select_circle',('笔刷选择','Circle Select')),('builtin.select_box',('框选','Box Select')),('builtin.select_lasso',('套索选择','Lasso Select'))]:tool(l,name,label(*names))
        l.separator()
        from .modeling import COMMANDS,available
        if context.mode=='EDIT_MESH':
            for cmd in ('LOOP_SELECT','RING_SELECT','BOUNDARY','FILL_SELECT','PATH_SELECT','SYMMETRIZE_SELECTION','INVERT','LINKED','GROW','SHRINK'):
                if available(context,cmd):l.operator('cw.model',text=label(*COMMANDS[cmd][:2])).command=cmd
            l.operator('mesh.hide',text=label('隐藏选择','Hide Selected')).unselected=False
            l.operator('mesh.hide',text=label('隐藏未选','Hide Unselected')).unselected=True
            l.operator('mesh.reveal',text=label('全部显示','Reveal All'))
        else:l.operator('cw.select',text=label('反选','Invert')).action='INVERT'

class CW_MT_v_snap(bpy.types.Menu):
    bl_label='Snapping'
    def draw(self,context):
        settings=context.scene.tool_settings
        self.layout.prop(settings,'use_snap',text=label('启用捕捉','Enable Snapping'))
        self.layout.prop(settings,'snap_elements',expand=True)

class CW_MT_v_recent(bpy.types.Menu):
    bl_label='Recent Tools'
    def draw(self,context):
        from .modeling import COMMANDS,available
        from .rail import TOOLS
        l=self.layout
        for op,key in recent:
            if op=='cw.model':
                if available(context,key):l.operator(op,text=label(*COMMANDS[key][:2])).command=key
            else:
                item=next((item for item in TOOLS if item[0]==key),None)
                if item:l.operator(op,text=label(*item[1:])).tool=key
        if not recent:l.label(text=label('暂无近期工具','No recent tools'))

class CW_MT_v_camera(bpy.types.Menu):
    bl_label='Camera'
    def draw(self,context):
        l=self.layout
        l.operator('view3d.view_camera',text=label('切换场景摄像机','Toggle Scene Camera'))
        l.operator('view3d.view_selected',text=label('框显选中项','Frame Selected'))
        l.operator('view3d.view_all',text=label('框显全部','Frame All'))
        l.menu('CW_MT_camera',text=label('视角','View Angles'))

class CW_OT_v_scene(bpy.types.Operator):
    bl_idname='cw.v_scene'
    bl_label='Switch Scene'
    name:bpy.props.StringProperty()
    def execute(self,context):
        scene=bpy.data.scenes.get(self.name)
        if scene is None:return {'CANCELLED'}
        if context.mode=='EDIT_MESH':bpy.ops.object.mode_set(mode='OBJECT')
        context.window.scene=scene
        return {'FINISHED'}

class CW_MT_v_scene(bpy.types.Menu):
    bl_label='Scene'
    def draw(self,context):
        for scene in bpy.data.scenes:
            self.layout.operator('cw.v_scene',text=scene.name,icon='CHECKMARK' if scene==context.scene else 'SCENE_DATA').name=scene.name

class CW_MT_v_extensions(bpy.types.Menu):
    bl_label='Extensions'
    def draw(self,context):
        self.layout.operator('cw.shortcut_help',text=label('快捷键速查','Shortcut Reference'))
        self.layout.operator('cw.materials',text=label('材质管理','Materials'))
        self.layout.menu('CW_MT_modeling',text=label('建模命令','Modeling Commands'))

class CW_MT_v_pie(bpy.types.Menu):
    bl_label='X4D Quick Menu'
    def draw(self,context):
        pie=self.layout.menu_pie()
        for key,names in [('view',('查看','View')),('snap',('捕捉','Snapping')),('scene',('场景','Scene')),('modes',('模式','Modes')),('recent',('近期工具','Recent Tools')),('select',('选择','Select')),('camera',('摄像机','Camera')),('extensions',('扩展','Extensions'))]:
            pie.menu('CW_MT_v_'+key,text=label(*names))

classes=[CW_MT_v_view,CW_MT_v_modes,CW_MT_v_select,CW_MT_v_snap,CW_MT_v_recent,CW_MT_v_camera,CW_OT_v_scene,CW_MT_v_scene,CW_MT_v_extensions,CW_MT_v_pie]
