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
    operation:EnumProperty(name='Operation',items=[(v,v,'') for v in ['UNION','DIFFERENCE','INTERSECT']],default='UNION',update=changed)
    count:IntProperty(name='Count',default=12,min=1,max=32,update=changed)
    resolution:IntProperty(name='Resolution',default=24,min=4,max=128,update=changed)
    radius:FloatProperty(name='Radius',default=1,min=.001,unit='LENGTH',update=changed)
    height:FloatProperty(name='Height',default=3,min=.001,unit='LENGTH',update=changed)
    inner:FloatProperty(name='Inner Radius',default=.6,min=.001,unit='LENGTH',update=changed)
    amount:FloatProperty(name='Amount',default=.5,update=changed)
    speed:FloatProperty(name='Speed',default=1,update=changed)
    size:FloatVectorProperty(name='Size',size=3,default=(10,10,2),min=.001,unit='LENGTH',update=changed)
    seed:IntProperty(name='Seed',default=42,update=changed)
    iterations:IntProperty(name='Iterations',default=3,min=1,max=50,update=changed)
    voxel:FloatProperty(name='Voxel Size',default=.15,min=.005,unit='LENGTH',update=changed)
    threshold:FloatProperty(name='Threshold',default=.1,min=.001,max=1,update=changed)
    formula:StringProperty(name='Formula',default='sin(i*0.5+t)',update=changed)
    x_formula:StringProperty(name='X(t)',default='cos(t)',update=changed)
    y_formula:StringProperty(name='Y(t)',default='sin(t)',update=changed)
    z_formula:StringProperty(name='Z(t)',default='t/6.283185',update=changed)
    start:FloatProperty(name='Start',default=0,update=changed)
    end:FloatProperty(name='End',default=6.283185,update=changed)
    source:PointerProperty(name='Source',type=bpy.types.Object,update=changed)
    target:PointerProperty(name='Target',type=bpy.types.Object,update=changed)
    image:PointerProperty(name='Image',type=bpy.types.Image,update=changed)
    texture:PointerProperty(name='Texture',type=bpy.types.Texture,update=changed)
    script:PointerProperty(name='Script',type=bpy.types.Text)
    audio:StringProperty(name='WAV File',subtype='FILE_PATH',update=changed)
    ies:StringProperty(name='IES File',subtype='FILE_PATH',update=changed)
    base_mesh:PointerProperty(type=bpy.types.Mesh)
classes=[CWExtra]



