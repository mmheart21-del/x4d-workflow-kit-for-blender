"""Parameter panels for the extended tools."""
import bpy
from .catalog import label as ui_label
from .catalog import label

LAYOUTS={
'CAPSULE':['radius','height','resolution'],'OIL_TANK':['radius','height','resolution'],'TUBE':['radius','inner','height','resolution'],'FIGURE':['height','resolution'],'LANDSCAPE':['size','resolution','seed'],'RELIEF':['image','size','resolution'],'BACKGROUND':['image','size'],
'FORMULA_SPLINE':['x_formula','y_formula','z_formula','start','end','resolution'],'PROFILE':['radius','height','inner'],'LOFT':['resolution'],'SPLINE_MASK':['operation','resolution'],'LOD':['source','target','count','height','amount'],'PYTHON_GENERATOR':['source','script'],
'VOLUME_BUILDER':['voxel'],'VOLUME_MESHER':['voxel','threshold'],'SDF_SMOOTH':['voxel','iterations','amount'],'FOG_SMOOTH':['voxel','iterations','amount'],'VECTOR_SMOOTH':['source','iterations','amount'],
'FRACTURE':['source'],'VORONOI':['source','count','seed'],'TRACER':['source','resolution'],'MOSPLINE':['source','resolution','radius','height','speed'],'MOEXTRUDE':['source','amount'],
'COLLISION':['source','target','amount'],'FORMULA_DEFORM':['source','formula','amount'],'MELT':['source','amount'],'IES':['ies']}

def draw(layout,obj,links):
    s=obj.cw_extra;kind=s.kind
    if obj.cw.kind=='EFFECTOR':
        kind='EFFECTOR_'+obj.cw.effector
        keys={'DELAY':['amount'],'FORMULA':['formula'],'SHADER':['texture'],'SOUND':['audio','amount'],'TIME':['speed'],'TARGET':['target','amount'],'SPLINE':['target'],'PYTHON':['script']}.get(obj.cw.effector,[])
    elif obj.cw.kind=='FIELD':
        kind='FIELD_'+obj.cw.field_type
        keys={'CYLINDER':['height'],'CONE':['height'],'CAPSULE':['height'],'TORUS':['inner'],'SHADER':['texture'],'SOUND':['audio','amount'],'FORMULA':['formula'],'GROUP':[]}.get(obj.cw.field_type,[])
    else:keys=LAYOUTS.get(kind,[])
    for key in keys:
        layout.prop(s,key)
        if key in {'image','ies','audio'}:layout.operator('cw.load_asset',text=label('载入文件','Load File'),icon='FILE_FOLDER').field=key
    if 'texture' in keys and not s.texture:layout.operator('cw.new_texture',text=label('新建噪波纹理','New Noise Texture'))
    if kind in {'LOFT','SPLINE_MASK','FRACTURE','TRACER','LOD'}:links(layout,obj.cw,'inputs')
    if kind in {'FRACTURE','VORONOI','MOEXTRUDE'}:links(layout,obj.cw,'effectors')
    if kind=='FIELD_GROUP':links(layout,obj.cw,'fields')
    if 'script' in keys:
        row=layout.row(align=True);row.operator('cw.edit_python',text=label('编辑脚本','Edit Script'));row.operator('cw.run_python',text=label('运行','Run'))
        layout.label(text=label('修改脚本后须点击运行','Click Run after changing script'),icon='INFO')
    if obj.type=='LIGHT':layout.prop(obj.data,'color',text=label('颜色','Color'));layout.prop(obj.data,'energy',text=label('功率','Power'))
    if kind in {'VOLUME_BUILDER','VOLUME_MESHER','SDF_SMOOTH','FOG_SMOOTH'}:
        from .object_lists import draw_sources
        draw_sources(layout,obj)
        layout.label(text=label('网格转体积流程；输入须为网格','Mesh-to-volume workflow; mesh input required'),icon='INFO')
    if kind=='SPLINE_MASK':layout.label(text=label('栅格轮廓布尔：分辨率控制精度','Raster contour Boolean; resolution controls accuracy'),icon='INFO')

