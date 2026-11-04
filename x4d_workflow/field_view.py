"""Viewport guides and draggable radius handles for spatial fields."""
import math
import bpy
import gpu
from gpu_extras.batch import batch_for_shader
from bpy_extras.view3d_utils import location_3d_to_region_2d
from mathutils import Vector
from .catalog import label

def project(context, obj, point):
    return location_3d_to_region_2d(context.region,context.region_data,obj.matrix_world @ Vector(point))

def handles(context,obj):
    kind=obj.cw.field_type
    axes=(2,) if kind=='LINEAR' else (0,1) if kind in {'CYLINDER','CONE','CAPSULE','TORUS'} else (0,1,2)
    for inner in (False,True):
        radius=obj.cw.radius*(obj.cw.inner_range if inner else 1)
        if radius<=0:continue
        for axis in axes:
            p=[0.,0.,0.];p[axis]=radius
            xy=project(context,obj,p)
            p[axis]+=max(.01,obj.cw.radius*.1)
            end=project(context,obj,p)
            if xy is not None and end is not None and (end-xy).length>1:
                yield inner,xy,(end-xy)/(max(.01,obj.cw.radius*.1))

def draw(context):
    if not context.region_data or not context.space_data.overlay.show_overlays:return
    shader=gpu.shader.from_builtin('UNIFORM_COLOR')
    for obj in context.visible_objects:
        if obj.cw.kind!='FIELD':continue
        selected=obj.select_get()
        for inner in (False,True):
            radius=obj.cw.radius*(obj.cw.inner_range if inner else 1)
            if radius<=0:continue
            lines=[]
            if obj.cw.field_type=='SPHERE':
                for axis in range(3):
                    circle=[]
                    for i in range(49):
                        point=[0.,0.,0.];angle=math.tau*i/48
                        point[(axis+1)%3]=radius*math.cos(angle);point[(axis+2)%3]=radius*math.sin(angle)
                        circle.append(point)
                    lines.extend(zip(circle,circle[1:]))
            elif obj.cw.field_type in {'CYLINDER','CONE','CAPSULE','TORUS'}:
                kind=obj.cw.field_type
                half=obj.cw_extra.height/2
                if kind=='TORUS':
                    tube=obj.cw_extra.inner
                    profile=[(radius+tube*math.cos(i*math.tau/24),tube*math.sin(i*math.tau/24)) for i in range(25)]
                elif kind=='CAPSULE':
                    cap=max(0,half-radius)
                    profile=[(radius*math.cos(i*math.pi/24),radius*math.sin(i*math.pi/24)+(-cap if i<0 else cap)) for i in range(-12,13)]
                    profile.insert(12,(radius,-cap))
                else:
                    profile=[(radius,-half),(0 if kind=='CONE' else radius,half)]
                for angle in (0,math.pi/2,math.pi,3*math.pi/2):
                    meridian=[(r*math.cos(angle),r*math.sin(angle),z) for r,z in profile]
                    lines.extend(zip(meridian,meridian[1:]))
                for r,z in profile[::max(1,len(profile)//8)]:
                    ring=[(r*math.cos(i*math.tau/48),r*math.sin(i*math.tau/48),z) for i in range(49)]
                    lines.extend(zip(ring,ring[1:]))
            elif obj.cw.field_type!='LINEAR':
                corners=[(x*radius,y*radius,z*radius) for x in (-1,1) for y in (-1,1) for z in (-1,1)]
                lines=[(a,b) for i,a in enumerate(corners) for b in corners[i+1:] if sum(x!=y for x,y in zip(a,b))==1]
            else:
                for z in (-radius,radius):
                    r=obj.cw.radius
                    corners=[(-r,-r,z),(r,-r,z),(r,r,z),(-r,r,z)]
                    lines.extend(zip(corners,corners[1:]+corners[:1]))
                    lines.extend([((-r,0,z),(r,0,z)),((0,-r,z),(0,r,z))])
            vertices=[]
            for a,b in lines:
                pa,pb=project(context,obj,a),project(context,obj,b)
                if pa is not None and pb is not None:vertices.extend((pa,pb))
            if vertices:
                shader.bind()
                shader.uniform_float('color',(.65,.36,.14,1) if selected and inner else (1,.55,.2,1) if selected else (.49,.32,.52,1) if inner else (.85,.54,.91,1))
                batch_for_shader(shader,'LINES',{'pos':vertices}).draw(shader)
        if selected and obj==context.active_object:
            from .rail import rect
            for inner,xy,_ in handles(context,obj):
                rect(xy.x-4,xy.y-4,8,8,(1,.84,.35,1) if inner else (1,.62,.25,1))

class CW_OT_field_resize(bpy.types.Operator):
    bl_idname='cw.field_resize'
    bl_label='Resize Field'
    bl_options={'INTERNAL','UNDO'}

    def invoke(self,context,event):
        obj=context.active_object
        if not obj or obj.cw.kind!='FIELD' or not obj.select_get() or not context.space_data.overlay.show_overlays:
            return {'PASS_THROUGH'}
        mouse=Vector((event.mouse_x-context.region.x,event.mouse_y-context.region.y))
        candidates=[(inner,xy,direction) for inner,xy,direction in handles(context,obj) if (xy-mouse).length<9]
        if not candidates:return {'PASS_THROUGH'}
        self.inner,_,self.direction=min(candidates,key=lambda h:(h[1]-mouse).length)
        self.obj=obj;self.start=Vector((event.mouse_x,event.mouse_y))
        self.radius=obj.cw.radius;self.ratio=obj.cw.inner_range
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self,context,event):
        if event.type in {'ESC','RIGHTMOUSE','WINDOW_DEACTIVATE'}:
            self.obj.cw.radius=self.radius
            self.obj.cw.inner_range=self.ratio
            return {'CANCELLED'}
        if event.type=='LEFTMOUSE' and event.value=='RELEASE':return {'FINISHED'}
        if event.type=='MOUSEMOVE':
            delta=Vector((event.mouse_x,event.mouse_y))-self.start
            change=delta.dot(self.direction)/self.direction.length_squared
            if self.inner:self.obj.cw.inner_range=max(0,min(.99,self.ratio+change/self.radius))
            else:self.obj.cw.radius=max(.001,self.radius+change)
            context.area.tag_redraw()
        return {'RUNNING_MODAL'}

classes=[CW_OT_field_resize]
