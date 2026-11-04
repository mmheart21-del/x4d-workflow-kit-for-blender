import bpy
from .catalog import label as ui_label

PARAM_LABELS={'inner_range':('内部范围','Inner Range'),'source':('源对象','Source'),'mode':('模式','Mode'),'count':('数量','Count'),'spacing':('间距','Spacing'),'radius':('半径','Radius'),'surface':('分布表面','Surface'),'seed':('随机种子','Seed'),'effector':('效果器类型','Effector'),'strength':('强度','Strength'),'move':('位移','Position'),'rotate':('旋转','Rotation'),'scale':('缩放变化','Scale Change'),'field_type':('域类型','Field Type'),'dimensions':('维度','Dimensions'),'resolution_u':('细分','Resolution'),'extrude':('挤压深度','Extrude'),'bevel_depth':('倒角半径','Bevel'),'body':('文字','Text'),'size':('大小','Size'),'type':('类型','Type'),'color':('颜色','Color'),'energy':('强度','Power')}
def parameter(layout,data,name):
    from .catalog import label
    cn,en=PARAM_LABELS.get(name,(name,name))
    layout.prop(data,name,text=label(cn,en))

LABELS={
'CLONER':('克隆','Cloner'),'FIELD':('域','Field'),'EFFECTOR':('效果器','Effector'),
'SUBSURF':('细分曲面','Subdivision'),'BOOLEAN':('布尔','Boolean'),'EXTRUDE':('挤压','Extrude'),'LATHE':('旋转','Lathe'),'SWEEP':('扫描','Sweep'),
'BEND':('弯曲','Bend'),'TWIST':('扭曲','Twist'),'TAPER':('锥化','Taper'),'GROUP':('空对象分组','Group'),
'EDITABLE':('转为可编辑','Make Editable'),'STATE':('当前状态转对象','Current State to Object'),'MATERIAL':('新建并分配材质','Assign New Material'),
'SELECTION':('保存点选择集','Store Point Selection'),'SMOOTH':('平滑着色','Smooth'),'TARGET':('目标约束','Target Constraint')}
def text(key):
    pair=LABELS.get(key,(key,key));return pair[0] if bpy.context.preferences.view.language.startswith('zh') else pair[1]
def action(layout,key):
    op=layout.operator('cw.action',text=text(key));op.action=key

class CW_PT_create(bpy.types.Panel):
    bl_label=ui_label('创建','X4D · Create');bl_idname='CW_PT_create';bl_space_type='VIEW_3D';bl_region_type='UI';bl_category='X4D'
    def draw(self,context):
        l=self.layout
        row=l.row();row.operator('cw.workspace',text='X4D');row.operator('cw.restore',text='Blender')
        l.label(text=ui_label('对象','Objects'),icon='OUTLINER_OB_MESH')
        grid=l.grid_flow(columns=3,align=True)
        for op,label in [('cube',ui_label('立方体','Cube')),('uv_sphere',ui_label('球','Sphere')),('cylinder',ui_label('圆柱','Cylinder')),('cone',ui_label('圆锥','Cone')),('plane',ui_label('平面','Plane')),('torus',ui_label('圆环','Torus'))]:grid.operator('cw.primitive',text=label).kind={'cube':'CUBE','uv_sphere':'SPHERE','cylinder':'CYLINDER','cone':'CONE','plane':'PLANE','torus':'TORUS'}[op]
        row=l.row(align=True)
        for kind in ['CLONER','EFFECTOR','FIELD']:row.operator('cw.create',text=text(kind)).kind=kind
        if context.object:
            for title,items in [(ui_label('生成器','Generators'),['SUBSURF','BOOLEAN','EXTRUDE','LATHE','SWEEP']),(ui_label('变形器','Deformers'),['BEND','TWIST','TAPER']),(ui_label('对象与标签','Objects & Tags'),['GROUP','EDITABLE','STATE','MATERIAL','SELECTION','SMOOTH','TARGET'])]:
                box=l.box();box.label(text=title);grid=box.grid_flow(columns=2,align=True)
                for key in items:action(grid,key)

class CW_PT_attributes(bpy.types.Panel):
    bl_label=ui_label('属性','Attributes');bl_idname='CW_PT_attributes';bl_space_type='VIEW_3D';bl_region_type='UI';bl_category='X4D'
    @classmethod
    def poll(cls,context):return context.object is not None
    def draw(self,context):
        from .catalog import label
        l=self.layout;obj=context.object;s=obj.cw
        l.prop(obj,'name',text=ui_label('名称','Name'))
        l.prop(obj,'cw_position',text=ui_label('位置','Position'))
        l.prop(obj,'cw_rotation',text=ui_label('旋转','Rotation'))
        l.prop(obj,'cw_scale',text=ui_label('缩放','Scale'))
        if s.kind=='EXTRA':
            from .extra_ui import draw
            draw(l,obj,self.links)
        elif s.kind=='GENERATOR':
            l.label(text=s.generator,icon='MODIFIER')
            for child in obj.children:
                l.label(text=child.name,icon='OBJECT_DATA')
                if child.cw_primitive.kind:
                    l.prop(child,'cw_size',text=label('源对象尺寸','Source Size'))
            draw_modifiers(l,obj)
            if obj.type=='CURVE':
                l.prop(obj.data,'extrude',text=label('挤压','Extrude'))
                l.prop(obj.data,'bevel_depth',text=label('半径','Radius'))
        elif obj.cw_primitive.kind:
            l.prop(obj,'cw_size',text=ui_label('尺寸','Size'));l.prop(obj.cw_primitive,'subdivisions' if obj.cw_primitive.kind=='CUBE' else 'segments',text=ui_label('分段','Segments'))
            if obj.cw_primitive.kind=='TORUS':l.prop(obj.cw_primitive,'tube')
        if s.kind=='CLONER':
            for prop in ['mode','count','spacing','radius'] :parameter(l,s,prop)
            if s.mode=='SURFACE':parameter(l,s,'surface');parameter(l,s,'seed')
            from .object_lists import draw_sources
            draw_sources(l,obj);self.links(l,s,'effectors')
        elif s.kind=='EFFECTOR':
            for prop in ['effector','strength','move','rotate','scale','seed']:parameter(l,s,prop)
            self.links(l,s,'fields')
        elif s.kind=='DEFORMER':
            l.prop(s,'deform_target',text=ui_label('目标对象','Target'))
            l.prop(s,'deform_axis',text=ui_label('轴向','Axis'))
            l.prop(s,'deform_factor' if s.deform_type=='TAPER' else 'deform_angle',text=ui_label('强度','Strength') if s.deform_type=='TAPER' else ui_label('角度','Angle'))
        elif s.kind=='FIELD':
            for prop in ['field_type','radius','inner_range','seed']:parameter(l,s,prop)
        if s.kind in {'EFFECTOR','FIELD'}:
            from .extra_ui import draw
            draw(l,obj,self.links)
        if s.kind not in {'GENERATOR','EXTRA'} and obj.modifiers:draw_modifiers(l,obj)
        if s.status:l.label(text=s.status,icon='ERROR')
    def links(self,l,s,name):
        box=l.box();box.label(text=ui_label('域','Fields') if name=='fields' else ui_label('输入对象','Inputs') if name=='inputs' else ui_label('其他克隆源','Additional Sources') if name=='sources' else ui_label('效果器','Effectors'))
        for i,item in enumerate(getattr(s,name)):
            row=box.row(align=True);row.prop(item,'target',text='')
            for a,icon in [('UP','TRIA_UP'),('DOWN','TRIA_DOWN'),('REMOVE','X')]:
                op=row.operator('cw.list_edit',text='',icon=icon);op.action=a;op.collection=name;op.index=i
            if name=='fields':
                box.prop(item,'mode');box.prop(item,'invert');row=box.row();row.prop(item,'low');row.prop(item,'high')
        op=box.operator('cw.list_edit',text=ui_label('添加','Add'),icon='ADD');op.collection=name

classes=[CW_PT_create,CW_PT_attributes]


def draw_modifiers(layout,obj):
    from .catalog import label
    props={'SUBSURF':['levels','render_levels'],'SIMPLE_DEFORM':['deform_method','deform_axis','angle','factor'],'BOOLEAN':['operation','object'],'ARRAY':['count','relative_offset_displace'],'MIRROR':['use_axis','use_clip','use_mirror_merge'],'SOLIDIFY':['thickness','offset'],'WIREFRAME':['thickness'],'DECIMATE':['decimate_type','ratio'],'WELD':['merge_threshold'],'SCREW':['axis','angle','steps','render_steps'],'DISPLACE':['strength','mid_level','texture'],'CAST':['cast_type','factor','radius'],'SMOOTH':['factor','iterations'],'SHRINKWRAP':['target','wrap_method','offset'],'MESH_DEFORM':['object','precision'],'CURVE':['object','deform_axis'],'LATTICE':['object','strength'],'CORRECTIVE_SMOOTH':['factor','iterations','smooth_type'],'LAPLACIANSMOOTH':['lambda_factor','lambda_border','iterations']}
    for modifier in obj.modifiers:
        if modifier.name=='CW Instances':continue
        box=layout.box();row=box.row(align=True)
        row.prop(modifier,'show_viewport',text='');row.prop(modifier,'name',text='')
        for name in props.get(modifier.type,[]):
            if modifier.type=='SIMPLE_DEFORM' and ((name=='angle' and modifier.deform_method in {'TAPER','STRETCH'}) or (name=='factor' and modifier.deform_method in {'TWIST','BEND'})):continue
            if name in modifier.bl_rna.properties:box.prop(modifier,name)
        if modifier.type=='MESH_DEFORM' and modifier.object:
            op=box.operator('object.meshdeform_bind',text=label('解除绑定' if modifier.is_bound else '绑定','Unbind' if modifier.is_bound else 'Bind'));op.modifier=modifier.name

class CWManagerDrawing:
    links=CW_PT_attributes.links
    bl_label=ui_label('属性管理器','X4D Attributes')
    bl_idname='CW_PT_manager'
    bl_options={'HIDE_HEADER'}
    bl_order=-100
    bl_space_type='PROPERTIES'
    bl_region_type='WINDOW'
    bl_context='constraint'
    bl_category=''
    def draw(self,context):
        from .catalog import label
        l=self.layout;obj=context.object
        l.prop(obj,'name',text=label('名称','Name'))
        l.prop(context.window_manager,'cw_attribute_tab',expand=True)
        tab=context.window_manager.cw_attribute_tab
        if tab=='COORD':
            l.prop(obj,'cw_position',text=label('位置','Position'));l.prop(obj,'cw_rotation',text=label('旋转','Rotation'));l.prop(obj,'cw_scale',text=label('缩放','Scale'))
        elif tab=='BASIC':
            l.prop(obj,'parent',text=label('父级','Parent'));l.prop(obj,'hide_viewport',text=label('编辑器隐藏','Hide in Viewport'));l.prop(obj,'hide_render',text=label('渲染隐藏','Hide in Render'));l.prop(obj,'color',text=label('显示颜色','Display Color'))
        elif tab=='TAGS':
            from .object_lists import draw_tags
            draw_tags(l,obj)
        else:
            self.draw_settings(l,obj)
    def draw_settings(self,l,obj):
        from .catalog import label
        s=obj.cw
        if s.kind=='EXTRA':
            from .extra_ui import draw
            draw(l,obj,self.links)
        elif s.kind=='GENERATOR':
            l.label(text=s.generator,icon='MODIFIER')
            for child in obj.children:
                l.label(text=child.name,icon='OBJECT_DATA')
                if child.cw_primitive.kind:
                    l.prop(child,'cw_size',text=label('源对象尺寸','Source Size'))
            draw_modifiers(l,obj)
            if obj.type=='CURVE':
                l.prop(obj.data,'extrude',text=label('挤压','Extrude'))
                l.prop(obj.data,'bevel_depth',text=label('半径','Radius'))
        elif obj.cw_primitive.kind:
            l.prop(obj,'cw_size',text=ui_label('尺寸','Size'));l.prop(obj.cw_primitive,'subdivisions' if obj.cw_primitive.kind=='CUBE' else 'segments',text=ui_label('分段','Segments'))
            if obj.cw_primitive.kind=='TORUS':l.prop(obj.cw_primitive,'tube')
        elif s.kind=='CLONER':
            for p in ['mode','count','spacing','radius']:parameter(l,s,p)
            if s.mode=='SURFACE':parameter(l,s,'surface');parameter(l,s,'seed')
            from .object_lists import draw_sources
            draw_sources(l,obj);self.links(l,s,'effectors')
        elif s.kind=='EFFECTOR':
            for p in ['effector','strength','move','rotate','scale','seed']:parameter(l,s,p)
            self.links(l,s,'fields')
        elif s.kind=='DEFORMER':
            l.prop(s,'deform_target',text=ui_label('目标对象','Target'))
            l.prop(s,'deform_axis',text=ui_label('轴向','Axis'))
            l.prop(s,'deform_factor' if s.deform_type=='TAPER' else 'deform_angle',text=ui_label('强度','Strength') if s.deform_type=='TAPER' else ui_label('角度','Angle'))
        elif s.kind=='FIELD':
            for p in ['field_type','radius','inner_range','seed']:parameter(l,s,p)
        elif obj.type=='CURVE':
            for p in ['dimensions','resolution_u','extrude','bevel_depth']:parameter(l,obj.data,p)
        elif obj.type=='FONT':
            for p in ['body','size','extrude','bevel_depth']:parameter(l,obj.data,p)
        elif obj.type=='LATTICE':
            for p in ['points_u','points_v','points_w']:l.prop(obj.data,p)
            l.operator('object.editmode_toggle',text=label('编辑控制点','Edit Control Points'))
        elif obj.type=='LIGHT':
            for p in ['type','color','energy']:parameter(l,obj.data,p)
        else:l.label(text=label('原生对象：使用坐标和标签页','Native object: use Coordinates and Tags'))
        if s.kind in {'EFFECTOR','FIELD'}:
            from .extra_ui import draw
            draw(l,obj,self.links)
        if s.kind not in {'GENERATOR','EXTRA'} and obj.modifiers:draw_modifiers(l,obj)
        if s.status:l.label(text=s.status,icon='ERROR')
    @classmethod
    def poll(cls,context):return context.object is not None and context.workspace.name=='X4D'
class CW_PT_manager(CWManagerDrawing,bpy.types.Panel):
    pass
classes.append(CW_PT_manager)




_ATTRIBUTE_ZH=[('OBJECT','对象','对象参数'),('COORD','坐标','坐标参数'),('BASIC','基本','基本属性'),('TAGS','标签','材质和标签')]
_ATTRIBUTE_EN=[('OBJECT','Object','Object parameters'),('COORD','Coord.','Coordinates'),('BASIC','Basic','Basic properties'),('TAGS','Tags','Materials and tags')]
def attribute_tabs(self,context):
    return _ATTRIBUTE_ZH if bpy.context.preferences.view.language.startswith('zh') else _ATTRIBUTE_EN











