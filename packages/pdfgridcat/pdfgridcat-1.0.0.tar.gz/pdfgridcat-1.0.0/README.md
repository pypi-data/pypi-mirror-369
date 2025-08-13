# pdfgridcat

Arrange multiple PDF images both horizontally and vertically on a single page without scaling or margins.

## Features
- Combine multiple PDF files into a grid (no scaling, no margins)
- Specify number of columns and rows per page
- Both CLI and Python API

## Installation
```bash
pip install pdfgridcat
````

## Usage (CLI)

```bash
pdfgridcat -i *.pdf -o output.pdf -c 2 -r 3
```

This arranges PDFs in 2 columns × 3 rows per page.

## Usage (Python)

```python
from pdfgridcat import concat_pdf_pages

concat_pdf_pages(
    input_files=["a.pdf", "b.pdf", "c.pdf"],
    output_file="output.pdf",
    col=2,
    row=3
)
````

## License

MIT License
