"""Manage source parenting and visibility while a cloner owns a source."""
import bpy
from mathutils import Matrix

KEY = 'x4d_clone_owner'

def visibility(obj, scene, hidden):
    for layer in scene.view_layers:
        if layer.objects.get(obj.name) == obj:
            if obj.hide_get(view_layer=layer)!=hidden:obj.hide_set(hidden, view_layer=layer)

def release(obj, scene):
    world = obj.matrix_world.copy()
    parent = obj.get('x4d_clone_previous_parent')
    obj.parent = parent
    obj.parent_type = obj.get('x4d_clone_parent_type', 'OBJECT')
    obj.parent_bone = obj.get('x4d_clone_parent_bone', '')
    values = obj.get('x4d_clone_parent_inverse')
    if values:
        obj.matrix_parent_inverse = Matrix([values[i:i+4] for i in range(0,16,4)])
    obj.matrix_world = world
    obj.hide_render = bool(obj.get('x4d_clone_hide_render'))
    layers = obj.get('x4d_clone_hidden_layers', {})
    for layer in scene.view_layers:
        if layer.objects.get(obj.name) == obj:
            obj.hide_set(bool(layers.get(layer.name, False)), view_layer=layer)
    for key in (KEY,'x4d_clone_previous_parent','x4d_clone_parent_type','x4d_clone_parent_bone','x4d_clone_parent_inverse','x4d_clone_hide_render','x4d_clone_hidden_layers'):
        if key in obj:del obj[key]

def sync(scene):
    from .engine import clone_sources
    desired = {}
    for cloner in scene.objects:
        if cloner.cw.kind != 'CLONER' or cloner.cw_extra.kind == 'MATRIX':continue
        for source in clone_sources(cloner):
            if source.library or source.cw.kind == 'CLONER' or source.name not in scene.objects:continue
            if source == cloner or cloner in source.children_recursive:continue
            desired.setdefault(source, cloner)
    for obj in list(scene.objects):
        if KEY in obj and obj.get(KEY) != desired.get(obj):
            release(obj, scene)
        elif KEY in obj and obj not in desired:
            release(obj, scene)
    for obj, cloner in desired.items():
        if KEY not in obj:
            world = obj.matrix_world.copy()
            if obj.parent:obj['x4d_clone_previous_parent'] = obj.parent
            obj['x4d_clone_parent_type'] = obj.parent_type
            obj['x4d_clone_parent_bone'] = obj.parent_bone
            obj['x4d_clone_parent_inverse'] = [value for row in obj.matrix_parent_inverse for value in row]
            obj['x4d_clone_hide_render'] = obj.hide_render
            obj['x4d_clone_hidden_layers'] = {layer.name:obj.hide_get(view_layer=layer) for layer in scene.view_layers if layer.objects.get(obj.name)==obj}
            obj.parent = cloner
            obj.parent_type = 'OBJECT'
            obj.matrix_parent_inverse = cloner.matrix_world.inverted_safe()
            obj.matrix_world = world
            obj[KEY] = cloner
        if not obj.hide_render:obj.hide_render = True
        visibility(obj, scene, True)


