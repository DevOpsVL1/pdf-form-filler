from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from pypdf import PdfReader, PdfWriter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io

def format_ic_number(text, space_after_positions=[6, 8]):
    """
    Format IC number by inserting spaces at specific positions
    Example: "123456789012" with positions [6, 8] becomes "123456 78 9012"

    Args:
        text: The IC number text
        space_after_positions: List of positions after which to insert spaces

    Returns:
        Formatted text with spaces
    """
    result = []
    for i, char in enumerate(text):
        result.append(char)
        # Check if we need to add space after this position (1-indexed)
        if (i + 1) in space_after_positions and (i + 1) < len(text):
            result.append(' ')
    return ''.join(result)


def format_phone_number(text, space_after_position=3, add_leading_space=False):
    """
    Format phone number with space after specified position

    Args:
        text: The phone number text
        space_after_position: Position after which to add space (2 or 3)
        add_leading_space: If True, add leading space (start from 2nd box)

    Returns:
        Formatted text with spaces
    """
    text = text.strip()
    formatted = format_ic_number(text, space_after_positions=[space_after_position])

    if add_leading_space:
        formatted = ' ' + formatted

    return formatted


def fill_date_boxes(text, start_x, start_y, box_width=15, box_spacing=2,
                    separator_width=7, separator_char='-'):
    """
    Fill date boxes with format DD-MM-YYYY where separators use smaller boxes
    Separator characters are not rendered (left empty) but spacing is preserved

    Args:
        text: Date string (e.g., "06-06-1976")
        start_x: Starting X coordinate
        start_y: Starting Y coordinate
        box_width: Width of regular character boxes
        box_spacing: Spacing between boxes
        separator_width: Width of separator boxes (smaller)
        separator_char: Character to use as separator

    Returns:
        List of tuples (char, x_pos, y_pos) - separators return empty string ''
    """
    positions = []
    current_x = start_x

    for char in text:
        x_pos = current_x
        y_pos = start_y

        # If it's a separator, add empty string (won't be rendered)
        if char == separator_char:
            positions.append(('', x_pos, y_pos))  # Empty string instead of separator
            current_x += separator_width + box_spacing
        else:
            positions.append((char, x_pos, y_pos))
            current_x += box_width + box_spacing

    return positions


def fill_phone_boxes(text, start_x, start_y, box_width=15, box_spacing=2,
                     space_separator_width=7, space_after_position=3, add_leading_space=False):
    """
    Fill phone number boxes where space separator can have different width than character boxes

    Args:
        text: Phone number string (without spaces, e.g., "0321234567")
        start_x: Starting X coordinate
        start_y: Starting Y coordinate
        box_width: Width of regular character boxes
        box_spacing: Spacing between boxes
        space_separator_width: Width of the empty space box (for the separator)
        space_after_position: Position after which to add space (2 or 3)
        add_leading_space: If True, add leading space (start from 2nd box)

    Returns:
        List of tuples (char, x_pos, y_pos) - space returns empty string ''
    """
    positions = []
    current_x = start_x

    text = text.strip()

    # Add leading space if requested
    if add_leading_space:
        positions.append(('', current_x, start_y))
        current_x += box_width + box_spacing

    # Process each character
    for i, char in enumerate(text):
        x_pos = current_x
        y_pos = start_y

        positions.append((char, x_pos, y_pos))
        current_x += box_width + box_spacing

        # Add space separator after specified position
        if (i + 1) == space_after_position and (i + 1) < len(text):
            positions.append(('', current_x, y_pos))  # Empty space box
            current_x += space_separator_width + box_spacing

    return positions


def fill_sequential_boxes(text, start_x, start_y, box_width=15, box_spacing=2,
                          boxes_per_row=20, row_height=20, max_rows=3):
    """
    Fill boxes sequentially character by character, strictly according to available boxes
    No word-wrapping - characters fill left to right, top to bottom

    Args:
        text: String to fill in boxes
        start_x: Starting X coordinate
        start_y: Starting Y coordinate (top of first row)
        box_width: Width of each box
        box_spacing: Spacing between boxes
        boxes_per_row: Number of boxes per row
        row_height: Height between rows
        max_rows: Maximum number of rows available

    Returns:
        List of tuples (char, x_pos, y_pos)
    """
    positions = []
    total_boxes = boxes_per_row * max_rows
    char_index = 0

    for row in range(max_rows):
        for col in range(boxes_per_row):
            if char_index >= len(text):
                break  # No more characters to place

            char = text[char_index]
            x_pos = start_x + (col * (box_width + box_spacing))
            y_pos = start_y - (row * row_height)

            positions.append((char, x_pos, y_pos))
            char_index += 1

        if char_index >= len(text):
            break  # No more characters to place

    if char_index < len(text):
        print(f"Warning: Text '{text}' truncated. Only {char_index}/{len(text)} characters fit in {total_boxes} boxes.")

    return positions


def fill_character_boxes(text, start_x, start_y, box_width=15, box_spacing=2,
                         boxes_per_row=20, row_height=20, max_rows=3,
                         remove_commas=False, respect_newlines=False):
    """
    Calculate positions for each character to fit in individual boxes with multi-row support
    Words are kept together - if a word doesn't fit in the current row, it moves to the next row

    Args:
        text: String to fill in boxes (spaces indicate word boundaries)
        start_x: Starting X coordinate
        start_y: Starting Y coordinate (top of first row)
        box_width: Width of each box
        box_spacing: Spacing between boxes
        boxes_per_row: Number of boxes per row
        row_height: Height between rows
        max_rows: Maximum number of rows available
        remove_commas: If True, remove all commas from text
        respect_newlines: If True, newline characters force move to next row

    Returns:
        List of tuples (char, x_pos, y_pos)
    """
    positions = []

    # Remove commas if specified
    if remove_commas:
        text = text.replace(',', '')
        print(f"After removing commas: '{text}'")

    # If respecting newlines, split by newlines first
    if respect_newlines:
        lines = text.split('\n')
        print(f"Split into {len(lines)} lines by newlines")
    else:
        lines = [text]

    current_row = 0

    for line_idx, line in enumerate(lines):
        # Reset column for each new line
        current_col = 0
        words = line.split(' ')  # Split by space to get words

        print(f"Processing line {line_idx + 1}: '{line}'")

        for word_idx, word in enumerate(words):
            word_length = len(word)

            print(f"  Processing word '{word}' (length={word_length}) at row={current_row}, col={current_col}")

            # Check if we exceed max rows before processing this word
            if current_row >= max_rows:
                print(f"Warning: Text '{text}' exceeds {max_rows} rows. Truncating...")
                break

            # Check if current word fits in the remaining space of current row
            remaining_boxes = boxes_per_row - current_col
            print(f"    Remaining boxes in row: {remaining_boxes}")

            if current_col + word_length > boxes_per_row:
                # Word doesn't fit, move to next row
                print(f"    Word doesn't fit, moving to next row")
                current_row += 1
                current_col = 0

                # Check again if we exceed max rows after moving to next row
                if current_row >= max_rows:
                    print(f"Warning: Text '{text}' exceeds {max_rows} rows. Truncating...")
                    break

            # Place each character of the word (word is guaranteed to fit now)
            for char in word:
                # Calculate position
                x_pos = start_x + (current_col * (box_width + box_spacing))
                y_pos = start_y - (current_row * row_height)  # Subtract to move DOWN (PDF coordinates)

                positions.append((char, x_pos, y_pos))
                current_col += 1

            print(f"    After placing word: row={current_row}, col={current_col}")

            # Add space after word (except for last word in line)
            if word_idx < len(words) - 1:
                # Space takes up one box position but we don't render it
                current_col += 1
                print(f"    After space: row={current_row}, col={current_col}")

        # Move to next row after each line (except last line)
        if respect_newlines and line_idx < len(lines) - 1:
            current_row += 1
            print(f"  Moving to next row due to newline: row={current_row}")

    return positions

def create_overlay_pdf(field_data, draw_grid=False):
    """
    Create a PDF overlay with text at specific coordinates

    Args:
        field_data: Dictionary with field names and their data
                   Format: {field_name: {'text': 'value', 'x': x_pos, 'y': y_pos, 'size': font_size}}
        draw_grid: If True, draw coordinate grid with 10-unit spacing

    Returns:
        PDF bytes buffer
    """
    packet = io.BytesIO()

    # Get page size from original PDF
    can = canvas.Canvas(packet, pagesize=A4)
    width, height = A4

    # Draw grid if requested
    if draw_grid:
        can.setStrokeColorRGB(0.8, 0.8, 0.8)  # Light gray
        can.setLineWidth(0.5)
        can.setFont("Helvetica", 6)

        # Draw vertical lines (every 10 units along x-axis)
        for x in range(0, int(width) + 1, 10):
            can.line(x, 0, x, height)
            # Label every 50 units at top and bottom
            if x % 50 == 0:
                can.setFillColorRGB(1, 0, 0)  # Red text
                can.drawString(x + 2, height - 10, f"x={x}")  # Top
                can.drawString(x + 2, 5, f"x={x}")  # Bottom
                can.setFillColorRGB(0, 0, 0)  # Back to black

        # Draw horizontal lines (every 10 units along y-axis from top)
        for y_from_top in range(0, int(height) + 1, 10):
            y_from_bottom = height - y_from_top
            can.line(0, y_from_bottom, width, y_from_bottom)
            # Label every 50 units at left and right
            if y_from_top % 50 == 0:
                can.setFillColorRGB(0, 0, 1)  # Blue text
                can.drawString(2, y_from_bottom + 2, f"y={y_from_top}")  # Left
                can.drawString(width - 35, y_from_bottom + 2, f"y={y_from_top}")  # Right
                can.setFillColorRGB(0, 0, 0)  # Back to black

    # Try to use a standard font (Arial or Helvetica)
    can.setFont("Helvetica", 10)

    # Draw each field
    for field_name, data in field_data.items():
        text = data['text']

        # Check if this is a checkbox/option field
        if data.get('is_checkbox', False):
            font_size = data.get('size', 10)
            can.setFont("Helvetica", font_size)

            checkbox_options = data.get('checkbox_options', {})
            # Find which option matches the text
            for option_value, coords in checkbox_options.items():
                if text == option_value:
                    # Draw the checkmark "/" at the specified coordinates
                    check_x = coords['x']
                    check_y = height - coords['y']  # Convert from top-left to bottom-left
                    can.drawString(check_x, check_y, "/")
                    print(f"Checkbox '{option_value}' marked at ({check_x}, {check_y})")
                    break
            continue  # Skip to next field

        # Check if this field is conditional and should be skipped
        if data.get('conditional_on', False):
            parent_field = data.get('conditional_field')
            required_value = data.get('conditional_value')
            # Check if parent field exists and has the required value
            if parent_field in field_data:
                if field_data[parent_field].get('text') != required_value:
                    continue  # Skip this field

        # Apply IC number formatting if specified
        if data.get('format_ic', False):
            space_positions = data.get('ic_space_positions', [6, 8])
            text = format_ic_number(text, space_positions)
            print(f"IC formatted: '{data['text']}' -> '{text}'")

        # Apply phone number formatting if specified
        if data.get('format_phone', False):
            space_pos = data.get('phone_space_position', 3)
            leading_space = data.get('phone_leading_space', False)
            text = format_phone_number(text, space_after_position=space_pos, add_leading_space=leading_space)
            print(f"Phone formatted: '{data['text']}' -> '{text}'")

        # Add leading space if single character and specified
        if data.get('add_leading_space_if_single', False):
            if len(text.strip()) == 1:
                text = ' ' + text.strip()
                print(f"Added leading space for single character: '{data['text']}' -> '{text}'")

        x = data['x']
        y = height - data['y']  # Convert from top-left to bottom-left origin
        font_size = data.get('size', 10)

        can.setFont("Helvetica", font_size)

        # Check if this is a phone field with custom space separator width
        if data.get('is_phone', False):
            positions = fill_phone_boxes(
                text, x, y,
                box_width=data.get('box_width', 15),
                box_spacing=data.get('box_spacing', 2),
                space_separator_width=data.get('phone_space_separator_width', 7),
                space_after_position=data.get('phone_space_position', 3),
                add_leading_space=data.get('phone_leading_space', False)
            )
            for char, char_x, char_y in positions:
                if char:  # Only draw non-empty characters (skip separators)
                    can.drawString(char_x + 2, char_y - 3, char)  # Slight offset for centering
        # Check if this is a date field with special separator boxes
        elif data.get('is_date', False):
            positions = fill_date_boxes(
                text, x, y,
                box_width=data.get('box_width', 15),
                box_spacing=data.get('box_spacing', 2),
                separator_width=data.get('separator_width', 7),
                separator_char=data.get('separator_char', '-')
            )
            for char, char_x, char_y in positions:
                if char:  # Only draw non-empty characters (skip separators)
                    can.drawString(char_x + 2, char_y - 3, char)  # Slight offset for centering
        # Check if this field should use sequential box filling (no word wrapping)
        elif data.get('fill_sequential', False):
            positions = fill_sequential_boxes(
                text, x, y,
                box_width=data.get('box_width', 15),
                box_spacing=data.get('box_spacing', 2),
                boxes_per_row=data.get('boxes_per_row', 20),
                row_height=data.get('row_height', 20),
                max_rows=data.get('max_rows', 3)
            )
            for char, char_x, char_y in positions:
                can.drawString(char_x + 2, char_y - 3, char)  # Slight offset for centering
        # Check if this field should use character boxes
        elif data.get('use_boxes', False):
            positions = fill_character_boxes(
                text, x, y,
                box_width=data.get('box_width', 15),
                box_spacing=data.get('box_spacing', 2),
                boxes_per_row=data.get('boxes_per_row', 20),
                row_height=data.get('row_height', 20),
                max_rows=data.get('max_rows', 3),
                remove_commas=data.get('remove_commas', False),
                respect_newlines=data.get('respect_newlines', False)
            )
            for char, char_x, char_y in positions:
                can.drawString(char_x + 2, char_y - 3, char)  # Slight offset for centering
        else:
            can.drawString(x, y, text)

    can.save()
    packet.seek(0)
    return packet

def fill_pdf_with_overlay(input_pdf, output_pdf, field_data, draw_grid=False):
    """
    Fill PDF by overlaying text at specific coordinates

    Args:
        input_pdf: Path to input PDF file
        output_pdf: Path to output filled PDF file
        field_data: Dictionary with field data and positions
        draw_grid: If True, draw coordinate grid on PDF
    """
    # Create overlay PDF
    overlay_pdf = create_overlay_pdf(field_data, draw_grid=draw_grid)

    # Read the original PDF
    original_pdf = PdfReader(input_pdf)
    overlay = PdfReader(overlay_pdf)

    # Create output PDF
    writer = PdfWriter()

    # Merge overlay with first page
    page = original_pdf.pages[0]
    page.merge_page(overlay.pages[0])
    writer.add_page(page)

    # Add remaining pages without modification
    for page_num in range(1, len(original_pdf.pages)):
        writer.add_page(original_pdf.pages[page_num])

    # Write output
    with open(output_pdf, 'wb') as output_file:
        writer.write(output_file)

    print(f"PDF filled successfully! Saved to: {output_pdf}")

if __name__ == "__main__":
    import os

    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))

    input_pdf = os.path.join(script_dir, "BORANG CIF-1.pdf")
    output_pdf = os.path.join(script_dir, "BORANG CIF-1 - Filled.pdf")

    # Field data with coordinates (measured from top-left in points)
    # You'll need to adjust these coordinates based on the actual PDF layout
    # Uncomment fields one by one to test and adjust coordinates
    field_data = {
        # SECTION A - MAKLUMAT PELANGGAN (CUSTOMER INFORMATION)

         "Negara Asal": {
             "text": "Lain-lain",  # Options: "My Malaysia", "Lain-lain"
             "is_checkbox": True,
             "size": 10,
             "checkbox_options": {
                 "My Malaysia": {"x": 51, "y": 238},
                 "Lain-lain": {"x": 51, "y": 247}
             }
         },

         "Negara Asal Lain-lain": {
             "text": "Indonesia",
             "x": 108,
             "y": 242,
             "size": 5,
             "use_boxes": True,
             "box_width": 5,
             "box_spacing": 0.01,
             "boxes_per_row": 10,
             "row_height": 5,
             "max_rows": 3,
             "conditional_on": True,
             "conditional_field": "Negara Asal",
             "conditional_value": "Lain-lain"
         },

         "Jenis Pengenalan Diri": {
             "text": "KP Polis",  # Options: "Kad Pengenalan Baru", "Sijil Kelahiran", "Pasport", "KP Tentera", "Kad Pengenalan Lama", "KP Polis"
             "is_checkbox": True,
             "size": 10,
             "checkbox_options": {
                 "Kad Pengenalan Baru": {"x": 183, "y": 240},
                 "Sijil Kelahiran": {"x": 183, "y": 249},
                 "Pasport": {"x": 183, "y": 259},
                 "KP Tentera": {"x": 183, "y": 268},
                 "Kad Pengenalan Lama": {"x": 183, "y": 276},
                 "KP Polis": {"x": 183, "y": 285}
             }
         },

         "Kewarganegaraan": {
             "text": "Penduduk Tetap",  # Options: "Warganegara", "Bukan warganegara", "Penduduk Tetap"
             "is_checkbox": True,
             "size": 10,
             "checkbox_options": {
                 "Warganegara": {"x": 51, "y": 273},
                 "Bukan warganegara": {"x": 51, "y": 282},
                 "Penduduk Tetap": {"x": 51, "y": 291}
             }
         },

         "No. Kad Pengenalan Baru": {
             "text": "920315105438",
             "x": 52,
             "y": 316,
             "size": 9,
             "is_date": False,
             "format_ic": True,
             "ic_space_positions": [6, 8],
             "use_boxes": True,
             "box_width": 12,
             "box_spacing": 0.2,
             "boxes_per_row": 15,
             "row_height": 15,
             "max_rows": 1
         },

         "No. Pengenalan Lama": {
             "text": "A1234567",
             "x": 52,
             "y": 344,
             "size": 9,
             "use_boxes": True,
             "box_width": 12,
             "box_spacing": 0.2,
             "boxes_per_row": 12,
             "row_height": 15,
             "max_rows": 1
         },

         "Tarikh Lahir": {
             "text": "15-03-1992",
             "x": 52,
             "y": 374,
             "size": 9,
             "is_date": True,
             "box_width": 12,
             "box_spacing": 0.2,
             "separator_width": 6,
             "separator_char": "-"
         },

         "Nama": {
             "text": "Ahmad Fariz bin Abdullah",
             "x": 52,
             "y": 403,
             "size": 9,
             "use_boxes": True,
             "box_width": 12,
             "box_spacing": 0.2,
             "boxes_per_row": 21,
             "row_height": 13,
             "max_rows": 3
         },

         "Nama Pilihan": {
             "text": "Fariz",
             "x": 52,
             "y": 458,
             "size": 9,
             "use_boxes": True,
             "box_width": 12,
             "box_spacing": 0.2,
             "boxes_per_row": 21,
             "row_height": 13,
             "max_rows": 2
         },

         "Gelaran": {
             "text": "Lain-lain",  # Options: "En", "Puan", "Cik", "Profesor", "Dato", "Datin", "Tan Sri", "Puan Sri", "Dr", "Yang Berhormat", "Lain-lain"
             "is_checkbox": True,
             "size": 10,
             "checkbox_options": {
                 "En": {"x": 52, "y": 504},
                 "Puan": {"x": 99, "y": 504},
                 "Cik": {"x": 142, "y": 504},
                 "Profesor": {"x": 199, "y": 504},
                 "Dato": {"x": 52, "y": 512},
                 "Datin": {"x": 99, "y": 512},
                 "Tan Sri": {"x": 52, "y": 521},
                 "Puan Sri": {"x": 99, "y": 521},
                 "Dr": {"x": 142, "y": 512},
                 "Yang Berhormat": {"x": 199, "y": 512},
                 "Lain-lain": {"x": 142, "y": 521}
             }
         },

         "Gelaran Lain-lain": {
             "text": "Tuan Besar",
             "x": 171,
             "y": 516,
             "size": 5,
             "use_boxes": True,
             "box_width": 5,
             "box_spacing": 0.01,
             "boxes_per_row": 10,
             "row_height": 5,
             "max_rows": 3,
             "conditional_on": True,
             "conditional_field": "Gelaran",
             "conditional_value": "Lain-lain"
         },

         "Jantina": {
             "text": "Perempuan",  # Options: "Lelaki", "Perempuan"
             "is_checkbox": True,
             "size": 10,
             "checkbox_options": {
                 "Lelaki": {"x": 141, "y": 539},
                 "Perempuan": {"x": 199, "y": 539}
             }
         },

         "Taraf Perkahwinan": {
             "text": "Bercerai",  # Options: "Bujang", "Balu", "Berkahwin", "Bercerai", "Lain-lain"
             "is_checkbox": True,
             "size": 10,
             "checkbox_options": {
                 "Bujang": {"x": 52, "y": 565},
                 "Balu": {"x": 141, "y": 565},
                 "Berkahwin": {"x": 52, "y": 574},
                 "Bercerai": {"x": 141, "y": 574},
                 "Lain-lain": {"x": 52, "y": 584}
             }
         },

         "Bilangan Tanggungan": {
             "text": "2",
             "x": 172,
             "y": 591,
             "size": 9,
             "use_boxes": True,
             "box_width": 10,
             "box_spacing": 0.09,
             "boxes_per_row": 2,
             "row_height": 13,
             "max_rows": 1,
             "add_leading_space_if_single": True
         },

         "Bangsa": {
             "text": "Lain-lain",  # Options: "Bumiputera", "Cina", "India", "Lain-lain"
             "is_checkbox": True,
             "size": 10,
             "checkbox_options": {
                 "Bumiputera": {"x": 52, "y": 620},
                 "Cina": {"x": 141, "y": 620},
                 "India": {"x": 52, "y": 631},
                 "Lain-lain": {"x": 141, "y": 631}
             }
         },

         "Bangsa Lain-lain": {
             "text": "Serani",
             "x": 196,
             "y": 626,
             "size": 5,
             "use_boxes": True,
             "box_width": 5,
             "box_spacing": 0.01,
             "boxes_per_row": 10,
             "row_height": 5,
             "max_rows": 3,
             "conditional_on": True,
             "conditional_field": "Bangsa",
             "conditional_value": "Lain-lain"
         },

         "Agama": {
             "text": "Lain-lain",  # Options: "Islam", "Buddha", "Hindu", "Kristian", "Lain-lain"
             "is_checkbox": True,
             "size": 10,
             "checkbox_options": {
                 "Islam": {"x": 52, "y": 656},
                 "Buddha": {"x": 141, "y": 656},
                 "Hindu": {"x": 226, "y": 656},
                 "Kristian": {"x": 52, "y": 667},
                 "Lain-lain": {"x": 141, "y": 667}
             }
         },

         "Agama Lain-lain": {
             "text": "Animisme",
             "x": 198,
             "y": 662,
             "size": 5,
             "use_boxes": True,
             "box_width": 5,
             "box_spacing": 0.01,
             "boxes_per_row": 10,
             "row_height": 5,
             "max_rows": 3,
             "conditional_on": True,
             "conditional_field": "Agama",
             "conditional_value": "Lain-lain"
         },

         "Pendidikan": {
             "text": "Lain-lain",  # Options: "Rendah", "Profesional", "Menengah", "Tinggi", "Lain-lain"
             "is_checkbox": True,
             "size": 10,
             "checkbox_options": {
                 "Rendah": {"x": 52, "y": 692},
                 "Profesional": {"x": 190, "y": 692},
                 "Menengah": {"x": 52, "y": 701},
                 "Tinggi": {"x": 190, "y": 701},
                 "Lain-lain": {"x": 52, "y": 711}
             }
         },

         "Pendidikan Lain-lain": {
             "text": "Homeschool",
             "x": 85,
             "y": 705,
             "size": 5,
             "use_boxes": True,
             "box_width": 5,
             "box_spacing": 0.01,
             "boxes_per_row": 10,
             "row_height": 5,
             "max_rows": 3,
             "conditional_on": True,
             "conditional_field": "Pendidikan",
             "conditional_value": "Lain-lain"
         },

         "Kategori Pelanggan": {
             "text": "Warga Kerja Co-opbank Pertama",  # Options: "Anggota Co-opbank Pertama", "Warga Kerja Co-opbank Pertama", "Bukan Anggota Tetapi Layak Menjadi Anggota", "Keluarga Terdekat Warga Kerja"
             "is_checkbox": True,
             "size": 10,
             "checkbox_options": {
                 "Anggota Co-opbank Pertama": {"x": 52, "y": 738},
                 "Warga Kerja Co-opbank Pertama": {"x": 190, "y": 738},
                 "Bukan Anggota Tetapi Layak Menjadi Anggota": {"x": 52, "y": 748},
                 "Keluarga Terdekat Warga Kerja": {"x": 52, "y": 759}
             }
         },

         "Nama Ibu": {
             "text": "Siti Aminah binti Hassan",
             "x": 52,
             "y": 788,
             "size": 9,
             "use_boxes": True,
             "box_width": 12,
             "box_spacing": 0.2,
             "boxes_per_row": 21,
             "row_height": 13,
             "max_rows": 2
         },

        # SECTION B - MAKLUMAT KONTAK (CONTACT DETAILS)

         "Alamat Kediaman": {
             "text": "No 25, Jalan Mawar 3/5,\nTaman Bunga Raya\nKuala Lumpur",
             "x": 316,
             "y": 203,
             "size": 9,
             "use_boxes": True,
             "box_width": 12,
             "box_spacing": 0.1,
             "boxes_per_row": 21,
             "row_height": 13,
             "max_rows": 3,
             "remove_commas": True,
             "respect_newlines": True
         },

         "Poskod Kediaman": {
             "text": "50100",
             "x": 317,
             "y": 255,
             "size": 9,
             "use_boxes": True,
             "box_width": 12,
             "box_spacing": 0.2,
             "boxes_per_row": 5,
             "row_height": 13,
             "max_rows": 1
         },

         "Bandar Kediaman": {
             "text": "Kuala Lumpur",
             "x": 388,
             "y": 255,
             "size": 9,
             "use_boxes": True,
             "box_width": 12,
             "box_spacing": 0.2,
             "boxes_per_row": 15,
             "row_height": 13,
             "max_rows": 1
         },

         "Negeri Kediaman": {
             "text": "Wilayah Persekutuan",
             "x": 315,
             "y": 280,
             "size": 9,
             "use_boxes": True,
             "box_width": 12,
             "box_spacing": 0,
             "boxes_per_row": 20,
             "row_height": 13,
             "max_rows": 1
         },

         "Jenis Pemilikan": {
             "text": "Lain-lain",  # Options: "Sendiri", "Sewa", "Lain-lain"
             "is_checkbox": True,
             "size": 10,
             "checkbox_options": {
                 "Sendiri": {"x": 320, "y": 308},
                 "Sewa": {"x": 372, "y": 308},
                 "Lain-lain": {"x": 424, "y": 308}
             }
         },

         "Jenis Pemilikan Lain-lain": {
             "text": "Warisan",
             "x": 476,
             "y": 303,
             "size": 5,
             "use_boxes": True,
             "box_width": 5,
             "box_spacing": 0.01,
             "boxes_per_row": 10,
             "row_height": 5,
             "max_rows": 3,
             "conditional_on": True,
             "conditional_field": "Jenis Pemilikan",
             "conditional_value": "Lain-lain"
         },

         "Alamat Surat Menyurat": {
             "text": "No 25, Jalan Mawar 3/5,\nTaman Bunga Raya\nKuala Lumpur",
             "x": 316,
             "y": 327,
             "size": 9,
             "use_boxes": True,
             "box_width": 12,
             "box_spacing": 0.1,
             "boxes_per_row": 21,
             "row_height": 13,
             "max_rows": 2,
             "remove_commas": True,
             "respect_newlines": True
         },

         "Poskod Surat": {
             "text": "50100",
             "x": 317,
             "y": 366,
             "size": 9,
             "use_boxes": True,
             "box_width": 12,
             "box_spacing": 0.2,
             "boxes_per_row": 5,
             "row_height": 13,
             "max_rows": 1
         },

         "Bandar Surat": {
             "text": "Kuala Lumpur",
             "x": 388,
             "y": 366,
             "size": 9,
             "use_boxes": True,
             "box_width": 12,
             "box_spacing": 0.2,
             "boxes_per_row": 15,
             "row_height": 13,
             "max_rows": 1
         },

         "Negeri Surat": {
             "text": "Wilayah Persekutuan",
             "x": 315,
             "y": 391,
             "size": 9,
             "use_boxes": True,
             "box_width": 12,
             "box_spacing": 0,
             "boxes_per_row": 25,
             "row_height": 13,
             "max_rows": 1
         },

         "Tel Kediaman": {
             "text": "0321234567",
             "x": 389,
             "y": 420,
             "size": 9,
             "is_phone": True,
             "box_width": 12,
             "box_spacing": 0.1,
             "phone_space_separator_width": 6,  # Adjust this value to change the space box width
             "phone_space_position": 2,
             "phone_leading_space": True
         },

         "Tel Pejabat": {
             "text": "0387654321",
             "x": 389,
             "y": 433,
             "size": 9,
             "is_phone": True,
             "box_width": 12,
             "box_spacing": 0.1,
             "phone_space_separator_width": 6,  # Adjust this value to change the space box width
             "phone_space_position": 2,
             "phone_leading_space": True
         },

         "Tel Bimbit": {
             "text": "0123456789",
             "x": 377,
             "y": 446,
             "size": 9,
             "is_phone": True,
             "box_width": 12,
             "box_spacing": 0.1,
             "phone_space_separator_width": 6,  # Adjust this value to change the space box width
             "phone_space_position": 3,
             "phone_leading_space": True
         },

         "Faks": {
             "text": "0321234568",
             "x": 389,
             "y": 459,
             "size": 9,
             "is_phone": True,
             "box_width": 12,
             "box_spacing": 0.1,
             "phone_space_separator_width": 6,  # Adjust this value to change the space box width
             "phone_space_position": 2,
             "phone_leading_space": True
         },

         "Alamat Email": {
             "text": "ahmad.fariz@email.com",
             "x": 388,
             "y": 471,
             "size": 9,
             "fill_sequential": True,  # Fill character by character, no word wrapping
             "box_width": 11,
             "box_spacing": 0.9,
             "boxes_per_row": 15,
             "row_height": 13,
             "max_rows": 2
         },

        # SECTION C - MAKLUMAT PEKERJAAN (INFORMATION OF EMPLOYMENT)

         "Nama Majikan": {
             "text": "Syarikat ABC Sdn Bhd",
             "x": 316,
             "y": 530,
             "size": 9,
             "use_boxes": True,
             "box_width": 12,
             "box_spacing": 0.1,
             "boxes_per_row": 21,
             "row_height": 13,
             "max_rows": 2
         },

         "Alamat Majikan": {
             "text": "Tingkat 10, Menara XYZ,\nJalan Sultan Ismail\nKuala Lumpur",
             "x": 316,
             "y": 568,
             "size": 9,
             "use_boxes": True,
             "box_width": 12,
             "box_spacing": 0.1,
             "boxes_per_row": 21,
             "row_height": 13,
             "max_rows": 3,
             "remove_commas": True,
             "respect_newlines": True
         },

         "Tarikh Mula Berkhidmat": {
             "text": "01-06-2025",
             "x": 316,
             "y": 620,
             "size": 9,
             "is_date": True,
             "box_width": 12,
             "box_spacing": 0.1,
             "separator_width": 7,
             "separator_char": "-"
         },

         "Pangkat": {
             "text": "Pengurus",
             "x": 458,
             "y": 619,
             "size": 9,
             "use_boxes": True,
             "box_width": 12,
             "box_spacing": 0.2,
             "boxes_per_row": 8,
             "row_height": 13,
             "max_rows": 1
         },

         "Taraf Jawatan": {
             "text": "Tetap",
             "x": 316,
             "y": 653,
             "size": 9,
             "use_boxes": True,
             "box_width": 12,
             "box_spacing": 0.2,
             "boxes_per_row": 20,
             "row_height": 13,
             "max_rows": 1
         },

         "Sektor Pekerjaan": {
             "text": "Tidak Berkenaan",  # Options: "Kakitangan Kerajaan", "Pertanian", "Pendidikan", "Kewangan", "Kesihatan", "Pembuatan", "Perkhidmatan", "Perniagaan", "Lain-lain", "Tidak Berkenaan"
             "is_checkbox": True,
             "size": 10,
             "checkbox_options": {
                 "Kakitangan Kerajaan": {"x": 316, "y": 684},
                 "Pertanian": {"x": 316, "y": 692},
                 "Pendidikan": {"x": 316, "y": 702},
                 "Kewangan": {"x": 316, "y": 710},
                 "Kesihatan": {"x": 316, "y": 719},
                 "Pembuatan": {"x": 316, "y": 728},
                 "Perkhidmatan": {"x": 316, "y": 738},
                 "Perniagaan": {"x": 316, "y": 746},
                 "Lain-lain": {"x": 316, "y": 755},
                 "Tidak Berkenaan": {"x": 316, "y": 765}
             }
         },

         "Pekerjaan": {
             "text": "Tidak Berkenaan",  # Multiple options available
             "is_checkbox": True,
             "size": 10,
             "checkbox_options": {
                 "Kerani": {"x": 441, "y": 684},
                 "Pegawai": {"x": 441, "y": 692},
                 "Pengurus": {"x": 441, "y": 702},
                 "Profesional": {"x": 441, "y": 710},
                 "Pendidik": {"x": 441, "y": 719},
                 "Pelajar": {"x": 441, "y": 728},
                 "Lain-lain": {"x": 441, "y": 738},
                 "Tidak Berkenaan": {"x": 441, "y": 746}
             }
         },

         "Julat Pendapatan": {
             "text": "Bawah RM 1,000",  # Options: "Bawah RM 1,000", "RM 1,000 - RM 3,000", "RM 3,001 - RM 5,000", "Melebihi RM 5,000", "Tidak Berkenaan"
             "is_checkbox": True,
             "size": 10,
             "checkbox_options": {
                 "Bawah RM 1,000": {"x": 316, "y": 786},
                 "RM 1,000 - RM 3,000": {"x": 316, "y": 795},
                 "RM 3,001 - RM 5,000": {"x": 316, "y": 803},
                 "Melebihi RM 5,000": {"x": 441, "y": 788},
                 "Tidak Berkenaan": {"x": 441, "y": 797}
             }
         }
    }

    # Set to True to draw coordinate grid on PDF (helps with finding x,y positions)
    DRAW_GRID = False

    if field_data or DRAW_GRID:
        fill_pdf_with_overlay(input_pdf, output_pdf, field_data, draw_grid=DRAW_GRID)
        if DRAW_GRID:
            print("\nGrid overlay created with 10-unit spacing.")
            print("- Red labels (x=) show horizontal positions")
            print("- Blue labels (y=) show vertical positions from top")
            print("- Grid lines every 10 units, labels every 50 units")
        print("\nNote: The coordinates may need adjustment to align perfectly with the boxes.")
        print("You can modify the 'x' and 'y' values in the script to fine-tune positioning.")
    else:
        print("No field_data provided yet. Please add field definitions to the field_data dictionary.")
