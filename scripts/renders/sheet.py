import sys
from PIL import Image
names = sys.argv[1:] or ["deluge","companion","sealegs","stolperbeats","stages"]
ims = [Image.open(f"out/{n}.png").resize((800,500)) for n in names]
cols = 2; rows = (len(ims)+1)//2
sh = Image.new("RGB", (1600, 500*rows), (40,40,40))
for i, im in enumerate(ims): sh.paste(im, ((i%cols)*800, (i//cols)*500))
sh.save("out/sheet.png")
