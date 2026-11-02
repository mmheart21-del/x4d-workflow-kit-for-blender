"""Extended fields and ordered effector behaviors."""
import math
from mathutils import Vector
from .core import field_weight,blend_weight
from .expressions import evaluate
from .procedural_scripts import wav_level,program
_DELAY={}
_SPLINES={}
def begin():_SPLINES.clear()
def clamp(v):return max(0.,min(1.,float(v)))

def field(field,world,index,scene,stack=()):
    if field.as_pointer() in stack:raise ValueError('域循环引用 / Field cycle')
    if len(stack)>16:raise ValueError('Field group nesting exceeds 16')
    kind=field.cw.field_type;s=field.cw_extra;r=max(field.cw.radius,1e-6)
    p=field.matrix_world.inverted_safe()@world;x,y,z=p;time=scene.frame_current/max(1,scene.render.fps)
    if kind in {'LINEAR','SPHERE','BOX','RANDOM'}:return field_weight(kind,p,r,seed=field.cw.seed,index=index)
    if kind=='CYLINDER':return clamp(min(1-math.hypot(x,y)/r,1-abs(z)/(s.height/2)))
    if kind=='CONE':
        height=max(s.height,1e-6);level=(z+height/2)/height
        return clamp(min(1-abs(z)/(height/2),1-math.hypot(x,y)/max(r*(1-level),1e-6))) if 0<=level<=1 else 0
    if kind=='CAPSULE':
        dz=max(0,abs(z)-max(0,s.height/2-r));return clamp(1-math.sqrt(x*x+y*y+dz*dz)/r)
    if kind=='TORUS':return clamp(1-math.hypot(math.hypot(x,y)-r,z)/max(s.inner,1e-6))
    if kind=='FORMULA':return clamp(evaluate(s.formula,x=x,y=y,z=z,t=time,frame=scene.frame_current,i=index,seed=s.seed))
    if kind=='SHADER':
        if s.texture:return clamp(s.texture.evaluate(p)[3])
        raise ValueError('请选择纹理 / Select a texture')
    if kind=='SOUND':return clamp(wav_level(s.audio,scene.frame_current,scene.render.fps)*s.amount)
    if kind=='GROUP':return layers(field.cw.fields,world,index,scene,stack+(field.as_pointer(),))
    raise ValueError('Unknown field: '+kind)

def layers(values,world,index,scene,stack=()):
    result=None
    for layer in values:
        if not layer.target:continue
        if layer.target.cw.kind!='FIELD':raise ValueError('域列表中存在非域对象 / Non-field object in field list')
        value=field(layer.target,world,index,scene,stack)
        value=clamp((value-layer.low)/max(1e-6,layer.high-layer.low))
        if layer.invert:value=1-value
        result=value if result is None else blend_weight(result,value,layer.mode)
    return 0. if result is None else result

def factors(effector,point,index,total,scene):
    kind=effector.cw.effector;s=effector.cw_extra;time=scene.frame_current/max(1,scene.render.fps)
    if kind=='FORMULA':value=evaluate(s.formula,x=point.x,y=point.y,z=point.z,t=time,frame=scene.frame_current,i=index,n=total,seed=s.seed)
    elif kind=='SHADER':
        if not s.texture:raise ValueError('请选择效果器纹理 / Select an effector texture')
        value=s.texture.evaluate(point)[3]
    elif kind=='SOUND':value=wav_level(s.audio,scene.frame_current,scene.render.fps)*s.amount
    elif kind=='TIME':value=time*s.speed
    elif kind=='PYTHON':
        fn=program(effector)
        if fn is None:raise ValueError('点击运行以启用 Python 效果器 / Click Run to activate Python effector')
        value=float(fn(index,tuple(point),scene.frame_current))
    elif kind in {'TARGET','SPLINE','DELAY'}:value=0
    else:value=1
    if not math.isfinite(value):raise ValueError('Non-finite effector result')
    return [value]*9

def post(cloner,effector,index,total,p,rotation,scale,weight,scene):
    kind=effector.cw.effector;s=effector.cw_extra
    if kind=='TARGET':
        if not s.target:raise ValueError('请选择目标对象 / Select a target')
        target=cloner.matrix_world.inverted_safe()@s.target.matrix_world.translation
        direction=target-p
        if direction.length>1e-8:
            angle=direction.to_track_quat('Z','Y').to_euler()
            rotation=Vector(rotation).lerp(Vector(angle),clamp(weight*s.amount))
        p=p.lerp(target,clamp(weight*s.amount))
    elif kind=='SPLINE':
        from .extras import curve_points,resample
        if not s.target or s.target.type!='CURVE':raise ValueError('请选择样条 / Select a spline')
        key=(s.target.as_pointer(),total)
        if key not in _SPLINES:_SPLINES[key]=resample(curve_points(s.target),max(2,total))
        points=_SPLINES[key]
        if points:p=p.lerp(cloner.matrix_world.inverted_safe()@points[min(index,len(points)-1)],clamp(weight))
    elif kind=='DELAY':
        key=(cloner.as_pointer(),effector.as_pointer());frame=scene.frame_current
        state=_DELAY.get(key)
        if not state or frame<state['frame'] or frame>state['frame']+1:state={'frame':frame,'previous':{},'current':{}};_DELAY[key]=state
        elif frame>state['frame']:state['previous']=state['current'];state['current']={};state['frame']=frame
        previous=state['previous'].get(index)
        if previous is not None:p=Vector(previous).lerp(p,1-clamp(s.amount*weight))
        state['current'][index]=tuple(p)
    return p,rotation,scale

def stop():_DELAY.clear()

