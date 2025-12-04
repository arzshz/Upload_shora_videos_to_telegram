from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).resolve().parent


def thumbnail_creator(image_path=f"{BASE_DIR}/images/base.jpg", title="", name=""):
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)

    persian_font = ImageFont.truetype(f"{BASE_DIR}/fonts/B_Zar_Bold_0.ttf", size=100)

    image_width, image_height = image.size

    lines = title.split("\n")

    # Measure line height using bbox
    sample_bbox = draw.textbbox((0, 0), "Ay", font=persian_font)
    line_height = sample_bbox[3] - sample_bbox[1]

    line_spacing = 90

    # Compute total text height
    total_text_height = len(lines) * line_height + (len(lines) - 1) * line_spacing
    text_y = (image_height - total_text_height) // 2

    for index, line in enumerate(lines):
        if line.strip():
            # Proper width calculation
            bbox = draw.textbbox((0, 0), line, font=persian_font)
            text_width = bbox[2] - bbox[0]

            text_x = (image_width - text_width) // 2

            outline_offset = 2

            # Draw outline
            for dx in [-outline_offset, 0, outline_offset]:
                for dy in [-outline_offset, 0, outline_offset]:
                    draw.text(
                        (text_x + dx, text_y + dy),
                        line,
                        font=persian_font,
                        fill="black",
                    )

            # Draw main text
            draw.text((text_x, text_y), line, font=persian_font, fill="white")

            text_y += line_height + line_spacing

    image.save(f"{BASE_DIR}/thumbnails/{name}.jpg")
    return f"{BASE_DIR}/thumbnails/{name}.jpg"
