import bpy,sys,os,traceback
sys.path.insert(0,os.getcwd())
import x4d_workflow as kit
kit.register();kit.material_previews.request=lambda:None
state={}
def fail():traceback.print_exc();kit.unregister();bpy.ops.wm.quit_blender()
def event(kind,value,x,y):bpy.context.window.event_simulate(type=kind,value=value,x=x,y=y)
def begin():
 try:
  bpy.ops.cw.primitive(kind='CUBE');state['obj']=bpy.context.object
  mat=bpy.data.materials.new('Selection Test');mat.use_nodes=True;state['mat']=mat
  bpy.ops.cw.materials();bpy.app.timers.register(pick,first_interval=1)
 except Exception:fail()
def pick():
 try:
  kit.material_editors.select(bpy.context,state['mat'])
  area=next(a for a in bpy.context.screen.areas if a.type=='VIEW_3D');region=next(r for r in area.regions if r.type=='WINDOW')
  from bpy_extras.view3d_utils import location_3d_to_region_2d
  p=location_3d_to_region_2d(region,area.spaces.active.region_3d,state['obj'].matrix_world.translation)
  event('MOUSEMOVE','NOTHING',region.x+int(p.x),region.y+int(p.y));event('LEFTMOUSE','PRESS',region.x+int(p.x),region.y+int(p.y));event('LEFTMOUSE','RELEASE',region.x+int(p.x),region.y+int(p.y))
  bpy.app.timers.register(check_object,first_interval=1)
 except Exception:fail()
def check_object():
 try:
  props=next(a for a in bpy.context.screen.areas if a.type=='PROPERTIES' and not kit.material_dock.is_dock(a))
  if props.spaces.active.context!='CONSTRAINT' and state.get('tries',0)<20:
   state['tries']=state.get('tries',0)+1;return .5
  assert props.spaces.active.context=='CONSTRAINT',props.spaces.active.context
  assert not props.spaces.active.use_pin_id
  print('X4D_SAME_OBJECT_CLICK_RETURNS_PROPERTIES_OK')
  area=next(a for a in bpy.context.screen.areas if a.type=='VIEW_3D');region=next(r for r in area.regions if r.type=='WINDOW');state.update(area=area,region=region)
  with bpy.context.temp_override(area=area,region=region):assert bpy.ops.cw.render('INVOKE_DEFAULT',mode='REGION')=={'RUNNING_MODAL'}
  event('ESC','PRESS',region.x+200,region.y+200)
  bpy.app.timers.register(check_cancel,first_interval=.5)
 except Exception:fail()
def check_cancel():
 try:
  assert not kit.rendering._borders
  area=state['area'];region=state['region']
  # Suppress costly final rendering while testing the real drag modal.
  kit.rendering.CW_OT_render.run_render=lambda *args,**kwargs:{'FINISHED'}
  with bpy.context.temp_override(area=area,region=region):bpy.ops.cw.render('INVOKE_DEFAULT',mode='REGION')
  event('LEFTMOUSE','PRESS',region.x+200,region.y+200);event('MOUSEMOVE','NOTHING',region.x+400,region.y+400);event('LEFTMOUSE','RELEASE',region.x+400,region.y+400)
  bpy.app.timers.register(finish,first_interval=.5)
 except Exception:fail()
def finish():
 try:
  assert not kit.rendering._borders
  print('X4D_RENDER_REGION_DRAG_AND_CANCEL_OK')
  kit.unregister();bpy.ops.wm.quit_blender()
 except Exception:fail()
bpy.app.timers.register(begin,first_interval=6)


