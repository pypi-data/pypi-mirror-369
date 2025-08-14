# colorwsap

Swap the color of non-transparent areas in a PNG image by specifying a file path, color (name or RGB tuple), and output file.

## Installation

pip install opencv-python numpy


## Usage

from colorwsap import swap_color

swap_color("input.png", "red", "output.png")
swap_color("input.png", (0, 128, 255), "output.png") # RGB tuple
swap_color("input.png", "magenta", "output.png")


- Supported colors: red, green, blue, white, black, yellow, cyan, magenta, grey, silver, maroon, olive, purple, teal, navy, orange, pink.
- The function replaces all visible pixels with the chosen color, preserving transparency.

