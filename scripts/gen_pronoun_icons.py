#!/usr/bin/env python3

import cairosvg
from PIL import Image, ImageColor
import numpy as np
from pathlib import Path
import argparse


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
		runs = text.upper().split('/')

		max_len = max(map(len, runs))

		font_size = (56 if max_len < 4 else 42 if max_len < 8 else 32) * (min(width, height) / 128)

		file.write(f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">""")

		for y, text in enumerate(runs):
			yo = (y + 1) / (len(runs) + 1) * 0.92 + y * 0.08 - 0.028
			#                               ^^^^^^^^^^^^^^^^^^^^^^^^^
			#               fixup to account for weird baseline placement by CairoSVG
			#
			file.write(f"""
	<text x="50%" y="{yo * height}" dominant-baseline="middle" text-anchor="middle" font-family="Segoe UI Black" font-size="{font_size}px" font-weight="bold" fill="{color}">{text}</text>""")

		file.write("""
</svg>
""")


def read_png(file):
	with Image.open(file) as img:
		return np.asarray(img)

def write_png(file, pixels):
	with Image.fromarray(pixels, 'RGBA') as img:
		img.save(file)

def svg_to_png(dest, src, background):
	with open(src, "rb") as in_file, open(dest, "wb") as out_file:
		cairosvg.svg2png(write_to=out_file, file_obj=in_file)

	# CairoSVG outputs transparent black for fully-transparent fills regardless
	# of color. However, while it thus effectively produces premultiplied alpha
	# for this one case, it produces unassociated alpha in all other cases.
	# What we end up with are fringes with blurry dark spots around letters when
	# the icons are downscaled to fit client DPI.
	# Ideally, we'd just work with premultiplied alpha. However, Discord 
	# performs server-side image scaling in a way that expects unassociated 
	# alpha. Thus, there's not much we can do here other than make sure that we
	# feed Discord what Discord demands.
	# Since there seems to be no way to make CairoSVG be at least consistent
	# about what it does, we simply overwrite the R, G, and B channels with the
	# input color values (which is what should be in there anyways) and keep
	# only the alpha channel (which is all we needed anyways).
	#
	pixels = read_png(dest)
	pixels[:,:,:3] = ImageColor.getrgb(background)
	write_png(dest, pixels)



def main(args):
	this_dir = Path(__file__).parent.absolute()
	output_dir = this_dir/"pronouns"

	output_dir.mkdir(parents=True, exist_ok=True)

	for pronoun, (text, color) in pronouns.items():
		filename = f"{pronoun.translate({ord('/'): '_', ord(' '): '_'})}.svg"
		svg_file = output_dir/filename
		png_file = svg_file.with_suffix(".png")

		generate_svg(svg_file, text if text else pronoun, args.width, args.height, color)
		svg_to_png(png_file, svg_file, color)


if __name__ == "__main__":
	args = argparse.ArgumentParser()
	args.add_argument("-rx", "--res-x", default=128, type=int, dest="width", help="width of the generated icons (default: 128)")
	args.add_argument("-ry", "--res-y", default=128, type=int, dest="height", help="height of the generated icons (default: 128)")
	main(args.parse_args())
