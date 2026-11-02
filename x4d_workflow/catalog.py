"""Creation palette inventory transcribed from the supplied 2027 screenshots.
Rows with no implementation are intentionally disabled, never fake operators.
"""
import bpy
import math
from . import icons
from bpy.props import StringProperty

# key, Chinese, English, icon, color, (label, English, command) entries
CATEGORIES=[('SPLINE', '样条', 'Splines', 'CURVE_BEZCURVE', (0.35, 0.76, 0.91), [('圆弧', 'Arc', 'SPLINE:ARC'), ('圆环', 'Circle', 'SPLINE:CIRCLE'), ('螺旋线', 'Helix', 'SPLINE:HELIX'), ('多边', 'Polygon', 'SPLINE:POLYGON'), ('矩形', 'Rectangle', 'SPLINE:RECTANGLE'), ('五角样条', 'Pentagon', 'SPLINE:PENTAGON'), ('四边', 'Diamond', 'SPLINE:DIAMOND'), ('齿轮', 'Cogwheel', 'SPLINE:COG'), ('花瓣形', 'Flower', 'SPLINE:FLOWER'), ('星形', 'Star', 'SPLINE:STAR'), ('公式', 'Formula', 'EXTRA:FORMULA_SPLINE'), ('轮廓', 'Profile', 'EXTRA:PROFILE'), ('空白样条', 'Empty Spline', 'SPLINE:EMPTY')]), ('MESH', '网格', 'Primitives', 'MESH_CUBE', (0.35, 0.76, 0.91), [('立方体', 'Cube', 'PRIM:CUBE'), ('圆柱体', 'Cylinder', 'PRIM:CYLINDER'), ('平面', 'Plane', 'PRIM:PLANE'), ('圆盘', 'Disc', 'MESH:DISC'), ('多边形', 'Polygon', 'MESH:POLYGON'), ('球体', 'Sphere', 'PRIM:SPHERE'), ('胶囊', 'Capsule', 'EXTRA:CAPSULE'), ('圆锥体', 'Cone', 'PRIM:CONE'), ('人形对象', 'Figure', 'EXTRA:FIGURE'), ('地形', 'Landscape', 'EXTRA:LANDSCAPE'), ('管道', 'Tube', 'EXTRA:TUBE'), ('金字塔', 'Pyramid', 'MESH:PYRAMID'), ('宝石体', 'Platonic', 'MESH:ICOSPHERE'), ('油罐', 'Oil Tank', 'EXTRA:OIL_TANK'), ('圆环体', 'Torus', 'PRIM:TORUS'), ('景观', 'Relief', 'EXTRA:RELIEF'), ('背景', 'Background', 'EXTRA:BACKGROUND'), ('空白多边形', 'Empty Polygon', 'MESH:EMPTY')]), ('TEXT', '文字', 'Text', 'FONT_DATA', (0.35, 0.76, 0.91), [('文本', 'Text', 'TEXT:TEXT'), ('文本样条', 'Text Spline', 'TEXT:SPLINE')]), ('GENERATOR', '生成器', 'Generators', 'MOD_SUBSURF', (0.35, 0.8, 0.43), [('细分曲面', 'Subdivision', 'ACTION:SUBSURF'), ('布料曲面', 'Cloth Surface', 'MOD:SOLIDIFY'), ('挤压', 'Extrude', 'ACTION:EXTRUDE'), ('旋转', 'Lathe', 'ACTION:LATHE'), ('放样', 'Loft', 'EXTRA:LOFT'), ('扫描', 'Sweep', 'ACTION:SWEEP'), ('样条布尔', 'Spline Mask', 'EXTRA:SPLINE_MASK'), ('布尔', 'Boolean', 'ACTION:BOOLEAN'), ('连接', 'Connect', 'MOD:WELD'), ('对称', 'Symmetry', 'MOD:MIRROR'), ('晶格', 'Atom Array', 'MOD:WIREFRAME'), ('阵列', 'Array', 'MOD:ARRAY'), ('减面', 'Polygon Reduction', 'MOD:DECIMATE'), ('LOD', 'Level of Detail', 'EXTRA:LOD'), ('浮雕', 'Relief', 'EXTRA:RELIEF'), ('矢量导入', 'Vector Import', 'IMPORT:SVG'), ('Python 生成器', 'Python Generator', 'EXTRA:PYTHON_GENERATOR')]), ('VOLUME', '体积', 'Volumes', 'VOLUME_DATA', (0.35, 0.8, 0.43), [('体积生成', 'Volume Builder', 'EXTRA:VOLUME_BUILDER'), ('体积网格', 'Volume Mesher', 'EXTRA:VOLUME_MESHER'), ('SDF 平滑', 'SDF Smooth', 'EXTRA:SDF_SMOOTH'), ('雾平滑', 'Fog Smooth', 'EXTRA:FOG_SMOOTH'), ('矢量平滑', 'Vector Smooth', 'EXTRA:VECTOR_SMOOTH')]), ('MOGRAPH', '克隆', 'MoGraph', 'OUTLINER_OB_POINTCLOUD', (0.35, 0.8, 0.43), [('克隆', 'Cloner', 'CREATE:CLONER'), ('矩阵', 'Matrix', 'EXTRA:MATRIX'), ('散布', 'Scatter', 'EXTRA:SCATTER'), ('分裂', 'Fracture', 'EXTRA:FRACTURE'), ('破碎 (Voronoi)', 'Voronoi Fracture', 'EXTRA:VORONOI'), ('追踪对象', 'Tracer', 'EXTRA:TRACER'), ('运动样条', 'MoSpline', 'EXTRA:MOSPLINE'), ('实例', 'Instance', 'INSTANCE:LINKED'), ('运动挤压', 'MoExtrude', 'EXTRA:MOEXTRUDE')]), ('DEFORMER', '变形器', 'Deformers', 'MOD_SIMPLEDEFORM', (0.52, 0.49, 0.88), [('弯曲', 'Bend', 'ACTION:BEND'), ('膨胀', 'Bulge', 'MOD:CAST'), ('扭转', 'Twist', 'ACTION:TWIST'), ('锥化', 'Taper', 'ACTION:TAPER'), ('FFD', 'FFD', 'LATTICE:CREATE'), ('网格', 'Mesh Deform', 'MOD:MESH_DEFORM'), ('置换', 'Displace', 'MOD:DISPLACE'), ('平滑', 'Smooth', 'MOD:SMOOTH'), ('碰撞', 'Collision', 'EXTRA:COLLISION'), ('收缩包裹', 'Shrinkwrap', 'MOD:SHRINKWRAP'), ('修正', 'Correction', 'MOD:CORRECTIVE_SMOOTH'), ('Delta Mush', 'Delta Mush', 'MOD:LAPLACIANSMOOTH'), ('样条', 'Spline', 'MOD:CURVE'), ('公式', 'Formula', 'EXTRA:FORMULA_DEFORM'), ('融解', 'Melt', 'EXTRA:MELT')]), ('EFFECTOR', '修改器', 'Effectors', 'MOD_NOISE', (0.52, 0.49, 0.88), [('简易', 'Plain', 'EFFECTOR:PLAIN'), ('随机', 'Random', 'EFFECTOR:RANDOM'), ('步幅', 'Step', 'EFFECTOR:STEP'), ('延迟', 'Delay', 'EFFECTOR:DELAY'), ('公式', 'Formula', 'EFFECTOR:FORMULA'), ('着色', 'Shader', 'EFFECTOR:SHADER'), ('声音', 'Sound', 'EFFECTOR:SOUND'), ('时间', 'Time', 'EFFECTOR:TIME'), ('目标', 'Target', 'EFFECTOR:TARGET'), ('样条', 'Spline', 'EFFECTOR:SPLINE'), ('Python', 'Python', 'EFFECTOR:PYTHON')]), ('FIELD', '域', 'Fields', 'OUTLINER_OB_FORCE_FIELD', (0.76, 0.52, 0.86), [('线性域', 'Linear Field', 'FIELD:LINEAR'), ('球体域', 'Spherical Field', 'FIELD:SPHERE'), ('盒形域', 'Box Field', 'FIELD:BOX'), ('随机域', 'Random Field', 'FIELD:RANDOM'), ('圆柱体域', 'Cylindrical Field', 'FIELD:CYLINDER'), ('圆锥体域', 'Cone Field', 'FIELD:CONE'), ('胶囊体域', 'Capsule Field', 'FIELD:CAPSULE'), ('圆环体域', 'Torus Field', 'FIELD:TORUS'), ('着色器域', 'Shader Field', 'FIELD:SHADER'), ('声音域', 'Sound Field', 'FIELD:SOUND'), ('公式域', 'Formula Field', 'FIELD:FORMULA'), ('组域', 'Group Field', 'FIELD:GROUP')]), ('LIGHT', '灯光', 'Lights', 'LIGHT', (0.73, 0.78, 0.88), [('灯光', 'Light', 'LIGHT:POINT'), ('聚光灯', 'Spot Light', 'LIGHT:SPOT'), ('目标聚光灯', 'Target Spot', 'LIGHT:TARGET'), ('区域光', 'Area Light', 'LIGHT:AREA'), ('无限光', 'Infinite Light', 'LIGHT:SUN'), ('IES 灯', 'IES Light', 'EXTRA:IES'), ('物理天空', 'Physical Sky', 'WORLD:SKY')])]
BY_KEY={row[0]:row for row in CATEGORIES}

def zh():return bpy.context.preferences.view.language.startswith('zh')
def label(cn,en):return cn if zh() else en

class CW_OT_catalog(bpy.types.Operator):
    bl_idname='cw.catalog';bl_label='Create';bl_options={'REGISTER','UNDO'}
    command:StringProperty()
    def execute(self,context):
        family,value=self.command.split(':',1)
        if context.object and context.object.mode!='OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        if family=='EXTRA':return bpy.ops.cw.extra(kind=value)
        if family=='IMPORT' and value=='SVG':return bpy.ops.cw.import_svg('INVOKE_DEFAULT')
        if family=='PRIM':return bpy.ops.cw.primitive(kind=value)
        if family=='ACTION' and value in {'SUBSURF','BOOLEAN','EXTRUDE','LATHE','SWEEP'}:return bpy.ops.cw.generator(kind=value)
        if family=='ACTION' and value in {'BEND','TWIST','TAPER'}:return bpy.ops.cw.deformer(kind=value)
        if family=='ACTION':return bpy.ops.cw.action(action=value)
        if family in {'CREATE','FIELD','EFFECTOR'}:
            result=bpy.ops.cw.create(kind=value if family=='CREATE' else family)
            if family=='FIELD':context.object.cw.field_type=value
            elif family=='EFFECTOR':
                context.object.cw.effector=value
                if value=='PYTHON':
                    from .procedural_scripts import prepare
                    prepare(context.object)
            return result
        if family=='MOD' and value in {'SOLIDIFY','MIRROR','WIREFRAME','ARRAY','DECIMATE','WELD'}:return bpy.ops.cw.generator(kind=value)
        if family=='MOD':
            if not context.object or context.object.type not in {'MESH','CURVE','FONT'}:
                self.report({'WARNING'},label('请选择网格或曲线','Select a mesh or curve'));return {'CANCELLED'}
            context.object.modifiers.new(value.replace('_',' ').title(),value)
        elif family=='TEXT':
            bpy.ops.object.text_add();context.object.name=label('文本','Text')
            if value=='SPLINE':bpy.ops.object.convert(target='CURVE')
        elif family=='LIGHT':
            bpy.ops.object.light_add(type='SPOT' if value=='TARGET' else value,location=context.scene.cursor.location)
            if value=='TARGET':
                lamp=context.object;target=bpy.data.objects.new('Light Target',None);context.collection.objects.link(target)
                con=lamp.constraints.new('TRACK_TO');con.target=target;con.track_axis='TRACK_NEGATIVE_Z';con.up_axis='UP_Y'
        elif family=='WORLD':
            if not context.scene.world:context.scene.world=bpy.data.worlds.new('Sky')
            w=context.scene.world;w.use_nodes=True;nodes=w.node_tree.nodes
            sky=nodes.new('ShaderNodeTexSky');w.node_tree.links.new(sky.outputs['Color'],nodes.get('Background').inputs['Color'])
        elif family=='INSTANCE':
            if not context.object:return {'CANCELLED'}
            bpy.ops.object.duplicate(linked=True)
        elif family=='MESH':
            if value=='DISC':bpy.ops.mesh.primitive_circle_add(vertices=64,fill_type='NGON')
            elif value=='POLYGON':bpy.ops.mesh.primitive_circle_add(vertices=6,fill_type='NGON')
            elif value=='PYRAMID':bpy.ops.mesh.primitive_cone_add(vertices=4,radius1=1,radius2=0,depth=2,rotation=(0,0,math.pi/4))
            elif value=='ICOSPHERE':bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2)
            else:self.new_mesh(context)
        elif family=='LATTICE':
            target=context.object if context.object and context.object.type=='MESH' else None
            bpy.ops.object.add(type='LATTICE');cage=context.object;cage.name='FFD'
            cage.data.points_u=3;cage.data.points_v=3;cage.data.points_w=3
            if target:
                cage.matrix_world=target.matrix_world.copy();cage.scale=tuple(max(d,.01)*1.05 for d in target.dimensions)
                modifier=target.modifiers.new('FFD','LATTICE');modifier.object=cage
        elif family=='SPLINE':self.spline(context,value)
        return {'FINISHED'}
    def new_mesh(self,context):
        obj=bpy.data.objects.new('Polygon',bpy.data.meshes.new('Polygon'));context.collection.objects.link(obj)
        for o in context.selected_objects:o.select_set(False)
        obj.select_set(True);context.view_layer.objects.active=obj
    def spline(self,context,value):
        data=bpy.data.curves.new(value,'CURVE');data.dimensions='3D';data.resolution_u=16
        points=[];cyclic=True
        if value=='RECTANGLE':points=[(-1,-1,0),(1,-1,0),(1,1,0),(-1,1,0)]
        elif value in {'POLYGON','PENTAGON','DIAMOND'}:
            n={'POLYGON':6,'PENTAGON':5,'DIAMOND':4}[value];points=[(math.cos(i*2*math.pi/n),math.sin(i*2*math.pi/n),0) for i in range(n)]
        elif value in {'STAR','COG','FLOWER'}:
            n=10 if value=='STAR' else 64
            for i in range(n):
                a=i*2*math.pi/n;r=(1 if i%2==0 else .45) if value=='STAR' else (1+.2*math.cos((8 if value=='COG' else 5)*a));points.append((r*math.cos(a),r*math.sin(a),0))
        elif value=='HELIX':
            cyclic=False;points=[(math.cos(i*.15),math.sin(i*.15),i*.02) for i in range(128)]
        elif value in {'ARC','CIRCLE'}:
            cyclic=value=='CIRCLE';points=[(math.cos(i*math.pi/(32 if value=='ARC' else 16)),math.sin(i*math.pi/(32 if value=='ARC' else 16)),0) for i in range(33 if value=='ARC' else 32)]
        if points:
            spline=data.splines.new('POLY');spline.points.add(len(points)-1)
            for p,co in zip(spline.points,points):p.co=(*co,1)
            spline.use_cyclic_u=cyclic
        obj=bpy.data.objects.new(value,data);context.collection.objects.link(obj)
        for o in context.selected_objects:o.select_set(False)
        obj.select_set(True);context.view_layer.objects.active=obj

class CW_OT_palette(bpy.types.Operator):
    bl_idname='cw.palette';bl_label='创建';bl_description='Open the X4D creation palette'
    category:StringProperty(default='MESH')
    @classmethod
    def description(cls,context,properties):
        item=BY_KEY.get(properties.category)
        return label('创建'+item[1]+'：打开对象列表','Create '+item[2]+': open the object palette') if item else label('打开创建列表','Open the creation palette')
    def invoke(self,context,event):return context.window_manager.invoke_popup(self,width=270 if len(BY_KEY[self.category][5])>8 else 190)
    def draw(self,context):
        category=BY_KEY[self.category];l=self.layout
        l.operator_context='EXEC_DEFAULT'
        entries=category[5];cols=2 if len(entries)>8 else 1
        row=l.row();columns=[row.column(align=True) for _ in range(cols)]
        half=math.ceil(len(entries)/cols)
        for i,(cn,en,cmd) in enumerate(entries):
            line=columns[i%cols].row();line.alignment='LEFT'
            if cmd:line.operator('cw.catalog',text=label(cn,en),icon_value=icons.icon_id(icons.key(category[0],en)),emboss=False).command=cmd
            else:
                line.enabled=False;line.label(text=label(cn,en)+' · '+label('待实现','Pending'),icon_value=icons.icon_id(icons.key(category[0],en)))
        if any(not e[2] for e in entries):l.separator();l.label(text=label('灰色项目尚未实现','Disabled items are not implemented'),icon='INFO')
    def execute(self,context):return {'FINISHED'}

class CW_MT_create(bpy.types.Menu):
    bl_idname='CW_MT_create';bl_label='创建'
    def draw(self,context):
        for key,cn,en,icon,color,entries in CATEGORIES:self.layout.operator('cw.palette',text=label(cn,en),icon_value=icons.icon_id(icons.key(key))).category=key

def header(self,context):
    if context.workspace.name!='X4D':return
    row=self.layout.row(align=True)
    row.operator('cw.new_scene',text=label('新建','New'),icon='FILE_NEW')
    row.menu('CW_MT_create',text=label('创建','Create'))
    for key in ['MESH','SPLINE','GENERATOR','MOGRAPH','DEFORMER','FIELD','LIGHT']:
        c=BY_KEY[key];row.operator('cw.palette',text='',icon_value=icons.icon_id(icons.key(key))).category=key
    row.operator('cw.restore',text='',icon='LOOP_BACK')

classes=[CW_OT_catalog,CW_OT_palette,CW_MT_create]








