import os
import platform
import random
from io import BytesIO

import requests
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

from config import DISPLAY_MODE

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "..", "Assets")

if DISPLAY_MODE == "screen":
    FONT_PATH = os.path.join(
        ASSETS_DIR, "Fonts", "Outfit", "Outfit-VariableFont_wght.ttf")
else:
    FONT_PATH = os.path.join(BASE_DIR, "..", "Assets",
                             "Fonts", "Outfit", "Outfit-VariableFont_wght.ttf")


VINYL_PATH = os.path.join(ASSETS_DIR, "vinyl.png")
OUTPUT_PATH = os.path.join(BASE_DIR, "..", "current.png")


class DisplayManager:
    def __init__(self, width=600, height=400):
        self.width = width
        self.height = height
        self.output_path = OUTPUT_PATH
        self.mode = DISPLAY_MODE

        self.font_title = ImageFont.truetype(FONT_PATH, 40)
        self.font_sub = ImageFont.truetype(FONT_PATH, 15)
        self.font_small = ImageFont.truetype(FONT_PATH, 15)

        if self.mode == "eink":
            from waveshare_epd import epd3in6e
            self.epd = epd3in6e.EPD()
            self.epd.init()
            self.epd.Clear()

    def fetch_art(self, url):
        if not url:
            return Image.new("RGB", (self.height, self.height), "gray")
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        return img.resize((self.height, self.height))

    def render(self, track):
        # ~~~~~~~~~~~~~~ Canvas ~~~~~~~~~~~~~~
        canvas = self.fetch_art(track.album_art_url).resize(
            (self.width, self.height))
        canvas = canvas.filter(ImageFilter.GaussianBlur(radius=8))
        # ~~~~~~~~~~~~~~ Canvas ~~~~~~~~~~~~~~

        overlay = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        ImageDraw.Draw(overlay).rectangle(
            [0, 0, self.width, self.height], fill=(255, 255, 255, 80))
        canvas = canvas.convert("RGBA")
        canvas = Image.alpha_composite(canvas, overlay)
        canvas = canvas.convert("RGB")

        draw = ImageDraw.Draw(canvas)

        # ~~~~~~~~~~~~~~ Vinyl ~~~~~~~~~~~~~~
        pallette = [(119, 183, 208), (132, 0, 136), (135, 189, 197),
                    (208, 19, 67), (203, 85, 67), (110, 119, 84),
                    (139, 94, 142), (255, 90, 90), (218, 255, 0),
                    (255, 87, 51), (255, 173, 5), (147, 205, 120),
                    (102, 190, 203), (168, 230, 207), (220, 237, 193),
                    (255, 211, 182), (255, 139, 148), (206, 151, 251),
                    (246, 165, 235), (250, 169, 157), (253, 223, 126),
                    (103, 235, 250)]

        ic_color = random.choice(pallette)
        ic_radius = 40
        oc_color = random.choice(pallette)
        oc_radius = 62

        vinyl_center_x = 333
        vinyl_center_y = self.height // 2

        draw.ellipse(
            (vinyl_center_x - oc_radius, vinyl_center_y - oc_radius,
             vinyl_center_x + oc_radius, vinyl_center_y + oc_radius),
            fill=oc_color)
        draw.ellipse(
            (vinyl_center_x - ic_radius, vinyl_center_y - ic_radius,
             vinyl_center_x + ic_radius, vinyl_center_y + ic_radius),
            fill=ic_color)
        draw.ellipse(
            (vinyl_center_x - 62, vinyl_center_y - 62,
             vinyl_center_x + 62, vinyl_center_y + 62),
            fill="white")

        vinyl = Image.open(VINYL_PATH).resize((262, 262)).convert("RGBA")
        vinyl = vinyl.rotate(random.randint(0, 360))
        vinyl_coords = (vinyl_center_x - 131, vinyl_center_y - 131)
        canvas.paste(im=vinyl, box=vinyl_coords, mask=vinyl)
        # ~~~~~~~~~~~~~~ Vinyl ~~~~~~~~~~~~~~

        # ~~~~~~~~~~~~~~ Artist ~~~~~~~~~~~~~~
        artist_art = self.fetch_art(track.artist_art_url).resize((86, 86))
        artist_mask = Image.new("L", (86, 86), 0)
        ImageDraw.Draw(artist_mask).ellipse((0, 0, 86, 86), fill=255)
        artist_art = ImageOps.fit(artist_art, (86, 86), centering=(0.5, 0.5))

        canvas.paste(im=artist_art,
                     box=(vinyl_center_x - 43, vinyl_center_y - 43),
                     mask=artist_mask)

        outline_box = (vinyl_center_x - 43, vinyl_center_y - 43,
                       vinyl_center_x + 43, vinyl_center_y + 43)
        draw.ellipse(outline_box, outline="gray", width=1)
        # ~~~~~~~~~~~~~~ Artist ~~~~~~~~~~~~~~

        # ~~~~~~~~~~~~~~ Album ~~~~~~~~~~~~~~
        album_art = self.fetch_art(track.album_art_url).resize((272, 272))
        border_album = ImageOps.expand(album_art, border=2, fill='black')
        canvas.paste(border_album, (43, (self.height - 276) // 2))
        canvas.paste(album_art, (45, (self.height - 272) // 2))
        # ~~~~~~~~~~~~~~ Album ~~~~~~~~~~~~~~

        # ~~~~~~~~~~~~~~ Text ~~~~~~~~~~~~~~
        text_x = self.height + 16
        draw.text((text_x, 20), track.name, font=self.font_title,
                  fill="white", stroke_width=2, stroke_fill="black")
        draw.text((text_x, 80), track.artist, font=self.font_sub,
                  fill="white", stroke_width=1, stroke_fill="black")
        draw.text((text_x, 110), track.album, font=self.font_small,
                  fill="white", stroke_width=1, stroke_fill="black")
        # ~~~~~~~~~~~~~~ Text ~~~~~~~~~~~~~~

        canvas.save(self.output_path)

        if self.mode == "eink":
            image = Image.open(self.output_path)
            self.epd.display(self.epd.getbuffer(image))

    def clear(self):
        canvas = Image.new("RGB", (self.width, self.height), "black")
        canvas.save(self.output_path)
        if self.mode == "eink":
            self.epd.Clear()
