import bpy,sys,os,traceback
sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))
import x4d_workflow as kit
kit.register();state={'kind':'BOOLEAN'}
def fail():traceback.print_exc();kit.unregister();bpy.ops.wm.quit_blender()
def setup():
    try:
        for obj in list(bpy.context.scene.objects):bpy.data.objects.remove(obj,do_unlink=True)
        bpy.ops.mesh.primitive_cube_add();a=bpy.context.object;a.name='Input A'
        bpy.ops.mesh.primitive_cube_add(location=(1,0,0));b=bpy.context.object;b.name='Input B'
        a.select_set(True);bpy.context.view_layer.objects.active=a
        if state['kind']=='BOOLEAN':bpy.ops.cw.generator(kind='BOOLEAN')
        else:bpy.ops.cw.extra(kind='VOLUME_BUILDER')
        state.update(a=a,b=b)
        area=next(a for a in bpy.context.screen.areas if a.type=='OUTLINER');state['outliner']=area
        with bpy.context.temp_override(area=area,region=next(r for r in area.regions if r.type=='WINDOW')):bpy.ops.outliner.show_hierarchy();bpy.ops.outliner.show_one_level(open=True);bpy.ops.outliner.show_one_level(open=True)
        bpy.app.timers.register(click,first_interval=1)
    except Exception:fail()
    return None
def click():
    try:
        area=state['outliner'];
        with bpy.context.temp_override(area=area,region=next(r for r in area.regions if r.type=='WINDOW')):bpy.ops.outliner.show_one_level(open=True)
        region=next(r for r in area.regions if r.type=='WINDOW');window=bpy.context.window
        bpy.ops.screen.screenshot(filepath=os.path.join(os.path.dirname(os.path.dirname(__file__)),'artifacts','source-before-click.png'))
        x=region.x+110;y=region.y+region.height-90
        window.event_simulate(type='MOUSEMOVE',value='NOTHING',x=x,y=y)
        window.event_simulate(type='LEFTMOUSE',value='PRESS',x=x,y=y)
        window.event_simulate(type='LEFTMOUSE',value='RELEASE',x=x,y=y)
        bpy.app.timers.register(check,first_interval=1)
    except Exception:fail()
    return None
def check():
    try:
        a=state['a'];active=bpy.context.view_layer.objects.active
        assert active==a,('Outliner did not activate Input A',active.name if active else None)
        assert not a.hide_get() and a.display_type=='WIRE'
        a.location.x+=.3;bpy.context.view_layer.update()
        bpy.ops.screen.screenshot(filepath=os.path.join(os.path.dirname(os.path.dirname(__file__)),'artifacts','source-wire-'+state['kind'].lower()+'.png'))
        a.select_set(False);bpy.app.timers.register(deselected,first_interval=.6)
    except Exception:fail()
    return None
def deselected():
    try:
        assert state['a'].hide_get()
        print('X4D_OUTLINER_WIRE_EVENTS_OK',state['kind'])
        if state['kind']=='BOOLEAN':state['kind']='VOLUME';bpy.app.timers.register(setup,first_interval=.5)
        else:kit.unregister();bpy.ops.wm.quit_blender()
    except Exception:fail()
    return None
bpy.app.timers.register(setup,first_interval=6)



