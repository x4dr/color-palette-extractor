#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Color Palette and Harmony Generator

This script extracts a color palette from an image and generates various color harmonies.

Usage:
Ensure all required libraries are installed (numpy, scikit-learn, Pillow, click)
First Parameter is the image Path, second is the number of colors to extract
"""

import numpy as np
import colorsys
import click
from sklearn.cluster import KMeans
from PIL import Image, ImageFont, ImageDraw, ImageChops, ImageOps


def rgb_to_cmyk(r, g, b):
    """Convert RGB to CMYK color space."""
    if (r, g, b) == (0, 0, 0):
        return 0, 0, 0, 100

    c = 1 - r / 255
    m = 1 - g / 255
    y = 1 - b / 255
    k = min(c, m, y)
    
    c = (c - k) / (1 - k) * 100
    m = (m - k) / (1 - k) * 100
    y = (y - k) / (1 - k) * 100
    k = k * 100
    
    return round(c), round(m), round(y), round(k)

def extract_color_palette(image_path, num_colors):
    """Extract a color palette from an image using KMeans clustering."""
    num_colors = min(num_colors, 12)  # Limit to a maximum of 12 colors
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
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    img_array = np.array(img)

    # Reshape to a list of pixels
    img_pixels = img_array.reshape((-1, 3))

    # Apply KMeans clustering
    kmeans = KMeans(n_clusters=num_colors, n_init=10, random_state=42)
    kmeans.fit(img_pixels)

    # Get the cluster centers (dominant colors)
    dominant_colors = kmeans.cluster_centers_.astype(int)

    # Convert to desired formats
    color_palette = []
    for color in dominant_colors:
        hex_color = '#{:02x}{:02x}{:02x}'.format(*color)
        rgb_color = tuple(color)
        cmyk_color = rgb_to_cmyk(*color)
        color_palette.append((hex_color, rgb_color, cmyk_color))

    return color_palette

def rgb_to_hex(rgb):
    """Convert RGB tuple to HEX string."""
    return '#{:02x}{:02x}{:02x}'.format(*rgb)

def get_harmonies(color_palette):
    """Generate common color harmonies based on the palette."""
    harmonies = {
        "Complementary": [],
        "Analogous": [],
        "Triadic": [],
        "Tetradic": [],
        "Tints": [],
        "Shades": []
    }

    for color in color_palette:
        rgb = color[1]
        h, s, v = colorsys.rgb_to_hsv(rgb[0]/255, rgb[1]/255, rgb[2]/255)

        # Complementary
        comp_h = (h + 0.5) % 1
        comp_rgb = colorsys.hsv_to_rgb(comp_h, s, v)
        harmonies["Complementary"].append({
            "Base": rgb_to_hex(rgb),
            "Complement": rgb_to_hex(tuple(int(x*255) for x in comp_rgb))
        })

        # Analogous
        analog_h1 = (h + 1/12) % 1
        analog_h2 = (h - 1/12) % 1
        analog_rgb1 = colorsys.hsv_to_rgb(analog_h1, s, v)
        analog_rgb2 = colorsys.hsv_to_rgb(analog_h2, s, v)
        harmonies["Analogous"].append({
            "Base": rgb_to_hex(rgb),
            "Analog 1": rgb_to_hex(tuple(int(x*255) for x in analog_rgb1)),
            "Analog 2": rgb_to_hex(tuple(int(x*255) for x in analog_rgb2))
        })

        # Triadic
        triad_h1 = (h + 1/3) % 1
        triad_h2 = (h + 2/3) % 1
        triad_rgb1 = colorsys.hsv_to_rgb(triad_h1, s, v)
        triad_rgb2 = colorsys.hsv_to_rgb(triad_h2, s, v)
        harmonies["Triadic"].append({
            "Base": rgb_to_hex(rgb),
            "Triad 1": rgb_to_hex(tuple(int(x*255) for x in triad_rgb1)),
            "Triad 2": rgb_to_hex(tuple(int(x*255) for x in triad_rgb2))
        })

        # Tetradic
        tetra_h1 = (h + 0.25) % 1
        tetra_h2 = (h + 0.5) % 1
        tetra_h3 = (h + 0.75) % 1
        tetra_rgb1 = colorsys.hsv_to_rgb(tetra_h1, s, v)
        tetra_rgb2 = colorsys.hsv_to_rgb(tetra_h2, s, v)
        tetra_rgb3 = colorsys.hsv_to_rgb(tetra_h3, s, v)
        harmonies["Tetradic"].append({
            "Base": rgb_to_hex(rgb),
            "Tetra 1": rgb_to_hex(tuple(int(x*255) for x in tetra_rgb1)),
            "Tetra 2": rgb_to_hex(tuple(int(x*255) for x in tetra_rgb2)),
            "Tetra 3": rgb_to_hex(tuple(int(x*255) for x in tetra_rgb3))
        })

        # Tints
        tints = []
        for i in range(5):
            tint_s = max(0.0, float(s - (s * (i / 5))))
            tint_v = min(1.0, v + ((1 - v) * (i / 5)))
            tint_rgb = colorsys.hsv_to_rgb(h, tint_s, tint_v)
            tints.append(rgb_to_hex(tuple(int(x*255) for x in tint_rgb)))
        harmonies["Tints"].append({f"Tint {i+1}": tint for i, tint in enumerate(tints)})

        # Shades
        shades = []
        for i in range(5):
            shade_v = v * (1 - i / 5)
            shade_rgb = colorsys.hsv_to_rgb(h, s, shade_v)
            shades.append(rgb_to_hex(tuple(int(x*255) for x in shade_rgb)))
        harmonies["Shades"].append({f"Shade {i+1}": shade for i, shade in enumerate(shades)})

    return harmonies

def is_dark(hex_color):
    """Determine if a color is dark based on its luminance."""
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return luminance < 0.5

def save_palette_to_png(color_palette, harmonies, output_file="color_palette.png", image_file=""):
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

def save_palette_and_harmonies(color_palette, harmonies, filename="color_info.txt"):
    """Save the color palette and harmonies to a text file."""
    with open(filename, 'w') as f:
        f.write("Color Palette:\n")
        for color in color_palette:
            f.write(f"HEX: {color[0]}, RGB: {color[1]}, CMYK: {color[2]}\n")
        
        f.write("\nColor Harmonies:\n")
        for harmony_type, harmony_sets in harmonies.items():
            f.write(f"\n{harmony_type}:\n")
            for harmony_set in harmony_sets:
                for color_name, color_hex in harmony_set.items():
                    rgb = tuple(int(color_hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
                    cmyk = rgb_to_cmyk(*rgb)
                    f.write(f"  {color_name}: HEX: {color_hex}, RGB: {rgb}, CMYK: {cmyk}\n")
                f.write("\n")

def print_palette_terminal(color_palette, harmonies):
    def rgb_from_hex(h):
        r = int(h[1:3], 16)
        g = int(h[3:5], 16)
        b = int(h[5:7], 16)
        return r, g, b

    def color_block(hex_color):
        r, g, b = rgb_from_hex(hex_color)
        return f"\033[48;2;{r};{g};{b}m  \033[0m"

    print("\nOriginal Palette:")
    for hex_color, _, _ in color_palette:
        print(f"{color_block(hex_color)} {hex_color}", end='  ')
    print("\n")

    for name, harmony_sets in harmonies.items():
        print(f"{name} Harmony:")
        for hset in harmony_sets:
            for hex_color in hset.values():
                print(f"{color_block(hex_color)} {hex_color}", end='  ')
            print()
        print()


@click.command()
@click.argument('file', type=click.Path(exists=True))
@click.argument('number', type=click.IntRange(1, 20))
@click.option('--png', is_flag=True, default=False, help="Render to reference PNG (default is False)")
def main(file, number, png):
    """Main function to run the color palette and harmony generator."""

    print("Extracting color palette...")
    color_palette = extract_color_palette(file, number)

    print("\nColor Palette:")
    for color in color_palette:
        print(f"HEX: {color[0]}, RGB: {color[1]}, CMYK: {color[2]}")

    print("\nGenerating color harmonies...")
    harmonies = get_harmonies(color_palette)
    print("Color Harmonies:")
    for harmony_type, harmony_sets in harmonies.items():
        print(f"\n{harmony_type}:")
        for harmony_set in harmony_sets:
            for color_name, color_hex in harmony_set.items():
                print(f"  {color_name}: {color_hex}")
            print()

    print("Saving harmonies")
    save_palette_and_harmonies(color_palette, harmonies)
    if png:
        print("Saving to png")
        save_palette_to_png(color_palette, harmonies, image_file=file)
    print("\nColor palette and harmonies have been saved to 'color_info.txt' and 'color_palette.pdf'")
    print_palette_terminal(color_palette, harmonies)


if __name__ == "__main__":
    main()
