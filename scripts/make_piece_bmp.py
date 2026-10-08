#!/usr/bin/env python3
"""Generate a native 17 x 1 YixinBoard BMP sprite atlas; standard library only.

YixinBoard obtains tile width from the bitmap HEIGHT.  The bitmap consists of
17 square horizontal sprites.  Sprite 16 is the transparency key for overlays.
"""
from pathlib import Path
import argparse
import math
import struct

W = 44
COUNT = 17
BOARD = (232, 205, 159)
LINE = (107, 76, 46)
DARK = (28, 35, 43)
LIGHT = (249, 250, 248)
GOLD = (211, 137, 54)

def make(path):
    width, height = W * COUNT, W
    pixels = [[list(BOARD) for _ in range(width)] for __ in range(height)]
    def dot(tile, x, y, color):
        if 0 <= x < W and 0 <= y < W:
            pixels[y][tile * W + x] = list(color)
    def line(tile, x1, y1, x2, y2, color, thickness=1):
        steps = int(max(abs(x2-x1), abs(y2-y1))) + 1
        for k in range(steps+1):
            t = k / steps
            x = round(x1+(x2-x1)*t)
            y = round(y1+(y2-y1)*t)
            for dy in range(-thickness//2+1, thickness//2+1):
                for dx in range(-thickness//2+1, thickness//2+1):
                    dot(tile,x+dx,y+dy,color)
    def disk(tile, cx, cy, radius, color):
        for y in range(W):
            for x in range(W):
                if (x-cx)**2+(y-cy)**2 <= radius*radius:
                    dot(tile,x,y,color)
    mid = W//2
    # 0: normal intersection. 1: top-left corner. 2: top edge.
    line(0,0,mid,W-1,mid,LINE)
    line(0,mid,0,mid,W-1,LINE)
    line(1,mid,mid,W-1,mid,LINE)
    line(1,mid,mid,mid,W-1,LINE)
    line(2,0,mid,W-1,mid,LINE)
    line(2,mid,mid,mid,W-1,LINE)
    # 3/4: clean, slightly dimensional black/white stones.
    for tile,base in ((3,DARK),(4,LIGHT)):
        disk(tile,mid+1,mid+2,17,(153,132,103))  # shadow
        disk(tile,mid,mid,17,base)
        if tile == 3:
            disk(tile,mid-5,mid-6,8,(52,61,69))
            disk(tile,mid-8,mid-9,3,(87,98,106))
        else:
            disk(tile,mid-4,mid-6,10,(255,255,255))
            for a in range(65,180):
                rad=math.radians(a)
                dot(tile,round(mid+16*math.cos(rad)),round(mid+16*math.sin(rad)),(187,186,180))
    # 5/6: selection markers; 7-15: engine annotations.
    disk(5,mid,mid,9,(222,81,69))
    disk(5,mid,mid,5,(255,219,199))
    disk(6,mid,mid,6,GOLD)
    disk(6,mid,mid,3,(255,245,206))
    colors=[(45,142,119),(61,124,210),(181,104,68),(194,69,92),
            (129,98,180),(45,142,119),(211,137,54),(52,117,147),(111,127,151)]
    for tile, color in enumerate(colors,start=7):
        disk(tile,mid,mid,12,color)
        disk(tile,mid,mid,9,BOARD)
        disk(tile,mid,mid,5,color)
    # 16: pure board color. Source samples pixel (tile16, x0, y3) as key.
    row_stride=(width*3+3)&~3
    img_size=row_stride*height
    path=Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("wb") as f:
        f.write(b"BM")
        f.write(struct.pack("<IHHI",54+img_size,0,0,54))
        f.write(struct.pack("<IiiHHIIiiII",40,width,height,1,24,0,img_size,2835,2835,0,0))
        for row in reversed(pixels):
            out=bytearray()
            for red,green,blue in row:
                out.extend((blue,green,red))
            out.extend(bytes(row_stride-len(out)))
            f.write(out)
    assert path.stat().st_size == 54+img_size
    print(f"Created {path} ({width}x{height}, 24-bit BMP, {path.stat().st_size} bytes)")

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("output",nargs="?",default="piece.bmp")
    args=parser.parse_args()
    make(args.output)
