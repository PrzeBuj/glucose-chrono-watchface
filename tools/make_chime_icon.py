from PIL import Image, ImageDraw
S=8; W=96
img=Image.new("RGBA",(W*S,W*S),(0,0,0,0)); d=ImageDraw.Draw(img)
d.ellipse([0,0,W*S-1,W*S-1],fill=(16,18,21,255))
c=W*S/2
# tarcza zegarka
r=30*S
d.ellipse([c-r,c-r-2*S,c+r,c+r-2*S],outline=(244,245,247,255),width=5*S)
d.line([c,c-2*S,c,c-20*S],fill=(244,245,247,255),width=5*S)
d.line([c,c-2*S,c+13*S,c-2*S],fill=(244,245,247,255),width=5*S)
# fale dźwięku
for k,rr in enumerate((38,46)):
    a=(77,163,255,255)
    d.arc([c-rr*S,c-rr*S-2*S,c+rr*S,c+rr*S-2*S],start=-35,end=35,fill=a,width=4*S)
    d.arc([c-rr*S,c-rr*S-2*S,c+rr*S,c+rr*S-2*S],start=145,end=215,fill=a,width=4*S)
img.resize((192,192),Image.LANCZOS).save("chime/src/main/res/drawable-nodpi/ic_launcher.png")
