import bpy,sys,os,traceback,time
sys.path.insert(0,os.getcwd())
import x4d_workflow as kit
kit.register();state={}
def fail():traceback.print_exc();kit.unregister();bpy.ops.wm.quit_blender()
def send(key):
 r=state['region'];w=state['window'];x=r.x+r.width//2;y=r.y+r.height//2
 w.event_simulate(type=key,value='PRESS',x=x,y=y,unicode=key.lower() if len(key)==1 else '');w.event_simulate(type=key,value='RELEASE',x=x,y=y)
def begin():
 try:
  state['window']=bpy.context.window;state['area']=next(a for a in bpy.context.screen.areas if a.type=='VIEW_3D');state['region']=next(r for r in state['area'].regions if r.type=='WINDOW')
  send('M');state['start']=time.monotonic();bpy.app.timers.register(timeout,first_interval=.5)
 except Exception:fail()
def timeout():
 try:
  if time.monotonic()-state['start']<5:return .5
  assert not kit.modeling._active
  # Editing text in another editor must never dispatch viewport sequences.
  area=state['area'];area.type='TEXT_EDITOR';text=bpy.data.texts.new('Shortcut input test');area.spaces.active.text=text
  bpy.app.timers.register(type_text,first_interval=.5)
 except Exception:fail()
def type_text():
 try:
  area=state['area'];r=next(r for r in area.regions if r.type=='WINDOW');state['region']=r;w=state['window'];x=r.x+100;y=r.y+r.height-40
  w.event_simulate(type='MOUSEMOVE',value='NOTHING',x=x,y=y)
  w.event_simulate(type='LEFTMOUSE',value='PRESS',x=x,y=y);w.event_simulate(type='LEFTMOUSE',value='RELEASE',x=x,y=y)
  send('M');send('F');bpy.app.timers.register(typed,first_interval=1)
 except Exception:fail()
def typed():
 try:
  text=state['area'].spaces.active.text
  if text.as_string()!='mf' and state.get('tries',0)<10:state['tries']=state.get('tries',0)+1;return .5
  assert text.as_string()=='mf',text.as_string()
  assert not kit.modeling._active
  assert not kit.modeling.viewport(bpy.context)
  print('X4D_SHORTCUT_TIMEOUT_TEXT_INPUT_OK')
  kit.unregister();bpy.ops.wm.quit_blender()
 except Exception:fail()
bpy.app.timers.register(begin,first_interval=6)


