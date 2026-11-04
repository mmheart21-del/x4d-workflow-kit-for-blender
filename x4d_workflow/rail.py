"""Reference-inspired left tools and right creation rail; native popups handle input."""
import bpy,blf,gpu
from gpu_extras.batch import batch_for_shader
from bpy.props import StringProperty
from .catalog import CATEGORIES,label
from . import icons,drag_tools
_pointer={}
_pressed={}
_handle=None
_running={}
_generation=0
_enabled=False
_hover={}
TOOLS=[('SELECT','选择','Select'),('MOVE','移动','Move'),('ROTATE','旋转','Rotate'),('SCALE','缩放','Scale'),('OBJECT','对象模式','Object Mode'),('POINT','点模式','Point Mode'),('EDGE','边模式','Edge Mode'),('FACE','面模式','Face Mode'),('AXIS','编辑轴心','Edit Axis')]

def left_tools(context):
    if context.mode!='EDIT_MESH':return TOOLS
    from .modeling import COMMANDS
    mode=context.tool_settings.mesh_select_mode
    common=['POLY_BUILD','ADD_POINT','FILL_HOLE','BEVEL','EXTRUDE']
    specific=['WELD','CONNECT','SET_POINT','SLIDE'] if mode[0] else ['BRIDGE','SUBDIVIDE','ROTATE_EDGE','SLIDE'] if mode[1] else ['INSET','BRIDGE','DISCONNECT','NORMAL_MOVE']
    return TOOLS[:4]+[(key,*COMMANDS[key][:2]) for key in common+specific+['KNIFE','SMOOTH','SYMMETRIZE']]

def rect(x,y,w,h,color):
    shader=gpu.shader.from_builtin('UNIFORM_COLOR');shader.bind();shader.uniform_float('color',color)
    batch_for_shader(shader,'TRIS',{'pos':[(x,y),(x+w,y),(x+w,y+h),(x,y),(x+w,y+h),(x,y+h)]}).draw(shader)
def sprite(name,x,y,size):
    texture=gpu.texture.from_image(icons.image(name))
    shader=gpu.shader.from_builtin('IMAGE');shader.bind();shader.uniform_sampler('image',texture)
    batch_for_shader(shader,'TRI_FAN',{'pos':[(x,y),(x+size,y),(x+size,y+size),(x,y+size)],'texCoord':[(0,0),(1,0),(1,1),(0,1)]}).draw(shader)
def metrics(context):
    scale=context.preferences.system.ui_scale
    return max(28,int(30*scale)),max(25,int(28*scale))
def right_edge(area,region):
    sidebar=next((r for r in area.regions if r.type=='UI' and r.width>1),None)
    if area.spaces.active.show_region_ui and sidebar:
        return min(region.width,sidebar.x-region.x)
    return region.width

def draw():
    context=bpy.context
    if not _enabled or context.workspace.name!='X4D' or not context.region:return
    from . import field_view,loop_preview
    field_view.draw(context)
    loop_preview.draw(context)
    width,height=metrics(context);r=context.region
    gpu.state.blend_set('ALPHA')
    hovered=_hover.get(context.window.as_pointer(),('',-1))
    for side,entries,x in [('RIGHT',CATEGORIES,right_edge(context.area,r)-width),('LEFT',left_tools(context),0)]:
        rect(x,0,width,r.height,(.145,.148,.155,1))
        for i,item in enumerate(entries):
            y=r.height-26-(i+1)*height
            selected=False
            if side=='LEFT':
                selected=(item[0] in {'POINT','EDGE','FACE'} and context.mode=='EDIT_MESH' and context.tool_settings.mesh_select_mode[['POINT','EDGE','FACE'].index(item[0])]) or (item[0]=='AXIS' and context.scene.tool_settings.use_transform_data_origin)
                tool=context.workspace.tools.from_space_view3d_mode(context.mode,create=False)
                selected=selected or (tool and tool.idname=={'SELECT':'builtin.select_box','MOVE':'builtin.move','ROTATE':'builtin.rotate','SCALE':'builtin.scale'}.get(item[0],''))
            if side=='LEFT' and item[0]==drag_tools.armed.get(context.window.as_pointer()):selected=True
            tile=min(width,height)-4
            left=x+(width-tile)/2
            bottom=y+(height-tile)/2
            rect(left,bottom,tile,tile,(.10,.105,.12,1))
            color=(.31,.36,.57,1) if selected else (.28,.29,.33,1) if hovered==(side,i) else (.20,.21,.23,1)
            rect(left+1,bottom+1,tile-2,tile-2,color)
            if side=='RIGHT':name=icons.key(item[0])
            elif item in TOOLS:name='tool_'+item[0].lower()
            else:name='mesh_'+item[0].lower()
            size=tile-3
            sprite(name,left+1.5,bottom+1.5,size)
    side,index=hovered
    entries=CATEGORIES if side=='RIGHT' else left_tools(context)
    if 0<=index<len(entries):
        item=entries[index];title=label(item[1],item[2]);blf.size(0,max(11,int(12*context.preferences.system.ui_scale)))
        tw,th=blf.dimensions(0,title);y=r.height-26-(index+1)*height
        x=right_edge(context.area,r)-width-tw-22 if side=='RIGHT' else width+5
        rect(x,y,tw+16,height,(.075,.08,.09,.98));blf.color(0,.9,.9,.93,1);blf.position(0,x+8,y+(height-th)/2,0);blf.draw(0,title)
    key=context.window.as_pointer()
    tool=drag_tools.armed.get(key)
    pointer=_pointer.get(key)
    if tool and pointer and pointer[0]==context.area.as_pointer() and context.mode=='EDIT_MESH':
        sprite('mesh_'+tool.lower(),pointer[1]+13,pointer[2]-25,23)
    from .modeling import draw_sequence
    draw_sequence(context)
    gpu.state.blend_set('NONE')

class CW_OT_tool(bpy.types.Operator):
    bl_idname='cw.tool';bl_label='Tool';bl_options={'UNDO'}
    tool:StringProperty()
    @classmethod
    def description(cls,context,properties):
        descriptions={
            'SELECT':('选择：框选视口中的对象或组件','Select objects or components with a box'),
            'MOVE':('移动（E）：沿坐标轴移动选中项','Move (E): translate the selection'),
            'ROTATE':('旋转（R）：围绕轴心旋转选中项','Rotate (R): rotate around the pivot'),
            'SCALE':('缩放（T）：调整选中项的大小','Scale (T): resize the selection'),
            'OBJECT':('对象模式：选择和变换完整对象','Object mode: select and transform whole objects'),
            'POINT':('点模式：编辑网格顶点或晶格控制点','Point mode: edit mesh vertices or lattice points'),
            'EDGE':('边模式：选择和编辑网格边','Edge mode: select and edit mesh edges'),
            'FACE':('面模式：选择和编辑多边形','Polygon mode: select and edit mesh faces'),
            'AXIS':('轴心编辑：切换仅变换对象原点','Axis editing: toggle transform origins only')}
        return label(*descriptions.get(properties.tool,('切换当前工具','Switch the active tool')))
    def execute(self,context):
        if not context.area or context.area.type!='VIEW_3D':
            area=next((a for a in context.screen.areas if a.type=='VIEW_3D'),None)
            if not area:return {'CANCELLED'}
            with context.temp_override(area=area,region=next(r for r in area.regions if r.type=='WINDOW')):return bpy.ops.cw.tool(tool=self.tool)
        tool=self.tool
        from .quick_menu import remember
        remember('cw.tool',tool)
        if tool in {'SELECT','MOVE','ROTATE','SCALE'}:
            bpy.ops.wm.tool_set_by_id(name={'SELECT':'builtin.select_box','MOVE':'builtin.move','ROTATE':'builtin.rotate','SCALE':'builtin.scale'}[tool])
        elif tool=='AXIS':context.scene.tool_settings.use_transform_data_origin=not context.scene.tool_settings.use_transform_data_origin
        else:
            obj=context.object
            if obj and obj.type=='LATTICE' and tool in {'POINT','OBJECT'}:
                bpy.ops.object.mode_set(mode='EDIT' if tool=='POINT' else 'OBJECT');return {'FINISHED'}
            if not obj or obj.type!='MESH':self.report({'WARNING'},label('请选择网格对象','Select a mesh'));return {'CANCELLED'}
            bpy.ops.object.mode_set(mode='OBJECT' if tool=='OBJECT' else 'EDIT')
            if tool!='OBJECT':context.tool_settings.mesh_select_mode=tuple(k==tool for k in ['POINT','EDGE','FACE'])
        return {'FINISHED'}

class CW_OT_rail(bpy.types.Operator):
    bl_idname='cw.rail';bl_label='X4D Creation Rail';bl_options={'INTERNAL'}
    def invoke(self,context,event):
        token=context.window.as_pointer()
        if _running.get(token)==_generation:return {'CANCELLED'}
        self.token=token;self.generation=_generation;_running[token]=_generation;context.window_manager.modal_handler_add(self);return {'RUNNING_MODAL'}
    def modal(self,context,event):
        if not _enabled or self.generation!=_generation:
            if _running.get(self.token)==self.generation:_running.pop(self.token,None)
            return {'CANCELLED'}
        if context.workspace.name!='X4D':
            drag_tools.armed.pop(self.token,None)
            _pressed.pop(self.token,None)
            return {'PASS_THROUGH'}
        if event.type=='WINDOW_DEACTIVATE' or (event.value=='PRESS' and event.type in {'ESC','E','R','T'}):
            _pressed.pop(self.token,None)
            if drag_tools.armed.pop(self.token,None):
                for view in context.screen.areas:
                    if view.type=='VIEW_3D':view.tag_redraw()
        if event.type=='LEFTMOUSE' and event.value=='RELEASE' and self.token in _pressed:
            area,tool=_pressed.pop(self.token)
            drag_tools.armed[self.token]=tool
            from .quick_menu import remember
            remember('cw.model',tool)
            area.tag_redraw()
            return {'RUNNING_MODAL'}
        area=next((a for a in context.screen.areas if a.type=='VIEW_3D' and a.x<=event.mouse_x<a.x+a.width and a.y<=event.mouse_y<a.y+a.height),None)
        if not area:
            if _hover.pop(self.token,None) is not None:
                for a in context.screen.areas:a.tag_redraw()
            return {'PASS_THROUGH'}
        region=next((r for r in area.regions if r.type=='WINDOW'),None)
        if not region:return {'PASS_THROUGH'}
        width,height=metrics(context);mx=event.mouse_x-region.x;my=event.mouse_y-region.y
        index=int((region.height-26-my)//height)
        edge=right_edge(area,region)
        if context.mode!='EDIT_MESH':drag_tools.armed.pop(self.token,None)
        if event.type=='ESC' and self.token in drag_tools.armed:
            drag_tools.armed.pop(self.token,None);area.tag_redraw()
            return {'PASS_THROUGH'}
        if mx>=edge or mx<0:return {'PASS_THROUGH'}
        if self.token in drag_tools.armed and event.type=='MOUSEMOVE':
            _pointer[self.token]=(area.as_pointer(),mx,my)
            area.tag_redraw()
        side='RIGHT' if edge-width<=mx<edge else 'LEFT' if 0<=mx<width else ''
        entries=CATEGORIES if side=='RIGHT' else left_tools(context)
        hovered=(side,index) if side and 0<=index<len(entries) else ('',-1)
        if _hover.get(self.token)!=hovered:_hover[self.token]=hovered;area.tag_redraw()
        if not side and event.type=='LEFTMOUSE' and event.value=='CLICK_DRAG' and self.token in drag_tools.armed:
            with context.temp_override(area=area,region=region):
                drag_tools.run(context,drag_tools.armed[self.token])
            return {'RUNNING_MODAL'}
        if hovered[0] and event.type=='LEFTMOUSE' and event.value=='PRESS':
            from . import loop_preview
            preview=loop_preview.active.get(self.token)
            if preview:preview.cancel(context)
            command=entries[index][0]
            if side=='LEFT' and command in {'EXTRUDE','INSET'}:
                token=self.token
                pending=(area,command)
                _pressed[token]=pending
                window=context.window
                def hold():
                    if _pressed.get(token) is not pending:return None
                    _pressed.pop(token,None)
                    if window.workspace.name=='X4D' and area in window.screen.areas:
                        with bpy.context.temp_override(window=window,area=area,region=region):
                            bpy.ops.wm.call_menu(name='CW_MT_extrude_drag' if command=='EXTRUDE' else 'CW_MT_inset_drag')
                    return None
                bpy.app.timers.register(hold,first_interval=.45)
                return {'RUNNING_MODAL'}
            drag_tools.armed.pop(self.token,None)
            try:
                with context.temp_override(area=area,region=region):
                    if side=='RIGHT':bpy.ops.cw.palette('INVOKE_DEFAULT',category=CATEGORIES[index][0])
                    elif entries[index] in TOOLS:bpy.ops.cw.tool(tool=entries[index][0])
                    else:bpy.ops.cw.model('INVOKE_DEFAULT',command=entries[index][0])
            except Exception as exc:self.report({'WARNING'},str(exc))
            return {'RUNNING_MODAL'}
        if event.type=='LEFTMOUSE' and event.value=='PRESS' and context.mode=='OBJECT':
            with context.temp_override(area=area,region=region):
                if 'RUNNING_MODAL' in bpy.ops.cw.field_resize('INVOKE_DEFAULT'):return {'RUNNING_MODAL'}
        return {'PASS_THROUGH'}

def start(window):
    global _enabled,_handle
    _enabled=True
    if _handle is None:_handle=bpy.types.SpaceView3D.draw_handler_add(draw,(),'WINDOW','POST_PIXEL')
    if _running.get(window.as_pointer())!=_generation:
        with bpy.context.temp_override(window=window):bpy.ops.cw.rail('INVOKE_DEFAULT')
def reset_input():
    global _generation
    _generation+=1;_running.clear()
    _hover.clear();_pointer.clear();_pressed.clear();drag_tools.armed.clear();drag_tools.choices.clear()

def stop():
    global _enabled,_handle
    reset_input()
    _enabled=False
    if _handle is not None:bpy.types.SpaceView3D.draw_handler_remove(_handle,'WINDOW');_handle=None
classes=[CW_OT_tool,CW_OT_rail]







