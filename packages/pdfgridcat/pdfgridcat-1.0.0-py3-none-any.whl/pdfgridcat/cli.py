#!/usr/bin/env python3
"""
pdfgridcat - Arrange multiple PDF pages into a grid without scaling or margins.
"""

DESCRIPTION = 'Arrange multiple PDF images both horizontally and vertically within a single page, resulting in multiple pages'
MAX_OPEN_FILE = 30


def main():
    """
    Command-line interface entry point.

    Parses command-line arguments for:
      - Input PDF files
      - Output PDF file
      - Number of columns
      - Number of rows

    Then calls `concat_pdf_pages` to generate the output PDF.
    """
    import argparse
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument("-i", "--input", type=str, nargs="+", required=True,
                        help="Input PDF files")
    parser.add_argument("-o", "--output", type=str, required=True,
                        help="Output PDF file")
    parser.add_argument("-c", "--columns", type=int, default=1,
                        help="Number of columns per page")
    parser.add_argument("-r", "--rows", type=int, default=1,
                        help="Number of rows per page")
    args = parser.parse_args()
    concat_pdf_pages(args.input, args.output, args.columns, args.rows)


def concat_pdf_pages(input_files, output_file, col, row):
    """
    Arrange multiple PDF pages into a grid (no scaling, no margins).

    Parameters
    ----------
    input_files : list of str
        Paths to input PDF files. Only the first page of each is used.
    output_file : str
        Path to output PDF file.
    col : int
        Number of columns in the grid per page.
    row : int
        Number of rows in the grid per page.

    Behavior
    --------
    - Reads the first page from each input file.
    - Groups them into `col * row` pages per output page.
    - Concatenates horizontally to form rows, then vertically to form the page.
    - Creates multiple output pages if needed.
    - If the number of input files exceeds MAX_OPEN_FILE, calls `use_temp_files`.
    """
    from pypdf import PdfReader, PdfWriter
    import os

    if len(input_files) > max(MAX_OPEN_FILE, col * row):
        use_temp_files(input_files, output_file, col, row)
        return

    output = PdfWriter()
    per_page = col * row

    for i in range(0, len(input_files), per_page):
        page_rows = []
        pages_in_block = []

        for j in range(i, min(i + per_page, len(input_files))):
            reader = PdfReader(input_files[j], strict=False)
            pages_in_block.append(reader.pages[0])

        for j in range(0, min(per_page, len(input_files) - i), col):
            page_rows.append(concat_pdf(
                pages_in_block[j:min(j + col, len(pages_in_block))],
                horizontal=True
            ))

        os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)
        output.add_page(concat_pdf(page_rows, horizontal=False))

    with open(output_file, "wb") as f:
        output.write(f)


def use_temp_files(input_files, output_file, col, row):
    """
    Process input files in smaller batches to avoid 'Too many open files' errors.

    Parameters
    ----------
    input_files : list of str
        Paths to input PDF files.
    output_file : str
        Path to final output PDF file.
    col : int
        Number of columns per output page.
    row : int
        Number of rows per output page.

    Behavior
    --------
    - Splits input files into chunks that fit within MAX_OPEN_FILE.
    - Creates temporary intermediate PDFs for each chunk by calling `concat_pdf_pages`.
    - Merges all temporary PDFs into the final output file.
    - Deletes temporary files afterward.
    """
    import os
    from pypdf import PdfWriter

    total_files = len(input_files)
    pdf_in_page = col * row
    pdf_in_file = max((MAX_OPEN_FILE // pdf_in_page), 1) * pdf_in_page
    num_files = (total_files - 1) // pdf_in_file + 1

    out_dir = os.path.dirname(output_file) or "."
    out_base = os.path.basename(output_file)
    os.makedirs(out_dir, exist_ok=True)

    print(f"As number of PDFs ({total_files}) exceeds {MAX_OPEN_FILE}, using temporary files.")
    tmp_files = []
    for i in range(num_files):
        tmp_file = os.path.join(out_dir, f'tmp_{i}_{out_base}')
        tmp_files.append(tmp_file)
        concat_pdf_pages(input_files[pdf_in_file*i : min(total_files, pdf_in_file*(i+1))], tmp_file, col, row)

    writer = PdfWriter()
    for file in tmp_files:
        try:
            writer.append(file)
        except AttributeError:
            from pypdf import PdfReader
            reader = PdfReader(file, strict=False)
            for p in reader.pages:
                writer.add_page(p)

    with open(output_file, "wb") as f:
        writer.write(f)

    for file in tmp_files:
        os.remove(file)
    print(f"{output_file} created and temporary files removed.")


def concat_pdf(pages, horizontal=False):
    """
    Concatenate multiple PDF pages horizontally or vertically (no scaling, no margins).

    Parameters
    ----------
    pages : list of pypdf.PageObject
        PDF pages to combine. Must be non-empty.
    horizontal : bool, optional
        If True, pages are concatenated left-to-right (horizontally).
        If False, pages are concatenated top-to-bottom (vertically).

    Returns
    -------
    pypdf.PageObject
        A new PDF page containing the concatenated pages.

    Raises
    ------
    ValueError
        If `pages` is empty.

    Notes
    -----
    - Uses the exact page dimensions (mediabox) of input pages.
    - Does not scale or add margins.
    """
    from pypdf import PageObject
    if not pages:
        raise ValueError("pages must be a non-empty list")

    def w(p): return float(p.mediabox.width)
    def h(p): return float(p.mediabox.height)

    if horizontal:
        total_width = sum(w(page) for page in pages)
        total_height = max(h(page) for page in pages)
    else:
        total_width = max(w(page) for page in pages)
        total_height = sum(h(page) for page in pages)

    new_page = PageObject.create_blank_page(width=total_width, height=total_height)

    if horizontal:
        new_page.merge_page(pages[0])
        offset = w(pages[0])
    else:
        offset = total_height - h(pages[0])
        new_page.merge_translated_page(pages[0], 0, offset)

    for i in range(1, len(pages)):
        if horizontal:
            new_page.merge_translated_page(pages[i], offset, 0)
            offset += w(pages[i])
        else:
            offset -= h(pages[i])
            new_page.merge_translated_page(pages[i], 0, offset)

    return new_page
