import urllib.request
import os

# Agar image web par ho to direct download kar sakte hain, ya local logo.png ko use karein
if os.path.exists("logo.png"):
    from PIL import Image
    img = Image.open("logo.png")
    img.save("app_icon.ico", format="ICO", sizes=[(256, 256), (128, 128), (64, 64), (32, 32)])
    print("✔ New aesthetic icon saved as app_icon.ico!")
else:
    print("Pehle apni AI image ko 'logo.png' ke naam se folder mein paste karein.")
