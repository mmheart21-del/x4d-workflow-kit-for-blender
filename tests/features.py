import sys,os,math
sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))
import bpy
import x4d_workflow as kit
from x4d_workflow.core import field_weight,blend_weight,positions
kit.register()
assert field_weight('SPHERE',(0,0,0))==1
assert field_weight('SPHERE',(2,0,0))==0
assert field_weight('BOX',(.5,0,0))==.5
assert field_weight('LINEAR',(0,0,0))==.5
assert field_weight('RANDOM',(0,0,0),seed=4,index=5)==field_weight('RANDOM',(1,1,1),seed=4,index=5)
assert blend_weight(.8,.5,'SUBTRACT')==.8-.5
assert len(positions('GRID',(2,3,4),(1,1,1),2))==24
for kind in ['CUBE','SPHERE','CYLINDER','CONE','PLANE','TORUS']:
    bpy.ops.cw.primitive(kind=kind)
    obj=bpy.context.object
    assert len(obj.data.vertices)>0,kind
    obj.cw_primitive.size=(4,6,8)
    assert len(obj.data.vertices)>0
    obj.cw_position=(1,2,3)
    assert tuple(obj.location)==(1,-3,2)
    obj.cw_scale=(1,2,3)
    assert tuple(obj.scale)==(1,3,2)
bpy.ops.cw.workspace()
assert bpy.data.workspaces.get('X4D') is not None
assert bpy.data.workspaces.get('Layout') is not None
before=len(bpy.data.workspaces)
bpy.ops.cw.workspace();assert len(bpy.data.workspaces)==before
bpy.ops.cw.restore()
kit.unregister()
print('CW_FEATURE_TEST_OK')

