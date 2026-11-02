import bpy,sys,os,json,traceback
root=os.path.dirname(os.path.dirname(__file__));sys.path.insert(0,root)
import x4d_workflow
x4d_workflow.register()
bpy.context.preferences.view.language='zh_HANS'
bpy.context.preferences.view.use_translate_interface=True
bpy.context.object.cw_primitive.kind='CUBE'

def finish():
    try:
        screen=bpy.context.screen;areas=list(screen.areas)
        data={'workspace':bpy.context.workspace.name,'areas':[(a.type,a.x,a.y,a.width,a.height) for a in areas],'errors':x4d_workflow.layout._errors}
        assert not data['errors'],data
        assert sorted(a.type for a in areas)==sorted(['VIEW_3D','OUTLINER','PROPERTIES','DOPESHEET_EDITOR']),data
        view=next(a for a in areas if a.type=='VIEW_3D');time=next(a for a in areas if a.type=='DOPESHEET_EDITOR')
        assert view.x<10 and view.width/bpy.context.window.width>.74 and time.height/bpy.context.window.height<.08,data
        width=bpy.context.window.width
        with open(os.path.join(root,'artifacts',f'layout-{width}.json'),'w') as f:json.dump(data,f,indent=2)
        bpy.ops.screen.screenshot(filepath=os.path.join(root,'artifacts',f'workspace-v060-{width}.png'))
        region=next(r for r in view.regions if r.type=='WINDOW')
        with bpy.context.temp_override(area=view,region=region):bpy.ops.cw.palette('INVOKE_DEFAULT',category='MESH')
        bpy.app.timers.register(palette_shot,first_interval=1.5)
    except Exception:
        traceback.print_exc();bpy.ops.wm.quit_blender()
    return None

def palette_shot():
    bpy.ops.screen.screenshot(filepath=os.path.join(root,'artifacts',f'palette-v060-{bpy.context.window.width}.png'))
    print('CW_UI_OK',bpy.context.window.width)
    bpy.ops.wm.quit_blender()
    return None
bpy.app.timers.register(finish,first_interval=6)



