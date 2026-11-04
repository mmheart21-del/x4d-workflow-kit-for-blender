"""SVG curve import, implemented locally so Blender 4.5 needs no extra extension."""
import bpy,math,re,xml.etree.ElementTree as ET
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty,FloatProperty
from mathutils import Matrix,Vector

def numbers(text):return [float(v) for v in re.findall(r'[-+]?(?:\d*\.\d+|\d+\.?\d*)(?:[eE][-+]?\d+)?',text or '')]
def path_points(text):
    tokens=re.findall(r'[MmLlHhVvCcSsQqTtAaZz]|[-+]?(?:\d*\.\d+|\d+\.?\d*)(?:[eE][-+]?\d+)?',text or '')
    i=0;command='M';p=Vector((0.,0.));start=p.copy();last=None;paths=[];current=[]
    sizes={'M':2,'L':2,'H':1,'V':1,'C':6,'S':4,'Q':4,'T':2,'A':7}
    while i<len(tokens):
        if tokens[i].isalpha():command=tokens[i];i+=1
        upper=command.upper();relative=command.islower()
        if upper=='Z':
            if current:paths.append((current,True));current=[]
            p=start.copy();command='M';continue
        count=sizes[upper]
        if i+count>len(tokens) or any(v.isalpha() for v in tokens[i:i+count]):raise ValueError('Invalid SVG path')
        values=[float(v) for v in tokens[i:i+count]];i+=count;origin=p.copy()
        def point(x,y):return Vector((x,y))+(origin if relative else Vector((0.,0.)))
        if upper=='M':
            if current:paths.append((current,False))
            p=point(*values);current=[tuple(p)];start=p.copy();command='l' if relative else 'L';last=None
        elif upper=='L':p=point(*values);current.append(tuple(p));last=None
        elif upper=='H':p.x=values[0]+(origin.x if relative else 0);current.append(tuple(p));last=None
        elif upper=='V':p.y=values[0]+(origin.y if relative else 0);current.append(tuple(p));last=None
        elif upper in {'C','S','Q','T'}:
            if upper=='C':a=point(*values[:2]);b=point(*values[2:4]);end=point(*values[4:6])
            elif upper=='S':a=2*origin-last if last is not None else origin;b=point(*values[:2]);end=point(*values[2:4])
            elif upper=='Q':a=point(*values[:2]);end=point(*values[2:4]);b=None
            else:a=2*origin-last if last is not None else origin;end=point(*values);b=None
            for step in range(1,17):
                t=step/16;v=(1-t)**3*origin+3*(1-t)**2*t*a+3*(1-t)*t*t*b+t**3*end if b is not None else (1-t)**2*origin+2*(1-t)*t*a+t*t*end
                current.append(tuple(v))
            p=end;last=b if b is not None else a
        elif upper=='A':
            rx,ry,rotation,large,sweep,x,y=values;end=point(x,y);rx=abs(rx);ry=abs(ry)
            if min(rx,ry)<1e-9:current.append(tuple(end));p=end;continue
            phi=math.radians(rotation);c=math.cos(phi);s=math.sin(phi);d=(origin-end)*.5;xp=c*d.x+s*d.y;yp=-s*d.x+c*d.y
            ratio=xp*xp/(rx*rx)+yp*yp/(ry*ry)
            if ratio>1:rx*=math.sqrt(ratio);ry*=math.sqrt(ratio)
            factor=math.sqrt(max(0,(rx*rx*ry*ry-rx*rx*yp*yp-ry*ry*xp*xp)/max(1e-20,rx*rx*yp*yp+ry*ry*xp*xp)))*(-1 if bool(large)==bool(sweep) else 1)
            cxp=factor*rx*yp/ry;cyp=-factor*ry*xp/rx;mid=(origin+end)*.5;center=Vector((c*cxp-s*cyp+mid.x,s*cxp+c*cyp+mid.y))
            a=Vector(((xp-cxp)/rx,(yp-cyp)/ry));b=Vector(((-xp-cxp)/rx,(-yp-cyp)/ry));start_angle=math.atan2(a.y,a.x);delta=math.atan2(a.x*b.y-a.y*b.x,a.dot(b))
            if not sweep and delta>0:delta-=math.tau
            elif sweep and delta<0:delta+=math.tau
            for step in range(1,25):
                angle=start_angle+delta*step/24;xx=rx*math.cos(angle);yy=ry*math.sin(angle);current.append((center.x+c*xx-s*yy,center.y+s*xx+c*yy))
            p=end;last=None
    if current:paths.append((current,False))
    return paths

def transform(text):
    result=Matrix.Identity(3)
    for name,args in re.findall(r'(\w+)\s*\(([^)]*)\)',text or ''):
        v=numbers(args);m=Matrix.Identity(3)
        if name=='translate':m[0][2]=v[0];m[1][2]=v[1] if len(v)>1 else 0
        elif name=='scale':m[0][0]=v[0];m[1][1]=v[1] if len(v)>1 else v[0]
        elif name=='rotate':
            a=math.radians(v[0]);m=Matrix(((math.cos(a),-math.sin(a),0),(math.sin(a),math.cos(a),0),(0,0,1)))
            if len(v)==3:
                t=Matrix.Identity(3);t[0][2]=v[1];t[1][2]=v[2];m=t@m@t.inverted()
        elif name=='skewX':m[0][1]=math.tan(math.radians(v[0]))
        elif name=='skewY':m[1][0]=math.tan(math.radians(v[0]))
        elif name=='matrix' and len(v)==6:m=Matrix(((v[0],v[2],v[4]),(v[1],v[3],v[5]),(0,0,1)))
        result=result@m
    return result

class CW_OT_import_svg(bpy.types.Operator,ImportHelper):
    bl_idname='cw.import_svg';bl_label='Import SVG';bl_options={'REGISTER','UNDO'}
    filename_ext='.svg'
    filter_glob:StringProperty(default='*.svg',options={'HIDDEN'})
    scale:FloatProperty(name='Scale',default=.01,min=.000001)
    def execute(self,context):
        try:root=ET.parse(self.filepath).getroot()
        except Exception as exc:self.report({'ERROR'},str(exc));return {'CANCELLED'}
        data=bpy.data.curves.new('SVG','CURVE');data.dimensions='2D';data.fill_mode='BOTH'
        def walk(element,parent):
            matrix=parent@transform(element.get('transform'));tag=element.tag.rsplit('}',1)[-1];paths=[]
            def value(key,default=0):
                values=numbers(str(element.get(key,default)));return values[0] if values else default
            if tag=='path':paths=path_points(element.get('d',''))
            elif tag in {'polygon','polyline'}:
                v=numbers(element.get('points'));paths=[(list(zip(v[::2],v[1::2])),tag=='polygon')]
            elif tag=='rect':
                x=value('x');y=value('y');w=value('width');h=value('height');paths=[([(x,y),(x+w,y),(x+w,y+h),(x,y+h)],True)]
            elif tag in {'circle','ellipse'}:
                x=value('cx');y=value('cy');rx=value('r') if tag=='circle' else value('rx');ry=rx if tag=='circle' else value('ry');paths=[([(x+rx*math.cos(i*math.tau/64),y+ry*math.sin(i*math.tau/64)) for i in range(64)],True)]
            elif tag=='line':paths=[([(value('x1'),value('y1')),(value('x2'),value('y2'))],False)]
            for points,closed in paths:
                if not points:continue
                spline=data.splines.new('POLY');spline.points.add(len(points)-1)
                for p,(x,y) in zip(spline.points,points):v=matrix@Vector((x,y,1));p.co=(v.x*self.scale,-v.y*self.scale,0,1)
                spline.use_cyclic_u=closed
            for child in element:walk(child,matrix)
        try:walk(root,Matrix.Identity(3))
        except Exception as exc:bpy.data.curves.remove(data);self.report({'ERROR'},str(exc));return {'CANCELLED'}
        if not data.splines:bpy.data.curves.remove(data);self.report({'ERROR'},'SVG 中没有支持的曲线几何 / No supported SVG curve geometry');return {'CANCELLED'}
        obj=bpy.data.objects.new('SVG',data);(context.collection or context.scene.collection).objects.link(obj)
        for o in context.selected_objects:o.select_set(False)
        obj.select_set(True);context.view_layer.objects.active=obj
        return {'FINISHED'}
classes=[CW_OT_import_svg]


