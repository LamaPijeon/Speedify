from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
import requests
import random
from io import BytesIO
from waveshare_epd import epd3in6e  # type: ignore


class DisplayManager:
    def __init__(self, width=600, height=400):
        self.width = width
        self.height = height
        self.output_path = "current.png"

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
        canvas = canvas.filter(ImageFilter.GaussianBlur(radius=40))
        canvas = canvas.point(lambda p: p * 0.55)  # Darken the background
        # ~~~~~~~~~~~~~~ Canvas ~~~~~~~~~~~~~~

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
        ImageDraw.Draw(canvas).ellipse(
            (vinyl_center_x - oc_radius, vinyl_center_y - oc_radius,
             vinyl_center_x + oc_radius, vinyl_center_y + oc_radius), fill=oc_color)

        ImageDraw.Draw(canvas).ellipse(
            (vinyl_center_x - ic_radius, vinyl_center_y - ic_radius,
             vinyl_center_x + ic_radius, vinyl_center_y + ic_radius), fill=ic_color)

        vinyl = Image.open("vinyl.png").resize((262, 262)).convert("RGBA")
        vinyl = vinyl.rotate(random.randint(0, 360))
        vinyl_coords = (vinyl_center_x - 131, vinyl_center_y - 131)
        canvas.paste(im=vinyl, box=vinyl_coords, mask=vinyl)
        # ~~~~~~~~~~~~~~ Vinyl ~~~~~~~~~~~~~~

        # ~~~~~~~~~~~~~~ Artist ~~~~~~~~~~~~~~
        artist_art = self.fetch_art(track.artist_art_url).resize((64, 64))
        artist_mask = Image.new("L", (64, 64), 0)
        ImageDraw.Draw(artist_mask).ellipse((0, 0, 64, 64), fill=255)
        artist_art = ImageOps.fit(artist_art, (64, 64), centering=(0.5, 0.5))

        canvas.paste(im=artist_art,
                     box=(vinyl_center_x - 32, vinyl_center_y - 32),
                     mask=artist_mask)

        # Draw a black outline circle 2 pixels larger in radius than the avatar
        outline_box = (vinyl_center_x - 32,
                       vinyl_center_y - 32,
                       vinyl_center_x + 32,
                       vinyl_center_y + 32)
        draw.ellipse(outline_box, outline="gray", width=1)

        # ~~~~~~~~~~~~~~ Artist ~~~~~~~~~~~~~~

        # ~~~~~~~~~~~~~~ Album ~~~~~~~~~~~~~~
        # Album art on the left
        album_art = self.fetch_art(track.album_art_url).resize(
            (272, 272))

        border_album = ImageOps.expand(album_art, border=2, fill='black')

        canvas.paste(
            album_art, (45, (self.height-272) // 2))
        canvas.paste(
            border_album, (45 - 2, (self.height-272) // 2 - 2))
        # ~~~~~~~~~~~~~~ Album ~~~~~~~~~~~~~~

        # Text on the right
        text_x = self.height + 10
        draw.text((text_x, 20), track.name, fill="white")
        draw.text((text_x, 60), track.artist, fill="gray")
        draw.text((text_x, 90), track.album, fill="gray")

        canvas.save(self.output_path)

        self.display(self.epd_init())

    def clear(self):
        canvas = Image.new("RGB", (self.width, self.height), "black")
        canvas.save(self.output_path)

    def display(self, epd):
        image = Image.open(self.output_path)
        epd.display(epd.getbuffer(image))

    def epd_init(self):
        epd = epd3in6e.EPD()
        epd.init()
        epd.Clear()
        return epd
