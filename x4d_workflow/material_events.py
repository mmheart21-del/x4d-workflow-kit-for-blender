"""Hit testing for native preview tiles; route clicks before icon zoom handles them."""
import bpy,math,time
_running={};_generation=0

def grid_columns(region):
    left=region.view2d.region_to_view(0,0)[0];right=region.view2d.region_to_view(region.width,0)[0]
    scale=bpy.context.preferences.system.ui_scale
    return max(1,int((right-left)/(85*scale)))

def rectangles(area,region,count,scale=None):
    scale=bpy.context.preferences.system.ui_scale if scale is None else scale
    columns=grid_columns(region);rows=math.ceil(count/columns)
    if not rows:return []
    left=region.view2d.region_to_view(0,0)[0];right=region.view2d.region_to_view(region.width,0)[0]
    cell=(right-left-20*scale)/columns
    return [(10*scale+(i//rows)*cell,(-76-(i%rows)*102)*scale,cell,78*scale) for i in range(count)]

def hit(area,region,x,y,names):
    # Convert through View2D so scrolling and Properties zoom stay in sync.
    vx,vy=region.view2d.region_to_view(x,y)
    for name,(left,top,width,height) in zip(names,rectangles(area,region,len(names))):
        if left<=vx<left+width and top-height<=vy<=top:return name
    return None

class CW_OT_material_events(bpy.types.Operator):
    bl_idname='cw.material_events';bl_label='Material Tile Interaction';bl_options={'INTERNAL'}
    def invoke(self,context,event):
        key=context.window.as_pointer()
        if _running.get(key)==_generation:return {'CANCELLED'}
        self.key=key;self.generation=_generation;self.last_name='';self.last_time=0
        _running[key]=_generation;context.window_manager.modal_handler_add(self);return {'RUNNING_MODAL'}
    def modal(self,context,event):
        if self.generation!=_generation:
            if _running.get(self.key)==self.generation:_running.pop(self.key,None)
            return {'CANCELLED'}
        if event.type=='LEFTMOUSE' and event.value=='RELEASE':
            area=next((a for a in context.window.screen.areas if a.x<=event.mouse_x<a.x+a.width and a.y<=event.mouse_y<a.y+a.height),None)
            if area and area.type in {'VIEW_3D','OUTLINER'}:
                window=context.window
                def follow_object():
                    from . import selection
                    try:
                        obj=window.view_layer.objects.active
                        if obj and obj.select_get():
                            selection._last.pop(window.as_pointer(),None);selection.focus()
                    except ReferenceError:pass
                    return None
                bpy.app.timers.register(follow_object,first_interval=.1)
        deleting=event.type=='DEL' and event.value=='PRESS'
        if not deleting and (event.type!='LEFTMOUSE' or event.value not in {'PRESS','DOUBLE_CLICK'}):return {'PASS_THROUGH'}
        from . import material_dock,material_editors
        for area in context.window.screen.areas:
            if not material_dock.is_dock(area):continue
            region=next((r for r in area.regions if r.type=='WINDOW'),None)
            if region is None:continue
            x=event.mouse_x-region.x;y=event.mouse_y-region.y
            if not (0<=x<region.width and 0<=y<region.height):continue
            if deleting:
                with context.temp_override(area=area,region=region):bpy.ops.cw.material_delete()
                return {'RUNNING_MODAL'}
            names=[item[0] for item in material_dock.items(context.window_manager,context)]
            name=hit(area,region,x,y,names)
            if not name:return {'PASS_THROUGH'}
            mat=bpy.data.materials.get(name)
            now=time.monotonic();double=event.value=='DOUBLE_CLICK' or (self.last_name==name and now-self.last_time<.4)
            self.last_name=name;self.last_time=now
            with context.temp_override(area=area,region=region):
                if double:material_editors.open_nodes(context,mat)
                else:material_editors.select(context,mat)
            return {'RUNNING_MODAL'}
        return {'PASS_THROUGH'}

def start(window):
    if window.as_pointer() not in _running:
        with bpy.context.temp_override(window=window):bpy.ops.cw.material_events('INVOKE_DEFAULT')

def stop():
    global _generation
    _generation+=1;_running.clear()
classes=[CW_OT_material_events]
