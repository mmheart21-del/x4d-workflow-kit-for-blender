import bpy,sys,os,bmesh
sys.path.insert(0,os.getcwd())
import x4d_workflow as kit
kit.register();bpy.ops.cw.workspace()
area=next(a for a in bpy.context.screen.areas if a.type=='VIEW_3D');region=next(r for r in area.regions if r.type=='WINDOW')
def mesh(vertices,faces,mode='FACE'):
 if bpy.context.object and bpy.context.object.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
 for o in list(bpy.context.scene.objects):bpy.data.objects.remove(o,do_unlink=True)
 data=bpy.data.meshes.new('Test');data.from_pydata(vertices,[],faces);o=bpy.data.objects.new('Test',data);bpy.context.collection.objects.link(o);o.select_set(True);bpy.context.view_layer.objects.active=o
 bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_mode(type=mode);bpy.ops.mesh.select_all(action='SELECT');return bmesh.from_edit_mesh(data)
def run(command):return kit.modeling.dispatch(bpy.context,command,False)
with bpy.context.temp_override(area=area,region=region):
 bm=mesh([(0,0,0),(1,0,0),(1,1,0),(0,1,0)],[(0,1,2,3)])
 run('SUBDIVIDE');assert len(bm.verts)==9 and len(bm.faces)==4
 run('FLIP_NORMALS');bm.normal_update();assert all(f.normal.z<0 for f in bm.faces)
 run('FLIP_NORMALS');bm.normal_update();assert all(f.normal.z>0 for f in bm.faces)
 bm=mesh([(0,0,0),(1,0,0),(1,1,0),(0,1,0)],[(0,1,2,3)],'VERT')
 bpy.ops.mesh.select_all(action='DESELECT');bm.verts.ensure_lookup_table()
 for i in (0,2):bm.verts[i].select_set(True);bm.select_history.add(bm.verts[i])
 run('CONNECT');assert len(bm.faces)==2
 bm=mesh([(0,0,0),(0,0,0),(1,0,0)],[],'VERT');run('OPTIMIZE');assert len(bm.verts)==2
 bm=mesh([(0,0,0),(2,0,0)],[],'VERT');run('WELD');assert len(bm.verts)==1 and abs(list(bm.verts)[0].co.x-1)<1e-6
 bm=mesh([(0,0,0),(1,0,0),(1,1,0),(0,1,0)],[(0,1,2,3)]);run('DELETE');assert len(bm.faces)==0
 # Two open loops, bridge creates four walls.
 bm=mesh([(0,0,0),(1,0,0),(1,1,0),(0,1,0),(0,0,1),(1,0,1),(1,1,1),(0,1,1)],[(0,1,2,3),(4,5,6,7)],'EDGE')
 run('BRIDGE');assert len(bm.faces)==6
 # Loop and ring commands use the installed Blender's capability branch.
 bpy.ops.mesh.select_all(action='DESELECT');bm.edges.ensure_lookup_table();bm.edges[0].select_set(True)
 run('LOOP_SELECT');assert sum(e.select for e in bm.edges)>=1
 run('RING_SELECT');assert sum(e.select for e in bm.edges)>=1
 bpy.ops.object.mode_set(mode='OBJECT')
 a=bpy.data.materials.new('A');b=bpy.data.materials.new('B');c=bpy.data.materials.new('C');o=bpy.context.object;o.data.materials.append(a);o.data.materials.append(b)
 bpy.context.window_manager.cw_material=c
 assert kit.material_dock.highlighted(bpy.context.window)=={'A','B'}
 o.select_set(False);assert not kit.material_dock.highlighted(bpy.context.window)
 o.select_set(True);o.data.materials.clear();assert not kit.material_dock.highlighted(bpy.context.window)
 bpy.context.view_layer.objects.active=None;assert not kit.material_dock.highlighted(bpy.context.window)
 assert bpy.context.window_manager.cw_material==c
 assert kit.modeling.SEQUENCES[('U','A')]=='ALIGN_NORMALS'
 assert kit.modeling.SEQUENCES[('K','K')]=='KNIFE'
print('X4D_MODELING_GEOMETRY_AND_HIGHLIGHT_OK')
kit.unregister()

