#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Color Palette and Harmony Generator

This script extracts a color palette from an image and generates various color harmonies.
It creates a PDF report and a text file with the color information.

Usage:
1. Ensure all required libraries are installed (numpy, scikit-learn, Pillow, reportlab)
2. Place the Inter-Bold.ttf and Inter-Regular.ttf fonts in the same directory as the script
3. Run the script and follow the prompts to input an image file and number of colors
"""

import numpy as np
import colorsys
from sklearn.cluster import KMeans
from PIL import Image as PILImage
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.platypus import Image as ReportLabImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import inch
import os

# Register Inter-Bold font
try:
    pdfmetrics.registerFont(TTFont('Inter-Bold', 'Inter-Bold.ttf'))
    pdfmetrics.registerFont(TTFont('Inter-Regular', 'Inter-Regular.ttf'))
except:
    print("Warning: Unable to register Inter fonts. The PDF may not display correctly.")
    print("Make sure 'Inter-Bold.ttf' and 'Inter-Regular.ttf' are in the same directory as this script.")

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
    img = PILImage.open(image_path)
    
    # Calculate new dimensions
    max_dimension = 1000  # Maximum dimension for processing
    width, height = img.size
    if max(width, height) > max_dimension:
        scale_factor = max_dimension / max(width, height)
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)
        img = img.resize((new_width, new_height), PILImage.LANCZOS)
    
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
            tint_s = max(0, s - (s * (i / 4)))
            tint_v = min(1, v + ((1 - v) * (i / 4)))
            tint_rgb = colorsys.hsv_to_rgb(h, tint_s, tint_v)
            tints.append(rgb_to_hex(tuple(int(x*255) for x in tint_rgb)))
        harmonies["Tints"].append({f"Tint {i+1}": tint for i, tint in enumerate(tints)})

        # Shades
        shades = []
        for i in range(5):
            shade_v = v * (1 - i / 4)
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

def save_palette_to_pdf(color_palette, harmonies, filename="color_palette.pdf", image_filename=""):
    """Save the color palette and harmonies to a PDF file with improved layout."""
    doc = SimpleDocTemplate(filename, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(name='Title', fontName='Inter-Bold', fontSize=18, leading=20, alignment=TA_LEFT, spaceAfter=10)
    heading_style = ParagraphStyle(name='Heading2', fontName='Inter-Bold', fontSize=14, leading=16, alignment=TA_LEFT, spaceBefore=16, spaceAfter=8)
    
    title = f"Color Palette and Harmonies for {os.path.basename(image_filename)}"
    elements.append(Paragraph(title, title_style))
    elements.append(Spacer(1, 0.2*inch))

    # Add the original image
    img = PILImage.open(image_filename)
    img_width, img_height = img.size
    aspect = img_height / float(img_width)
    
    # Set the width to 3 inches, and calculate the height based on the aspect ratio
    display_width = 3 * inch
    display_height = display_width * aspect

    elements.append(ReportLabImage(image_filename, width=display_width, height=display_height))
    elements.append(Spacer(1, 0.2*inch))

    # Add color palette (in two rows)
    elements.append(Paragraph("Original Color Palette", heading_style))
    palette_data = [
        [color[0] for color in color_palette[:6]],
        [color[0] for color in color_palette[6:]]
    ]
    palette_table = Table(palette_data, colWidths=60, rowHeights=60)
    
    palette_style = TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, -1), 'Inter-Regular'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
    ])
    
    for i, color in enumerate(color_palette):
        row = 0 if i < 6 else 1
        col = i % 6
        hex_color = color[0]
        palette_style.add('BACKGROUND', (col, row), (col, row), colors.HexColor(hex_color))
        text_color = colors.white if is_dark(hex_color) else colors.black
        palette_style.add('TEXTCOLOR', (col, row), (col, row), text_color)
    
    palette_table.setStyle(palette_style)
    elements.append(palette_table)

    # Add harmonies
    harmony_pages = ["Original Color Palette"]  # Start with the palette page
    for harmony_type, harmony_sets in harmonies.items():
        # Add a page break before "Complementary Harmonies"
        if harmony_type == "Complementary":
            elements.append(PageBreak())

        elements.append(Paragraph(f"{harmony_type} Harmonies", heading_style))
        harmony_pages.append(harmony_type)
        for idx, harmony_set in enumerate(harmony_sets):
            harmony_data = [list(harmony_set.values())]
            harmony_table = Table(harmony_data, colWidths=60, rowHeights=60)
            
            harmony_style = TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, -1), 'Inter-Regular'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
            ])
            
            for i, color_hex in enumerate(harmony_set.values()):
                harmony_style.add('BACKGROUND', (i, 0), (i, 0), colors.HexColor(color_hex))
                text_color = colors.white if is_dark(color_hex) else colors.black
                harmony_style.add('TEXTCOLOR', (i, 0), (i, 0), text_color)
            
            harmony_table.setStyle(harmony_style)
            elements.append(harmony_table)

        # Add page break after each harmony type, except for the last one
        if harmony_type != list(harmonies.keys())[-1]:
            elements.append(PageBreak())

    def add_page_number(canvas, doc):
        page_num = canvas.getPageNumber()
        harmony_name = harmony_pages[min(page_num - 1, len(harmony_pages) - 1)]
        text = f"Page {page_num} | Image: {os.path.basename(image_filename)} | {harmony_name}"
        canvas.setFont("Inter-Regular", 8)
        canvas.drawString(inch, 0.5*inch, text)

    doc.build(elements, onFirstPage=add_page_number, onLaterPages=add_page_number)

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

def main():
    """Main function to run the color palette and harmony generator."""
    print("Welcome to the Color Palette and Harmony Generator!")
    print("This script extracts a color palette from an image and generates various color harmonies.")

    # Get image file path
    while True:
        image_path = input("Enter the path to the image file: ").strip()
        if os.path.isfile(image_path):
            try:
                with PILImage.open(image_path) as img:
                    # Check if the image is in RGB mode
                    if img.mode != 'RGB':
                        print("Warning: The image is not in RGB mode. Converting to RGB.")
                        img = img.convert('RGB')
                break
            except IOError:
                print("Error: The file is not a valid image. Please try again.")
        else:
            print("Error: The specified file does not exist. Please try again.")

    # Get number of colors
    while True:
        try:
            num_colors = int(input("Enter the number of colors for the palette (1-12): "))
            if 1 <= num_colors <= 12:
                break
            else:
                print("Error: Please enter a number between 1 and 12.")
        except ValueError:
            print("Error: Please enter a valid number between 1 and 12.")

    try:
        print("Extracting color palette...")
        color_palette = extract_color_palette(image_path, num_colors)

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

        print("Saving results to files...")
        save_palette_and_harmonies(color_palette, harmonies)
        save_palette_to_pdf(color_palette, harmonies, image_filename=image_path)
        print("\nColor palette and harmonies have been saved to 'color_info.txt' and 'color_palette.pdf'")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print("Please check your input and try again.")
        print("If the error persists, ensure you have all required libraries installed:")
        print("numpy, scikit-learn, Pillow, and reportlab")

if __name__ == "__main__":
    main()