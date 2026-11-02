import bpy, bmesh, math
from bpy.props import StringProperty, IntProperty, FloatProperty, FloatVectorProperty, PointerProperty

def rebuild(self,context):
    obj=self.id_data
    if not self.kind or obj.type!='MESH':return
    bm=bmesh.new()
    sx,sy,sz=self.size
    n=self.segments
    if self.kind=='CUBE':
        bmesh.ops.create_cube(bm,size=1)
        if self.subdivisions>1:bmesh.ops.subdivide_edges(bm,edges=list(bm.edges),cuts=self.subdivisions-1,use_grid_fill=True)
        for v in bm.verts:v.co.x*=sx;v.co.y*=sy;v.co.z*=sz
    elif self.kind=='SPHERE':
        bmesh.ops.create_uvsphere(bm,u_segments=n,v_segments=max(4,n//2),radius=1)
        for v in bm.verts:v.co.x*=sx/2;v.co.y*=sy/2;v.co.z*=sz/2
    elif self.kind in {'CYLINDER','CONE'}:
        bmesh.ops.create_cone(bm,cap_ends=True,cap_tris=False,segments=n,radius1=sx/2,radius2=0 if self.kind=='CONE' else sx/2,depth=sz)
        for v in bm.verts:v.co.y*=sy/max(sx,.0001)
    elif self.kind=='PLANE':
        verts=[bm.verts.new(p) for p in [(-sx/2,-sy/2,0),(sx/2,-sy/2,0),(sx/2,sy/2,0),(-sx/2,sy/2,0)]];bm.faces.new(verts)
    elif self.kind=='TORUS':
        rows=[]
        for i in range(n):
            a=2*math.pi*i/n;row=[]
            for j in range(max(4,n//2)):
                b=2*math.pi*j/max(4,n//2);r=sx/2+self.tube*math.cos(b)
                row.append(bm.verts.new((r*math.cos(a),r*math.sin(a),self.tube*math.sin(b))))
            rows.append(row)
        for i in range(n):
            for j in range(len(rows[0])):bm.faces.new((rows[i][j],rows[(i+1)%n][j],rows[(i+1)%n][(j+1)%len(rows[0])],rows[i][(j+1)%len(rows[0])]))
    bm.to_mesh(obj.data);bm.free();obj.data.update()

class CWPrimitive(bpy.types.PropertyGroup):
    kind:StringProperty()
    size:FloatVectorProperty(name='Size / 尺寸 (Blender XYZ)',size=3,default=(2,2,2),unit='LENGTH',min=.001,update=rebuild)
    subdivisions:IntProperty(name='分段 / Segments',default=1,min=1,max=128,update=rebuild)
    segments:IntProperty(name='Segments / 分段',default=32,min=4,max=256,update=rebuild)
    tube:FloatProperty(name='Tube / 管半径',default=.25,min=.001,update=rebuild)

class CW_OT_primitive(bpy.types.Operator):
    bl_idname='cw.primitive';bl_label='参数基础体 / Parametric Primitive';bl_options={'REGISTER','UNDO'}
    kind:StringProperty(default='CUBE')
    def execute(self,context):
        obj=bpy.data.objects.new(self.kind,bpy.data.meshes.new(self.kind));context.collection.objects.link(obj)
        obj.cw_primitive.kind=self.kind;rebuild(obj.cw_primitive,context)
        for selected in context.selected_objects:selected.select_set(False)
        obj.select_set(True);context.view_layer.objects.active=obj
        return {'FINISHED'}
classes=[CWPrimitive,CW_OT_primitive]
def register_properties():bpy.types.Object.cw_primitive=PointerProperty(type=CWPrimitive)
def unregister_properties():del bpy.types.Object.cw_primitive


