import bpy,sys,os,traceback
root=os.path.dirname(os.path.dirname(__file__));sys.path.insert(0,root)
import x4d_workflow as kit
kit.register();state={}
def begin():
    try:
        window=bpy.context.window;state['main']=window
        bpy.ops.cw.primitive(kind='CUBE')
        a=bpy.data.materials.new('Material A');a.use_nodes=True;b=bpy.data.materials.new('Material B');b.use_nodes=True
        state.update(a=a,b=b)
        bpy.ops.cw.materials();bpy.app.timers.register(select,first_interval=.7)
    except Exception:traceback.print_exc();bpy.ops.wm.quit_blender()
    return None
def select():
    try:
        window=state['main'];dock=next(a for a in window.screen.areas if kit.material_dock.is_dock(a))
        with bpy.context.temp_override(window=window,area=dock):
            kit.material_editors.select(bpy.context,state['a'])
            props=next(a for a in window.screen.areas if a.type=='PROPERTIES' and not kit.material_dock.is_dock(a))
            assert props.spaces.active.context=='MATERIAL';assert props.spaces.active.pin_id==state['a']
            assert 'FINISHED' in kit.material_editors.open_nodes(bpy.context,state['a'])
        bpy.app.timers.register(follow,first_interval=1)
    except Exception:traceback.print_exc();bpy.ops.wm.quit_blender()
    return None
def follow():
    try:
        window=state['main'];other=next(w for w in bpy.context.window_manager.windows if w!=window);state['nodewindow']=other
        area=next(a for a in other.screen.areas if a.type=='NODE_EDITOR');assert area.spaces.active.node_tree==state['a'].node_tree
        dock=next(a for a in window.screen.areas if kit.material_dock.is_dock(a))
        with bpy.context.temp_override(window=window,area=dock):
            kit.material_editors.select(bpy.context,state['b'])
            assert area.spaces.active.node_tree==state['b'].node_tree
            assert 'FINISHED' in kit.material_editors.open_nodes(bpy.context,state['b'])
            assert len(bpy.context.window_manager.windows)==2
            bpy.ops.screen.screenshot(filepath=os.path.join(root,'artifacts','material-editor-main.png'))
        with bpy.context.temp_override(window=other,area=area,region=next(r for r in area.regions if r.type=='WINDOW')):
            before=len(state['b'].node_tree.nodes)
            bpy.ops.node.add_node(type='ShaderNodeTexNoise')
            assert len(state['b'].node_tree.nodes)==before+1
            bpy.ops.screen.screenshot(filepath=os.path.join(root,'artifacts','material-editor-nodes.png'))
            bpy.ops.wm.window_close()
        bpy.app.timers.register(finish,first_interval=.5)
    except Exception:traceback.print_exc();bpy.ops.wm.quit_blender()
    return None
def finish():
    assert len(bpy.context.window_manager.windows)==1
    kit.unregister();print('X4D_MATERIAL_EDITOR_WORKFLOW_OK');bpy.ops.wm.quit_blender();return None
bpy.app.timers.register(begin,first_interval=6)
