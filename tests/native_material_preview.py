import bpy,sys,os,traceback,time
root=os.path.dirname(os.path.dirname(__file__));sys.path.insert(0,root)
import x4d_workflow as kit
kit.register();started=time.monotonic()
def begin():
    bpy.ops.cw.primitive(kind='CUBE')
    for name in ['Red','Metal','Checker','Glass','White']:
        bpy.ops.cw.material_new();mat=bpy.context.window_manager.cw_material;mat.name=name
        bsdf=mat.node_tree.nodes.get('Principled BSDF')
        if name=='Red':bsdf.inputs['Base Color'].default_value=(.7,.01,.01,1)
        if name=='Metal':bsdf.inputs['Metallic'].default_value=1;bsdf.inputs['Roughness'].default_value=.08
        if name=='Glass':bsdf.inputs['Transmission Weight'].default_value=1;bsdf.inputs['Roughness'].default_value=.02
        if name=='Checker':
            checker=mat.node_tree.nodes.new('ShaderNodeTexChecker');checker.inputs['Scale'].default_value=5;mat.node_tree.links.new(checker.outputs['Color'],bsdf.inputs['Base Color'])
    bpy.ops.cw.materials();bpy.app.timers.register(finish,first_interval=10);return None
def finish():
    try:
        pending=[m.name for m in bpy.data.materials if not getattr(m,'is_grease_pencil',False) and (not m.preview or m.preview.image_size[0]==0 or not any(list(m.preview.image_pixels_float)[::101]))]
        if pending and time.monotonic()-started<80:
            print('PREVIEWS_PENDING',pending,flush=True)
            return 5
        print('NATIVE_JOBS',bpy.app.is_job_running('RENDER_PREVIEW'),flush=True)
        print('PREVIEW_SIZES',[(m.name,tuple(m.preview.image_size) if m.preview else None) for m in bpy.data.materials],flush=True)
        bpy.app.timers.register(capture,first_interval=1)
        return None
        area=next(a for a in bpy.context.screen.areas if kit.material_dock.is_dock(a));region=next(r for r in area.regions if r.type=='WINDOW')
        print('NATIVE_PREVIEW_GRID_OK',region.width,region.height,region.view2d.region_to_view(0,region.height))
        return None
    except Exception:traceback.print_exc()
    bpy.ops.wm.quit_blender();return None
def capture():
    bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP',iterations=1)
    bpy.ops.screen.screenshot(filepath=os.path.join(root,'artifacts','native-material-previews.png'))
    kit.unregister();bpy.ops.wm.quit_blender();return None
bpy.app.timers.register(begin,first_interval=6)
