"""Mouse-driven preview for quad loops and rings in the edit viewport."""
import bpy
import bmesh
import gpu
from gpu_extras.batch import batch_for_shader
from bpy_extras.view3d_utils import region_2d_to_origin_3d, region_2d_to_vector_3d, location_3d_to_region_2d
from mathutils.bvhtree import BVHTree
from mathutils.geometry import intersect_point_line

active={}

def walk(seed,ring):
    found={seed}
    if ring:
        pending=[(seed,face) for face in seed.link_faces if not face.hide]
        while pending:
            edge,face=pending.pop()
            if len(face.edges)!=4:continue
            opposite=next(e for e in face.edges if not set(e.verts)&set(edge.verts))
            if opposite in found or opposite.hide:continue
            found.add(opposite)
            pending.extend((opposite,f) for f in opposite.link_faces if f!=face and not f.hide)
    else:
        for vertex in seed.verts:
            edge=seed
            while len(vertex.link_edges)==4:
                adjacent={e for face in edge.link_faces for e in face.edges}
                options=[e for e in vertex.link_edges if e not in adjacent and not e.hide]
                if len(options)!=1 or options[0] in found:break
                edge=options[0];found.add(edge);vertex=edge.other_vert(vertex)
    return found

def draw(context):
    op=active.get(context.window.as_pointer())
    if not op or context.region!=op.region or not op.points:return
    shader=gpu.shader.from_builtin('POLYLINE_UNIFORM_COLOR')
    shader.bind()
    shader.uniform_float('viewportSize',(context.region.width,context.region.height))
    shader.uniform_float('lineWidth',3)
    shader.uniform_float('color',(.24,.83,1,1))
    vertices=[]
    for a,b in zip(op.points[::2],op.points[1::2]):
        pa=location_3d_to_region_2d(context.region,context.region_data,a)
        pb=location_3d_to_region_2d(context.region,context.region_data,b)
        if pa is not None and pb is not None:vertices.extend((pa,pb))
    if vertices:batch_for_shader(shader,'LINES',{'pos':vertices}).draw(shader)

class CW_OT_loop_preview(bpy.types.Operator):
    bl_idname='cw.loop_preview'
    bl_label='Loop or Ring Preview'
    bl_options={'INTERNAL'}
    ring:bpy.props.BoolProperty()

    def invoke(self,context,event):
        if context.mode!='EDIT_MESH' or not context.region_data:return {'CANCELLED'}
        self.area=context.area;self.region=context.region;self.key=context.window.as_pointer()
        if self.key in active:return {'CANCELLED'}
        self.meshes=[]
        for obj in context.objects_in_mode_unique_data:
            bm=bmesh.from_edit_mesh(obj.data)
            bm.faces.ensure_lookup_table()
            self.meshes.append((obj,bm,BVHTree.FromBMesh(bm)))
        self.points=[];self.target=None
        active[self.key]=self
        self.update_preview(context,event)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def update_preview(self,context,event):
        xy=(event.mouse_x-self.region.x,event.mouse_y-self.region.y)
        origin=region_2d_to_origin_3d(self.region,context.region_data,xy)
        direction=region_2d_to_vector_3d(self.region,context.region_data,xy)
        closest=None
        self.points=[];self.target=None
        for obj,bm,tree in self.meshes:
            inverse=obj.matrix_world.inverted_safe()
            hit,_,index,_=tree.ray_cast(inverse@origin,inverse.to_3x3()@direction)
            if hit is None:continue
            face=bm.faces[index]
            if face.hide:continue
            distance=(obj.matrix_world@hit-origin).length_squared
            if closest is not None and closest<=distance:continue
            closest=distance
            def edge_distance(edge):
                a,b=(v.co for v in edge.verts)
                _,fraction=intersect_point_line(hit,a,b)
                return (hit-a-(b-a)*min(1,max(0,fraction))).length_squared
            seed=min(face.edges,key=edge_distance)
            edges=walk(seed,self.ring)
            faces={f for e in walk(seed,True) for f in e.link_faces if not f.hide}
            mode=context.tool_settings.mesh_select_mode
            if mode[2]:edges={e for f in faces for e in f.edges}
            self.points=[obj.matrix_world@v.co for e in edges for v in e.verts]
            self.target=obj,bm,edges,faces
        self.area.tag_redraw()

    def cancel(self,context):
        if active.get(self.key)==self:active.pop(self.key,None)
        self.area.tag_redraw()

    def modal(self,context,event):
        if self.key not in active or context.mode!='EDIT_MESH' or context.area!=self.area:
            self.cancel(context);return {'CANCELLED'}
        if event.type in {'ESC','RIGHTMOUSE','WINDOW_DEACTIVATE'}:
            self.cancel(context);return {'CANCELLED'}
        if event.value=='PRESS':
            if event.type=='LEFTMOUSE':
                from .rail import metrics,right_edge
                x=event.mouse_x-self.region.x;y=event.mouse_y-self.region.y
                width,_=metrics(context)
                if not (width<=x<right_edge(self.area,self.region)-width and 0<=y<self.region.height):
                    self.cancel(context)
                    return {'CANCELLED','PASS_THROUGH'}
            elif event.type not in {'RET','NUMPAD_ENTER','LEFT_SHIFT','RIGHT_SHIFT','LEFT_CTRL','RIGHT_CTRL','MIDDLEMOUSE','WHEELUPMOUSE','WHEELDOWNMOUSE'}:
                self.cancel(context)
                return {'CANCELLED','PASS_THROUGH'}
        if event.type in {'MOUSEMOVE','INBETWEEN_MOUSEMOVE'}:
            self.update_preview(context,event)
        if event.value=='PRESS' and event.type in {'LEFTMOUSE','RET','NUMPAD_ENTER'} and self.target:
            if not event.shift and not event.ctrl:
                bpy.ops.mesh.select_all(action='DESELECT')
            obj,bm,edges,faces=self.target
            mode=context.tool_settings.mesh_select_mode
            elements=faces if mode[2] else edges if mode[1] else {v for e in edges for v in e.verts}
            for element in elements:element.select_set(not event.ctrl)
            bm.select_flush_mode()
            bmesh.update_edit_mesh(obj.data,loop_triangles=False,destructive=False)
            bpy.ops.ed.undo_push(message='X4D Loop Selection')
            return {'RUNNING_MODAL'}
        if event.type in {'MIDDLEMOUSE','WHEELUPMOUSE','WHEELDOWNMOUSE','TIMER'}:return {'PASS_THROUGH'}
        return {'RUNNING_MODAL'}

