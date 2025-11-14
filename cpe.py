#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Color Palette Extractor
"""
import json
from pathlib import Path

import click
import numpy as np
from PIL import Image, ImageFont, ImageDraw, ImageChops, ImageOps
from sklearn.cluster import KMeans

from colors.Color import Color, ColorEncoder
from colors.roles import get_roles


def extract_color_palette(image_path, num_colors):
    """Extract a color palette from an image using KMeans clustering."""
    img = Image.open(image_path)

    # Calculate new dimensions
    max_dimension = 1000  # Maximum dimension for processing
    width, height = img.size
    if max(width, height) > max_dimension:
        scale_factor = max_dimension / max(width, height)
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)
        img = img.resize((new_width, new_height), Image.LANCZOS)

    # Convert image to RGB mode if it's not already
    if img.mode != "RGB":
        img = img.convert("RGB")

    img_array = np.array(img)

    # Reshape to a list of pixels
    img_pixels = img_array.reshape((-1, 3))

    # Apply KMeans clustering
    kmeans = KMeans(n_clusters=num_colors, n_init=10, random_state=42)
    kmeans.fit(img_pixels)

    # Extract Info
    labels, counts = np.unique(kmeans.labels_, return_counts=True)
    sorted_indices = np.argsort(-counts)  # Descending order of population

    color_palette = {"Colors": []}
    for rank, idx in enumerate(sorted_indices):
        color = Color.from_rgb(*kmeans.cluster_centers_[idx].astype(int))
        color_palette["Colors"].append(color)
    color_palette["Roles"] = get_roles(img_array, kmeans, color_palette["Colors"])

    return color_palette


def get_harmonies(color_palette):
    """Generate common color harmonies based on the palette."""
    harmonies = {}
    for color in color_palette:
        harmony = {
            "Complementary": [color.complementary(i) for i in range(1)],
            "Analogous": [color.analogous(i) for i in range(2)],
            "Triadic": [color.triadic(i) for i in range(2)],
            "Tetradic": [color.tetradic(i) for i in range(3)],
            "Tints": [color.tint(i / 5) for i in range(1, 5)],
            "Shades": [color.shade(i / 5) for i in range(1, 5)],
        }
        harmonies[color] = harmony
    return harmonies


def save_palette_to_png(
    color_palette, harmonies, output_file="color_palette.png", image_file=""
):
    # Load base image
    base_img = Image.open(image_file).resize((300, 200))
    font = ImageFont.load_default()

    # Create blank canvas
    width = 1000
    height = 600 + 500 * len(harmonies)
    out_img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(out_img)

    # Paste original image
    out_img.paste(base_img, (20, 20))

    # Draw palette
    draw.text((20, 240), "Original Palette:", font=font, fill="black")
    for i, (hex_color, _, _) in enumerate(color_palette):
        x = 20 + i * 60
        draw.rectangle([x, 270, x + 50, 320], fill=hex_color)
        draw.text((x, 325), hex_color, font=font, fill="black")

    # Draw harmonies
    y_start = 370
    for name, harmony_sets in harmonies.items():
        draw.text((20, y_start), f"{name} Harmony:", font=font, fill="black")
        y_start += 30
        for hset in harmony_sets:
            for i, hex_color in enumerate(hset.values()):
                x = 20 + i * 60
                draw.rectangle([x, y_start, x + 50, y_start + 50], fill=hex_color)
                draw.text((x, y_start + 55), hex_color, font=font, fill="black")
            y_start += 80

    bg = Image.new(out_img.mode, out_img.size, "white")
    diff = ImageChops.difference(out_img, bg)
    bbox = diff.getbbox()
    if bbox:
        out_img = out_img.crop(bbox)
        out_img = ImageOps.expand(out_img, border=20, fill="white")

    out_img.save(output_file)


def save_palette_and_harmonies(color_palette, harmonies, filename="color_info"):
    """Save the color palette and harmonies to a text file."""
    with open(filename + ".txt", "w") as f:
        f.write("Color Palette:\n")
        for color in color_palette:
            f.write(f"HEX: {color[0]}, RGB: {color[1]}\n")

        f.write("\nColor Harmonies:\n")
        for color, harmony in harmonies["Colors"].items():
            f.write(f"{color}\n")
            for harmony_type, colors in harmony.items():
                f.write(f"\n{harmony_type}:\n")
                if not isinstance(colors, list):
                    colors = [colors]
                for c in colors:
                    f.write(f"{c.hex} ")
                f.write("\n")
    # Save the data to a JSON file
    with open(filename + ".json", "w") as f:
        json.dump(color_palette, f, indent=4, cls=ColorEncoder)


def print_palette_terminal(color_palette, harmonies):
    def color_block(color):
        if isinstance(color, str):
            color = Color.from_hex(color)
        r, g, b = color.rgb
        return f"\033[48;2;{r};{g};{b}m  \033[0m"

    print("\nOriginal Palette:")
    for color in color_palette["Colors"]:
        print(f"{color_block(color)} {color.hex}", end="  ")
    print("\n")

    for role, color in color_palette["Roles"].items():
        print(f"{role.title()} {color_block(color)} {color.hex}")

    for section, harmony_section in harmonies.items():
        for name, harmony_sets in harmony_section.items():
            print(f"{color_block(name)} {name.hex} Harmony:")
            for hname, hset in harmony_sets.items():
                print(f"{hname:<20}", end="")
                if not isinstance(hset, list):
                    hset = [hset]
                for color in hset:
                    print(f"{color_block(color)} {color.hex}", end="\t")
                print()
            print()


@click.command()
@click.argument("number", type=click.IntRange(1, 20))
@click.argument("file", type=click.Path(exists=True))
@click.argument(
    "output",
    type=click.Path(exists=True, file_okay=False, writable=True),
    required=False,
)
@click.option(
    "--png",
    is_flag=True,
    default=False,
    help="Render to reference PNG (default is False)",
)
@click.option("-q", is_flag=True, default=False, help="Quiet")
def main(file, number, png, q, output):
    """Main function to run the color palette and harmony generator."""

    color_palette = extract_color_palette(file, number)
    output = output if output else Path("~/.cache/cpe").expanduser().as_posix()
    harmonies = {
        "Colors": get_harmonies(color_palette["Colors"]),
        "Roles": get_harmonies(color_palette["Roles"].values()),
    }
    save_palette_and_harmonies(color_palette, harmonies, output + "/colors")
    if png:
        save_palette_to_png(color_palette, harmonies, image_file=file)
    if not q:
        print_palette_terminal(color_palette, harmonies)


if __name__ == "__main__":
    main()
