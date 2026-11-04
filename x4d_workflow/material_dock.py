"""Embedded material editor with stable, immediately available sphere thumbnails."""
import bpy
from .catalog import label
_areas=set();_items=[];_draws=[];_polls=[]
_highlight_handle=None

def track_creation(scene, depsgraph):
    materials=[m for m in bpy.data.materials if not m.library]
    latest=max((m.get('x4d_created',0) for m in materials),default=0)
    for mat in sorted((m for m in materials if 'x4d_created' not in m),key=lambda m:m.session_uid):
        latest+=1
        mat['x4d_created']=latest

def ordered_materials():
    scene=bpy.context.scene
    used={slot.material for obj in scene.objects for slot in obj.material_slots} if scene else set()
    return sorted(
        (m for m in bpy.data.materials if not getattr(m,'is_grease_pencil',False)
         and (not m.get('x4d_factory_material') or m in used)),
        key=lambda m:(m.get('x4d_created',0),m.session_uid),reverse=True)

def highlighted(window):
    obj=window.view_layer.objects.active
    if obj is None or not obj.select_get():return set()
    return {slot.material.name for slot in obj.material_slots if slot.material}

def draw_highlights():
    context=bpy.context
    if not context.window or not context.region or not is_dock(context.area):return
    names=highlighted(context.window)
    if not names:return
    import gpu
    from gpu_extras.batch import batch_for_shader
    from .material_events import rectangles
    materials=ordered_materials()
    shader=gpu.shader.from_builtin('UNIFORM_COLOR')
    shader.bind();shader.uniform_float('color',(.12,.7,1.,1.))
    scale=context.preferences.system.ui_scale
    for mat,(left,top,width,height) in zip(materials,rectangles(context.area,context.region,len(materials))):
        if mat.name not in names:continue
        x,y=context.region.view2d.view_to_region(left,top+2*scale,clip=False)
        u,v=context.region.view2d.view_to_region(left+width-3*scale,top-height-20*scale,clip=False)
        t=max(2,round(2*scale))
        points=[]
        for a,b,c,d in [(x,v,u,v+t),(x,y-t,u,y),(x,v,x+t,y),(u-t,v,u,y)]:
            points.extend([(a,b),(c,b),(c,d),(a,b),(c,d),(a,d)])
        batch_for_shader(shader,'TRIS',{'pos':points}).draw(shader)
def is_dock(area):
    if area is None:return False
    if area.as_pointer() in _areas:return True
    if area.type!='PROPERTIES':return False
    space=area.spaces.active
    if space.context!='SCENE' or not space.use_pin_id or not isinstance(space.pin_id,bpy.types.Scene):return False
    return any(w.workspace.name=='X4D' and any(a==area for a in w.screen.areas) for w in bpy.context.window_manager.windows)

def is_open(window):return any(is_dock(a) for a in window.screen.areas)
def items(self,context):
    global _items
    result=[]
    for i,mat in enumerate(ordered_materials()):
        if getattr(mat,'is_grease_pencil',False):continue
        mat.preview_ensure()
        result.append((mat.name,mat.name,'Native material preview',mat.preview.icon_id,i))
    _items=result
    return _items

def selected(self,context):
    mat=bpy.data.materials.get(self.cw_material_tile)
    if mat:self.cw_material=mat

def toggle(context):
    window=context.window
    if is_open(window):
        dock=next(a for a in window.screen.areas if is_dock(a));view=next((a for a in window.screen.areas if a.type=='VIEW_3D' and abs(a.y-dock.y)<5 and abs(a.height-dock.height)<5),None)
        if not view:return {'CANCELLED'}
        _areas.discard(dock.as_pointer())
        from .layout import join
        join(window,view,dock);return {'FINISHED'}
    view=max((a for a in window.screen.areas if a.type=='VIEW_3D'),key=lambda a:a.width*a.height)
    before={a.as_pointer() for a in window.screen.areas}
    with context.temp_override(area=view):bpy.ops.screen.area_split(direction='VERTICAL',factor=max(.5,1-300/view.width))
    new=next(a for a in window.screen.areas if a.as_pointer() not in before)
    def finish():
        dock=max((view,new),key=lambda a:a.x)
        dock.type='PROPERTIES';_areas.add(dock.as_pointer());dock.spaces.active.context='SCENE'
        dock.spaces.active.pin_id=window.scene;dock.spaces.active.use_pin_id=True
        nav=next((r for r in dock.regions if r.type=='NAVIGATION_BAR'),None)
        if nav and nav.width>4:
            with bpy.context.temp_override(window=window,area=dock):bpy.ops.screen.region_toggle(region_type='NAVIGATION_BAR')
        from . import material_events
        material_events.start(window)
        dock.tag_redraw()
        return None
    bpy.app.timers.register(finish,first_interval=.3)
    from . import material_previews
    material_previews.request()
    install();return {'FINISHED'}

def install():
    global _highlight_handle
    if _highlight_handle is None and not bpy.app.background:
        _highlight_handle=bpy.types.SpaceProperties.draw_handler_add(draw_highlights,(),'WINDOW','POST_PIXEL')
    if _draws:return
    def wrap(original):
        def draw(self,context):
            if not is_dock(context.area):original(self,context)
        return draw
    for cls in bpy.types.Panel.__subclasses__():
        cls=getattr(bpy.types,cls.__name__,cls)
        if getattr(cls,'bl_context',None)=='scene' and cls is not CW_PT_material_dock and hasattr(cls,'draw'):
            original=cls.draw
            original_poll=getattr(cls,'poll',None)
            def make_poll(fn):
                def poll(cls,context):return not is_dock(context.area) and (fn(context) if fn else True)
                return classmethod(poll)
            had_poll='poll' in cls.__dict__;own_poll=cls.__dict__.get('poll')
            _polls.append((cls,had_poll,own_poll));cls.poll=make_poll(original_poll)
            draw=wrap(original)
            cls.draw=draw;_draws.append((cls,original,draw))
            bpy.utils.unregister_class(cls);bpy.utils.register_class(cls)

def stop():
    global _highlight_handle
    if _highlight_handle is not None:
        try:bpy.types.SpaceProperties.draw_handler_remove(_highlight_handle,'WINDOW')
        except (ValueError,ReferenceError):pass
        _highlight_handle=None
    for cls,original,wrapper in _draws:
        if cls.draw is wrapper:cls.draw=original
    for cls,had_poll,own_poll in _polls:
        if had_poll:cls.poll=own_poll
        else:delattr(cls,'poll')
        bpy.utils.unregister_class(cls);bpy.utils.register_class(cls)
    _polls.clear()
    _draws.clear();_areas.clear();_items.clear()

class CW_PT_material_dock(bpy.types.Panel):
    bl_label='Materials';bl_idname='CW_PT_material_dock';bl_space_type='PROPERTIES';bl_region_type='WINDOW';bl_context='scene';bl_options={'HIDE_HEADER'}
    @classmethod
    def poll(cls,context):return is_dock(context.area)
    def draw(self,context):
        l=self.layout;wm=context.window_manager
        row=l.row(align=True);row.label(text=label('材质','Materials'));row.operator('cw.material_new',text='',icon='ADD');row.operator('cw.material_refresh',text='',icon='FILE_REFRESH');row.operator('cw.materials',text='',icon='PANEL_CLOSE')
        if not items(wm,context):return
        from .material_events import grid_columns
        grid=l.grid_flow(columns=grid_columns(context.region,len(_items)),even_columns=True,align=True)
        for key,name,description,icon,index in items(wm,context):
            col=grid.column(align=True);col.template_icon(icon_value=icon,scale=4)
            col.operator('cw.material_pick',text=name,depress=bool(wm.cw_material and wm.cw_material.name==key)).material=key
        mat=wm.cw_material
        if mat and mat.name in bpy.data.materials:
            l.separator()
            l.label(text=label('使用此材质的对象','Objects using this material'))
            for obj in context.scene.objects:
                if any(s.material==mat for s in obj.material_slots):l.operator('cw.material_user',text=obj.name,icon='OBJECT_DATA').object=obj.name
        from . import material_previews
        l.label(text=material_previews.status(),icon='INFO')
class CW_OT_material_pick(bpy.types.Operator):
    bl_idname='cw.material_pick';bl_label='Select Material'
    material:bpy.props.StringProperty()
    def invoke(self,context,event):
        from . import material_editors
        mat=bpy.data.materials.get(self.material)
        if event.value=='DOUBLE_CLICK':return material_editors.open_nodes(context,mat)
        return self.execute(context)
    def execute(self,context):
        from . import material_editors
        material_editors.select(context,bpy.data.materials.get(self.material))
        return {'FINISHED'}

class CW_OT_material_refresh(bpy.types.Operator):
    bl_idname='cw.material_refresh';bl_label='Refresh Rendered Previews'
    def execute(self,context):
        from . import material_previews
        material_previews.request();return {'FINISHED'}

classes=[CW_PT_material_dock,CW_OT_material_pick,CW_OT_material_refresh]
