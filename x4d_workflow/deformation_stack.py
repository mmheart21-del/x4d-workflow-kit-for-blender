"""Evaluate controller stacks from one persistent rest mesh, avoiding repeated deformation."""
import bpy
from mathutils.bvhtree import BVHTree
from .expressions import evaluate
_STACKS={}

def update(scene):
    groups={}
    for obj in scene.objects:
        if obj.cw.kind=='EXTRA' and obj.cw_extra.kind in {'FORMULA_DEFORM','MELT','COLLISION'}:
            source=obj.cw_extra.source
            if source and source.type=='MESH':groups.setdefault(source.as_pointer(),(source,[]))[1].append(obj)
            else:obj.cw.status='请选择需要变形的网格 / Select a mesh target'
    for key,state in list(_STACKS.items()):
        if key not in groups:
            try:
                target=state['target'];base=state['base']
                if len(target.data.vertices)==len(base.vertices):target.data.vertices.foreach_set('co',[x for v in base.vertices for x in v.co]);target.data.update()
            except ReferenceError:pass
            del _STACKS[key]
    for key,(target,controllers) in groups.items():
        current=tuple(tuple(v.co) for v in target.data.vertices);state=_STACKS.get(key)
        if state is None:
            base=controllers[0].cw_extra.base_mesh
            if base is None or len(base.vertices)!=len(current):base=target.data.copy()
            state={'target':target,'base':base,'last':current};_STACKS[key]=state
        elif current!=state['last'] or len(state['base'].vertices)!=len(current):state['base']=target.data.copy()
        base=state['base'];points=[v.co.copy() for v in base.vertices]
        for controller in controllers:
            s=controller.cw_extra
            if s.base_mesh!=base:s.base_mesh=base
            low=min((p.z for p in points),default=0);high=max((p.z for p in points),default=1)
            bvh=None
            if s.kind=='COLLISION':
                if not s.target or s.target.type!='MESH' or s.target==target:controller.cw.status='请选择其他碰撞网格 / Select another collision mesh';continue
                bvh=BVHTree.FromPolygons([s.target.matrix_world@v.co for v in s.target.data.vertices],[tuple(p.vertices) for p in s.target.data.polygons])
            output=[]
            try:
                for i,value in enumerate(points):
                    p=value.copy()
                    if s.kind=='FORMULA_DEFORM':p.z+=s.amount*evaluate(s.formula,x=p.x,y=p.y,z=p.z,t=scene.frame_current/max(1,scene.render.fps),frame=scene.frame_current,i=i,seed=s.seed)
                    elif s.kind=='MELT':
                        a=max(0,min(1,s.amount));level=(p.z-low)/max(1e-6,high-low);p.x*=1+a*(1-level);p.y*=1+a*(1-level);p.z=low+(p.z-low)*(1-a)
                    elif bvh:
                        world=target.matrix_world@p;hit,normal,index,distance=bvh.find_nearest(world)
                        if hit is not None and (world-hit).dot(normal)<s.amount*.01:p=target.matrix_world.inverted_safe()@(hit+normal*s.amount*.01)
                    output.append(p)
                points=output
                if controller.cw.status:controller.cw.status=''
            except Exception as exc:controller.cw.status=str(exc)
        result=tuple(tuple(p) for p in points)
        if current!=result:target.data.vertices.foreach_set('co',[x for p in points for x in p]);target.data.update()
        state['last']=result

def stop():_STACKS.clear()
