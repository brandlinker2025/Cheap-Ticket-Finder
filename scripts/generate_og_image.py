"""Generate assets/og-image.png (1200x630) — colourful bright sky->mint->peach, gold accent.
No invented prices, no airline logos. Text: brand + Bengali tagline."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import glob, math, os
W,H=1200,630
def find_font(*names):
    fonts=glob.glob("/usr/share/fonts/**/*.ttf", recursive=True)+glob.glob("/usr/share/fonts/**/*.otf", recursive=True)
    for n in names:
        for f in fonts:
            if n.lower() in os.path.basename(f).lower(): return f
    return fonts[0]
latin_b=find_font("Poppins-Bold","Montserrat-Bold","DejaVuSans-Bold","NotoSans-Bold")
latin_sb=find_font("Poppins-SemiBold","Poppins-Medium","DejaVuSans-Bold","NotoSans-Bold")
beng_b=find_font("Mina-Bold","NotoSansBengali-Bold","Atma-Bold","NotoSans-Bold")
def lerp(a,b,t): return tuple(int(a[i]+(b[i]-a[i])*t) for i in range(3))
sky=(56,189,248); mint=(110,231,183); peach=(254,215,170)
img=Image.new("RGB",(W,H)); px=img.load()
for y in range(H):
    for x in range(W):
        t=(x/W*0.65+y/H*0.35)
        px[x,y]=lerp(sky,mint,t*2) if t<0.5 else lerp(mint,peach,(t-0.5)*2)
img=img.filter(ImageFilter.GaussianBlur(0.4)); d=ImageDraw.Draw(img,"RGBA")
for cx,cy,r,col in [(1020,90,180,(255,255,255,55)),(1080,520,220,(255,255,255,45)),(120,560,140,(255,255,255,40)),(920,300,90,(245,197,66,55)),(180,110,70,(255,255,255,50))]:
    d.ellipse([cx-r,cy-r,cx+r,cy+r],fill=col)
pts=[(760+360*(i/100),250-150*math.sin((i/100)*math.pi)+40*(i/100)) for i in range(101)]
for i in range(0,len(pts)-1,2): d.line([pts[i],pts[min(i+4,len(pts)-1)]],fill=(15,42,67,110),width=4)
for x,y in [pts[0],pts[-1]]: d.ellipse([x-9,y-9,x+9,y+9],fill=(15,42,67,255),outline=(255,255,255,255),width=3)
cx,cy=pts[-1]
d.polygon([(cx+2,cy-2),(cx+52,cy-28),(cx+34,cy+18),(cx+18,cy+6)],fill=(245,197,66,255),outline=(15,42,67,255))
d.line([(cx+18,cy+6),(cx+52,cy-28)],fill=(15,42,67,255),width=2)
slate=(15,42,67); slate2=(30,64,94)
f_pill=ImageFont.truetype(latin_sb,26); label="CHEAPTICKETFINDER.SITE"
tw=d.textbbox((0,0),label,font=f_pill)[2]
d.rounded_rectangle([70,64,70+tw+44,116],radius=26,fill=(245,197,66,255)); d.text((92,77),label,font=f_pill,fill=slate)
f_title=ImageFont.truetype(latin_b,76)
d.text((70,150),"Cheap Ticket",font=f_title,fill=slate); d.text((70,238),"Finder BD",font=f_title,fill=slate)
d.rounded_rectangle([72,332,372,344],radius=6,fill=(217,164,32,255))
d.text((70,362),"সস্তা ফ্লাইট, হোটেল ও ট্যুর প্যাকেজ",font=ImageFont.truetype(beng_b,54),fill=slate)
d.text((70,452),"Flights  \u2022  Hotels  \u2022  Packages  \u2022  eSIM  \u2022  Transfers",font=ImageFont.truetype(latin_sb,30),fill=slate2)
d.text((70,552),"Real prices checked on the provider \u2014 no invented fares",font=ImageFont.truetype(latin_sb,24),fill=(51,84,110))
out=os.path.join(os.path.dirname(__file__),"..","assets","og-image.png")
img.save(out,optimize=True); print("wrote",out,img.size)
