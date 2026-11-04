import bpy,sys,os,time,traceback
sys.path.insert(0,os.getcwd())
import x4d_workflow as kit
kit.register();state={'start':time.monotonic()}
def fail():traceback.print_exc();kit.unregister();bpy.ops.wm.quit_blender()
def activate(obj):
 for o in bpy.context.view_layer.objects:o.select_set(False)
 bpy.context.view_layer.objects.active=obj
 if obj:obj.select_set(True)
 kit.selection.focus()
def begin():
 try:
  bpy.ops.cw.primitive(kind='CUBE');a=bpy.context.object;a.name='Object One';state['one']=a
  bpy.ops.mesh.primitive_cube_add(location=(3,0,0));state['two']=bpy.context.object
  bpy.ops.mesh.primitive_cube_add(location=(-3,0,0));state['empty']=bpy.context.object
  for mat in list(bpy.data.materials):bpy.data.materials.remove(mat,do_unlink=True)
  mats=[]
  for name,color,metallic in [('Red',(0.8,.015,.01,1),0),('Metal',(.7,.7,.7,1),1),('Blue',(.01,.08,.8,1),0)]:
   m=bpy.data.materials.new(name);m.use_nodes=True;bsdf=m.node_tree.nodes.get('Principled BSDF');bsdf.inputs['Base Color'].default_value=color;bsdf.inputs['Metallic'].default_value=metallic;bsdf.inputs['Roughness'].default_value=.2;mats.append(m)
  state['one'].data.materials.append(mats[0]);state['one'].data.materials.append(mats[1]);state['two'].data.materials.append(mats[1]);state['two'].data.materials.append(mats[2]);state['blue']=mats[2]
  activate(state['one']);assert kit.material_dock.highlighted(bpy.context.window)=={'Red','Metal'}
  activate(state['two']);assert kit.material_dock.highlighted(bpy.context.window)=={'Metal','Blue'}
  activate(state['empty']);assert not kit.material_dock.highlighted(bpy.context.window)
  activate(None);assert not kit.material_dock.highlighted(bpy.context.window)
  activate(state['one']);kit.material_editors.select(bpy.context,state['blue'])
  bpy.ops.cw.materials();kit.material_previews.request();bpy.app.timers.register(wait,first_interval=2)
 except Exception:fail()
def wait():
 try:
  mats=list(bpy.data.materials)
  ready=all(m.preview and m.preview.image_size[0] and any(list(m.preview.image_pixels_float)[::53]) for m in mats)
  if not ready:
   if time.monotonic()-state['start']>160:raise RuntimeError('Native previews not ready')
   return 2
  bpy.app.timers.register(finish,first_interval=1)
 except Exception:fail()
def finish():
 try:
  assert bpy.context.window_manager.cw_material==state['blue']
  assert kit.material_dock.highlighted(bpy.context.window)=={'Red','Metal'}
  bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP',iterations=1)
  bpy.ops.screen.screenshot(filepath=os.path.join(os.getcwd(),'artifacts','material-object-highlight.png'))
  kit.material_editors.select(bpy.context,state['blue'])
  area=next(a for a in bpy.context.screen.areas if a.type=='VIEW_3D');region=next(r for r in area.regions if r.type=='WINDOW')
  with bpy.context.temp_override(area=area,region=region):assert bpy.ops.cw.render(mode='SETTINGS')=={'FINISHED'}
  assert next(a for a in bpy.context.screen.areas if a.type=='PROPERTIES' and not kit.material_dock.is_dock(a)).spaces.active.context=='RENDER'
  assert next(a for a in bpy.context.screen.areas if kit.material_dock.is_dock(a)).spaces.active.context=='SCENE'
  print('X4D_HIGHLIGHT_NATIVE_PREVIEWS_ALL_SELECTION_CASES_AND_RENDER_SETTINGS_OK')
  kit.unregister();bpy.ops.wm.quit_blender()
 except Exception:fail()
bpy.app.timers.register(begin,first_interval=6)

