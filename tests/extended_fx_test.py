import bpy,sys,os,math,wave,struct,json
from mathutils import Vector
root=os.path.dirname(os.path.dirname(__file__));sys.path.insert(0,root)
import x4d_workflow as kit
from x4d_workflow import advanced_fx
kit.register();results=[]
path=os.path.join(root,'artifacts','test-sound.wav')
with wave.open(path,'wb') as f:f.setnchannels(1);f.setsampwidth(2);f.setframerate(8000);f.writeframes(b''.join(struct.pack('<h',int(16000*math.sin(i*.2))) for i in range(8000)))
def clean():
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);advanced_fx.stop()
for kind in ['LINEAR','SPHERE','BOX','RANDOM','CYLINDER','CONE','CAPSULE','TORUS','SHADER','SOUND','FORMULA','GROUP']:
    clean();bpy.ops.cw.catalog(command='FIELD:'+kind);obj=bpy.context.object
    if kind=='SHADER':bpy.ops.cw.new_texture()
    if kind=='SOUND':obj.cw_extra.audio=path
    if kind=='GROUP':
        bpy.ops.cw.catalog(command='FIELD:SPHERE');child=bpy.context.object;obj.cw.fields.add().target=child
    value=advanced_fx.field(obj,Vector((.2,.1,.1)),2,bpy.context.scene)
    assert math.isfinite(value) and 0<=value<=1,(kind,value)
    results.append('FIELD:'+kind)
for kind in ['PLAIN','RANDOM','STEP','DELAY','FORMULA','SHADER','SOUND','TIME','TARGET','SPLINE','PYTHON']:
    clean();bpy.ops.cw.primitive(kind='CUBE');source=bpy.context.object
    bpy.ops.cw.create(kind='CLONER');cloner=bpy.context.object
    bpy.ops.cw.catalog(command='EFFECTOR:'+kind);obj=bpy.context.object
    if kind=='SHADER':bpy.ops.cw.new_texture()
    if kind=='SOUND':obj.cw_extra.audio=path
    if kind=='TARGET':obj.cw_extra.target=source
    if kind=='SPLINE':
        bpy.ops.cw.catalog(command='SPLINE:CIRCLE');curve=bpy.context.object;obj.cw_extra.target=curve
    if kind=='PYTHON':bpy.context.view_layer.objects.active=obj;bpy.ops.cw.run_python()
    cloner.cw.effectors.add().target=obj
    kit.engine.rebuild_all(bpy.context.scene)
    assert not cloner.cw.status,(kind,cloner.cw.status)
    assert len(cloner.data.vertices)==9
    assert all(math.isfinite(v.co.z) for v in cloner.data.vertices)
    results.append('EFFECTOR:'+kind)
# Verify group cycle rejection.
clean();bpy.ops.cw.catalog(command='FIELD:GROUP');group=bpy.context.object;group.cw.fields.add().target=group
try:advanced_fx.field(group,Vector(),0,bpy.context.scene)
except ValueError:pass
else:raise AssertionError('Field cycle accepted')
with open(os.path.join(root,'artifacts','extended-fx-results.json'),'w') as f:json.dump(results,f,indent=2)
print('CW_EXTENDED_FX_OK',len(results))
kit.unregister()
