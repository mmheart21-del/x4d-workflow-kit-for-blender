"""X4D-like deformers are independent controller objects with editable bindings."""
import bpy
from bpy.app.handlers import persistent
from bpy.props import StringProperty
_busy=False
PREFIX='CW Deformer '

def assign(owner,name,value):
    if getattr(owner,name)!=value:setattr(owner,name,value)
@persistent
def sync(scene,*args):
    global _busy
    if _busy:return
    _busy=True
    try:
        for obj in scene.objects:
            if obj.cw.kind!='DEFORMER':continue
            s=obj.cw;target=s.deform_target
            if not target or target.type!='MESH' or target==obj:
                previous=obj.get('cw_deformer_previous_target')
                if previous:
                    for m in list(previous.modifiers):
                        if m.type=='SIMPLE_DEFORM' and m.origin==obj and m.name.startswith(PREFIX):previous.modifiers.remove(m)
                    del obj['cw_deformer_previous_target']
                if s.status!='选择需要变形的网格对象 / Select a mesh target':s.status='选择需要变形的网格对象 / Select a mesh target'
                continue
            previous=obj.get('cw_deformer_previous_target')
            if previous and previous!=target:
                for m in list(previous.modifiers):
                    if m.type=='SIMPLE_DEFORM' and m.origin==obj and m.name.startswith(PREFIX):previous.modifiers.remove(m)
            if previous!=target:obj['cw_deformer_previous_target']=target
            m=next((m for m in target.modifiers if m.type=='SIMPLE_DEFORM' and m.origin==obj and m.name.startswith(PREFIX)),None)
            if not m:m=target.modifiers.new(PREFIX+obj.name,'SIMPLE_DEFORM');m.origin=obj
            assign(m,'deform_method',s.deform_type);assign(m,'deform_axis',{'X':'X','Y':'Z','Z':'Y'}[s.deform_axis])
            if s.deform_type=='TAPER':assign(m,'factor',s.deform_factor)
            else:assign(m,'angle',s.deform_angle)
            if s.status:s.status=''
        for target in scene.objects:
            for m in list(target.modifiers):
                if m.type=='SIMPLE_DEFORM' and m.name.startswith(PREFIX) and m.origin is None:target.modifiers.remove(m)
    finally:_busy=False

class CW_OT_deformer(bpy.types.Operator):
    bl_idname='cw.deformer';bl_label='Create Deformer';bl_options={'REGISTER','UNDO'}
    kind:StringProperty(default='BEND')
    def execute(self,context):
        if self.kind not in {'BEND','TWIST','TAPER'}:return {'CANCELLED'}
        target=context.object if context.object and context.object.type=='MESH' else None
        obj=bpy.data.objects.new({'BEND':'弯曲','TWIST':'扭转','TAPER':'锥化'}[self.kind],None)
        context.collection.objects.link(obj);obj.empty_display_type='CUBE';obj.empty_display_size=2;obj.color=(.6,.45,.9,1)
        obj.cw.kind='DEFORMER';obj.cw.deform_type=self.kind
        if target:
            obj.matrix_world=target.matrix_world.copy();obj.parent=target;obj.matrix_parent_inverse=target.matrix_world.inverted_safe()
            obj.cw.deform_target=target
        for selected in context.selected_objects:selected.select_set(False)
        obj.select_set(True);context.view_layer.objects.active=obj
        sync(context.scene)
        return {'FINISHED'}
classes=[CW_OT_deformer]

