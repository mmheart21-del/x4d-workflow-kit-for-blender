"""Draw original X4D-inspired icons, without extracting Maxon resources.
Pure Python PNG rasterizer, 3x supersampling; rebuild with Blender's Python.
"""
import math,struct,zlib,os,sys,ast
ROOT=os.path.dirname(os.path.dirname(__file__))
S=3;W=48;N=W*S
class Canvas:
    def __init__(self):self.p=bytearray(N*N*4)
    def put(self,x,y,c):
        if 0<=x<N and 0<=y<N:
            j=4*((N-1-y)*N+x);self.p[j:j+4]=bytes(c)
    def polygon(self,pts,c):
        pts=[(x*S,y*S) for x,y in pts]
        for y in range(max(0,int(min(p[1] for p in pts))),min(N,int(max(p[1] for p in pts))+1)):
            hits=[]
            for a,b in zip(pts,pts[1:]+pts[:1]):
                if (a[1]<=y+.5<b[1]) or (b[1]<=y+.5<a[1]):hits.append(a[0]+(y+.5-a[1])*(b[0]-a[0])/(b[1]-a[1]))
            hits.sort()
            for i in range(0,len(hits)-1,2):
                for x in range(max(0,int(hits[i])),min(N,int(hits[i+1])+1)):self.put(x,y,c)
    def line(self,pts,c,width=1.8):
        for a,b in zip(pts,pts[1:]):
            x1,y1=a[0]*S,a[1]*S;x2,y2=b[0]*S,b[1]*S
            d=(x2-x1)**2+(y2-y1)**2;r=width*S/2
            for y in range(max(0,int(min(y1,y2)-r)),min(N,int(max(y1,y2)+r)+1)):
                for x in range(max(0,int(min(x1,x2)-r)),min(N,int(max(x1,x2)+r)+1)):
                    t=max(0,min(1,((x-x1)*(x2-x1)+(y-y1)*(y2-y1))/d)) if d else 0
                    if (x-x1-t*(x2-x1))**2+(y-y1-t*(y2-y1))**2<=r*r:self.put(x,y,c)
    def ellipse(self,cx,cy,rx,ry,c,fill=False):
        pts=[(cx+rx*math.cos(i*math.pi/32),cy+ry*math.sin(i*math.pi/32)) for i in range(65)]
        self.polygon(pts[:-1],c) if fill else self.line(pts,c)
    def save(self,path):
        raw=bytearray()
        for y in range(W):
            raw.append(0)
            for x in range(W):
                samples=[self.p[4*((y*S+dy)*N+x*S+dx):4*((y*S+dy)*N+x*S+dx)+4] for dy in range(S) for dx in range(S)]
                alpha=sum(p[3] for p in samples)
                rgb=[int(sum(p[j]*p[3] for p in samples)/alpha) if alpha else 0 for j in range(3)]
                raw.extend(rgb+[alpha//(S*S)])
        def chunk(t,data):return struct.pack('>I',len(data))+t+data+struct.pack('>I',zlib.crc32(t+data)&0xffffffff)
        with open(path,'wb') as f:f.write(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',W,W,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(raw))+chunk(b'IEND',b''))

CYAN=(111,207,239,255);GREEN=(112,220,134,255);PURPLE=(158,145,238,255);PINK=(201,147,217,255);GRAY=(182,194,215,255)
def shaded(c,k):return tuple(min(255,int(v*k)) for v in c[:3])+(255,)
def cube(p,c,x=24,y=24,size=17,wire=False):
    a=[(x,y+size),(x+size*.87,y+size*.5),(x,y),(x-size*.87,y+size*.5)]
    b=[(x-size*.87,y+size*.5),(x,y),(x,y-size),(x-size*.87,y-size*.5)]
    d=[(x,y),(x+size*.87,y+size*.5),(x+size*.87,y-size*.5),(x,y-size)]
    for pts,m in [(a,1.1),(b,.77),(d,.94)]:
        if not wire:p.polygon(pts,shaded(c,m))
        p.line(pts+[pts[0]],c,1.4)
def draw(key,category):
    p=Canvas();c=CYAN if category in {'MESH','SPLINE','TEXT'} else GREEN if category in {'GENERATOR','VOLUME','MOGRAPH'} else PINK if category=='FIELD' else GRAY if category in {'LIGHT','TOOL'} else PURPLE
    k=key.upper()
    k={'SUBDIVISION':'SUBSURF','CLOTH SURFACE':'SUBSURF','OIL TANK':'OIL_TANK','PLATONIC':'ICOSPHERE','POLYGON':'POLYGON SPLINE' if category=='SPLINE' else 'POLYGON','BEND':'BEND','TORUS FIELD':'TORUS','CYLINDRICAL FIELD':'CYLINDER','CONE FIELD':'CONE','CAPSULE FIELD':'CAPSULE','BOX FIELD':'BOX','SPHERICAL FIELD':'SPHERE'}.get(k,k)
    if k in {'MESH','CUBE','SUBSURF','GENERATOR','POLYGON'}:cube(p,c,wire=category!='MESH')
    elif k in {'SPHERE','ICOSPHERE','PLATONIC'} and category=='MESH':
        p.ellipse(24,24,17,17,c,True);p.ellipse(24,24,8,17,shaded(c,.65));p.ellipse(24,24,17,7,shaded(c,.75))
    elif k in {'CYLINDER','TUBE','CAPSULE','OIL_TANK'}:
        p.polygon([(10,13),(10,35),(38,35),(38,13)],shaded(c,.86));p.ellipse(24,13,14,6,c,True);p.ellipse(24,35,14,6,shaded(c,1.1),True)
        if k=='TUBE':p.ellipse(24,35,7,3,shaded(c,.4),True)
    elif k in {'CONE','PYRAMID'}:
        p.polygon([(7,12),(24,42),(41,12)],c);p.ellipse(24,12,17,6,shaded(c,.8),True)
    elif k in {'TORUS','CIRCLE','DISC','RADIAL'}:
        if category=='MESH' and k!='DISC':
            p.ellipse(24,24,19,13,c,True);p.ellipse(24,24,10,6,(0,0,0,0),True);p.ellipse(24,24,15,10,shaded(c,.75))
        else:p.ellipse(24,24,18,18,c,k=='DISC')
    elif k=='PLANE':p.polygon([(4,17),(30,9),(44,30),(18,38)],c)
    elif k in {'TEXT','TEXT SPLINE'}:
        p.polygon([(9,40),(39,40),(39,34),(27,34),(27,7),(21,7),(21,34),(9,34)],c)
    elif k in {'SPLINE','RECTANGLE','BOX','BOX FIELD'}:p.line([(10,9),(10,38),(38,38),(38,9),(10,9)],c,2.4)
    elif k in {'ARC','HELIX','STAR','PENTAGON','DIAMOND','COG','FLOWER','POLYGON SPLINE'}:
        if k=='ARC':pts=[(24+18*math.cos(i*math.pi/32),26-18*math.sin(i*math.pi/32)) for i in range(33)]
        elif k=='HELIX':pts=[(24+15*math.sin(i*.18),7+i*.35) for i in range(96)]
        else:
            n=10 if k=='STAR' else 5 if k=='PENTAGON' else 4 if k=='DIAMOND' else 64
            pts=[]
            for i in range(n+1):
                a=math.pi/2+i*2*math.pi/n;r=18*(.48 if k=='STAR' and i%2 else 1) if k=='STAR' else 16+(3*math.cos(a*(8 if k=='COG' else 5)) if k in {'COG','FLOWER'} else 0)
                pts.append((24+r*math.cos(a),24+r*math.sin(a)))
        p.line(pts,c,2.2)
    elif k in {'MOGRAPH','CLONER','ARRAY','GRID'}:
        for x,y in [(12,13),(35,13),(24,35)]:cube(p,c,x,y,8)
        p.line([(12,24),(24,24),(24,26),(24,24),(35,24)],c)
    elif k in {'VOLUME','VOLUME BUILDER','VOLUME MESHER'}:
        for x,y in [(13,14),(34,14),(24,33)]:p.ellipse(x,y,10,10,c,True)
    elif k in {'DEFORMER','BEND','TWIST','TAPER','FFD'}:
        left=[(12,7),(12,18),(16,29),(26,40)];right=[(29,7),(28,18),(31,27),(39,33)]
        if k=='TAPER':left=[(9,7),(14,18),(18,29),(21,40)];right=[(39,7),(34,18),(30,29),(27,40)]
        p.line(left,c,2);p.line(right,c,2)
        for a,b in zip(left,right):p.line([a,b],c,1.5)
    elif k in {'EFFECTOR','PLAIN','RANDOM','STEP'}:
        if k=='RANDOM':
            for x,y in [(10,13),(30,8),(20,29),(39,34)]:cube(p,c,x,y,6,True)
        else:
            cube(p,c,24,24,16,True);p.line([(10,8),(10,40),(6,34),(10,40),(15,34)],c)
    elif category=='FIELD':
        if k in {'SPHERE','SPHERICAL FIELD'}:p.ellipse(24,24,17,17,c);p.ellipse(24,24,7,17,c);p.ellipse(24,24,17,6,c)
        else:p.line([(8,5),(8,41),(39,32),(39,12),(8,22)],c,2.3)
    elif category=='LIGHT':
        if k in {'AREA','AREA LIGHT'}:p.line([(10,12),(10,37),(36,37),(36,12),(10,12),(6,7),(40,7)],c)
        elif k in {'SPOT','TARGET','TARGET SPOT'}:p.line([(12,36),(36,36),(43,9),(5,9),(12,36)],c);p.ellipse(24,36,12,5,c)
        else:
            p.ellipse(24,24,9,9,c)
            for i in range(8):
                a=i*math.pi/4;p.line([(24+14*math.cos(a),24+14*math.sin(a)),(24+20*math.cos(a),24+20*math.sin(a))],c,2.2)
    elif k in {'MOVE','ROTATE','SCALE','SELECT','AXIS','POINT','EDGE','FACE','OBJECT'}:
        if k=='MOVE':
            for pts in [[(24,5),(24,43),(18,36),(24,43),(30,36)],[(5,24),(43,24),(36,30),(43,24),(36,18)]]:p.line(pts,c,2.3)
        elif k=='ROTATE':
            p.line([(24+16*math.cos(a*.1),24+16*math.sin(a*.1)) for a in range(55)],c,2.5);p.polygon([(38,10),(42,22),(30,17)],c)
        elif k=='SELECT':p.line([(10,40),(13,9),(21,20),(33,10),(38,16),(26,26),(40,30),(10,40)],c,2)
        elif k=='SCALE':p.line([(8,8),(39,39),(29,39),(39,39),(39,29)],c,2.5);p.polygon([(6,6),(15,6),(15,15),(6,15)],c)
        else:
            cube(p,c,wire=True)
            if k=='POINT':p.ellipse(24,24,4,4,(246,173,70,255),True)
            elif k=='EDGE':p.line([(24,24),(24,7)],(246,173,70,255),3)
            elif k=='FACE':p.polygon([(24,24),(39,32),(39,16),(24,7)],(246,173,70,255))
    else:
        cube(p,c,wire=True)
    return p

def slug(s):return ''.join(ch.lower() if ch.isalnum() else '_' for ch in s).strip('_')
# Read the literal inventory without importing Blender or the extension.
module=ast.parse(open(os.path.join(ROOT,'x4d_workflow','catalog.py'),encoding='utf-8-sig').read())
rows=next(ast.literal_eval(n.value) for n in module.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='CATEGORIES' for t in n.targets))
out=os.path.join(ROOT,'x4d_workflow','assets','icons');os.makedirs(out,exist_ok=True)
for cat,cn,en,icon,color,entries in rows:
    draw(cat,cat).save(os.path.join(out,cat.lower()+'.png'))
    for cn,en,command in entries:
        key=en
        draw(key,cat).save(os.path.join(out,cat.lower()+'_'+slug(en)+'.png'))
for key in ['MOVE','ROTATE','SCALE','SELECT','OBJECT','POINT','EDGE','FACE','AXIS']:draw(key,'TOOL').save(os.path.join(out,'tool_'+key.lower()+'.png'))
for kind in ['region','render','settings']:
    p=Canvas();c=GRAY
    p.line([(7,10),(41,10),(41,31),(7,31),(7,10)],c,2.3)
    p.polygon([(6,33),(40,38),(42,44),(8,39)],shaded(c,.9))
    for x in [10,22,34]:p.line([(x,34),(x+4,40)],(48,51,56,255),3)
    if kind=='render':p.polygon([(20,15),(20,27),(31,21)],c)
    elif kind=='region':
        for pts in [[(14,23),(14,27),(19,27)],[(29,27),(34,27),(34,23)],[(14,18),(14,14),(19,14)],[(29,14),(34,14),(34,18)]]:p.line(pts,c,1.6)
    else:
        p.ellipse(29,18,7,7,c);p.ellipse(29,18,2,2,c,True)
        for i in range(8):
            a=i*math.pi/4;p.line([(29+7*math.cos(a),18+7*math.sin(a)),(29+10*math.cos(a),18+10*math.sin(a))],c,2)
    p.save(os.path.join(out,'render_'+kind+'.png'))
print('CW_ICONS',len(os.listdir(out)))

