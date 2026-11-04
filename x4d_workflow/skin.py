"""Workspace-scoped viewport header. Restore the exact previous draw function on disable."""
import bpy
from .catalog import label,CATEGORIES
from . import icons
_original=None
_original_menus=None

class CW_MT_camera(bpy.types.Menu):
    bl_idname='CW_MT_camera';bl_label='摄像机'
    def draw(self,context):
        for view,cn,en in [('PERSP','透视视图','Perspective'),('TOP','顶视图','Top'),('RIGHT','右视图','Right'),('FRONT','正视图','Front'),('QUAD','四视图 / 单视图','Four Views / Single View')]:self.layout.operator('cw.view',text=label(cn,en)).view=view
class CW_MT_display(bpy.types.Menu):
    bl_idname='CW_MT_display';bl_label='显示'
    def draw(self,context):
        self.layout.prop(context.space_data.shading,'type',expand=True)
        self.layout.separator();self.layout.prop(context.space_data.overlay,'show_overlays',text=label('辅助显示','Overlays'))
class CW_MT_filter(bpy.types.Menu):
    bl_idname='CW_MT_filter';bl_label='过滤'
    def draw(self,context):
        for key,cn,en in [('show_floor','网格','Grid'),('show_axis_x','X 轴','X Axis'),('show_axis_y','Y 轴','Y Axis'),('show_cursor','3D 光标','3D Cursor'),('show_extras','灯光 / 摄像机等辅助对象','Extras'),('show_relationship_lines','层级连线','Relationships')]:self.layout.prop(context.space_data.overlay,key,text=label(cn,en))
def header(self,context):
    if context.workspace.name!='X4D':
        if _original:_original(self,context)
        return
    l=self.layout;row=l.row(align=True)
    row.menu('VIEW3D_MT_object' if context.mode=='OBJECT' else 'VIEW3D_MT_edit_mesh' if context.mode=='EDIT_MESH' else 'VIEW3D_MT_view',text=label('编辑','Edit'))
    if context.mode=='EDIT_MESH':row.menu('CW_MT_modeling',text=label('建模','Modeling'))
    row.menu('CW_MT_camera',text=label('摄像机','Camera'))
    row.menu('CW_MT_display',text=label('显示','Display'))
    row.menu('CW_MT_filter',text=label('过滤','Filter'))
    row.menu('CW_MT_create',text=label('创建','Create'))
    row.separator()
    tool=context.workspace.tools.from_space_view3d_mode(context.mode,create=False)
    transform={'builtin.rotate':'transform.rotate','builtin.scale':'transform.resize'}.get(tool.idname if tool else '', 'transform.translate')
    axes=row.row(align=True)
    axes.operator_context='INVOKE_REGION_WIN'
    for axis,index in [('X',0),('Y',2),('Z',1)]:
        action=axes.operator(transform,text=axis)
        action.constraint_axis=tuple(i==index for i in range(3))
    row.prop(context.scene.transform_orientation_slots[0],'type',text='')
    row.separator_spacer()
    for key in ['OBJECT','POINT','EDGE','FACE','MOVE','ROTATE','SCALE','AXIS']:row.operator('cw.tool',text='',icon_value=icons.icon_id('tool_'+key.lower())).tool=key
    settings=context.scene.tool_settings
    row.prop(settings,'transform_pivot_point',text='')
    row.prop(settings,'use_snap',text='',icon='SNAP_ON' if settings.use_snap else 'SNAP_OFF')
    row.popover(panel='VIEW3D_PT_snapping',text='',icon='DOWNARROW_HLT')
    row.prop(context.space_data.overlay,'show_overlays',text='',icon='OVERLAY')
    row.prop(context.space_data.shading,'show_xray',text='',icon='XRAY')
    row.separator_spacer()
    for mode in ['REGION','RENDER','SETTINGS']:
        row.operator('cw.render',text='',icon_value=icons.icon_id('render_'+mode.lower())).mode=mode
    row.operator('cw.materials',text='',icon='MATERIAL')

def install():
    install_panels()
    global _original,_original_menus
    if _original_menus is None:
        _original_menus=bpy.types.TOPBAR_MT_editor_menus.draw
        bpy.types.TOPBAR_MT_editor_menus.draw=top_menus
    if _original is None:
        _original=bpy.types.VIEW3D_HT_header.draw
        bpy.types.VIEW3D_HT_header.draw=header

def restore():
    restore_panels()
    global _original,_original_menus
    if _original_menus is not None:
        if bpy.types.TOPBAR_MT_editor_menus.draw is top_menus:bpy.types.TOPBAR_MT_editor_menus.draw=_original_menus
        _original_menus=None
    if _original is not None:
        if bpy.types.VIEW3D_HT_header.draw is header:bpy.types.VIEW3D_HT_header.draw=_original
        _original=None
classes=[CW_MT_camera,CW_MT_display,CW_MT_filter]

class CW_MT_modes(bpy.types.Menu):
    bl_idname='CW_MT_modes';bl_label='模式'
    def draw(self,context):
        for key,cn,en in [('OBJECT','对象','Object'),('POINT','点','Points'),('EDGE','边','Edges'),('FACE','面','Polygons')]:self.layout.operator('cw.tool',text=label(cn,en),icon_value=icons.icon_id('tool_'+key.lower())).tool=key
class CW_MT_tools(bpy.types.Menu):
    bl_idname='CW_MT_tools';bl_label='工具'
    def draw(self,context):
        for key,cn,en in [('SELECT','选择','Select'),('MOVE','移动','Move'),('ROTATE','旋转','Rotate'),('SCALE','缩放','Scale'),('AXIS','轴心','Axis')]:self.layout.operator('cw.tool',text=label(cn,en),icon_value=icons.icon_id('tool_'+key.lower())).tool=key
        self.layout.separator()
        self.layout.operator('cw.shortcut_help',text=label('快捷键速查','Shortcut Reference'),icon='HELP')
        self.layout.operator('cw.new_scene',text=label('新建空场景','New Empty Scene'),icon='FILE_NEW')
        self.layout.operator('cw.restore',text=label('恢复 Blender','Restore Blender'),icon='LOOP_BACK')
class CW_MT_mograph(bpy.types.Menu):
    bl_idname='CW_MT_mograph';bl_label='MoGraph'
    def draw(self,context):
        for key,cn,en in [('MOGRAPH','对象','Objects'),('EFFECTOR','效果器','Effectors'),('FIELD','域','Fields')]:self.layout.operator('cw.palette',text=label(cn,en),icon_value=icons.icon_id(icons.key(key))).category=key
class CW_MT_animation(bpy.types.Menu):
    bl_idname='CW_MT_animation';bl_label='动画'
    def draw(self,context):
        self.layout.operator('screen.animation_play',text=label('播放 / 停止','Play / Stop'))
        self.layout.prop(context.scene,'frame_current',text=label('当前帧','Frame'))
        self.layout.prop(context.scene,'frame_start',text=label('开始','Start'))
        self.layout.prop(context.scene,'frame_end',text=label('结束','End'))

def top_menus(self,context):
    if context.workspace is None or context.workspace.name!='X4D':
        if _original_menus:_original_menus(self,context)
        return
    row=self.layout.row(align=True)
    for menu,cn,en in [('TOPBAR_MT_file','文件','File'),('TOPBAR_MT_edit','编辑','Edit'),('CW_MT_create','创建','Create'),('CW_MT_modes','模式','Modes'),('CW_MT_tools','工具','Tools'),('CW_MT_mograph','MoGraph','MoGraph'),('CW_MT_animation','动画','Animate'),('TOPBAR_MT_render','渲染','Render'),('TOPBAR_MT_window','窗口','Window'),('TOPBAR_MT_help','帮助','Help')]:row.menu(menu,text=label(cn,en))

classes.extend([CW_MT_modes,CW_MT_tools,CW_MT_mograph,CW_MT_animation])



# Suppress the unrelated native constraint launcher only in the dedicated manager.
_panel_draws=[]
def _workspace_panel(original):
    def draw(self,context):
        if context.workspace is None or context.workspace.name!='X4D':original(self,context)
    return draw

def install_panels():
    if _panel_draws:return
    cls=getattr(bpy.types,'OBJECT_PT_constraints',None)
    if cls:
        original=cls.draw;wrapper=_workspace_panel(original);_panel_draws.append((cls,original,wrapper));cls.draw=wrapper

def restore_panels():
    for cls,original,wrapper in _panel_draws:
        if cls.draw is wrapper:cls.draw=original
    _panel_draws.clear()

