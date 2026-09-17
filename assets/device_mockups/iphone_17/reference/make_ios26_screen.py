from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path
import math
W,H=1206,2622
out=Path(__file__).with_name('ios26_home_screen_1206x2622.png')
im=Image.new('RGB',(W,H),(18,22,35)); px=im.load()
for y in range(H):
    for x in range(W):
        nx=(x-W*.58)/W; ny=(y-H*.38)/H
        glow=max(0,1-math.sqrt(nx*nx*2.4+ny*ny*1.3)*2.2)
        px[x,y]=(int(18+75*glow),int(22+55*glow),int(35+115*glow))
d=ImageDraw.Draw(im,'RGBA')
font='/Windows/Fonts/segoeui.ttf'; bold='/Windows/Fonts/seguisb.ttf'
def f(path,size): return ImageFont.truetype(path,size)
d.text((58,45),'9:41',font=f(bold,48),fill='white')
d.rounded_rectangle((945,57,1030,87),15,outline='white',width=5); d.rectangle((1033,66,1040,78),fill='white'); d.rounded_rectangle((951,63,1019,81),9,fill='white')
# widget
d.rounded_rectangle((64,245,1142,665),54,fill=(245,247,255,52),outline=(255,255,255,72),width=2)
d.text((110,300),'Tuesday',font=f(font,44),fill=(255,255,255,210)); d.text((108,350),'16',font=f(bold,150),fill='white'); d.text((300,385),'September',font=f(font,54),fill=(255,255,255,220))
# generic iOS-style app grid, intentionally not copying proprietary app artwork
labels=['Photos','Camera','Maps','Weather','Notes','Clock','Files','Music','Mail','Safari','Home','Settings']
cols=4; x0=95; gap=278; y0=790; vgap=310
for i,label in enumerate(labels):
    c=i%cols; r=i//cols; x=x0+c*gap; y=y0+r*vgap
    hue=[(250,250,252),(50,54,62),(90,170,255),(70,150,255),(255,224,90),(25,28,34),(70,145,255),(245,70,115),(70,145,255),(80,170,255),(245,145,65),(150,155,165)][i]
    d.rounded_rectangle((x,y,x+176,y+176),42,fill=hue+(245,),outline=(255,255,255,80),width=2)
    d.ellipse((x+58,y+58,x+118,y+118),fill=(255,255,255,190))
    tw=d.textbbox((0,0),label,font=f(font,29)); d.text((x+88-(tw[2]-tw[0])/2,y+190),label,font=f(font,29),fill='white')
# translucent dock
d.rounded_rectangle((70,2240,1136,2490),68,fill=(235,240,255,70),outline=(255,255,255,90),width=2)
for i,col in enumerate(((65,185,95),(55,125,245),(60,170,255),(245,70,105))):
    x=125+i*260; d.rounded_rectangle((x,2275,x+175,2450),42,fill=col+(245,)); d.ellipse((x+58,2333,x+117,2392),fill=(255,255,255,205))
d.rounded_rectangle((425,2565,781,2582),9,fill=(255,255,255,210))
im.save(out,optimize=True)
print(out)