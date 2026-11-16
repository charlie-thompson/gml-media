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
A=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"assets")
STYLES=["classic","eagle","hosts","emblem"]
def _asset(n): return Image.open(os.path.join(A,n))
def _fit(im,w,h,cx=0.5,cy=0.5):
    """Cover-crop im to w x h around the (cx,cy) fraction point."""
    s=max(w/im.width,h/im.height);im=im.resize((int(im.width*s+1),int(im.height*s+1)),Image.LANCZOS)
    x=int(min(max(im.width*cx-w/2,0),im.width-w));y=int(min(max(im.height*cy-h/2,0),im.height-h))
    return im.crop((x,y,x+w,y+h))
def _mono(width):
    m=_asset("monogram_white_gold.png").convert("RGBA");m=m.crop(m.getbbox())
    return m.resize((width,int(m.height*width/m.width)),Image.LANCZOS)
def pick_style(quote):
    """Deterministic rotation so the feed mixes looks without repeating the same quote's style."""
    import hashlib
    return STYLES[int(hashlib.md5(quote.encode()).hexdigest(),16)%len(STYLES)]
def _text_block(d,quote,speaker,top,height,center=False):
    maxw=W-160
    for size in range(84,38,-2):
        f=ImageFont.truetype(F+"InterDisplay-ExtraBold.otf",size)
        lines=wrap(d,quote,f,maxw);lh=int(size*1.22)
        if lh*len(lines)<=height: break
    y=top+(height-lh*len(lines))//2
    for l in lines:
        x=(W-d.textlength(l,font=f))//2 if center else 80
        d.text((x,y),l,font=f,fill=WHITE);y+=lh
    if speaker and speaker!="unclear":
        sf=ImageFont.truetype(F+"InterDisplay-SemiBold.otf",40);t=speaker.upper()
        x=(W-d.textlength(t,font=sf))//2 if center else 80
        d.text((x,y+30),t,font=sf,fill=GOLD)
def _footer(im,d,mono=False):
    lg=_mono(230) if mono else logo
    im.paste(lg,(80,H-90-lg.height),lg)
    hf=ImageFont.truetype(F+"InterDisplay-Medium.otf",32)
    h="@GoodMorningLiberty";d.text((W-80-d.textlength(h,font=hf),H-90-30),h,font=hf,fill=(170,170,170))
def card(quote,speaker,out,style=None):
    """style: classic, eagle, hosts, emblem, or None to rotate by quote."""
    style=style or pick_style(quote)
    if style=="eagle":
        bg=_fit(_asset("eagle_background.jpg").convert("RGB"),W,H,0.5,0.5)
        im=Image.blend(bg,Image.new("RGB",(W,H),BG),0.15);d=ImageDraw.Draw(im)
        d.rectangle([0,0,W,14],fill=GOLD)
        ov=Image.new("RGBA",(W,H),(0,0,0,0));od=ImageDraw.Draw(ov);od.rectangle([50,300,W-50,1010],fill=(0,0,0,120))
        im=Image.alpha_composite(im.convert("RGBA"),ov).convert("RGB");d=ImageDraw.Draw(im)
        _text_block(d,quote,speaker,330,600,center=True);_footer(im,d,mono=True);im.save(out,quality=95);return out
    if style=="hosts":
        im=Image.new("RGB",(W,H),BG);d=ImageDraw.Draw(im)
        top=_fit(_asset("hosts_thumbnail.jpg").convert("RGB").crop((0,0,2576,860)),W,520,0.5,0.45)
        im.paste(top,(0,0))
        g=Image.new("L",(1,200));[g.putpixel((0,i),int(255*i/199)) for i in range(200)]
        im.paste(Image.new("RGB",(W,200),BG),(0,320),g.resize((W,200)))
        d.rectangle([0,520,W,534],fill=GOLD)
        _text_block(d,quote,speaker,580,520);_footer(im,d,mono=True);im.save(out,quality=95);return out
    if style=="emblem":
        im=Image.new("RGB",(W,H),BG);d=ImageDraw.Draw(im)
        e=_asset("emblem_gold.png").convert("RGB").resize((300,300),Image.LANCZOS)
        mk=Image.new("L",(300,300),0);ImageDraw.Draw(mk).ellipse([4,4,296,296],fill=255)
        im.paste(e,((W-300)//2,90),mk)
        _text_block(d,quote,speaker,440,620,center=True)
        hf=ImageFont.truetype(F+"InterDisplay-Medium.otf",32);h="@GoodMorningLiberty"
        d.text(((W-d.textlength(h,font=hf))//2,H-110),h,font=hf,fill=(170,170,170))
        d.rectangle([0,H-14,W,H],fill=GOLD);im.save(out,quality=95);return out
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
    im.save(out,quality=95);return out
if __name__=="__main__":
    for i,(q,s,o) in enumerate(json.load(open(sys.argv[1]))): card(q,s,o)

def cover(title, out):
    """Carousel cover slide: big hook title."""
    im=Image.new("RGB",(W,H),BG);d=ImageDraw.Draw(im)
    d.rectangle([0,0,W,14],fill=GOLD)
    maxw=W-160
    for size in range(110,50,-4):
        f=ImageFont.truetype(F+"InterDisplay-Black.otf",size)
        lines=wrap(d,title.upper(),f,maxw);lh=int(size*1.12)
        if lh*len(lines)<=700: break
    y=260+(700-lh*len(lines))//2
    for i,l in enumerate(lines):
        d.text((80,y),l,font=f,fill=GOLD if i==len(lines)-1 else WHITE);y+=lh
    sf=ImageFont.truetype(F+"InterDisplay-SemiBold.otf",38)
    d.text((80,H-260),"SWIPE →",font=sf,fill=(170,170,170))
    im.paste(logo,(80,H-90-logo.height),logo)
    im.save(out,quality=95)

def end_slide(out):
    """Carousel closing slide: call to action."""
    im=Image.new("RGB",(W,H),BG);d=ImageDraw.Draw(im)
    d.rectangle([0,0,W,14],fill=GOLD)
    f=ImageFont.truetype(F+"InterDisplay-Black.otf",88)
    y=420
    for l,c in (("FULL EPISODES",WHITE),("EVERY WEEKDAY",GOLD)):
        d.text((80,y),l,font=f,fill=c);y+=110
    sf=ImageFont.truetype(F+"InterDisplay-Medium.otf",44)
    d.text((80,y+40),"Follow @GoodMorningLiberty",font=sf,fill=(200,200,200))
    im.paste(logo,(80,H-90-logo.height),logo)
    im.save(out,quality=95)

def carousel(title, quotes, out_prefix, style=None):
    """quotes: list of (quote, speaker). Writes cover, quote slides, end slide. Returns paths in order.
    All quote slides share one style (rotates by title when style is None)."""
    style=style or pick_style(title)
    paths=[f"{out_prefix}_0.jpg"];cover(title,paths[0])
    for i,(q,s) in enumerate(quotes,1):
        p=f"{out_prefix}_{i}.jpg";card(q,s,p,style);paths.append(p)
    p=f"{out_prefix}_{len(quotes)+1}.jpg";end_slide(p);paths.append(p)
    return paths
