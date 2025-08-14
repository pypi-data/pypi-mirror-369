# html2term

html2term is a lightweight Python library that converts minimal HTML-like markup into ANSI-styled terminal output. It supports text styles, colors (including truecolor hex), layout tags, and nested formatting, all with zero external dependencies and full cross-platform compatibility.

[![PyPI version](https://badge.fury.io/py/html2term.svg)](https://badge.fury.io/py/html2term)

## ✨ Features

-   **Text Styles**: `<b>`, `<i>`, `<u>`, `<strike>`, `<blink>`.
-   **Semantic Tags**: `<strong>` (bold) and `<em>` (italic).
-   **16 Standard Colors**: `<red>`, `<green>`, `<bg-blue>`, etc.
-   **Truecolor (24-bit)**: Hex color support like `<#RRGGBB>` and `<bg-#RRGGBB>`.
-   **Layout**: Line breaks (`<br>`) and tabs (`<tab>`).
-   **Nested Tags**: `<b><red>Important!</red></b>` works as expected.
-   **Cross-Platform**: Works on Windows, macOS, and Linux.
-   **Zero Dependencies**: Only uses the Python standard library.

## 💾 Installation

Install `html2term` directly from PyPI:

```bash
pip install html2term
```

## 🚀 Usage

The package provides a simple function `printc` to parse and print styled text directly to your terminal.

```python
from html2term import printc

# --- Basic Usage ---
printc("<b>Hello, <green>World</green>!</b>")
printc("<i>This is <u>very</u> important information.</i>")

# --- Nested Styles ---
printc("<b>This is bold, but <red>this part is also red.</red></b>")

# --- Hex Colors (Truecolor) ---
printc("<#ff00ff>This is magenta text.</#ff00ff>")
printc("<bg-#003366>Dark blue background.</bg-#003366>")
printc("<b><#ffff00>Combine styles with hex colors!</#ffff00></b>")

# --- Layout ---
printc("First line.<br/>Second line.")
printc("Column 1<tab/>Column 2")
```

You can also use the `convert()` function if you need the raw string with ANSI codes.

```python
from html2term import convert

ansi_string = convert("<b><blue>I am a string</blue></b>")
print(ansi_string)
# Output: '\x1b[1m\x1b[34mI am a string\x1b[0m\x1b[1m\x1b[0m'
```

## 🏷️ Supported Tags

### Styles
- `<b>`, `<strong>` - Bold
- `<i>`, `<em>` - Italic
- `<u>` - Underline
- `<strike>` - Strikethrough
- `<blink>` - Blinking text

### Foreground Colors
- **Standard**: `black`, `red`, `green`, `yellow`, `blue`, `magenta`, `cyan`, `white`, `default`
- **Hex**: `<#RRGGBB>` (e.g., `<#ff7f50>`)

### Background Colors
- **Standard**: `bg-black`, `bg-red`, `bg-green`, etc.
- **Hex**: `<bg-#RRGGBB>` (e.g., `<bg-#0a0a0a>`)

### Layout
- `<br>`, `<br/>`, `<br />` - Newline
- `<tab>`, `<tab/>`, `<tab />` - Tab character

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/Nikityyy/html2term/issues).
