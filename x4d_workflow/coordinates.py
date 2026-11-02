import bpy
from bpy.props import FloatVectorProperty

def get_position(self):
    v=self.location;return (v.x,v.z,-v.y)
def set_position(self,value):
    self.location=(value[0],-value[2],value[1])
def get_rotation(self):
    v=self.rotation_euler;return (v.x,v.z,-v.y)
def set_rotation(self,value):
    self.rotation_euler=(value[0],-value[2],value[1])
def get_scale(self):
    v=self.scale;return (v.x,v.z,v.y)
def set_scale(self,value):
    self.scale=(value[0],value[2],value[1])
def get_size(self):
    v=self.cw_primitive.size;return (v[0],v[2],v[1])
def set_size(self,value):self.cw_primitive.size=(value[0],value[2],value[1])
def register():
    bpy.types.Object.cw_size=FloatVectorProperty(name='Size XYZ (X4D)',size=3,get=get_size,set=set_size,unit='LENGTH',min=.001)
    bpy.types.Object.cw_position=FloatVectorProperty(name='Position XYZ (X4D)',size=3,get=get_position,set=set_position,subtype='TRANSLATION',unit='LENGTH')
    bpy.types.Object.cw_rotation=FloatVectorProperty(name='Rotation (X4D XYZ)',size=3,get=get_rotation,set=set_rotation,subtype='EULER')
    bpy.types.Object.cw_scale=FloatVectorProperty(name='Scale XYZ (X4D)',size=3,get=get_scale,set=set_scale)
def unregister():
    for name in ['cw_position','cw_rotation','cw_scale','cw_size']:delattr(bpy.types.Object,name)


