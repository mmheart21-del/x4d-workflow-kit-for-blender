import bpy,sys,os,json
root=os.path.dirname(os.path.dirname(__file__));sys.path.insert(0,root)
import x4d_workflow as kit
kit.register();report=[]
for category,cn,en,icon,color,entries in kit.catalog.CATEGORIES:
    for cn,en,command in entries:
        assert command,(category,en)
        if command=='IMPORT:SVG':continue
        bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);kit.extras.stop();kit.advanced_fx.stop()
        bpy.ops.cw.primitive(kind='CUBE')
        result=bpy.ops.cw.catalog(command=command)
        assert 'FINISHED' in result,(category,en,result)
        obj=bpy.context.object
        status=obj.cw.status if obj else ''
        assert not any(word in status for word in ['Unknown','Traceback','NoneType','attribute','enum','not found']),(category,en,status)
        report.append({'category':category,'name':cn,'command':command,'status':status,'object_type':obj.type if obj else None})
# Operator invocation from component mode must exit edit mode cleanly.
bpy.ops.cw.primitive(kind='CUBE');bpy.ops.object.mode_set(mode='EDIT')
assert 'FINISHED' in bpy.ops.cw.catalog(command='EXTRA:CAPSULE')
assert bpy.context.object.mode=='OBJECT'
# Matrix creation with an active prototype must still emit cube glyph instances.
bpy.ops.cw.primitive(kind='CUBE');bpy.ops.cw.extra(kind='MATRIX');obj=bpy.context.object
bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
assert any(n.bl_idname=='GeometryNodeMeshCube' for n in obj.modifiers[0].node_group.nodes)
with open(os.path.join(root,'artifacts','all-menu-routes.json'),'w',encoding='utf-8') as f:json.dump(report,f,ensure_ascii=False,indent=2)
print('CW_ALL_MENU_ROUTES_OK',len(report))
kit.unregister()
