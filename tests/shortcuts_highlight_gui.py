import bpy,sys,os,traceback,bmesh
sys.path.insert(0,os.getcwd())
import x4d_workflow as kit
kit.register();kit.material_previews.request=lambda:None
state={}
def fail():traceback.print_exc();kit.unregister();bpy.ops.wm.quit_blender()
def send(key,ctrl=False,shift=False):
 r=state['region'];x=r.x+r.width//2;y=r.y+r.height//2;w=state['window']
 w.event_simulate(type=key,value='PRESS',x=x,y=y,ctrl=ctrl,shift=shift);w.event_simulate(type=key,value='RELEASE',x=x,y=y,ctrl=ctrl,shift=shift)
def begin():
 try:
  state['window']=bpy.context.window
  bpy.ops.cw.primitive(kind='CUBE');state['obj']=bpy.context.object
  bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_mode(type='FACE');bpy.ops.mesh.select_all(action='SELECT')
  state['area']=next(a for a in bpy.context.screen.areas if a.type=='VIEW_3D');state['region']=next(r for r in state['area'].regions if r.type=='WINDOW')
  send('U');send('S');bpy.app.timers.register(check,first_interval=1)
 except Exception:fail()
def check():
 try:
  bm=bmesh.from_edit_mesh(state['obj'].data)
  if len(bm.verts)==8 and state.get('retry',0)<20:state['retry']=state.get('retry',0)+1;return .5
  assert len(bm.verts)==26,('U S was not dispatched',len(bm.verts))
  assert not kit.modeling._active
  send('K');send('K');bpy.app.timers.register(knife,first_interval=1)
 except Exception:fail()
def knife():
 try:
  tool=bpy.context.workspace.tools.from_space_view3d_mode('EDIT_MESH',create=False)
  assert tool.idname=='builtin.knife',tool.idname
  send('M');send('ESC');bpy.app.timers.register(cancelled,first_interval=.7)
 except Exception:fail()
def cancelled():
 try:
  assert not kit.modeling._active
  send('A',ctrl=True,shift=True);bpy.app.timers.register(deselected,first_interval=.7)
 except Exception:fail()
def deselected():
 try:
  assert not any(v.select for v in bmesh.from_edit_mesh(state['obj'].data).verts)
  send('A',ctrl=True);bpy.app.timers.register(selected,first_interval=.7)
 except Exception:fail()
def selected():
 try:
  assert all(v.select for v in bmesh.from_edit_mesh(state['obj'].data).verts)
  send('E');bpy.app.timers.register(moved,first_interval=.7)
 except Exception:fail()
def moved():
 try:
  assert bpy.context.workspace.tools.from_space_view3d_mode('EDIT_MESH',create=False).idname=='builtin.move'
  assert len(bmesh.from_edit_mesh(state['obj'].data).verts)==26,'E unexpectedly extruded'
  print('X4D_SEQUENCE_US_KK_ESCAPE_SELECTION_ERT_OK')
  bpy.ops.object.mode_set(mode='OBJECT')
  a=bpy.data.materials.new('A');b=bpy.data.materials.new('B');c=bpy.data.materials.new('C')
  state['obj'].data.materials.append(a);state['obj'].data.materials.append(b)
  kit.material_editors.select(bpy.context,c);state['selected_material']=c
  assert kit.material_dock.highlighted(bpy.context.window)=={'A','B'}
  bpy.ops.cw.materials();bpy.app.timers.register(highlight,first_interval=1)
 except Exception:fail()
def highlight():
 try:
  assert bpy.context.window_manager.cw_material==state['selected_material']
  state['obj'].select_set(False);assert kit.material_dock.highlighted(bpy.context.window)==set()
  state['obj'].select_set(True)
  bpy.ops.screen.screenshot(filepath=os.path.join(os.getcwd(),'artifacts','material-object-highlight.png'))
  print('X4D_MATERIAL_HIGHLIGHT_INDEPENDENT_OK')
  kit.unregister();bpy.ops.wm.quit_blender()
 except Exception:fail()
bpy.app.timers.register(begin,first_interval=6)


