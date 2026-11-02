"""WAV amplitude and explicitly activated Python procedural programs."""
import bpy,math,wave,os,struct
from bpy.props import StringProperty
from mathutils import Vector
_PROGRAMS={}
_AUDIO_LEVELS={}
GENERATOR_TEMPLATE='''# Click Run after editing. This text never runs automatically on file load.\ndef generate(frame, source):\n    return [(-1,-1,0),(1,-1,0),(1,1,0),(-1,1,0),(0,0,2)], [(0,1,4),(1,2,4),(2,3,4),(3,0,4),(3,2,1,0)]\n'''
EFFECTOR_TEMPLATE='''import math\ndef effect(index, position, frame):\n    return 0.5 + 0.5*math.sin(index*0.5+frame*0.1)\n'''

def wav_level(path,frame,fps):
    path=bpy.path.abspath(path)
    if not path or not os.path.isfile(path):return 0.0
    key=(path,os.path.getmtime(path),frame,fps)
    if key in _AUDIO_LEVELS:return _AUDIO_LEVELS[key]
    with wave.open(path,'rb') as stream:
        width=stream.getsampwidth();channels=stream.getnchannels();rate=stream.getframerate()
        offset=max(0,int(frame*rate/max(fps,1)))
        if offset>=stream.getnframes():return 0.0
        stream.setpos(offset);data=stream.readframes(max(1,int(rate/max(fps,1))))
    if width not in {1,2,3,4}:raise ValueError('Use PCM WAV audio')
    total=0.;count=0
    for i in range(0,len(data)-width+1,width*channels):
        raw=data[i:i+width]
        value=(raw[0]-128)/128 if width==1 else int.from_bytes(raw,'little',signed=True)/(2**(8*width-1))
        total+=value*value;count+=1
    value=min(1,math.sqrt(total/max(count,1)))
    if len(_AUDIO_LEVELS)>1024:_AUDIO_LEVELS.clear()
    _AUDIO_LEVELS[key]=value
    return value

def prepare(obj):
    s=obj.cw_extra
    if s.script is None:
        s.script=bpy.data.texts.new('CW Generator.py' if obj.cw.kind=='EXTRA' else 'CW Effector.py')
        s.script.write(GENERATOR_TEMPLATE if obj.cw.kind=='EXTRA' else EFFECTOR_TEMPLATE)

def compile_program(obj):
    prepare(obj);text=obj.cw_extra.script.as_string()
    scope={'bpy':bpy,'math':math,'Vector':Vector,'__name__':'cw_user_script'}
    exec(compile(text,obj.cw_extra.script.name,'exec'),scope)
    name='generate' if obj.cw.kind=='EXTRA' else 'effect'
    if not callable(scope.get(name)):raise ValueError('Script must define '+name+'(...)')
    _PROGRAMS[obj.as_pointer()]=(hash(text),scope[name])

def program(obj):
    value=_PROGRAMS.get(obj.as_pointer());text=obj.cw_extra.script
    return value[1] if value and text and value[0]==hash(text.as_string()) else None

def run_generator(obj,scene):
    from . import extras
    fn=program(obj)
    if fn is None:extras.set_status(obj,'编辑脚本后点击运行 / Click Run to activate this script');return
    vertices,faces=fn(scene.frame_current,obj.cw_extra.source)
    if len(vertices)>1000000:raise ValueError('Python generator exceeds one million vertices')
    extras.mesh_write(obj,[tuple(v) for v in vertices],[tuple(face) for face in faces])

class CW_OT_run_python(bpy.types.Operator):
    bl_idname='cw.run_python';bl_label='运行 Python / Run Python';bl_options={'REGISTER','UNDO'}
    def execute(self,context):
        obj=context.object
        if obj is None:return {'CANCELLED'}
        try:
            compile_program(obj)
            from . import extras,engine
            extras._CACHE.clear();extras.update(context.scene);engine.rebuild_all(context.scene)
            return {'FINISHED'}
        except Exception as exc:obj.cw.status=str(exc);self.report({'ERROR'},str(exc));return {'CANCELLED'}

class CW_OT_edit_python(bpy.types.Operator):
    bl_idname='cw.edit_python';bl_label='编辑脚本 / Edit Script'
    def execute(self,context):
        obj=context.object
        if obj is None:return {'CANCELLED'}
        prepare(obj)
        window=context.window
        # An explicit editor button opens a separate window, preserving the X4D workspace.
        if bpy.app.background:return {'CANCELLED'}
        before=set(context.window_manager.windows);bpy.ops.wm.window_new()
        new=next((w for w in context.window_manager.windows if w not in before),None)
        if new:
            area=max(new.screen.areas,key=lambda a:a.width*a.height);area.type='TEXT_EDITOR';area.spaces.active.text=obj.cw_extra.script
        return {'FINISHED'}

def stop():_PROGRAMS.clear()
classes=[CW_OT_run_python,CW_OT_edit_python]

