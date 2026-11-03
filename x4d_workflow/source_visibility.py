"""Selected generator inputs are editable wire overlays, hidden when deselected."""
import bpy
_active={}

def owned(obj):
    owner=obj.get('cw_generator_owner')
    return owner is not None and obj.parent==owner

def restore_display(obj):
    if 'cw_source_display_type' in obj:
        obj.display_type=obj['cw_source_display_type'];obj.show_in_front=bool(obj.get('cw_source_in_front',False))
        del obj['cw_source_display_type']
        if 'cw_source_in_front' in obj:del obj['cw_source_in_front']

def apply(obj,selected=None):
    if not owned(obj):restore_display(obj);return
    selected=obj.select_get() if selected is None else selected
    if selected:
        if 'cw_source_display_type' not in obj:
            obj['cw_source_display_type']=obj.display_type;obj['cw_source_in_front']=int(obj.show_in_front)
        if obj.hide_get():obj.hide_set(False)
        if obj.display_type!='WIRE':obj.display_type='WIRE'
        if not obj.show_in_front:obj.show_in_front=True
    else:
        restore_display(obj)
        if not obj.hide_get():obj.hide_set(True)

def sync(window):
    active=window.view_layer.objects.active;pointer=active.as_pointer() if active else 0
    previous=_active.get(window.as_pointer(),0);_active[window.as_pointer()]=pointer
    for obj in list(window.scene.objects):
        if not owned(obj):
            restore_display(obj);continue
        selected=obj.select_get()
        if obj==active and pointer!=previous:
            selected=True
            if obj.hide_get():obj.hide_set(False)
            if not obj.select_get():obj.select_set(True)
        apply(obj,selected)

def stop():
    for obj in getattr(bpy.data,'objects',()):
        if 'cw_source_display_type' in obj:
            restore_display(obj)
            if owned(obj):obj.hide_set(True)
    _active.clear()
