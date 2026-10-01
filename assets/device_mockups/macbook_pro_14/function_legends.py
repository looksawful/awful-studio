"""Small geometric function-row legends, independent of Unicode font coverage."""
import math
import bpy


def icon(name, number, collection, parent, material, location):
    strokes=[]
    def line(a,b): strokes.append((a,b))
    def path(points,closed=False):
        for a,b in zip(points,points[1:]): line(a,b)
        if closed: line(points[-1],points[0])
    def circle(x,y,r):
        path([(x+r*math.cos(i*math.tau/24),y+r*math.sin(i*math.tau/24)) for i in range(24)],True)
    def rect(x,y,w,h): path([(x,y),(x+w,y),(x+w,y+h),(x,y+h)],True)
    if number in (1,2):
        radius=.70 if number==1 else .9; circle(0,0,radius)
        for i in range(8):
            a=i*math.pi/4; line(((radius+.30)*math.cos(a),(radius+.30)*math.sin(a)),((radius+.65)*math.cos(a),(radius+.65)*math.sin(a)))
    elif number==3:
        rect(-1.5,-1.0,3,2); rect(-1.2,-.7,1.05,1.25); rect(.1,-.7,1.05,.55); rect(.1,.05,1.05,.5)
    elif number==4:
        circle(-.3,.3,.95); line((.4,-.4),(1.5,-1.5))
    elif number==5:
        rect(-.38,-.10,.76,1.65); path([(-.9,.2),(-.9,-.55),(0,-1.0),(.9,-.55),(.9,.2)])
        line((0,-1.0),(0,-1.5)); line((-.6,-1.5),(.6,-1.5))
    elif number==6:
        path([(math.cos(a)*1.25,math.sin(a)*1.25) for a in [math.radians(v) for v in range(70,301,10)]])
        path([(.65,-1.08),(-.2,-.5),(-.5,.3),(.43,1.18)])
    elif number in (7,9):
        direction=-1 if number==7 else 1
        for x in (-.9,.6): path([(direction*(x-.6),-1),(direction*(x+.7),0),(direction*(x-.6),1)],True)
        line((direction*1.7,-1.15),(direction*1.7,1.15))
    elif number==8:
        path([(-1.4,-1.1),(.1,0),(-1.4,1.1)],True); line((.65,-1.1),(.65,1.1)); line((1.35,-1.1),(1.35,1.1))
    else:
        path([(-1.5,-.45),(-.85,-.45),(-.10,-1.05),(-.10,1.05),(-.85,.45),(-1.5,.45)],True)
        if number==10:
            line((.45,-.65),(1.45,.65)); line((.45,.65),(1.45,-.65))
        else:
            for radius in ((.75,) if number==11 else (.75,1.35)):
                path([(.0+radius*math.cos(math.radians(a)),radius*math.sin(math.radians(a))) for a in range(-50,51,10)])
    vertices=[]; faces=[]
    for (ax,ay),(bx,by) in strokes:
        dx,dy=bx-ax,by-ay; length=math.hypot(dx,dy); nx,ny=-dy/length*.065,dx/length*.065
        start=len(vertices)
        vertices.extend((x*.001,y*.001,0) for x,y in ((ax+nx,ay+ny),(ax-nx,ay-ny),(bx-nx,by-ny),(bx+nx,by+ny)))
        faces.append((start,start+1,start+2,start+3))
    mesh=bpy.data.meshes.new(name+'_ICON'); mesh.from_pydata(vertices,[],faces); mesh.update()
    obj=bpy.data.objects.new(name,mesh); collection.objects.link(obj); obj.parent=parent; obj.location=location
    mesh.materials.append(material); obj['function_icon']=number
    return obj
