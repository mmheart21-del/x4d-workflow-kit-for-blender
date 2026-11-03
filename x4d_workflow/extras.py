"""Extended procedural geometry. Geometry stays editable through CWExtra controls."""
import bpy,bmesh,math,random
from mathutils import Vector
from bpy.app.handlers import persistent
from . import extra_properties as props
from .expressions import evaluate
_CACHE={};_OUTPUT={}

def set_status(obj,text):
    if obj.cw.status!=text:obj.cw.status=text

def mesh_write(obj,vertices,faces,edges=()):
    if obj.data.users>1:obj.data=obj.data.copy()
    obj.data.clear_geometry();obj.data.from_pydata(vertices,edges,faces);obj.data.update()

def sphere_mesh(center,scale,n=16):
    v=[];f=[]
    for j in range(n//2+1):
        a=-math.pi/2+j*math.pi/(n//2)
        for i in range(n):
            b=i*math.tau/n;v.append(tuple(center[k]+scale[k]*p for k,p in enumerate((math.cos(a)*math.cos(b),math.cos(a)*math.sin(b),math.sin(a)))))
    for j in range(n//2):
        for i in range(n):a=j*n+i;b=j*n+(i+1)%n;f.append((a,b,b+n,a+n))
    return v,f

def terrain(s):
    n=s.resolution;vertices=[];faces=[]
    image=s.image
    pixels=list(image.pixels) if image and image.has_data else None
    for y in range(n+1):
        for x in range(n+1):
            u=x/n;v=y/n
            if s.kind=='RELIEF' and pixels:
                ix=min(image.size[0]-1,int(u*(image.size[0]-1)));iy=min(image.size[1]-1,int(v*(image.size[1]-1)));j=4*(iy*image.size[0]+ix)
                z=sum(pixels[j:j+3])/3*s.size[2]
            else:
                z=sum(math.sin(u*math.tau*2**j+s.seed*.17)*math.cos(v*math.tau*2**j+s.seed*.29)/(2**j) for j in range(4))*s.size[2]*.35
                if s.kind=='RELIEF':z=0
            vertices.append(((u-.5)*s.size[0],(v-.5)*s.size[1],z))
    for y in range(n):
        for x in range(n):a=y*(n+1)+x;faces.append((a,a+1,a+n+2,a+n+1))
    return vertices,faces

def tube(s):
    n=s.resolution;v=[];f=[]
    inner=min(s.inner,s.radius*.99)
    for z,r in [(-s.height/2,s.radius),(s.height/2,s.radius),(-s.height/2,inner),(s.height/2,inner)]:
        v.extend((r*math.cos(i*math.tau/n),r*math.sin(i*math.tau/n),z) for i in range(n))
    for i in range(n):
        j=(i+1)%n;f.extend([(i,j,n+j,n+i),(2*n+j,2*n+i,3*n+i,3*n+j),(n+i,n+j,3*n+j,3*n+i),(j,i,2*n+i,2*n+j)])
    return v,f

def capsule(s):
    n=s.resolution;m=max(4,n//2);v=[];f=[]
    cap=s.radius if s.kind=='CAPSULE' else min(s.radius*.25,s.height*.25)
    straight=max(0,s.height-2*cap)
    for j in range(m+2):
        # Duplicate the equator so the cylinder has two distinct end rings.
        a=-math.pi/2+min(j,m//2)*math.pi/m if j<=m//2 else (j-m//2-1)*math.pi/m
        if j>m//2:a=min(a,math.pi/2)
        z=math.sin(a)*cap+(-straight/2 if j<=m//2 else straight/2)
        r=s.radius*math.cos(a)
        v.extend((r*math.cos(i*math.tau/n),r*math.sin(i*math.tau/n),z) for i in range(n))
    rows=len(v)//n
    for j in range(rows-1):
        for i in range(n):a=j*n+i;b=j*n+(i+1)%n;f.append((a,b,b+n,a+n))
    return v,f

def figure(s):
    v=[];f=[];scale=s.height/3.5
    parts=[((0,0,3.12),(.33,.3,.4)),((0,0,2.35),(.55,.27,.64)),((0,0,1.68),(.43,.3,.35))]
    for sign in [-1,1]:
        parts.extend([((sign*.76,0,2.47),(.22,.22,.47)),((sign*1.03,0,1.95),(.19,.19,.4)),((sign*1.11,0,1.51),(.2,.15,.2)),((sign*.26,0,1.08),(.23,.23,.6)),((sign*.26,-.08,.43),(.18,.2,.38)),((sign*.26,-.2,.12),(.2,.36,.13))])
    for center,radii in parts:
        vv,ff=sphere_mesh(tuple(x*scale for x in center),tuple(x*scale for x in radii),max(8,s.resolution//2));off=len(v);v+=vv;f += [tuple(i+off for i in face) for face in ff]
    return v,f

def curve_points(obj):
    if not obj or obj.type!='CURVE':return []
    result=[]
    for spline in obj.data.splines:
        points=spline.bezier_points if spline.type=='BEZIER' else spline.points
        result.extend(obj.matrix_world @ p.co.to_3d() for p in points)
    return result

def resample(points,count,closed=False):
    if len(points)<2:return points
    pts=[Vector(p) for p in points]+([Vector(points[0])] if closed else [])
    lengths=[0.]
    for a,b in zip(pts,pts[1:]):lengths.append(lengths[-1]+(b-a).length)
    if lengths[-1]<1e-9:return [pts[0].copy() for _ in range(count)]
    result=[];segment=0
    for i in range(count):
        t=lengths[-1]*i/(count if closed else max(1,count-1))
        while segment<len(pts)-2 and lengths[segment+1]<t:segment+=1
        factor=(t-lengths[segment])/max(1e-9,lengths[segment+1]-lengths[segment]);result.append(pts[segment].lerp(pts[segment+1],factor))
    return result

def curve_write(obj,points,closed=False):
    obj.data.splines.clear()
    if not points:return
    spline=obj.data.splines.new('POLY');spline.points.add(len(points)-1)
    for p,co in zip(spline.points,points):p.co=(*co,1)
    spline.use_cyclic_u=closed

def loft(obj):
    curves=[link.target for link in obj.cw.inputs if link.target and link.target.type=='CURVE']
    if len(curves)<2:curves=[c for c in obj.children if c.type=='CURVE']
    if len(curves)<2:set_status(obj,'需要至少两个截面样条 / Add at least two cross-section curves');return
    n=obj.cw_extra.resolution;v=[];f=[]
    for curve in curves:v += [tuple(obj.matrix_world.inverted_safe() @ p) for p in resample(curve_points(curve),n,True)]
    for j in range(len(curves)-1):
        for i in range(n):a=j*n+i;b=j*n+(i+1)%n;f.append((a,b,b+n,a+n))
    mesh_write(obj,v,f);set_status(obj,'')

def source_fingerprint(source):
    if not source:return None
    if source.type=='MESH' and source.mode=='EDIT':source.update_from_editmode()
    if source.type=='MESH':return (source.as_pointer(),hash(tuple(tuple(v.co) for v in source.data.vertices)),len(source.data.polygons),tuple(x for row in source.matrix_world for x in row))
    if source.type=='CURVE':return (source.as_pointer(),tuple(tuple(p) for p in curve_points(source)))
    return (source.as_pointer(),tuple(source.location))

def signature(obj,scene):
    s=obj.cw_extra
    animated=s.kind in {'FORMULA_SPLINE','MOSPLINE','TRACER','FORMULA_DEFORM','MELT','LOD','PYTHON_GENERATOR','FRACTURE','VORONOI','MOEXTRUDE'}
    return (s.kind,scene.frame_current if animated else 0,s.count,s.resolution,s.radius,s.height,s.inner,s.amount,s.speed,tuple(s.size),s.seed,s.iterations,s.voxel,s.threshold,s.formula,s.x_formula,s.y_formula,s.z_formula,s.start,s.end,s.operation,source_fingerprint(s.source),source_fingerprint(s.target),s.image.as_pointer() if s.image else 0,tuple((link.target.as_pointer(),source_fingerprint(link.target)) for link in obj.cw.inputs if link.target))

@persistent
def update(scene,*args):
    if props._busy:return
    props._busy=True
    try:
        for obj in list(scene.objects):
            if obj.cw.kind!='EXTRA' or obj.cw_extra.kind in {'FORMULA_DEFORM','MELT','COLLISION'}:continue
            try:
                sig=signature(obj,scene)
                if _CACHE.get(obj.as_pointer())==sig:continue
                build(obj,scene);_CACHE[obj.as_pointer()]=sig
            except Exception as exc:set_status(obj,str(exc))
        from . import deformation_stack
        deformation_stack.update(scene)
    finally:props._busy=False

def stop():
    from . import deformation_stack
    deformation_stack.stop();_CACHE.clear();_OUTPUT.clear()

def build(obj,scene):
    from . import extended_geometry
    s=obj.cw_extra;k=s.kind
    set_status(obj,'')
    if k=='IES':
        from .ies import configure
        configure(obj);return
    if k in {'CAPSULE','OIL_TANK'}:mesh_write(obj,*capsule(s))
    elif k=='TUBE':mesh_write(obj,*tube(s))
    elif k=='FIGURE':mesh_write(obj,*figure(s))
    elif k in {'LANDSCAPE','RELIEF'}:
        mesh_write(obj,*terrain(s))
        if k=='RELIEF' and not s.image:set_status(obj,'请选择高度图 / Select a height image')
    elif k=='FORMULA_SPLINE':
        points=[]
        for i in range(s.resolution+1):
            t=s.start+(s.end-s.start)*i/s.resolution;env={'t':t,'i':i,'frame':scene.frame_current,'seed':s.seed}
            points.append((evaluate(s.x_formula,**env),evaluate(s.y_formula,**env),evaluate(s.z_formula,**env)))
        curve_write(obj,points)
    elif k=='PROFILE':
        curve_write(obj,[(-s.radius,0,0),(-s.radius,0,s.height),(0,0,s.height),(0,0,s.inner),(s.radius,0,s.inner),(s.radius,0,0)],True)
    elif k=='LOFT':loft(obj)
    elif k=='MOSPLINE':
        if s.source and s.source.type=='CURVE':points=[obj.matrix_world.inverted_safe() @ p for p in resample(curve_points(s.source),s.resolution+1)]
        else:points=[Vector((s.radius*math.sin(i*.25+scene.frame_current*s.speed*.03),0,i*s.height/s.resolution)) for i in range(s.resolution+1)]
        curve_write(obj,points)
    elif k=='TRACER':
        points=[obj.matrix_world.inverted_safe() @ link.target.matrix_world.translation for link in obj.cw.inputs if link.target]
        if not points and s.source:
            # Evaluate keyed object transforms at the current frame without changing the playhead.
            history=obj.get('cw_trace_points',[]);frame=scene.frame_current
            if obj.get('cw_trace_frame',frame)>frame:history=[]
            if obj.get('cw_trace_frame')!=frame:history=list(history)+list(obj.matrix_world.inverted_safe() @ s.source.matrix_world.translation);obj['cw_trace_points']=history[-s.resolution*3:];obj['cw_trace_frame']=frame
            points=[Vector(obj.get('cw_trace_points',[])[i:i+3]) for i in range(0,len(obj.get('cw_trace_points',[])),3)]
        curve_write(obj,points)
    else:extended_geometry.build(obj,scene)
    if obj.type=='MESH' and k in {'CAPSULE','OIL_TANK','TUBE','FIGURE','LANDSCAPE'}:
        for polygon in obj.data.polygons:polygon.use_smooth=True



