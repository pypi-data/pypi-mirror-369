from PIL import Image

img = Image.new("P", (800, 480))

for x in range(256):
    for y in range(256):
        img.putpixel((x, y), (x, 0, 0))

img.save("test.png")
