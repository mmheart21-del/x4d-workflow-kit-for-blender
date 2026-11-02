"""X4D standard initial layout: viewport, object/attribute managers, slim timeline."""
import bpy
_pending=[]
_errors=[]
REVISION=4

def queue(window):
    if bpy.app.background:return
    if any(w==window for w,_ in _pending):return
    _pending.append((window,0))
    if not bpy.app.timers.is_registered(tick):bpy.app.timers.register(tick,first_interval=.25)

def join(window,source,target):
    with bpy.context.temp_override(window=window,area=source):
        bpy.ops.screen.area_join(source_xy=(source.x+source.width//2,source.y+source.height//2),target_xy=(target.x+target.width//2,target.y+target.height//2))

def configure_view(area):
    space=area.spaces.active
    space.show_gizmo_navigate=False
    space.show_region_ui=False
    space.show_region_toolbar=False
    space.show_region_tool_header=False
    space.overlay.show_floor=True
    space.shading.background_type='VIEWPORT'
    space.shading.background_color=(.025,.027,.03)

def tick():
    if not _pending:return None
    window,stage=_pending[0]
    if window.workspace.name!='X4D':
        _pending.pop(0);return .25 if _pending else None
    screen=window.screen
    try:
        if stage==0:
            if window.workspace.get('cw_layout_revision',0)>=REVISION:
                from . import rail
                rail.start(window);_pending.pop(0);return .25 if _pending else None
            # Collapse the previous release's central dope sheet first so its
            # viewport shares a full-height edge with the obsolete render area.
            main=max((a for a in screen.areas if a.type=='VIEW_3D'),key=lambda a:a.width*a.height)
            render=next((a for a in screen.areas if a.type=='IMAGE_EDITOR' and a.x<main.x),None)
            time=next((a for a in screen.areas if a.type=='DOPESHEET_EDITOR' and abs(a.x-main.x)<5 and abs(a.width-main.width)<5),None)
            if render and time:join(window,main,time)
        elif stage==1:
            main=max((a for a in screen.areas if a.type=='VIEW_3D'),key=lambda a:a.width*a.height)
            render=next((a for a in screen.areas if a.type=='IMAGE_EDITOR' and a.x<main.x),None)
            if render:join(window,main,render)
        elif stage==2:
            main=max((a for a in screen.areas if a.type=='VIEW_3D'),key=lambda a:a.width*a.height)
            configure_view(main)
            time=next((a for a in screen.areas if a.type=='DOPESHEET_EDITOR'),None)
            if time:
                time.spaces.active.mode='TIMELINE'
                time.spaces.active.show_region_ui=False
                target=max(44,int(window.height*.042))
                with bpy.context.temp_override(window=window,area=time):
                    bpy.ops.screen.area_move(x=time.x+time.width//2,y=time.y+time.height,delta=target-time.height)
            else:
                with bpy.context.temp_override(window=window,area=main):
                    bpy.ops.screen.area_split(direction='HORIZONTAL',factor=.045)
        elif stage==3:
            views=[a for a in screen.areas if a.type=='VIEW_3D']
            if len(views)>1:
                time=min(views,key=lambda a:a.height);time.type='DOPESHEET_EDITOR';time.spaces.active.mode='TIMELINE'
            for area in screen.areas:
                if area.type=='PROPERTIES':area.spaces.active.context='CONSTRAINT' if window.view_layer.objects.active else 'TOOL'
                elif area.type=='OUTLINER':
                    area.spaces.active.display_mode='VIEW_LAYER'
                    area.spaces.active.show_restrict_column_hide=True
                    area.spaces.active.show_restrict_column_render=True
            out=next((a for a in screen.areas if a.type=='OUTLINER'),None)
            if out:
                with bpy.context.temp_override(window=window,area=out):
                    bpy.ops.screen.area_move(x=out.x+out.width//2,y=out.y-1,delta=out.height-int(window.height*.43))
        elif stage==4:
            out=next((a for a in screen.areas if a.type=='OUTLINER'),None)
            if out:
                with bpy.context.temp_override(window=window,area=out):
                    bpy.ops.screen.area_move(x=out.x-1,y=out.y+out.height//2,delta=int(window.width*.775)-out.x)
        elif stage==5:
            from . import rail
            for area in screen.areas:
                if area.type=='VIEW_3D':configure_view(area)
                elif area.type=='PROPERTIES':
                    area.spaces.active.show_region_header=False
                    region=next((r for r in area.regions if r.type=='NAVIGATION_BAR'),None)
                    if region and region.width>4:
                        with bpy.context.temp_override(window=window,area=area):bpy.ops.screen.region_toggle(region_type='NAVIGATION_BAR')
                area.tag_redraw()
            rail.start(window)
            from . import selection
            selection.focus()
            window.workspace['cw_layout_revision']=REVISION
            if 'cw_layout_error' in window.workspace:del window.workspace['cw_layout_error']
            _pending.pop(0);return .25 if _pending else None
        _pending[0]=(window,stage+1)
    except Exception as exc:
        _errors.append(str(exc));print('CW layout:',exc)
        window.workspace['cw_layout_error']=str(exc);_pending.pop(0)
    return .25 if _pending else None

def stop():
    _pending.clear()
    if bpy.app.timers.is_registered(tick):bpy.app.timers.unregister(tick)




