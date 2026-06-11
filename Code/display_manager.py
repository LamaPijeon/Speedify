import os
import platform
import random
from io import BytesIO

import requests
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

from config import DISPLAY_MODE

base_dir = os.path.dirname(os.path.abspath(__file__))
assets_dir = os.path.join(base_dir, "..", "Assets")

font_path = os.path.join(assets_dir, "Fonts", "Outfit",
                         "Outfit-VariableFont_wght.ttf")
vinyl_path = os.path.join(assets_dir, "Pics", "vinyl.png")
output_path = os.path.join(base_dir, "..", "current.png")


class DisplayManager:
    def __init__(self, width=600, height=400):
        self.width = width
        self.height = height
        self.output_path = output_path
        self.mode = DISPLAY_MODE

        self.font_title = ImageFont.truetype(font_path, 40)
        self.font_sub = ImageFont.truetype(font_path, 15)
        self.font_small = ImageFont.truetype(font_path, 15)

        if self.mode == "eink":
            from waveshare_epd import epd3in6e  # type: ignore
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

        max_text_width = 192
        album_size = 300
        album_x = 16
        album_y = (self.height - album_size) // 2
        text_x = album_x + album_size + 8
        vinyl_center_x = self.width - 8
        vinyl_center_y = self.height // 2

        # ~~~~~~~~~~~~~~ Canvas ~~~~~~~~~~~~~~
        canvas = self.fetch_art(track.album_art_url).resize(
            (self.width, self.height))
        canvas = canvas.filter(ImageFilter.GaussianBlur(radius=8))

        overlay = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        ImageDraw.Draw(overlay).rectangle(
            [0, 0, self.width, self.height], fill=(1, 77, 78, 168))
        canvas = canvas.convert("RGBA")
        canvas = Image.alpha_composite(canvas, overlay)
        canvas = canvas.convert("RGB")
        draw = ImageDraw.Draw(canvas)
        # ~~~~~~~~~~~~~~ Canvas ~~~~~~~~~~~~~~

        # ~~~~~~~~~~~~~~ Vinyl ~~~~~~~~~~~~~~
        pallette = [(119, 183, 208), (132, 0, 136), (135, 189, 197),
                    (208, 19, 67), (203, 85, 67), (110, 119, 84),
                    (139, 94, 142), (255, 90, 90), (218, 255, 0),
                    (255, 87, 51), (255, 173, 5), (147, 205, 120),
                    (102, 190, 203), (168, 230, 207), (220, 237, 193),
                    (255, 211, 182), (255, 139, 148), (206, 151, 251),
                    (246, 165, 235), (250, 169, 157), (253, 223, 126),
                    (103, 235, 250)]

        draw.ellipse(
            (vinyl_center_x - 50, vinyl_center_y - 50,
             vinyl_center_x + 50, vinyl_center_y + 50),
            fill=random.choice(pallette))
        draw.ellipse(
            (vinyl_center_x - 37, vinyl_center_y - 37,
             vinyl_center_x + 37, vinyl_center_y + 37),
            fill=random.choice(pallette))

        vinyl = Image.open(vinyl_path).resize(
            (224, 224)).convert("RGBA")
        vinyl = vinyl.rotate(random.randint(0, 360))
        vinyl_coords = (vinyl_center_x - 112, vinyl_center_y - 112)

        cutoff_local = (text_x + max_text_width + 4) - vinyl_coords[0]
        vinyl_cropped = vinyl.crop(
            (cutoff_local, 0, vinyl.size[0], vinyl.size[1]))
        crop_coords = (vinyl_coords[0] + cutoff_local, vinyl_coords[1])

        canvas.paste(im=vinyl_cropped, box=crop_coords, mask=vinyl_cropped)
        # ~~~~~~~~~~~~~~ Vinyl ~~~~~~~~~~~~~~

        # ~~~~~~~~~~~~~~ Artist ~~~~~~~~~~~~~~
        artist_art = self.fetch_art(track.artist_art_url).resize((86, 86))
        artist_mask = Image.new("L", (86, 86), 0)
        ImageDraw.Draw(artist_mask).ellipse((0, 0, 86, 86), fill=255)
        artist_art = ImageOps.fit(
            artist_art, (86, 86), centering=(0.5, 0.5))
        canvas.paste(im=artist_art, box=(vinyl_center_x - 43,
                                         vinyl_center_y - 43), mask=artist_mask)
        draw.ellipse((vinyl_center_x - 43, vinyl_center_y - 43,
                      vinyl_center_x + 43, vinyl_center_y + 43),
                     outline="gray", width=1)
        # ~~~~~~~~~~~~~~ Artist ~~~~~~~~~~~~~~

        # ~~~~~~~~~~~~~~ Album ~~~~~~~~~~~~~~
        album_art = self.fetch_art(track.album_art_url).resize(
            (album_size, album_size))
        border_album = ImageOps.expand(album_art, border=2, fill='black')
        canvas.paste(border_album, (album_x - 2, album_y - 2))
        canvas.paste(album_art, (album_x, album_y))
        # ~~~~~~~~~~~~~~ Album ~~~~~~~~~~~~~~

        # ~~~~~~~~~~~~~~ Text ~~~~~~~~~~~~~~
        text_bg = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        ImageDraw.Draw(text_bg).rounded_rectangle(
            [text_x, album_y, text_x + max_text_width, album_y + album_size],
            radius=4, fill=(0, 0, 0, 128))
        canvas = canvas.convert("RGBA")
        canvas = Image.alpha_composite(canvas, text_bg)
        canvas = canvas.convert("RGB")
        draw = ImageDraw.Draw(canvas)

        draw.text((text_x + 8, album_y + 16), self._truncate(track.name,
                  self.font_title, max_text_width), font=self.font_title, fill="white")
        draw.text((text_x + 8, album_y + 70), self._truncate(track.artist,
                  self.font_sub, max_text_width), font=self.font_sub, fill="white")
        draw.text((text_x + 8, album_y + 96), self._truncate(track.album,
                  self.font_small, max_text_width), font=self.font_small, fill=(200, 200, 200))
        # ~~~~~~~~~~~~~~ Text ~~~~~~~~~~~~~~

        canvas.save(self.output_path)

        if self.mode == "eink":
            image = Image.open(self.output_path)
            self.epd.display(self.epd.getbuffer(image))

    def render_random(self):

        folder_path = os.path.join(assets_dir, "Pics")
        all_items = os.listdir(folder_path)
        random_item = random.choice(all_items)
        full_path = os.path.join(folder_path, random_item)

        img = Image.open(full_path).resize((self.width, self.height))
        img.save(self.output_path)
        if self.mode == "eink":
            image = Image.open(self.output_path)
            self.epd.display(self.epd.getbuffer(image))

    def _truncate(self, text, font, max_width):
        if not text:
            return ""
        while font.getlength(text) > max_width and len(text) > 1:
            text = text[:-1]
        return text + "…"

    def clear(self):
        canvas = Image.new("RGB", (self.width, self.height), "black")
        canvas.save(self.output_path)
        if self.mode == "eink":
            self.epd.Clear()
