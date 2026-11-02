"""Original reference-inspired icon resources shared by menus and viewport rails."""
import os
import bpy
import bpy.utils.previews
from .png import read_rgba
_preview=None
_images={}
ROOT=os.path.join(os.path.dirname(__file__),'assets','icons')
def slug(s):return ''.join(ch.lower() if ch.isalnum() else '_' for ch in s).strip('_')
def key(category,name=None):return category.lower()+('_'+slug(name) if name else '')
def register():
    global _preview
    if _preview is not None:return
    collection=bpy.utils.previews.new()
    try:
        for filename in sorted(os.listdir(ROOT)):
            if filename.endswith('.png'):
                width,height,pixels=read_rgba(os.path.join(ROOT,filename))
                preview=collection.new(filename[:-4]);preview.image_size=(width,height);preview.image_pixels_float=pixels
    except Exception:
        bpy.utils.previews.remove(collection)
        raise
    _preview=collection

def icon_id(name):return _preview[name].icon_id if _preview and name in _preview else 0
def image(name):
    if name in _images:
        try:_images[name].name
        except ReferenceError:_images.pop(name,None)
    if name not in _images:
        img=bpy.data.images.load(os.path.join(ROOT,name+'.png'),check_existing=False)
        img.name='CW UI '+name;_images[name]=img
    return _images[name]
def unregister():
    global _preview
    if _preview is not None:bpy.utils.previews.remove(_preview);_preview=None
    for img in _images.values():
        try:
            if img.users==0:bpy.data.images.remove(img)
        except ReferenceError:pass
    _images.clear()



