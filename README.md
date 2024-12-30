# Color Palette Extractor

This Python script extracts a color palette from an image and generates various color harmonies. It’s designed for design students and professionals to analyze and utilize color schemes in their projects.

## Features

- Extract dominant colors from any image
- Generate color harmonies (Complementary, Analogous, Triadic, Tetradic, Tints, and Shades)
- Create a PDF report with visual representation of colors and harmonies
- Save color information in a text file for easy reference

## Installation

1. Clone this repository:

   ```
   git clone https://github.com/MichailSemoglou/color-palette-extractor.git
   cd color-palette-extractor
   ```

2. Create a virtual environment (optional but recommended):

   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required dependencies:

   ```
   pip install -r requirements.txt
   ```

4. [Download](https://rsms.me/inter/) the Inter font files (Inter-Bold.ttf and Inter-Regular.ttf) and place them in the same directory as the script.

## Usage

Run the script from the command line as follows:

```
python3 color_palette_extractor.py path/to/your/image.jpg -n 6
```

- `path/to/your/image.jpg`: Path to the input image file
- `-n 6`: Number of colors to extract (optional, default is 6)

The script will generate two output files in the same directory as the script:

1. `color_info.txt`: A text file containing detailed color information, including:

   - HEX, RGB, and CMYK values for each color in the extracted palette
   - Color harmony information (Complementary, Analogous, Triadic, Tetradic, Tints, and Shades)

2. `color_palette.pdf`: A visual report in PDF format, including:
   - The original image
   - The extracted color palette
   - Visual representations of each color harmony

## Troubleshooting

Here are some common issues you might encounter and how to resolve them:

1. **ModuleNotFoundError**: If you see an error like `ModuleNotFoundError: No module named 'numpy'`, it means the required dependencies are not installed. Make sure you’ve run `pip install -r requirements.txt` in your virtual environment.

2. **FileNotFoundError for font files**: If you see an error mentioning `Inter-Bold.ttf` or `Inter-Regular.ttf`, ensure these font files are in the same directory as the script. You can download them from the Inter font website.

3. **Permission denied when saving output files**: Ensure you have write permissions in the directory where you’re running the script.

4. **Image file not found**: Double-check the path to your image file. Use the full path if the image is not in the same directory as the script.

5. **Unexpected color results**: For very large images, try increasing the `max_dimension` value in the `extract_color_palette` function for potentially more accurate results, at the cost of increased processing time.

If you encounter any other issues, please open an issue on the GitHub repository with a detailed description of the problem and the steps to reproduce it.

## Color Harmonies Explanation

1. **Complementary**: Colors opposite each other on the color wheel, creating a high-contrast effect.
2. **Analogous**: Colors adjacent to each other on the color wheel, creating a harmonious and cohesive look.
3. **Triadic**: Three colors evenly spaced on the color wheel, offering a balanced and vibrant color scheme.
4. **Tetradic**: Four colors arranged into two complementary pairs, providing a rich and varied palette.
5. **Tints**: Lighter variations of a color, created by adding white.
6. **Shades**: Darker variations of a color, created by adding black.

## Dependencies

- Python 3.6+
- numpy (1.19.5)
- scikit-learn (0.24.2)
- Pillow (8.2.0)
- reportlab (3.5.67)

For a complete list of dependencies with version information, see `requirements.txt`.

## Potential Use Cases

1. **Brand Identity Development**: Analyze existing logos or brand imagery to extract key colors and develop complementary palettes.

2. **Web Design**: Generate color schemes for websites based on a key visual element or photograph.

3. **Interior Design**: Extract colors from inspiration images to create cohesive room color schemes.

4. **Fashion Design**: Analyze fabric patterns or inspiration images to develop coordinated clothing collections.

5. **Data Visualization**: Create harmonious color palettes for charts, graphs, and infographics.

6. **Digital Art**: Generate color palettes from reference images for digital illustrations or concept art.

7. **Photography**: Analyze color composition in photographs and develop presets or filters based on extracted palettes.

8. **Print Design**: Ensure color consistency across various printed materials by extracting and using a consistent palette.

9. **Product Design**: Develop color schemes for product lines based on trend images or competitor analysis.

10. **Marketing Materials**: Create visually cohesive marketing campaigns by extracting colors from key visuals.

## License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.
