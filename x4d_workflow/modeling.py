"""Workspace-scoped modeling commands and an explicit sequential shortcut registry."""
import time
import bpy
import bmesh
from bpy.props import StringProperty, FloatVectorProperty, BoolVectorProperty, BoolProperty
from .catalog import label

# Keys are successive presses, not held chords. Keep menus, dispatch and help together.
COMMANDS={
 'POLY_BUILD':('多边形画笔','Poly Build','M E','Blender Poly Build tool'),
 'ADD_POINT':('创建点','Create Point','M A','Add a vertex at the 3D cursor'),
 'FILL_HOLE':('封闭多边形孔洞','Close Polygon Hole','M D','Fill selected boundary loops'),
 'BEVEL':('倒角','Bevel','M S','Bevel selected edges or vertices'),
 'EXTRUDE':('挤压','Extrude','M T / D','Extrude and move the selection'),
 'BRIDGE':('桥接','Bridge','M B / B','Bridge selected edge loops'),
 'CREASE':('细分曲面权重','Subdivision Weight','M R','Edit Blender edge or vertex crease'),
 'WELD':('焊接','Weld','M Q','Merge selected vertices at their center'),
 'STITCH':('缝合','Stitch','M P','Merge selected vertices by distance'),
 'COLLAPSE':('坍塌','Collapse','U C','Collapse selected edges'),
 'DISSOLVE':('融解','Dissolve','U Z','Dissolve selected components'),
 'DELETE':('消除','Delete','M N','Delete the selected component type'),
 'OPTIMIZE':('优化','Optimize','U O','Merge selected coincident vertices and remove degenerate edges'),
 'DISCONNECT':('断开连接','Disconnect','U D','Split selection from neighboring geometry'),
 'SPLIT':('分裂','Split to Object','U P','Separate selected geometry into another object'),
 'SYMMETRIZE':('对称化','Symmetrize','M H','Blender symmetrize; default -X to +X'),
 'KNIFE':('线性切割','Line Cut','K K / M K','Blender Knife tool; Enter confirms, Esc cancels'),
 'BISECT':('平面切割','Plane Cut','K J / M J','Blender Bisect tool'),
 'LOOP_CUT':('循环/路径切割','Loop Cut','K L / M L','Blender Loop Cut and Slide'),
 'SUBDIVIDE':('切割边 / 细分','Subdivide','M F / U S','Subdivide selected geometry'),
 'CONNECT':('连接点/边','Connect Points / Edges','M M','Connect selected vertices across faces'),
 'SMOOTH':('熨烫','Smooth','M G','Smooth selected vertex positions'),
 'SMOOTH_BRUSH':('平滑笔刷','Smooth Brush','M C','Blender mesh Smooth tool'),
 'MAGNET':('磁铁','Proportional Editing','M I','Toggle proportional editing for mesh transforms'),
 'SET_POINT':('设置点值','Set Point Values','M U','Set enabled local coordinate components of selected vertices'),
 'SLIDE':('滑动','Slide','M O','Blender vertex slide or edge slide'),
 'ROTATE_EDGE':('旋转边','Rotate Edge','M V','Rotate selected edges counterclockwise'),
 'INSET':('内挤压 / 嵌入','Inset','M W','Inset selected faces'),
 'NORMAL_MOVE':('沿法线移动','Move Along Normals','M Z','Blender Shrink/Fatten'),
 'ALIGN_NORMALS':('对齐法线','Align Normals','U A','Recalculate selected normals outside'),
 'FLIP_NORMALS':('翻转法线','Reverse Normals','U R','Reverse selected face normals'),
 'UNTRIANGULATE':('反三角化','Untriangulate','U U','Join selected triangles into quads'),
 'INVERT':('反选','Invert Selection','U I','Invert objects or mesh components'),
 'LINKED':('选择连接','Select Connected','U W','Select linked mesh geometry'),
 'GROW':('扩展选区','Grow Selection','U Y','Grow mesh selection'),
 'SHRINK':('收缩选区','Shrink Selection','U K','Shrink mesh selection'),
 'LOOP_SELECT':('循环选择','Loop Selection','U L','Expand selected edges to loops'),
 'RING_SELECT':('环状选择','Ring Selection','U B','Expand selected edges to rings'),
 'PATH_SELECT':('路径选择','Shortest Path','U M','Select the shortest path between selected components'),
 'FILL_SELECT':('填充选择','Fill Selection','U F','Convert selected boundary loops to a face region'),
 'SYMMETRIZE_SELECTION':('将所选项对称化','Symmetrize Selection','U V','Symmetrize selected components'),
 'BOUNDARY':('轮廓选择','Boundary Selection','U Q','Convert a face region to its boundary edges'),
}
SEQUENCES={}
for command,data in COMMANDS.items():
 for sequence in data[2].split(' / '):
  keys=tuple(sequence.split())
  if len(keys)>1:
   assert keys not in SEQUENCES,keys
   SEQUENCES[keys]=command

_active={}

def viewport(context):
 return bool(context.workspace and context.workspace.name=='X4D' and context.area and context.area.type=='VIEW_3D' and context.region and context.region.type=='WINDOW' and context.mode in {'OBJECT','EDIT_MESH'})

def selected_mesh(context):
 if context.mode!='EDIT_MESH':return False
 return any(any(v.select for v in bmesh.from_edit_mesh(obj.data).verts) for obj in context.objects_in_mode_unique_data)

def dispatch(context,command,interactive=True):
 """Execute only explicit mappings; native errors remain visible to the caller."""
 if command=='INVERT':
  return (bpy.ops.mesh.select_all if context.mode=='EDIT_MESH' else bpy.ops.object.select_all)(action='INVERT')
 if context.mode!='EDIT_MESH':raise ValueError(label('请先进入点、边或面模式','Enter point, edge or polygon mode first'))
 if command=='ADD_POINT':
  obj=context.edit_object;bm=bmesh.from_edit_mesh(obj.data)
  for v in bm.verts:v.select_set(False)
  vertex=bm.verts.new(obj.matrix_world.inverted() @ context.scene.cursor.location);vertex.select_set(True)
  bm.select_history.clear();bm.select_history.add(vertex);bmesh.update_edit_mesh(obj.data);return {'FINISHED'}
 if command=='MAGNET':
  settings=context.scene.tool_settings;settings.use_proportional_edit=not settings.use_proportional_edit;return {'FINISHED'}
 tools={'POLY_BUILD':'builtin.poly_build','KNIFE':'builtin.knife','BISECT':'builtin.bisect','LOOP_CUT':'builtin.loop_cut','SMOOTH_BRUSH':'builtin.smooth'}
 if command in tools:
  if bpy.app.background:raise ValueError('This tool requires an interactive viewport')
  return bpy.ops.wm.tool_set_by_id(name=tools[command])
 if not selected_mesh(context):raise ValueError(label('请先选择网格组件','Select mesh components first'))
 if command=='SET_POINT':return bpy.ops.cw.point_values('INVOKE_DEFAULT' if interactive else 'EXEC_DEFAULT')
 if command=='OPTIMIZE':
  bpy.ops.mesh.remove_doubles(threshold=.0001)
  return bpy.ops.mesh.dissolve_degenerate(threshold=.0001)
 if command in {'LOOP_SELECT','RING_SELECT'}:
  # 5.2 split the old loop_multi_select operator into two operators.
  name='select_edge_loop_multi' if command=='LOOP_SELECT' else 'select_edge_ring_multi'
  if name in dir(bpy.ops.mesh):return getattr(bpy.ops.mesh,name)()
  return bpy.ops.mesh.loop_multi_select(ring=command=='RING_SELECT')
 mode=context.tool_settings.mesh_select_mode
 route={
 'FILL_HOLE':('mesh.fill_holes',{'sides':0}),
 'BEVEL':('mesh.bevel',{'affect':'VERTICES' if mode[0] else 'EDGES'}),
 'EXTRUDE':('mesh.extrude_vertices_move' if mode[0] else 'mesh.extrude_edges_move' if mode[1] else 'mesh.extrude_region_move',{}),
 'BRIDGE':('mesh.bridge_edge_loops',{}),'CREASE':('transform.vert_crease' if mode[0] else 'transform.edge_crease',{}),
 'WELD':('mesh.merge',{'type':'CENTER'}),'STITCH':('mesh.remove_doubles',{'threshold':.0001}),
 'COLLAPSE':('mesh.edge_collapse',{}),'DISSOLVE':('mesh.dissolve_mode',{}),
 'DELETE':('mesh.delete',{'type':'VERT' if mode[0] else 'EDGE' if mode[1] else 'FACE'}),
 'DISCONNECT':('mesh.split',{}),'SPLIT':('mesh.separate',{'type':'SELECTED'}),
 'SYMMETRIZE':('mesh.symmetrize',{'direction':'NEGATIVE_X'}),
 'SUBDIVIDE':('mesh.subdivide',{'number_cuts':1}),'CONNECT':('mesh.vert_connect_path',{}),
 'SMOOTH':('mesh.vertices_smooth',{}),'SLIDE':('transform.vert_slide' if mode[0] else 'transform.edge_slide',{}),
 'ROTATE_EDGE':('mesh.edge_rotate',{'use_ccw':True}),'INSET':('mesh.inset',{}),
 'NORMAL_MOVE':('transform.shrink_fatten',{}),'ALIGN_NORMALS':('mesh.normals_make_consistent',{'inside':False}),
 'FLIP_NORMALS':('mesh.flip_normals',{}),'UNTRIANGULATE':('mesh.tris_convert_to_quads',{}),
 'LINKED':('mesh.select_linked',{}),'GROW':('mesh.select_more',{}),'SHRINK':('mesh.select_less',{}),
 'PATH_SELECT':('mesh.shortest_path_select',{}),'FILL_SELECT':('mesh.loop_to_region',{}),
 'SYMMETRIZE_SELECTION':('mesh.symmetrize',{'direction':'NEGATIVE_X'}),
 'BOUNDARY':('mesh.region_to_loop',{}),
 }
 target,args=route[command];module,name=target.split('.');op=getattr(getattr(bpy.ops,module),name)
 if not op.poll():raise ValueError(label('当前选择不适用于此命令','This command is unavailable for the current selection'))
 return op('INVOKE_DEFAULT' if interactive else 'EXEC_DEFAULT',**args)

class CW_OT_model(bpy.types.Operator):
 bl_idname='cw.model';bl_label='Modeling Command';bl_options={'REGISTER','UNDO'}
 command:StringProperty()
 @classmethod
 def poll(cls,context):return viewport(context)
 @classmethod
 def description(cls,context,properties):
  data=COMMANDS.get(properties.command)
  return (label(data[0],data[1])+' ('+data[2]+'): '+data[3]) if data else 'X4D modeling command'
 def invoke(self,context,event):
  from .quick_menu import remember
  if self.command in COMMANDS:remember('cw.model',self.command)
  if self.command in {'LOOP_SELECT','RING_SELECT'}:
   return bpy.ops.cw.loop_preview('INVOKE_DEFAULT',ring=self.command=='RING_SELECT')
  return self.run(context,True)
 def execute(self,context):return self.run(context,False)
 def run(self,context,interactive):
  if self.command not in COMMANDS:return {'CANCELLED'}
  try:return dispatch(context,self.command,interactive)
  except (RuntimeError,ValueError,TypeError,KeyError,AttributeError) as exc:
   self.report({'WARNING'},str(exc));return {'CANCELLED'}

class CW_OT_select(bpy.types.Operator):
 bl_idname='cw.select';bl_label='Selection';bl_options={'UNDO'}
 action:StringProperty(default='SELECT')
 @classmethod
 def poll(cls,context):return viewport(context)
 def execute(self,context):
  return (bpy.ops.mesh.select_all if context.mode=='EDIT_MESH' else bpy.ops.object.select_all)(action=self.action)

class CW_OT_point_values(bpy.types.Operator):
 bl_idname='cw.point_values';bl_label='Set Point Values';bl_options={'REGISTER','UNDO'}
 values:FloatVectorProperty(name='Local coordinates',subtype='TRANSLATION')
 axes:BoolVectorProperty(name='Apply axes',default=(True,True,True),subtype='XYZ')
 @classmethod
 def poll(cls,context):return context.mode=='EDIT_MESH'
 def invoke(self,context,event):return context.window_manager.invoke_props_dialog(self)
 def execute(self,context):
  for obj in context.objects_in_mode_unique_data:
   bm=bmesh.from_edit_mesh(obj.data)
   for v in bm.verts:
    if v.select:
     for axis,enabled in enumerate(self.axes):
      if enabled:v.co[axis]=self.values[axis]
   bmesh.update_edit_mesh(obj.data)
  return {'FINISHED'}

# The available commands follow the active component selection mode.
POINT_EDGE_ONLY={'SLIDE','PATH_SELECT'}
EDGE_ONLY={'ROTATE_EDGE','COLLAPSE'}
FACE_ONLY={'INSET','BOUNDARY'}

def available(context,command,keys=()):
 if context.mode!='EDIT_MESH':return command=='INVERT'
 point,edge,face=context.tool_settings.mesh_select_mode
 if keys==('M','F'):return edge
 return ((command not in POINT_EDGE_ONLY or point or edge)
         and (command!='FILL_SELECT' or edge or face)
         and (command not in EDGE_ONLY or edge)
         and (command not in FACE_ONLY or face))

def draw_sequence(context):
 import blf
 from .rail import rect
 operator=_active.get(context.window.as_pointer())
 if not operator or context.area!=operator.area or context.region!=operator.region:return
 entries=[(keys[-1],label(*COMMANDS[cmd][:2])) for keys,cmd in SEQUENCES.items()
          if keys[:-1]==operator.path and available(context,cmd,keys)]
 scale=context.preferences.system.ui_scale
 font=max(12,int(13*scale))
 blf.size(0,font)
 lines=[label('键','Key')+'  '+operator.path[0]]+[key+'  …  '+title for key,title in sorted(entries)]
 line_height=font+5
 width=max(blf.dimensions(0,line)[0] for line in lines)+20
 height=len(lines)*line_height+12
 x=max(2,min(operator.anchor[0]+12,context.region.width-width-2))
 y=max(2,min(operator.anchor[1]-height,context.region.height-height-2))
 rect(x,y,width,height,(.055,.057,.06,1))
 for index,line in enumerate(lines):
  blf.color(0,.72,.83,1,1) if index==0 else blf.color(0,.93,.93,.94,1)
  blf.position(0,x+9,y+height-(index+1)*line_height,0)
  blf.draw(0,line)

class CW_OT_sequence(bpy.types.Operator):
 bl_idname='cw.sequence';bl_label='Sequential Command'
 prefix:StringProperty(default='M')
 @classmethod
 def poll(cls,context):return viewport(context)
 def invoke(self,context,event):
  if self.prefix not in {'M','U','K'}:return {'CANCELLED'}
  key=context.window.as_pointer()
  if key in _active:return {'CANCELLED'}
  self.key=key;self.workspace=context.workspace;self.area=context.area;self.region=context.region;self.window=context.window
  self.path=(self.prefix,);self.deadline=time.monotonic()+4
  self.timer=context.window_manager.event_timer_add(.2,window=context.window)
  self.anchor=(event.mouse_x-context.region.x,event.mouse_y-context.region.y)
  _active[key]=self
  self.area.tag_redraw()
  context.window_manager.modal_handler_add(self)
  return {'RUNNING_MODAL'}
 def cleanup(self,context):
  if _active.get(self.key)!=self:return
  _active.pop(self.key,None)
  try:self.area.tag_redraw();context.window_manager.event_timer_remove(self.timer)
  except (ReferenceError,RuntimeError):pass
 def cancel(self,context):self.cleanup(context)
 def modal(self,context,event):
  if _active.get(self.key)!=self:return {'CANCELLED'}
  if event.type=='TIMER':
   if time.monotonic()>self.deadline:self.cleanup(context);return {'CANCELLED'}
   return {'PASS_THROUGH'}
  if not (self.region.x<=event.mouse_x<self.region.x+self.region.width and self.region.y<=event.mouse_y<self.region.y+self.region.height) or event.type=='LEFTMOUSE':
   self.cleanup(context);return {'CANCELLED','PASS_THROUGH'}
  if context.workspace!=self.workspace or context.area!=self.area or not viewport(context):self.cleanup(context);return {'CANCELLED'}
  if event.type in {'ESC','RIGHTMOUSE','WINDOW_DEACTIVATE'}:self.cleanup(context);return {'CANCELLED'}
  if event.value!='PRESS' or event.type in {'LEFT_SHIFT','RIGHT_SHIFT','LEFT_CTRL','RIGHT_CTRL','LEFT_ALT','RIGHT_ALT','MOUSEMOVE','INBETWEEN_MOUSEMOVE'}:return {'RUNNING_MODAL'}
  if getattr(event,'is_repeat',False):return {'RUNNING_MODAL'}
  command=SEQUENCES.get(self.path+(event.type,))
  self.cleanup(context)
  if not command or not available(context,command,self.path+(event.type,)) or event.ctrl or event.alt or event.oskey:return {'CANCELLED'}
  bpy.ops.cw.model('INVOKE_DEFAULT',command=command)
  return {'FINISHED'}

class CW_MT_modeling(bpy.types.Menu):
 bl_idname='CW_MT_modeling';bl_label='Modeling'
 def draw(self,context):
  for command,(cn,en,keys,_) in COMMANDS.items():
   if available(context,command):self.layout.operator('cw.model',text=label(cn,en)+'  ['+keys+']').command=command

class CW_OT_shortcut_help(bpy.types.Operator):
 bl_idname='cw.shortcut_help';bl_label='X4D Shortcuts'
 def invoke(self,context,event):return context.window_manager.invoke_popup(self,width=680)
 def draw(self,context):
  self.layout.label(text=label('连续按键：依次按下并松开，Esc 取消，4 秒超时','Sequences: press and release each key; Esc cancels; 4-second timeout'))
  self.layout.label(text='E / R / T: Move / Rotate / Scale   |   Ctrl+A / Ctrl+Shift+A: Select / Deselect All')
  self.layout.label(text='H / S: Frame All / Selected   |   F1–F5: Views   |   Ctrl+B: Render Settings')
  grid=self.layout.grid_flow(columns=2,even_columns=True)
  for _,(cn,en,keys,_) in COMMANDS.items():
   row=grid.row();row.label(text=keys);row.label(text=label(cn,en))
 def execute(self,context):return {'FINISHED'}

def stop():
 for op in list(_active.values()):op.cleanup(bpy.context)

classes=[CW_OT_model,CW_OT_select,CW_OT_point_values,CW_OT_sequence,CW_MT_modeling,CW_OT_shortcut_help]
