"""
Zero-Dependency Pure Python Binary .ICO Generator for Grace Outreach Assistant
Creates a valid 32x32 RGBA architectural blueprint icon using standard library only.
"""
import struct

def generate_native_ico(filename="app_icon.ico"):
    width = 32
    height = 32
    
    # 1. Generate 32x32 RGBA Pixels (Blue shield background with gold accent)
    pixels = bytearray()
    
    for y in range(height):
        for x in range(width):
            # Geometric Box / Border calculation
            is_border = (x == 2 or x == width - 3 or y == 2 or y == height - 3)
            is_inner_box = (8 <= x <= 23 and 8 <= y <= 23 and (x in (8, 23) or y in (8, 23)))
            is_center_cross = (x == 15 or y == 15)
            
            if is_inner_box:
                # Gold Accent (#F59E0B)
                b, g, r, a = 11, 158, 245, 255
            elif is_border or is_center_cross:
                # Cyan Architectural Line (#38BDF8)
                b, g, r, a = 248, 189, 56, 255
            else:
                # Dark Navy Background (#0B1324)
                b, g, r, a = 36, 19, 11, 255
                
            pixels.extend([b, g, r, a])
            
    # Bottom-up flip for Windows BMP/DIB bitmap format
    flipped_pixels = bytearray()
    for row in range(height - 1, -1, -1):
        start = row * width * 4
        flipped_pixels.extend(pixels[start:start + width * 4])

    # 2. Build BITMAPINFOHEADER (40 bytes)
    # Note: In ICO format, biHeight must be 2 * height (for XOR + AND masks)
    bih = struct.pack('<IIIHHIIIIII', 
                      40,            # biSize
                      width,         # biWidth
                      height * 2,    # biHeight (XOR mask + AND mask)
                      1,             # biPlanes
                      32,            # biBitCount (32-bit RGBA)
                      0,             # biCompression (BI_RGB)
                      len(flipped_pixels), # biSizeImage
                      0, 0, 0, 0)

    # 1bpp AND Mask (32 rows * 4 bytes per row = 128 bytes of zeros for full alpha visibility)
    and_mask = b'\x00' * (height * 4)

    image_data = bih + flipped_pixels + and_mask
    image_size = len(image_data)

    # 3. Build ICONDIR (6 bytes) + ICONDIRENTRY (16 bytes)
    icondir = struct.pack('<HHH', 0, 1, 1) # Reserved(0), Type(1 for icon), Count(1 image)
    
    # Width, Height, ColorCount, Reserved, Planes, BitCount, BytesInRes, ImageOffset
    offset = 6 + 16 # Header (6) + 1 Entry (16) = 22 bytes offset
    direntry = struct.pack('<BBBBHHII', 
                           width, height, 0, 0, 1, 32, image_size, offset)

    # 4. Write pure binary ICO file
    with open(filename, 'wb') as f:
        f.write(icondir)
        f.write(direntry)
        f.write(image_data)
        
    print(f"✔ Native Architectural Icon successfully generated: {filename}")

if __name__ == "__main__":
    generate_native_ico()
