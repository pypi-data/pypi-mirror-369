# Single-Stroke to Closed Contour Font Converter

This tool converts single-line open contour SVG fonts into closed contour formats suitable for TTF generation. It takes SVG paths that represent single strokes and creates closed paths by duplicating points and connecting them with rounded or square end caps.

## What it does

The converter:
- **Analyzes single-stroke paths**: Parses SVG path data to extract coordinate points
- **Creates offset paths**: Generates parallel paths on both sides of the original stroke
- **Adds end caps**: Connects the paths with rounded (default) or square end caps
- **Closes the contour**: Creates a complete closed path suitable for font generation

## Usage

```bash
python3 stroke_to_closed_converter.py input.svg output.svg [options]
```

### Basic Example
```bash
python3 stroke_to_closed_converter.py input_font.svg output_font.svg
```

### With Custom Options
```bash
python3 stroke_to_closed_converter.py input_font.svg output_font.svg --stroke-width 30 --join-style round
```

### Options
- `--stroke-width` or `-w`: Width of the stroke (default: 50.0)
- `--join-style` or `-j`: End cap style, either "round" or "square" (default: round)

## Example Conversion

**Original single-stroke path:**
```
M136 1741q3 -157 13 -286.5t24 -235.5t31.5 -190.5t33.5 -152.5 M253 -4q-11 34 -11.5 59t6.5 41.5t18 24.5t22 8t20 -8t12.5 -23t-1.5 -38t-22 -53
```

**Converted closed contour:**
```
M150.96 1739.95 L17.96 -155.85 ... A15.0 15.0 0 0 1 150.96 1739.95 Z
```

The converter successfully processed your PremiumUltra87v6 font:
- **Found**: 449 glyphs with path data
- **Converted**: 449/449 glyphs successfully
- **Output**: `PremiumUltra87v6_closed.svg`

## Technical Details

### How it works
1. **Path parsing**: Extracts coordinates from SVG path commands (M, L, H, V, C, Q, T)
2. **Offset calculation**: Creates perpendicular offsets for each line segment
3. **Path construction**: Builds a closed path by:
   - Drawing along one side of the stroke
   - Adding an end cap (arc for round, line for square)
   - Drawing back along the other side
   - Adding another end cap to close the path

### Supported SVG Path Commands
- `M` (Move to)
- `L` (Line to)  
- `H` (Horizontal line)
- `V` (Vertical line)
- `C` (Cubic Bezier curve)
- `Q` (Quadratic Bezier curve)
- `T` (Smooth quadratic curve)

### Next Steps for TTF Creation

After conversion, you can use tools like:
- **FontForge**: Convert SVG to TTF
- **fonttools**: Python library for font manipulation
- **ttfautohint**: Automatic hinting for TrueType fonts

## Requirements

- Python 3.6+
- Standard library only (no external dependencies)

## Files in this directory

- `stroke_to_closed_converter.py`: Main converter script
- `PremiumUltra87v6_closed.svg`: Your converted font file
- `README.md`: This documentation

The converter is now ready to process other single-stroke SVG fonts with the same approach!

# singlestroke

[`vpype`](https://github.com/abey79/vpype) plug-in to [_to be completed_]


## Examples

_to be completed_


## Installation

See the [installation instructions](https://vpype.readthedocs.io/en/latest/install.html) for information on how
to install `vpype`.

If *vpype* was installed using pipx, use the following command:

```bash
$ pipx inject vpype singlestroke
```

If *vpype* was installed using pip in a virtual environment, activate the virtual environment and use the following command:

```bash
$ pip install singlestroke
```

Check that your install is successful:

```
$ vpype singlestroke --help
[...]
```

## Documentation

The complete plug-in documentation is available directly in the CLI help:

```bash
$ vpype singlestroke --help
```


## Development setup

Here is how to clone the project for development:

```bash
$ git clone https://github.com/d-n-l-lab/singlestroke.git
$ cd singlestroke
```

Create a virtual environment:

```bash
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install --upgrade pip
```

Install `singlestroke` and its dependencies (including `vpype`):

```bash
$ pip install -e .
$ pip install -r dev-dependencies.txt
```


## License

See the [LICENSE](LICENSE) file for details.
