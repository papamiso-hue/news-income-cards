"""카드뉴스 생성기. 사용법: python3 tools/make_cards.py spec.json OUT_DIR
spec.json 예:
{"cover_top":"11월부터","cover_main":"달라지는\\n생활 제도\\n4가지","cover_sub":"오늘 1분이면 정리 끝  →","cover_src":"출처: 정책브리핑(korea.kr)",
 "items":[{"date":"11월 9일","title":"제목\\n두 줄","body":"본문","note":"참고(없으면 null)","src":"출처: ..."}],   # 2~3개
 "end_title":"내 생활에\\n해당되는 건\\n몇 개였나요?","end_sub":"도움이 됐다면 저장해 두고,\\n필요한 가족에게 공유해 주세요.","end_src":"출처: ... (확인일)\\n시행일은 바뀔 수 있어요. 정보 제공용이며 법률·투자 자문이 아닙니다."}
출력: OUT_DIR/insta/card_N.jpg (1080x1350), OUT_DIR/tiktok/card_N.jpg (1080x1920). 총 장수 = items+2.
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont
spec = json.load(open(sys.argv[1], encoding="utf-8")); OUT = sys.argv[2]
NAVY=(27,50,71); YEL=(255,184,28); WHITE=(245,246,247); SOFT=(160,180,198); DIM=(120,144,164)
D="/usr/share/fonts/opentype/noto/NotoSansCJK-"
def font(w,s): return ImageFont.truetype(f"{D}{w}.ttc", s, index=1)
def wrap(d,t,f,mw):
    out=[]
    for para in t.split("\n"):
        cur=""
        for word in para.split(" "):
            x=(cur+" "+word) if cur else word
            if d.textlength(x,font=f)<=mw: cur=x; continue
            if cur: out.append(cur)
            cur=""
            for ch in word:
                if d.textlength(cur+ch,font=f)<=mw: cur+=ch
                else: out.append(cur); cur=ch
        out.append(cur)
    return out
def block(d,t,f,x,y,c,mw,g=1.35):
    for l in wrap(d,t,f,mw): d.text((x,y),l,font=f,fill=c); y+=int(f.size*g)
    return y
def make(kind,n,total,H,top,draw_fn):
    W=1080; im=Image.new("RGB",(W,H),NAVY); d=ImageDraw.Draw(im); o=top
    d.rounded_rectangle((80,80+o,92,128+o),radius=6,fill=YEL); d.text((112,82+o),"1분 생활경제",font=font("Bold",40),fill=YEL)
    x=W-80-total*36
    for i in range(total): d.ellipse((x+i*36,96+o,x+i*36+18,114+o),fill=YEL if i==n-1 else (70,96,120))
    draw_fn(d,W,H,o); return im
def run(kind,H,o):
    items=spec["items"]; total=len(items)+2; os.makedirs(f"{OUT}/{kind}",exist_ok=True); cards=[]
    def cover(d,W,H,o):
        d.text((80,360+o*2//1 if False else 360+o*2),spec["cover_top"],font=font("Black",150),fill=YEL) if False else None
        base=360+(o*2 if kind=="tiktok" else 0)
        d.text((80,base),spec["cover_top"],font=font("Black",150),fill=YEL)
        y=block(d,spec["cover_main"],font("Black",150),80,base+180,WHITE,W-160,1.18)
        d.text((80,y+30),spec["cover_sub"],font=font("Medium",46),fill=SOFT)
        d.text((80,H-130-(200 if kind=="tiktok" else 0)),spec["cover_src"],font=font("Regular",32),fill=DIM)
    cards.append(make(kind,1,total,H,o,cover))
    for i,it in enumerate(items):
        def content(d,W,H,o,it=it):
            b=(300+o*2) if kind=="tiktok" else 300
            d.text((80,b),it["date"],font=font("Black",120),fill=YEL); d.rectangle((80,b+170,240,b+178),fill=YEL)
            y=block(d,it["title"],font("Black",74),80,b+240,WHITE,W-160,1.3)
            y=block(d,it["body"],font("Medium",48),80,y+40,SOFT,W-160,1.5)
            if it.get("note"): block(d,it["note"],font("Regular",36),80,y+40,DIM,W-160,1.5)
            d.text((80,H-130-(200 if kind=="tiktok" else 0)),it["src"],font=font("Regular",32),fill=DIM)
        cards.append(make(kind,i+2,total,H,o,content))
    def end(d,W,H,o):
        b=(330+o*2) if kind=="tiktok" else 330
        y=block(d,spec["end_title"],font("Black",110),80,b,WHITE,W-160,1.25)
        d.rectangle((80,y+20,240,y+28),fill=YEL)
        block(d,spec["end_sub"],font("Medium",46),80,y+70,SOFT,W-160,1.5)
        block(d,spec["end_src"],font("Regular",32),80,H-210-(200 if kind=="tiktok" else 0),DIM,W-160,1.5)
    cards.append(make(kind,total,total,H,o,end))
    for i,c in enumerate(cards): c.save(f"{OUT}/{kind}/card_{i+1}.jpg",quality=88)
run("insta",1350,0); run("tiktok",1920,120)
print("ok", len(spec["items"])+2, "cards")
