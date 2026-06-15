import os
import math
try:
    from PIL import Image, ImageDraw
except ImportError:
    print("Pillow not installed, installing it...")
    os.system("pip install Pillow")
    from PIL import Image, ImageDraw

def create_icon(size):
    # Deep dark purple background matching the Dark Fantasy Minimal theme
    img = Image.new("RGBA", (size, size), (20, 18, 30, 255))
    draw = ImageDraw.Draw(img)
    
    # Elegant elven gold outer ring
    margin = size // 10
    draw.ellipse([margin, margin, size - margin, size - margin], outline=(212, 175, 55, 255), width=max(2, size // 40))
    
    # Cyan magical circle inner ring
    margin2 = size // 5
    draw.ellipse([margin2, margin2, size - margin2, size - margin2], outline=(77, 238, 234, 255), width=max(1, size // 80))
    
    # 5-Pointed star mapping
    center = size // 2
    r = size // 4
    points = []
    for i in range(5):
        angle = i * 4 * math.pi / 5 - math.pi / 2
        x = center + r * math.cos(angle)
        y = center + r * math.sin(angle)
        points.append((x, y))
    
    # Draw star lines
    for i in range(5):
        draw.line([points[i], points[(i+1)%5]], fill=(212, 175, 55, 255), width=max(1, size // 100))
        
    return img

if __name__ == "__main__":
    os.makedirs("frontend/assets", exist_ok=True)
    create_icon(192).save("frontend/assets/icon-192.png")
    create_icon(512).save("frontend/assets/icon-512.png")
    print("Icons generated successfully in frontend/assets!")
