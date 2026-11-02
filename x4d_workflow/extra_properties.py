"""Shared persistent controls for extended geometry, fields and effectors."""
import bpy
from bpy.props import *
_busy=False

def changed(self,context):
    if _busy or context is None:return
    from . import extras,engine
    extras._CACHE.clear()
    extras.update(context.scene)
    engine.rebuild_all(context.scene)

class CWExtra(bpy.types.PropertyGroup):
    kind:StringProperty()
    operation:EnumProperty(name='运算 / Operation',items=[(v,v,'') for v in ['UNION','DIFFERENCE','INTERSECT']],default='UNION',update=changed)
    count:IntProperty(name='数量 / Count',default=12,min=1,max=32,update=changed)
    resolution:IntProperty(name='分辨率 / Resolution',default=24,min=4,max=128,update=changed)
    radius:FloatProperty(name='半径 / Radius',default=1,min=.001,unit='LENGTH',update=changed)
    height:FloatProperty(name='高度 / Height',default=3,min=.001,unit='LENGTH',update=changed)
    inner:FloatProperty(name='内半径 / Inner Radius',default=.6,min=.001,unit='LENGTH',update=changed)
    amount:FloatProperty(name='强度 / Amount',default=.5,update=changed)
    speed:FloatProperty(name='速度 / Speed',default=1,update=changed)
    size:FloatVectorProperty(name='尺寸 / Size',size=3,default=(10,10,2),min=.001,unit='LENGTH',update=changed)
    seed:IntProperty(name='随机种子 / Seed',default=42,update=changed)
    iterations:IntProperty(name='迭代 / Iterations',default=3,min=1,max=50,update=changed)
    voxel:FloatProperty(name='体素尺寸 / Voxel Size',default=.15,min=.005,unit='LENGTH',update=changed)
    threshold:FloatProperty(name='阈值 / Threshold',default=.1,min=.001,max=1,update=changed)
    formula:StringProperty(name='公式 / Formula',default='sin(i*0.5+t)',update=changed)
    x_formula:StringProperty(name='X(t)',default='cos(t)',update=changed)
    y_formula:StringProperty(name='Y(t)',default='sin(t)',update=changed)
    z_formula:StringProperty(name='Z(t)',default='t/6.283185',update=changed)
    start:FloatProperty(name='起点 / Start',default=0,update=changed)
    end:FloatProperty(name='终点 / End',default=6.283185,update=changed)
    source:PointerProperty(name='源对象 / Source',type=bpy.types.Object,update=changed)
    target:PointerProperty(name='目标 / Target',type=bpy.types.Object,update=changed)
    image:PointerProperty(name='图像 / Image',type=bpy.types.Image,update=changed)
    texture:PointerProperty(name='纹理 / Texture',type=bpy.types.Texture,update=changed)
    script:PointerProperty(name='脚本 / Script',type=bpy.types.Text)
    audio:StringProperty(name='WAV 文件 / WAV File',subtype='FILE_PATH',update=changed)
    ies:StringProperty(name='IES 文件 / IES File',subtype='FILE_PATH',update=changed)
    base_mesh:PointerProperty(type=bpy.types.Mesh)
classes=[CWExtra]



