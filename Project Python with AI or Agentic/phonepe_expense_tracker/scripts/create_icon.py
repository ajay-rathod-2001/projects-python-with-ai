"""
Generate high-fidelity PhonePe Windows Application Icon (.ico)
"""

from pathlib import Path
from PIL import Image, ImageDraw

def create_phonepe_icon(output_path: Path):
    sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
    images = []

    for width, height in sizes:
        # Create transparent RGBA canvas
        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Scale parameters
        pad = max(1, width // 16)
        radius = max(2, width // 4)

        # Purple rounded squircle background
        # #5F259F is PhonePe brand purple
        draw.rounded_rectangle(
            [pad, pad, width - pad, height - pad],
            radius=radius,
            fill=(95, 37, 159, 255),
            outline=(139, 92, 246, 200),
            width=max(1, width // 40),
        )

        scale = width / 64.0

        # Devanagari 'Pe' (पे) glyph representation in white
        # Top horizontal bar (Shirorekha)
        x1 = int(17 * scale)
        y1 = int(19 * scale)
        x2 = int(47 * scale)
        y2 = int(23 * scale)
        draw.rectangle([x1, y1, x2, y2], fill=(255, 255, 255, 255))

        # Main vertical stem
        sx1 = int(34 * scale)
        sy1 = int(21 * scale)
        sx2 = int(38 * scale)
        sy2 = int(47 * scale)
        draw.rectangle([sx1, sy1, sx2, sy2], fill=(255, 255, 255, 255))

        # Pa curve / loop
        lx1 = int(23 * scale)
        ly1 = int(23 * scale)
        lx2 = int(35 * scale)
        ly2 = int(38 * scale)
        line_w = max(1, int(3.5 * scale))
        draw.arc([lx1, ly1, lx2, ly2], start=0, end=180, fill=(255, 255, 255, 255), width=line_w)
        draw.line([(lx1, int(23 * scale)), (lx1, int(31 * scale))], fill=(255, 255, 255, 255), width=line_w)

        # Accent Gold Dot (Bindu)
        dot_r = max(1, int(2.5 * scale))
        dot_x = int(41 * scale)
        dot_y = int(14 * scale)
        draw.ellipse([dot_x - dot_r, dot_y - dot_r, dot_x + dot_r, dot_y + dot_r], fill=(245, 158, 11, 255))

        images.append(img)

    # Save as multi-resolution .ico
    output_path.parent.mkdir(parents=True, exist_ok=True)
    images[0].save(
        output_path,
        format="ICO",
        sizes=[(s[0], s[1]) for s in sizes],
        append_images=images[1:],
    )
    print(f"Icon successfully generated at: {output_path}")

if __name__ == "__main__":
    icon_file = Path(__file__).resolve().parent.parent / "data" / "phonepe.ico"
    create_phonepe_icon(icon_file)

