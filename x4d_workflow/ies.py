import bpy,os

def configure(obj):
    light=obj.data;s=obj.cw_extra
    light.use_nodes=True;nodes=light.node_tree.nodes
    emission=next((n for n in nodes if n.type=='EMISSION'),None) or nodes.new('ShaderNodeEmission')
    ies=next((n for n in nodes if n.bl_idname=='ShaderNodeTexIES'),None) or nodes.new('ShaderNodeTexIES')
    geometry=next((n for n in nodes if n.type=='NEW_GEOMETRY'),None) or nodes.new('ShaderNodeNewGeometry')
    output=next((n for n in nodes if n.type=='OUTPUT_LIGHT'),None) or nodes.new('ShaderNodeOutputLight')
    ies.mode='EXTERNAL';ies.filepath=bpy.path.abspath(s.ies)
    light.node_tree.links.new(geometry.outputs['Incoming'],ies.inputs['Vector'])
    light.node_tree.links.new(ies.outputs['Fac'],emission.inputs['Strength'])
    light.node_tree.links.new(emission.outputs['Emission'],output.inputs['Surface'])
    if not s.ies or not os.path.isfile(ies.filepath):obj.cw.status='请选择 IES 光度文件 / Select an IES photometric file'
