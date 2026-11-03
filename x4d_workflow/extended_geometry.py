import bpy,bmesh,math,random
from mathutils import Vector,Euler
from mathutils.bvhtree import BVHTree
from . import extras
from .expressions import evaluate

def raw_mesh(source,obj):
    if not source or source.type!='MESH':return [],[],[]
    if source.mode=='EDIT':source.update_from_editmode()
    matrix=obj.matrix_world.inverted_safe() @ source.matrix_world
    return [tuple(matrix@v.co) for v in source.data.vertices],[tuple(p.vertices) for p in source.data.polygons],[tuple(e.vertices) for e in source.data.edges]

def input_objects(obj,types=None):
    values=[link.target for link in obj.cw.inputs if link.target and link.target!=obj]
    if obj.cw_extra.source and obj.cw_extra.source not in values:values.insert(0,obj.cw_extra.source)
    values += [child for child in obj.children if child not in values]
    return [value for value in values if types is None or value.type in types]

def volume_graph(obj,kind):
    s=obj.cw_extra
    modifier=next((m for m in obj.modifiers if m.name=='CW Volume'),None)
    if modifier is None:
        tree=bpy.data.node_groups.new('CW Volume','GeometryNodeTree')
        tree.interface.new_socket(name='Geometry',in_out='INPUT',socket_type='NodeSocketGeometry');tree.interface.new_socket(name='Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
        inp=tree.nodes.new('NodeGroupInput');out=tree.nodes.new('NodeGroupOutput')
        vol=tree.nodes.new('GeometryNodeMeshToVolume');vol.name='Volume Builder'
        tree.links.new(inp.outputs['Geometry'],vol.inputs['Mesh'])
        if kind in {'VOLUME_MESHER','SDF_SMOOTH'}:
            mesh=tree.nodes.new('GeometryNodeVolumeToMesh');mesh.name='Volume Mesher'
            tree.links.new(vol.outputs['Volume'],mesh.inputs['Volume']);tree.links.new(mesh.outputs['Mesh'],out.inputs['Geometry'])
        else:tree.links.new(vol.outputs['Volume'],out.inputs['Geometry'])
        modifier=obj.modifiers.new('CW Volume','NODES');modifier.node_group=tree
        if kind=='SDF_SMOOTH':obj.modifiers.new('SDF Surface Smooth','SMOOTH')
    tree=modifier.node_group
    for n in tree.nodes:
        if n.bl_idname in {'GeometryNodeMeshToVolume','GeometryNodeVolumeToMesh'}:
            if hasattr(n,'resolution_mode'):n.resolution_mode='VOXEL_SIZE'
            elif 'Resolution Mode' in n.inputs:
                try:n.inputs['Resolution Mode'].default_value='Size'
                except TypeError:n.inputs['Resolution Mode'].default_value='Voxel Size'
            if 'Voxel Size' in n.inputs:n.inputs['Voxel Size'].default_value=s.voxel
            if 'Threshold' in n.inputs:n.inputs['Threshold'].default_value=s.threshold
    for m in obj.modifiers:
        if m.type=='SMOOTH':m.iterations=s.iterations;m.factor=s.amount


def smooth_vectors(obj):
    source=obj.cw_extra.source;s=obj.cw_extra
    if not source or source.type!='MESH':extras.set_status(obj,'请选择具有 velocity 向量属性的网格 / Select a vector mesh');return
    mesh=source.data;attribute=mesh.attributes.get('velocity') or mesh.attributes.get('cw_velocity')
    if attribute and attribute.data_type!='FLOAT_VECTOR':extras.set_status(obj,'velocity 属性需要是向量 / velocity must be a vector attribute');return
    vectors=[Vector(item.vector) for item in attribute.data] if attribute else [v.normal.copy() for v in mesh.vertices];neighbors=[set([i]) for i in range(len(mesh.vertices))]
    for edge in mesh.edges:a,b=edge.vertices;neighbors[a].add(b);neighbors[b].add(a)
    for _ in range(s.iterations):vectors=[v.lerp(sum((vectors[j] for j in neighbors[i]),Vector())/len(neighbors[i]),max(0,min(1,s.amount))) for i,v in enumerate(vectors)]
    vv,ff,ee=raw_mesh(source,obj);extras.mesh_write(obj,vv,ff,ee)
    attr=obj.data.attributes.new('cw_velocity','FLOAT_VECTOR','POINT');attr.data.foreach_set('vector',[x for v in vectors for x in v])


def pieces(obj,voronoi=False):
    sources=input_objects(obj,{'MESH'});s=obj.cw_extra
    if not sources:extras.set_status(obj,'请选择源网格 / Select a source mesh');return
    result=[]
    if voronoi:
        source=sources[0];rng=random.Random(s.seed)
        bounds=[v.co for v in source.data.vertices]
        if not bounds:return
        low=Vector(tuple(min(v[k] for v in bounds) for k in range(3)));high=Vector(tuple(max(v[k] for v in bounds) for k in range(3)))
        seeds=[Vector(tuple(rng.uniform(low[k],high[k]) for k in range(3))) for _ in range(min(s.count,32))]
        base=bmesh.new();base.from_mesh(source.data)
        matrix=obj.matrix_world.inverted_safe() @ source.matrix_world
        for seed in seeds:
            bm=base.copy()
            for other in seeds:
                if seed==other:continue
                if not bm.verts:break
                cut=bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-6,plane_co=(seed+other)*.5,plane_no=(other-seed).normalized(),clear_outer=True,clear_inner=False)
                boundary=[edge for edge in cut['geom_cut'] if isinstance(edge,bmesh.types.BMEdge) and edge.is_boundary]
                if boundary:
                    try:bmesh.ops.holes_fill(bm,edges=boundary,sides=0)
                    except RuntimeError:pass
            bm.verts.ensure_lookup_table();bm.verts.index_update()
            vv=[matrix@v.co for v in bm.verts];ff=[tuple(v.index for v in face.verts) for face in bm.faces]
            if vv and ff:result.append((vv,ff))
            bm.free()
        base.free()
    else:
        for source in sources:
            vv,ff,ee=raw_mesh(source,obj)
            if len(sources)>1:result.append(([Vector(v) for v in vv],ff));continue
            adjacency=[set() for _ in vv]
            for a,b in ee:adjacency[a].add(b);adjacency[b].add(a)
            unseen=set(range(len(vv)))
            while unseen:
                seed=unseen.pop();component={seed};stack=[seed]
                while stack:
                    for neighbor in adjacency[stack.pop()] & unseen:unseen.remove(neighbor);component.add(neighbor);stack.append(neighbor)
                ordered=sorted(component);mapping={old:new for new,old in enumerate(ordered)}
                faces=[tuple(mapping[i] for i in face) for face in ff if all(i in component for i in face)]
                if faces:result.append(([Vector(vv[i]) for i in ordered],faces))
    if not result:extras.set_status(obj,'未得到封闭碎片 / No solid fragments produced');return
    from .engine import evaluate_clones
    centers=[sum(vv,Vector())/len(vv) for vv,ff in result]
    positions,rotations,scales,warnings=evaluate_clones(obj,centers,bpy.context.scene)
    vertices=[];faces=[]
    for j,(vv,ff) in enumerate(result):
        off=len(vertices);rotation=Euler(rotations[j]).to_matrix();scale=Vector(scales[j])
        vertices += [tuple(positions[j]+rotation @ Vector(tuple((v-centers[j])[k]*scale[k] for k in range(3)))) for v in vv]
        faces += [tuple(i+off for i in face) for face in ff]
    extras.mesh_write(obj,vertices,faces)
    attr=obj.data.attributes.new('cw_piece','INT','FACE');cursor=0
    for j,(vv,ff) in enumerate(result):
        for _ in ff:attr.data[cursor].value=j;cursor+=1


def mask(obj):
    curves=input_objects(obj,{'CURVE'});s=obj.cw_extra
    polygons=[[obj.matrix_world.inverted_safe() @ p for p in extras.curve_points(c)] for c in curves]
    polygons=[p for p in polygons if len(p)>2]
    if not polygons:extras.set_status(obj,'添加闭合样条 / Add closed spline inputs');return
    xmin=min(p.x for poly in polygons for p in poly);xmax=max(p.x for poly in polygons for p in poly);ymin=min(p.y for poly in polygons for p in poly);ymax=max(p.y for poly in polygons for p in poly)
    n=s.resolution;dx=max(1e-6,(xmax-xmin)/n);dy=max(1e-6,(ymax-ymin)/n)
    def inside(x,y,poly):
        result=False
        for a,b in zip(poly,poly[1:]+poly[:1]):
            if (a.y>y)!=(b.y>y) and x<(b.x-a.x)*(y-a.y)/(b.y-a.y)+a.x:result=not result
        return result
    filled=set()
    for y in range(n):
        for x in range(n):
            values=[inside(xmin+(x+.5)*dx,ymin+(y+.5)*dy,p) for p in polygons]
            occupied=all(values) if s.operation=='INTERSECT' else values[0] and not any(values[1:]) if s.operation=='DIFFERENCE' else any(values)
            if occupied:filled.add((x,y))
    edges={}
    for x,y in filled:
        for neighbor,a,b in [((x,y-1),(x,y),(x+1,y)),((x+1,y),(x+1,y),(x+1,y+1)),((x,y+1),(x+1,y+1),(x,y+1)),((x-1,y),(x,y+1),(x,y))]:
            if neighbor not in filled:edges.setdefault(a,[]).append(b)
    obj.data.splines.clear()
    while edges:
        start=next(iter(edges));current=start;chain=[]
        while current in edges:
            chain.append(current);following=edges[current].pop()
            if not edges[current]:del edges[current]
            current=following
            if current==start:break
        if len(chain)<3:continue
        spline=obj.data.splines.new('POLY');spline.points.add(len(chain)-1)
        for point,(x,y) in zip(spline.points,chain):point.co=(xmin+x*dx,ymin+y*dy,0,1)
        spline.use_cyclic_u=True


def deform(obj,scene):
    s=obj.cw_extra;target=s.source
    if not target or target.type!='MESH':extras.set_status(obj,'请选择需要变形的网格 / Select a mesh target');return
    key=obj.as_pointer();current=tuple(tuple(v.co) for v in target.data.vertices)
    if s.base_mesh is None or len(s.base_mesh.vertices)!=len(current) or (key in extras._OUTPUT and current!=extras._OUTPUT[key]):
        previous=s.base_mesh;s.base_mesh=target.data.copy()
        if previous and previous.users==0:bpy.data.meshes.remove(previous)
    base=s.base_mesh
    bvh=None
    if s.kind=='COLLISION' and s.target and s.target.type=='MESH':bvh=BVHTree.FromPolygons([s.target.matrix_world@v.co for v in s.target.data.vertices],[tuple(p.vertices) for p in s.target.data.polygons])
    if s.kind=='COLLISION' and bvh is None:extras.set_status(obj,'请选择碰撞网格 / Select a collision surface');return
    low=min((v.co.z for v in base.vertices),default=0);high=max((v.co.z for v in base.vertices),default=1)
    output=[]
    for i,v in enumerate(base.vertices):
        p=v.co.copy()
        if s.kind=='FORMULA_DEFORM':p.z+=s.amount*evaluate(s.formula,x=p.x,y=p.y,z=p.z,t=scene.frame_current/scene.render.fps,frame=scene.frame_current,i=i,seed=s.seed)
        elif s.kind=='MELT':
            h=max(high-low,1e-6);a=max(0,min(1,s.amount));level=(p.z-low)/h
            spread=1+a*(1-level);p.x*=spread;p.y*=spread;p.z=low+(p.z-low)*(1-a)
        elif bvh:
            world=target.matrix_world@p;hit,normal,index,distance=bvh.find_nearest(world)
            if hit is not None and (world-hit).dot(normal)<s.amount*.01:p=target.matrix_world.inverted_safe()@(hit+normal*s.amount*.01)
        output.append(tuple(p))
    target.data.vertices.foreach_set('co',[value for point in output for value in point]);target.data.update();extras._OUTPUT[key]=tuple(output)


def build(obj,scene):
    s=obj.cw_extra;k=s.kind
    if k=='SPLINE_MASK':mask(obj);return
    if k in {'FRACTURE','VORONOI'}:pieces(obj,k=='VORONOI');return
    if k in {'FORMULA_DEFORM','MELT','COLLISION'}:deform(obj,scene);return
    if k=='PYTHON_GENERATOR':
        from .procedural_scripts import run_generator
        run_generator(obj,scene);return
    if k=='VECTOR_SMOOTH':smooth_vectors(obj);return
    if k=='BACKGROUND':
        r=s.size[0]/2;h=s.size[1]/2;extras.mesh_write(obj,[(-r,-h,0),(r,-h,0),(r,h,0),(-r,h,0)],[(0,1,2,3)])
        if not obj.data.materials:
            mat=bpy.data.materials.new('Background');mat.use_nodes=True;obj.data.materials.append(mat)
        mat=obj.data.materials[0];nodes=mat.node_tree.nodes
        image=next((n for n in nodes if n.type=='TEX_IMAGE'),None) or nodes.new('ShaderNodeTexImage');image.image=s.image
        emission=next((n for n in nodes if n.type=='EMISSION'),None) or nodes.new('ShaderNodeEmission')
        mat.node_tree.links.new(image.outputs['Color'],emission.inputs['Color'])
        mat.node_tree.links.new(emission.outputs['Emission'],next(n for n in nodes if n.type=='OUTPUT_MATERIAL').inputs['Surface'])
        uv=obj.data.uv_layers.new(name='UVMap')
        coords=[(0,0),(1,0),(1,1),(0,1)]
        for loop in obj.data.loops:uv.data[loop.index].uv=coords[loop.vertex_index]
        return
    sources=input_objects(obj,{'MESH'})
    if not sources:extras.set_status(obj,'请选择源网格 / Select a source mesh');return
    source=sources[0];vv,ff,ee=raw_mesh(source,obj)
    if k=='MOEXTRUDE':
        bm=bmesh.new();bm.from_mesh(source.data)
        created=bmesh.ops.extrude_discrete_faces(bm,faces=list(bm.faces))['faces']
        from .engine import evaluate_clones
        centers=[face.calc_center_median() for face in created]
        positions,rotations,scales,warnings=evaluate_clones(obj,centers,scene)
        for i,face in enumerate(created):
            normal=face.normal.copy()
            for v in face.verts:v.co+=normal*s.amount+(positions[i]-centers[i])
        bm.to_mesh(obj.data);bm.free();obj.data.update();return
    if k=='LOD':
        camera=s.target or scene.camera
        distance=(camera.matrix_world.translation-obj.matrix_world.translation).length if camera else 0
        level=min(s.count-1,int(distance/max(.001,s.height)))
        if len(sources)>1:vv,ff,ee=raw_mesh(sources[min(level,len(sources)-1)],obj)
        extras.mesh_write(obj,vv,ff,ee)
        mod=next((m for m in obj.modifiers if m.name=='CW LOD'),None) or obj.modifiers.new('CW LOD','DECIMATE')
        mod.ratio=max(.01,min(1,s.amount**level)) if len(sources)==1 else 1
        if camera is None:extras.set_status(obj,'可指定摄像机作为距离参考 / Assign a camera to drive distance LOD')
        return
    if k in {'VOLUME_BUILDER','VOLUME_MESHER','SDF_SMOOTH','FOG_SMOOTH'}:
        vv=[];ff=[];ee=[]
        for item in sources:
            vertices,faces,edges=raw_mesh(item,obj);offset=len(vv)
            vv.extend(vertices);ff.extend(tuple(i+offset for i in face) for face in faces);ee.extend(tuple(i+offset for i in edge) for edge in edges)
        extras.mesh_write(obj,vv,ff,ee)
        if k=='FOG_SMOOTH':
            smooth=next((m for m in obj.modifiers if m.type=='SMOOTH'),None) or obj.modifiers.new('Fog Boundary Smooth','SMOOTH');smooth.factor=s.amount;smooth.iterations=s.iterations
        volume_graph(obj,k);return
    raise ValueError('Unknown procedural geometry: '+k)


