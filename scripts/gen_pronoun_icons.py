#!/usr/bin/env python3

import cairosvg
from PIL import Image
from pathlib import Path


pronouns = {
	"she/her":       (None,       "#37BE37"),
	"he/him":        (None,       "#AFB602"),
	"they/them":     (None,       "#00CECF"),
	"ze/hir":        (None,       "#FFCDCD"),
	"ze/zir":        (None,       "#FFCDCD"),
	"xey/xem":       (None,       "#FFCDCD"),
	"ae/aer":        (None,       "#FFCDCD"),
	"e/em":          (None,       "#FFCDCD"),
	"ey/em":         (None,       "#FFCDCD"),
	"fae/faer":      (None,       "#FFCDCD"),
	"fae/fem":       (None,       "#FFCDCD"),
	"hu/hum":        (None,       "#FFCDCD"),
	"it/its":        (None,       "#FFCDCD"),
	"jee/jem":       (None,       "#FFCDCD"),
	"kit/kits":      (None,       "#FFCDCD"),
	"ne/nem":        (None,       "#FFCDCD"),
	"peh/pehm":      (None,       "#FFCDCD"),
	"per/per":       (None,       "#FFCDCD"),
	"sie/hir":       (None,       "#FFCDCD"),
	"se/sim":        (None,       "#FFCDCD"),
	"she/hir":       (None,       "#FFCDCD"),
	"si/hyr":        (None,       "#FFCDCD"),
	"thon/thon":     (None,       "#FFCDCD"),
	"ve/ver":        (None,       "#FFCDCD"),
	"ve/vem":        (None,       "#FFCDCD"),
	"vi/ver":        (None,       "#FFCDCD"),
	"vi/vim":        (None,       "#AAFFAA"),
	"xie/xer":       (None,       "#FFCDCD"),
	"xe/xem":        (None,       "#FFCDCD"),
	"yo/yo":         (None,       "#FFCDCD"),
	"ze/mer":        (None,       "#FFCDCD"),
	"zee/zed":       (None,       "#FFCDCD"),
	"zie/zir":       (None,       "#FFCDCD"),
	"zie/hir":       (None,       "#FFCDCD"),
	"zme/zmyr":      (None,       "#FFCDCD"),
	"zie/zem":       (None,       "#FFCDCD"),
	"xe/xyr":        (None,       "#AAFFAA"),
	"no pronouns":   ("no/prns",  "#AAFFAA"),
	"any pronouns":  ("any/prns", "#AAFFAA"),
	"ze/zem":        (None,       "#FFCDCD"),
	"xi/xir":        (None,       "#FFCDCD"),
	"zhe/zhim":      (None,       "#FFCDCD")
}


def generate_svg(filename, text, width, height, color):
	with open(filename, "wt") as file:
		parts = text.upper().split('/')

		max_len = max(map(len, parts))

		font_size = 56 if max_len < 4 else 42 if max_len < 8 else 32

		file.write(f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">""")
	# 	file.write(f"""
	# <rect x="0" y="0" width="{width}" height="{height}" fill="none" stroke="black" />""")

		for y, text in enumerate(parts):
			yo = (y + 1) / (len(parts) + 1) * 0.92 + y * 0.08 - 0.028
			#                               ^^^^^^^^^^^^^^^^^^^^^^^^^
			#                 fixup to account for weird baseline placement by cairo
			file.write(f"""
	<text x="50%" y="{yo * height}" dominant-baseline="middle" text-anchor="middle" font-family="Segoe UI Black" font-size="{font_size}px" font-weight="bold" fill="{color}">{text}</text>""")
	# 		file.write(f"""
	# <line x1="0" y1="{yo * height}" x2="{width}" y2="{yo * height}" stroke="black" />""")

		file.write("""
</svg>
""")


def svg_to_png(dest, src, background):
	with open(src, "rb") as in_file, open(dest, "wb") as out_file:
		cairosvg.svg2png(write_to=out_file, file_obj=in_file)

	# replace background color to work around discord downscaling artifacts.
	#    cairo outputs premultiplied alpha. discord server-side image scaling does not handle premultiplied alpha correctly.
	#    the result would be fringes with blurry dark spots around letters when downscaled to fit client DPI.
	img = Image.open(dest)
	pixels = img.load()

	for j in range(0, img.size[1]):
		for i in range(0, img.size[0]):
			if pixels[i, j][3] == 0:
				pixels[i, j] = background + (0,)

	img.save(dest)



def decode_sRGB(value):
	return value / 12.92 if value <= 0.04045 else pow((value + 0.055) / 1.055, 2.4)

def encode_sRGB(value):
	return value * 12.92 if value <= 0.0031308 else 1.055 * pow(value, 1.0 / 2.4) - 0.055

def unpack_rgb8(color):
	return ((color >> 16) & 0xFF, (color >> 8) & 0xFF, (color >> 0) & 0xFF)

def hex_to_rgb8(color):
	return unpack_rgb8(int(color[1:], 16))

def rgb8_to_hex(r, g, b):
	return f"#{r:02X}{g:02X}{b:02X}"



def main():
	this_dir = Path(__file__).parent.absolute()
	output_dir = this_dir/"pronouns"

	output_dir.mkdir(parents=True, exist_ok=True)

	for pronoun, (text, color) in pronouns.items():
		filename = f"{pronoun.translate({ord('/'): '_', ord(' '): '_'})}.svg"
		svg_file = output_dir/filename
		png_file = svg_file.with_suffix(".png")

		generate_svg(svg_file, text if text else pronoun, 128, 128, color)
		svg_to_png(png_file, svg_file, hex_to_rgb8(color))


if __name__ == "__main__":
	main()
