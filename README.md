# Color Palette Extractor

This Python script extracts a color palette from an image and generates various color harmonies. 
It was designed for design students and professionals to analyze and utilize color schemes in their projects.
This fork uses it as a color scheme extractor with more options than pywal, and so pdf support was dropped and the generation was slightly adjusted

## Features

- Extract dominant colors from any image
- Generate color harmonies (Complementary, Analogous, Triadic, Tetradic, Tints, and Shades)
- Save color information in a text file for easy reference

## Installation

1. Clone this repository:

   ```
   git clone https://github.com/x4dr/color-palette-extractor.git
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

## Usage

Run the script from the command line as follows:

```
python3 color_palette_extractor.py path/to/your/image.jpg 6
```

- `path/to/your/image.jpg`: Path to the input image file
- `6`: Number of colors to extract (maximum 20)

The script will generate two output files in the same directory as the script:

1. `color_info.txt`: A text file containing detailed color information, including:

   - HEX, RGB, and CMYK values for each color in the extracted palette
   - Color harmony information (Complementary, Analogous, Triadic, Tetradic, Tints, and Shades)

2. `color_palette.png`: A visual report in png format, including:
   - The original image
   - The extracted color palette
   - Visual representations of each color harmony

It will also try to use truecolor terminal output for quick reference

## Troubleshooting

Here are some common issues you might encounter and how to resolve them:

1. **ModuleNotFoundError**: If you see an error like `ModuleNotFoundError: No module named 'numpy'`, it means the required dependencies are not installed. Make sure you’ve run `pip install -r requirements.txt` in your virtual environment.

2. **Permission denied when saving output files**: Ensure you have write permissions in the directory where you’re running the script.

3. **Image file not found**: Double-check the path to your image file. Use the full path if the image is not in the same directory as the script.

4. **Unexpected color results**: For very large images, try increasing the `max_dimension` value in the `extract_color_palette` function for potentially more accurate results, at the cost of increased processing time.

If you encounter any other issues, please open an issue on the GitHub repository with a detailed description of the problem and the steps to reproduce it.

## Color Harmonies Explanation

1. **Complementary**: Colors opposite each other on the color wheel, creating a high-contrast effect.
2. **Analogous**: Colors adjacent to each other on the color wheel, creating a harmonious and cohesive look.
3. **Triadic**: Three colors evenly spaced on the color wheel, offering a balanced and vibrant color scheme.
4. **Tetradic**: Four colors arranged into two complementary pairs, providing a rich and varied palette.
5. **Tints**: Lighter variations of a color, created by adding white.
6. **Shades**: Darker variations of a color, created by adding black.

## Dependencies

- Python 3.11+

For a complete list of dependencies with version information, see `requirements.txt`.

## Potential Use Cases

The Original at [MichailSemoglou/color-palette-extractor](https://github.com/MichailSemoglou/color-palette-extractor) was aimed at Design/Branding,
this is designed for generating color palettes for automated use.
TODO: pywal like templating

## License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.
