"""Compare the exact 0.3.1 catalog route with installed 0.4 menu commands."""
import bpy,sys,os,types,zipfile,json
root=os.path.dirname(os.path.dirname(__file__));sys.path.insert(0,root)
import x4d_workflow as kit
kit.register()
commands=[entry[2] for entry in kit.catalog.BY_KEY['GENERATOR'][5] if entry[2]]
records=[]

def source(kind):
    bpy.ops.object.select_all(action='DESELECT');bpy.context.view_layer.objects.active=None
    if kind=='MESH':bpy.ops.mesh.primitive_cube_add()
    elif kind=='CURVE':bpy.ops.curve.primitive_bezier_circle_add()

legacy={}
with zipfile.ZipFile(os.path.join(root,'dist','x4d_workflow-0.3.1.zip')) as z:
    for name in ['catalog','operators']:
        module=types.ModuleType('x4d_workflow.legacy_'+name);module.__package__='x4d_workflow'
        exec(compile(z.read(name+'.py'),'0.3.1/'+name+'.py','exec'),module.__dict__)
        legacy[name]=module
new=[kit.catalog.CW_OT_catalog,kit.operators.CW_OT_action]
old=[legacy['catalog'].CW_OT_catalog,legacy['operators'].CW_OT_action]
for cls in new:bpy.utils.unregister_class(cls)
try:
    for cls in old:bpy.utils.register_class(cls)
    for kind in ['NONE','MESH','CURVE']:
        for command in commands:
            source(kind)
            try:
                result=bpy.ops.cw.catalog(command=command)
                records.append({'version':'0.3.1','source':kind,'command':command,'result':list(result)})
            except Exception as exc:records.append({'version':'0.3.1','source':kind,'command':command,'error':str(exc)})
finally:
    for cls in reversed(old):bpy.utils.unregister_class(cls)
    for cls in new:bpy.utils.register_class(cls)
# Exercise menu command dispatch in both 3D View and Properties contexts.
for area_type in ['VIEW_3D','PROPERTIES']:
    area=next(a for a in bpy.context.screen.areas if a.type==area_type)
    region=next(r for r in area.regions if r.type=='WINDOW')
    for kind in ['NONE','MESH','CURVE']:
        for command in commands:
            source(kind)
            with bpy.context.temp_override(area=area,region=region):result=bpy.ops.cw.catalog(command=command)
            assert 'FINISHED' in result,(area_type,kind,command,result)
            assert bpy.context.object.cw.kind=='GENERATOR',(area_type,kind,command)
            records.append({'version':'0.4.0','area':area_type,'source':kind,'command':command,'result':list(result)})
old_errors=[r for r in records if r['version']=='0.3.1' and 'error' in r]
with open(os.path.join(root,'artifacts','generator-menu-regression.json'),'w',encoding='utf-8') as f:json.dump(records,f,ensure_ascii=False,indent=2)
assert old_errors,'Old error must be reproduced'
print('CW_MENU_REGRESSION_OK',json.dumps({'old_errors_reproduced':len(old_errors),'new_routes_passed':sum(r['version']=='0.4.0' for r in records)}))
kit.unregister()
