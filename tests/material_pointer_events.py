import bpy,sys,os,traceback
root=os.path.dirname(os.path.dirname(__file__));sys.path.insert(0,root)
import x4d_workflow as kit
kit.register();kit.material_previews.request=lambda:None
state={}
def fail():
    traceback.print_exc();kit.unregister();bpy.ops.wm.quit_blender()
def click(name,double=False):
    window=state['window'];area=next(a for a in window.screen.areas if kit.material_dock.is_dock(a));region=next(r for r in area.regions if r.type=='WINDOW')
    names=[i[0] for i in kit.material_dock.items(bpy.context.window_manager,bpy.context)];index=names.index(name)
    x,y,w,h=kit.material_events.rectangles(area,region,len(names))[index]
    rx,ry=region.view2d.view_to_region(x+w/2,y-h/2,clip=False);x=region.x+rx;y=region.y+ry
    window.event_simulate(type='MOUSEMOVE',value='NOTHING',x=x,y=y)
    window.event_simulate(type='LEFTMOUSE',value='PRESS',x=x,y=y)
    window.event_simulate(type='LEFTMOUSE',value='RELEASE',x=x,y=y)
    if double:
        window.event_simulate(type='LEFTMOUSE',value='PRESS',x=x,y=y)
        window.event_simulate(type='LEFTMOUSE',value='RELEASE',x=x,y=y)
def begin():
    try:
        state['window']=bpy.context.window;bpy.ops.cw.primitive(kind='CUBE')
        for name in ['A','B']:
            m=bpy.data.materials.new(name);m.use_nodes=True;state[name]=m
        bpy.ops.cw.materials();bpy.app.timers.register(single,first_interval=.8)
    except Exception:fail()
    return None
def single():
    try:click('A');bpy.app.timers.register(double,first_interval=.7)
    except Exception:fail()
    return None
def double():
    try:
        assert bpy.context.window_manager.cw_material==state['A'],'Single click did not select A'
        props=next(a for a in state['window'].screen.areas if a.type=='PROPERTIES' and not kit.material_dock.is_dock(a))
        assert props.spaces.active.context=='MATERIAL'
        click('A',True);bpy.app.timers.register(change,first_interval=1)
    except Exception:fail()
    return None
def change():
    try:
        assert len(bpy.context.window_manager.windows)==2,'Double click did not open node window'
        nodewindow=next(w for w in bpy.context.window_manager.windows if w!=state['window']);state['nodewindow']=nodewindow
        nodearea=next(a for a in nodewindow.screen.areas if a.type=='NODE_EDITOR');state['nodearea']=nodearea
        assert nodearea.spaces.active.node_tree==state['A'].node_tree
        click('B');bpy.app.timers.register(finish,first_interval=1)
    except Exception:fail()
    return None
def finish():
    try:
        assert state['nodearea'].spaces.active.node_tree==state['B'].node_tree
        assert len(bpy.context.window_manager.windows)==2
        window=state['window'];area=next(a for a in window.screen.areas if kit.material_dock.is_dock(a));region=next(r for r in area.regions if r.type=='WINDOW')
        state['object_count']=len(window.scene.objects)
        window.event_simulate(type='DEL',value='PRESS',x=region.x+40,y=region.y+region.height-110)
        window.event_simulate(type='DEL',value='RELEASE',x=region.x+40,y=region.y+region.height-110)
        bpy.app.timers.register(deleted,first_interval=1)
    except Exception:fail()
    return None

def deleted():
    try:
        assert bpy.data.materials.get('B') is None,'Del did not delete selected material'
        assert len(state['window'].scene.objects)==state['object_count'],'Del deleted an object'
        assert state['nodearea'].spaces.active.node_tree==bpy.context.window_manager.cw_material.node_tree
        window=state['window'];area=next(a for a in window.screen.areas if kit.material_dock.is_dock(a));region=next(r for r in area.regions if r.type=='WINDOW')
        window.event_simulate(type='Z',value='PRESS',ctrl=True,x=region.x+40,y=region.y+region.height-110)
        window.event_simulate(type='Z',value='RELEASE',ctrl=True,x=region.x+40,y=region.y+region.height-110)
        bpy.app.timers.register(undone,first_interval=1)
    except Exception:fail()
    return None

def undone():
    try:
        assert bpy.data.materials.get('B') is not None,'Material deletion undo failed'
        with bpy.context.temp_override(window=state['window']):bpy.ops.screen.screenshot(filepath=os.path.join(root,'artifacts','material-click-main.png'))
        with bpy.context.temp_override(window=state['nodewindow']):bpy.ops.wm.window_close()
        kit.unregister();print('X4D_NATIVE_POINTER_EVENTS_AND_DELETE_UNDO_OK');bpy.ops.wm.quit_blender()
    except Exception:fail()
    return None
bpy.app.timers.register(begin,first_interval=6)
