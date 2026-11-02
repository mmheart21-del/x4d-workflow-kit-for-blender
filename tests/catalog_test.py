import bpy,sys,os,json
root=os.path.dirname(os.path.dirname(__file__));sys.path.insert(0,root)
import x4d_workflow
from x4d_workflow.catalog import CATEGORIES
x4d_workflow.register()
icons={i.identifier for i in bpy.types.UILayout.bl_rna.functions['operator'].parameters['icon'].enum_items}
results=[]
for key,cn,en,icon,color,entries in CATEGORIES:
    assert icon in icons,icon
    for cn,en,command in entries:
        if not command or command.startswith(('ACTION:','MOD:','INSTANCE:')):continue
        result=bpy.ops.cw.catalog(command=command)
        assert 'FINISHED' in result,(command,result)
        results.append(command)
# Native modifier helpers require an active mesh.
for command in [e[2] for c in CATEGORIES for e in c[5] if e[2] and e[2].startswith('MOD:')]:
    bpy.ops.mesh.primitive_cube_add()
    result=bpy.ops.cw.catalog(command=command)
    assert 'FINISHED' in result,command
    assert len(bpy.context.object.modifiers)==1,command
    results.append(command)
with open(os.path.join(root,'artifacts','catalog-test.json'),'w',encoding='utf-8') as f:json.dump({'commands':results,'count':len(results)},f,indent=2)
x4d_workflow.unregister()
print('CW_CATALOG_OK',len(results))
