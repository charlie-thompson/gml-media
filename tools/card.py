import json,sys,textwrap
from PIL import Image,ImageDraw,ImageFont
W,H=1080,1350;BG=(15,15,15);GOLD=(255,193,3);WHITE=(245,245,245)
F="/usr/share/fonts/opentype/inter/"
import os
logo=Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"logo.png")).convert("RGBA")
logo=logo.crop(logo.convert("L").point(lambda v:255 if v>40 else 0).getbbox())
lw=420;logo=logo.resize((lw,int(logo.height*lw/logo.width)),Image.LANCZOS)
def wrap(d,txt,font,maxw):
    words=txt.split();lines=[];cur=""
    for w in words:
        t=(cur+" "+w).strip()
        if d.textlength(t,font=font)<=maxw: cur=t
        else: lines.append(cur);cur=w
    lines.append(cur);return lines
def card(quote,speaker,out):
    im=Image.new("RGB",(W,H),BG);d=ImageDraw.Draw(im)
    d.rectangle([0,0,W,14],fill=GOLD)
    qm=ImageFont.truetype(F+"InterDisplay-Black.otf",260)
    d.text((80,90),"“",font=qm,fill=GOLD)
    maxw=W-160
    for size in range(84,38,-2):
        f=ImageFont.truetype(F+"InterDisplay-ExtraBold.otf",size)
        lines=wrap(d,quote,f,maxw);lh=int(size*1.22)
        if lh*len(lines)<=640: break
    y=330+(640-lh*len(lines))//2
    for l in lines: d.text((80,y),l,font=f,fill=WHITE);y+=lh
    if speaker and speaker!="unclear":
        sf=ImageFont.truetype(F+"InterDisplay-SemiBold.otf",40)
        d.text((80,y+30),speaker.upper(),font=sf,fill=GOLD)
    im.paste(logo,(80,H-90-logo.height),logo)
    hf=ImageFont.truetype(F+"InterDisplay-Medium.otf",32)
    h="@GoodMorningLiberty";d.text((W-80-d.textlength(h,font=hf),H-90-30),h,font=hf,fill=(170,170,170))
    im.save(out,quality=95)
if __name__=="__main__":
    for i,(q,s,o) in enumerate(json.load(open(sys.argv[1]))): card(q,s,o)
