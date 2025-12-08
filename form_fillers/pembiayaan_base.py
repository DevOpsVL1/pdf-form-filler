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


def format_decimal_amount(text):
    """
    Format decimal amount for income fields.
    - If no decimal point: Add ".00" (e.g., "5000" becomes "5000.00")
    - If decimal with 1 digit: Pad with "0" (e.g., "5000.4" becomes "5000.40")
    - If decimal with 2 digits: Keep as is (e.g., "5000.12" stays "5000.12")

    The last 2 digits (decimal part) will go to the last 2 boxes (Box 8 and 9).
    The integer part fills the remaining boxes right-to-left.

    Args:
        text: Amount string (e.g., "5000", "5000.4", "5000.00")

    Returns:
        Formatted string with exactly 2 decimal places
    """
    text = text.strip()

    if '.' in text:
        parts = text.split('.')
        integer_part = parts[0]
        decimal_part = parts[1] if len(parts) > 1 else ""

        # Pad or truncate decimal part to 2 digits
        if len(decimal_part) == 0:
            decimal_part = "00"
        elif len(decimal_part) == 1:
            decimal_part = decimal_part + "0"
        elif len(decimal_part) > 2:
            decimal_part = decimal_part[:2]  # Truncate to 2 digits
    else:
        # No decimal point
        integer_part = text
        decimal_part = "00"

    # Return formatted with exactly 2 decimal places
    result = f"{integer_part}.{decimal_part}"
    print(f"Decimal formatted: '{text}' -> '{result}'")
    return result


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


def fill_conditional_phone_boxes(text, start_x, start_y, box_width=15, box_spacing=2,
                                  space_separator_width=7, space_after_position=3,
                                  check_position=1, check_value='1'):
    """
    Fill phone number boxes conditionally based on a character check.
    - If character at check_position equals check_value: fill left-to-right
    - Otherwise: fill right-to-left
    - Empty space separator placed after space_after_position

    Args:
        text: Phone number string (without spaces, e.g., "0321234567" or "0121234567")
        start_x: Starting X coordinate
        start_y: Starting Y coordinate
        box_width: Width of regular character boxes
        box_spacing: Spacing between boxes
        space_separator_width: Width of the empty space box (for the separator)
        space_after_position: Position after which to add space (typically 3)
        check_position: Character position to check (0-indexed, default 1 for 2nd character)
        check_value: Value to check against (default '1')

    Returns:
        List of tuples (char, x_pos, y_pos) - space returns empty string ''
    """
    positions = []
    text = text.strip()

    # Check if we should fill left-to-right or right-to-left
    if len(text) > check_position and text[check_position] == check_value:
        # Fill left-to-right (mobile number starting with "01")
        fill_direction = "left-to-right"
        print(f"Phone '{text}': Character at position {check_position} is '{check_value}' - filling {fill_direction}")

        current_x = start_x
        for i, char in enumerate(text):
            x_pos = current_x
            y_pos = start_y

            positions.append((char, x_pos, y_pos))
            current_x += box_width + box_spacing

            # Add space separator after specified position
            if (i + 1) == space_after_position and (i + 1) < len(text):
                positions.append(('', current_x, y_pos))  # Empty space box
                current_x += space_separator_width + box_spacing
    else:
        # Fill right-to-left (landline number NOT starting with "01")
        fill_direction = "right-to-left"
        print(f"Phone '{text}': Character at position {check_position} is NOT '{check_value}' - filling {fill_direction}")

        # Calculate total boxes needed
        # We need enough boxes to fit: text + 1 empty box at the start
        text_length = len(text)
        total_boxes = text_length + 1  # +1 for the leading empty box

        # Calculate positions for all boxes (left to right layout)
        box_positions = []
        current_x = start_x

        for i in range(total_boxes):
            box_positions.append(current_x)
            current_x += box_width + box_spacing

            # Add space separator after specified position
            if (i + 1) == space_after_position:
                # Add empty space separator
                box_positions.append(current_x)  # This will be used for empty space
                current_x += space_separator_width + box_spacing

        # Now we have box_positions for: [Box1(empty), Box2, Box3, SPACE, Box4, ..., Box11]
        # For "0345678901" (10 chars), we want:
        # Box1[empty], Box2[0], Box3[3], SPACE, Box4[4], Box5[5], ..., Box11[1]

        # Process characters one by one
        for i, char in enumerate(text):
            # Character index i (0-9) should go to box position (i+1)
            # But we need to account for the space separator
            box_idx = i + 1  # +1 to skip the first empty box

            # If this box position is at or after the space, adjust index
            if box_idx >= space_after_position:
                box_idx += 1  # Skip the space separator position

            if box_idx < len(box_positions):
                x_pos = box_positions[box_idx]
                positions.append((char, x_pos, start_y))

            # Add space separator after specified position
            if (i + 1) == space_after_position:
                # Add empty space box
                positions.append(('', box_positions[space_after_position], start_y))

    return positions


def fill_sequential_boxes(text, start_x, start_y, box_width=15, box_spacing=2,
                          boxes_per_row=20, row_height=20, max_rows=3, skip_boxes=[],
                          skip_box_widths=None, fill_right_to_left=False):
    """
    Fill boxes sequentially character by character, strictly according to available boxes
    No word-wrapping - characters fill left to right, top to bottom (or right to left if specified)
    Skipped boxes can have independent widths and don't affect other boxes' positions

    Args:
        text: String to fill in boxes
        start_x: Starting X coordinate
        start_y: Starting Y coordinate (top of first row)
        box_width: Width of each box (default width for non-skipped boxes)
        box_spacing: Spacing between boxes
        boxes_per_row: Number of boxes per row
        row_height: Height between rows
        max_rows: Maximum number of rows available
        skip_boxes: List of box positions to skip (1-indexed, e.g., [3, 7] to skip 3rd and 7th boxes)
        skip_box_widths: Dict mapping box position to custom width (e.g., {3: 10, 7: 8} for different widths)
                        If None, skipped boxes use the default box_width
        fill_right_to_left: If True, fill from right to left (prioritize last box)

    Returns:
        List of tuples (char, x_pos, y_pos)
    """
    positions = []
    total_boxes = boxes_per_row * max_rows

    # If skip_box_widths not provided, use default box_width for all boxes
    if skip_box_widths is None:
        skip_box_widths = {}

    if fill_right_to_left:
        # First, calculate the x position for each box (considering custom widths for skipped boxes)
        box_x_positions = []  # Will store x position for each box (1-indexed)
        current_x = start_x

        for row in range(max_rows):
            for col in range(boxes_per_row):
                box_position = row * boxes_per_row + col + 1  # 1-indexed position
                y_pos = start_y - (row * row_height)

                # Get the width for this box
                if box_position in skip_boxes:
                    # Use custom width if specified, otherwise use default box_width
                    current_box_width = skip_box_widths.get(box_position, box_width)
                else:
                    current_box_width = box_width

                box_x_positions.append((box_position, current_x, y_pos, box_position in skip_boxes))
                current_x += current_box_width + box_spacing

            # Reset x position for next row
            if row < max_rows - 1:
                current_x = start_x

        # Build list of available boxes (not skipped)
        available_boxes = [(pos, x, y) for pos, x, y, is_skipped in box_x_positions if not is_skipped]

        # Calculate how many boxes we need
        text_length = len(text)
        num_available = len(available_boxes)

        if text_length > num_available:
            print(f"Warning: Text '{text}' truncated. Only {num_available} boxes available.")
            text_length = num_available

        # Fill from the end (right to left)
        start_index = num_available - text_length
        for i, char in enumerate(text):
            box_idx = start_index + i
            if box_idx < len(available_boxes):
                _, x_pos, y_pos = available_boxes[box_idx]
                positions.append((char, x_pos, y_pos))
    else:
        # Left-to-right logic with custom skip box widths
        # First, calculate the x position for each box (considering custom widths for skipped boxes)
        box_x_positions = []  # Will store x position for each box (1-indexed)
        current_x = start_x

        for row in range(max_rows):
            for col in range(boxes_per_row):
                box_position = row * boxes_per_row + col + 1  # 1-indexed position
                y_pos = start_y - (row * row_height)

                # Get the width for this box
                if box_position in skip_boxes:
                    # Use custom width if specified, otherwise use default box_width
                    current_box_width = skip_box_widths.get(box_position, box_width)
                else:
                    current_box_width = box_width

                box_x_positions.append((box_position, current_x, y_pos, box_position in skip_boxes))
                current_x += current_box_width + box_spacing

            # Reset x position for next row
            if row < max_rows - 1:
                current_x = start_x

        # Fill boxes left to right, skipping the ones in skip_boxes
        char_index = 0
        for box_position, x_pos, y_pos, is_skipped in box_x_positions:
            if is_skipped:
                continue  # Skip this box

            if char_index >= len(text):
                break  # No more characters to place

            char = text[char_index]
            positions.append((char, x_pos, y_pos))
            char_index += 1

        if char_index < len(text):
            print(f"Warning: Text '{text}' truncated. Only {char_index}/{len(text)} characters fit in available boxes.")

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

        # Apply decimal amount formatting if specified
        if data.get('format_decimal', False):
            formatted = format_decimal_amount(text)
            # Remove the decimal point - we only need the digits
            # The last 2 digits will go to Box 8 and 9, integer part fills right-to-left
            text = formatted.replace('.', '')
            print(f"After removing decimal point: '{text}'")

        # Add leading space if single character and specified
        if data.get('add_leading_space_if_single', False):
            if len(text.strip()) == 1:
                text = ' ' + text.strip()
                print(f"Added leading space for single character: '{data['text']}' -> '{text}'")

        x = data['x']
        y = height - data['y']  # Convert from top-left to bottom-left origin
        font_size = data.get('size', 10)

        can.setFont("Helvetica", font_size)

        # Check if this is a conditional phone field (direction based on character check)
        if data.get('is_conditional_phone', False):
            positions = fill_conditional_phone_boxes(
                text, x, y,
                box_width=data.get('box_width', 15),
                box_spacing=data.get('box_spacing', 2),
                space_separator_width=data.get('phone_space_separator_width', 7),
                space_after_position=data.get('phone_space_position', 3),
                check_position=data.get('phone_check_position', 1),
                check_value=data.get('phone_check_value', '1')
            )
            for char, char_x, char_y in positions:
                if char:  # Only draw non-empty characters (skip separators)
                    can.drawString(char_x + 2, char_y - 3, char)  # Slight offset for centering
        # Check if this is a phone field with custom space separator width
        elif data.get('is_phone', False):
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
                max_rows=data.get('max_rows', 3),
                skip_boxes=data.get('skip_boxes', []),
                skip_box_widths=data.get('skip_box_widths', None),
                fill_right_to_left=data.get('fill_right_to_left', False)
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

    input_pdf = os.path.join(script_dir, "BORANG PEMBIAYAAN PERIBADI-1.pdf")
    output_pdf = os.path.join(script_dir, "BORANG PEMBIAYAAN PERIBADI-1 - Filled.pdf")

    # Field data with coordinates (measured from top-left in points)
    # You'll need to adjust these coordinates based on the actual PDF layout
    # Uncomment fields one by one to test and adjust coordinates
    field_data = {
        # TOP SECTION - FINANCING DETAILS

         "Jumlah Pembiayaan": {
             "text": "50000",
             "x": 180,
             "y": 75,
             "size": 9,
             "fill_sequential": True,
             "box_width": 12,
             "box_spacing": 0.4,
             "boxes_per_row": 7,
             "row_height": 15,
             "max_rows": 1,
             "skip_boxes": [4],  # Skip the 4th box
             "fill_right_to_left": True  # Fill from right to left
         },

         "Tempoh (bulan)": {
             "text": "60",
             "x": 180,
             "y": 92,
             "size": 9,
             "fill_sequential": True,
             "box_width": 12,
             "box_spacing": 0.4,
             "boxes_per_row": 3,
             "row_height": 15,
             "max_rows": 1,
             "fill_right_to_left": True  # Fill from right to left
         },

        "No. Anggota / Membership No.": {
            "text": "7712345",
            "x": 180,
            "y": 107,
            "size": 9,
            "fill_sequential": True,
            "box_width": 12,
            "box_spacing": 0.7,
            "boxes_per_row": 14,
            "row_height": 15,
            "max_rows": 1,
            "skip_boxes": [1, 2, 3, 7],  # Skip boxes 1, 2, 3, and 7
            "fill_right_to_left": True  # Fill from right to left
        },

         "Cara Bayaran Balik": {
             "text": "Lain-lain / Others",  # Options: "Biro", "Gajian / Salary", "Tunai / Cash", "Lain-lain / Others"
             "is_checkbox": True,
             "size": 10,
             "checkbox_options": {
                 "Biro": {"x": 384, "y": 78},
                 "Gajian / Salary": {"x": 410, "y": 78},
                 "Tunai / Cash": {"x": 469, "y": 78},
                 "Lain-lain / Others": {"x": 384, "y": 87}
             }
         },

         "Cara Bayaran Balik Lain-lain": {
             "text": "Jual rumah",
             "x": 442,
             "y": 82,
             "size": 5,
             "use_boxes": True,
             "box_width": 5,
             "box_spacing": 0.01,
             "boxes_per_row": 10,
             "row_height": 5,
             "max_rows": 3,
             "conditional_on": True,
             "conditional_field": "Cara Bayaran Balik",
             "conditional_value": "Lain-lain / Others"  # Must match exactly with parent field text
         },

         "Jenis Pembiayaan": {
             "text": "Lain-lain / Others",  # Options: "Persendirian Al-Amal", "Lestari", "Lain-lain / Others"
             "is_checkbox": True,
             "size": 10,
             "checkbox_options": {
                 "Persendirian Al-Amal": {"x": 384, "y": 96},
                 "Lestari": {"x": 469, "y": 96},
                 "Lain-lain / Others": {"x": 384, "y": 104}
             }
         },

         "Jenis Pembiayaan Lain-lain": {
             "text": "Along",
             "x": 442,
             "y": 100,
             "size": 5,
             "use_boxes": True,
             "box_width": 5,
             "box_spacing": 0.01,
             "boxes_per_row": 10,
             "row_height": 5,
             "max_rows": 3,
             "conditional_on": True,
             "conditional_field": "Jenis Pembiayaan",
             "conditional_value": "Lain-lain / Others"  # Must match exactly with parent field text
         },

        # SECTION D - MAKLUMAT PASANGAN (SPOUSE INFORMATION)

         "Nama Suami/Isteri": {
             "text": "Siti Nurhaliza binti Ahmad",
             "x": 32,
             "y": 144,
             "size": 9,
             "use_boxes": True,
             "box_width": 12,
             "box_spacing": 0.7,
             "boxes_per_row": 21,
             "row_height": 15,
             "max_rows": 3
         },

         "Tarikh Lahir Pasangan": {
             "text": "05-08-1985",
             "x": 117,
             "y": 189,
             "size": 9,
             "is_date": True,
             "box_width": 12,
             "box_spacing": 0.7,
             "separator_width": 6,
             "separator_char": "-"
         },

         "No. Kad Pengenalan Pasangan Baru": {
             "text": "850805106789",
             "x": 32,
             "y": 222,
             "size": 9,
             "format_ic": True,
             "ic_space_positions": [6, 8],
             "use_boxes": True,
             "box_width": 12,
             "box_spacing": 0.9,
             "boxes_per_row": 15,
             "row_height": 15,
             "max_rows": 1
         },

         "No. Kad Pengenalan Pasangan Lama": {
             "text": "A1234567",
             "x": 32,
             "y": 246,
             "size": 9,
             "use_boxes": True,
             "box_width": 12,
             "box_spacing": 0.9,
             "boxes_per_row": 8,
             "row_height": 15,
             "max_rows": 1
         },

        "No. Tel. Pasangan": {
            "text": "0345678901",  # Test with landline (2nd char = '3')
            # "text": "0145678901",  # Test with mobile (2nd char = '1')
            "x": 149,
            "y": 246,
            "size": 9,
            "is_conditional_phone": True,  # Use conditional phone filling
            "box_width": 12,
            "box_spacing": 0.4,
            "phone_space_separator_width": 7,
            "phone_space_position": 3,
            "phone_check_position": 1,  # Check 2nd character (0-indexed)
            "phone_check_value": "1"  # If 2nd char is '1', fill left-to-right; otherwise right-to-left
        },

         "Nama & Alamat Majikan Pasangan": {
             "text": "Hospital Kuala Lumpur\nJalan Pahang\nKuala Lumpur",
             "x": 32,
             "y": 269,
             "size": 9,
             "use_boxes": True,
             "box_width": 12,
             "box_spacing": 0.8,
             "boxes_per_row": 21,
             "row_height": 15,
             "max_rows": 3,
             "remove_commas": True,
             "respect_newlines": True
         },

         "Poskod Pasangan": {
             "text": "50400",
             "x": 32,
             "y": 322,
             "size": 9,
             "use_boxes": True,
             "box_width": 12,
             "box_spacing": 0.4,
             "boxes_per_row": 6,
             "row_height": 15,
             "max_rows": 1
         },

         "No. Tel. Pejabat Pasangan": {
             "text": "0323456789",
             "x": 148,
             "y": 323,
             "size": 9,
             "is_phone": True,
             "box_width": 12,
             "box_spacing": 0.5,
             "phone_space_separator_width": 7,
             "phone_space_position": 2,
             "phone_leading_space": True
         },

         "Bandar / Negeri Pasangan": {
             "text": "Kuala Lumpur",
             "x": 32,
             "y": 346,
             "size": 9,
             "use_boxes": True,
             "box_width": 12,
             "box_spacing": 0.8,
             "boxes_per_row": 21,
             "row_height": 15,
             "max_rows": 1
         },

        # SECTION E - PERUJUK (REFERENCE)

         "Nama Perujuk": {
             "text": "Ahmad Bin Ali",
             "x": 309,
             "y": 144,
             "size": 9,
             "use_boxes": True,
             "box_width": 12,
             "box_spacing": 0.7,
             "boxes_per_row": 21,
             "row_height": 15,
             "max_rows": 2
         },

         "Alamat Kediaman Perujuk": {
             "text": "No 10 Jalan Merdeka\nTaman Bahagia\nSelangor",
             "x": 309,
             "y": 180,
             "size": 9,
             "use_boxes": True,
             "box_width": 12,
             "box_spacing": 0.7,
             "boxes_per_row": 21,
             "row_height": 14,
             "max_rows": 3,
             "remove_commas": True,
             "respect_newlines": True
         },

         "Poskod Perujuk": {
             "text": "43000",
             "x": 310,
             "y": 230,
             "size": 9,
             "use_boxes": True,
             "box_width": 12,
             "box_spacing": 0.4,
             "boxes_per_row": 6,
             "row_height": 15,
             "max_rows": 1
         },

         "Bandar / Negeri Perujuk": {
             "text": "Kajang Selangor",
             "x": 385,
             "y": 230,
             "size": 9,
             "use_boxes": True,
             "box_width": 12,
             "box_spacing": 1,
             "boxes_per_row": 20,
             "row_height": 15,
             "max_rows": 1
         },

         "No. Kad Pengenalan Perujuk": {
             "text": "750612085678",
             "x": 310,
             "y": 253,
             "size": 9,
             "format_ic": True,
             "ic_space_positions": [6, 8],
             "use_boxes": True,
             "box_width": 12,
             "box_spacing": 0.7,
             "boxes_per_row": 15,
             "row_height": 15,
             "max_rows": 1
         },

         "Pekerjaan Perujuk": {
             "text": "Guru",
             "x": 309,
             "y": 274,
             "size": 9,
             "use_boxes": True,
             "box_width": 12,
             "box_spacing": 0.7,
             "boxes_per_row": 20,
             "row_height": 15,
             "max_rows": 1
         },

         "Hubungan Perujuk": {
             "text": "Abang",
             "x": 309,
             "y": 297,
             "size": 9,
             "use_boxes": True,
             "box_width": 12,
             "box_spacing": 0.7,
             "boxes_per_row": 20,
             "row_height": 15,
             "max_rows": 1
         },

        "No. Untuk Dihubungi Perujuk Tel Bimbit": {
            "text": "0123456789",  # Mobile (2nd char = '1')
            "x": 385,
            "y": 320,
            "size": 9,
            "is_conditional_phone": True,  # Use conditional phone filling
            "box_width": 12,
            "box_spacing": 0.5,
            "phone_space_separator_width": 7,
            "phone_space_position": 3,
            "phone_check_position": 1,  # Check 2nd character (0-indexed)
            "phone_check_value": "1"  # If 2nd char is '1', fill left-to-right; otherwise right-to-left
        },

        "No. Untuk Dihubungi Perujuk Rumah": {
            "text": "0387654321",  # Landline (2nd char = '3')
            "x": 385,
            "y": 333,
            "size": 9,
            "is_conditional_phone": True,  # Use conditional phone filling
            "box_width": 12,
            "box_spacing": 0.5,
            "phone_space_separator_width": 7,
            "phone_space_position": 3,
            "phone_check_position": 1,  # Check 2nd character (0-indexed)
            "phone_check_value": "1"  # If 2nd char is '1', fill left-to-right; otherwise right-to-left
        },

        "No. Untuk Dihubungi Perujuk Pejabat": {
            "text": "0398765432",  # Landline (2nd char = '3')
            "x": 385,
            "y": 347,
            "size": 9,
            "is_conditional_phone": True,  # Use conditional phone filling
            "box_width": 12,
            "box_spacing": 0.5,
            "phone_space_separator_width": 7,
            "phone_space_position": 3,
            "phone_check_position": 1,  # Check 2nd character (0-indexed)
            "phone_check_value": "1"  # If 2nd char is '1', fill left-to-right; otherwise right-to-left
        },

        # SECTION F - LATAR BELAKANG KEWANGAN (FINANCIAL BACKGROUND)

        # PENDAPATAN (A) / INCOME (A)

         "Gaji Bulanan Asas": {
             "text": "5000",
             "x": 46,
             "y": 405,
             "size": 9,
             "format_decimal": True,  # Apply decimal formatting
             "fill_sequential": True,
             "box_width": 12,
             "box_spacing": 0.3,
             "boxes_per_row": 9,  # 9 boxes total
             "row_height": 15,
             "max_rows": 1,
             "skip_boxes": [3, 7],  # Skip boxes 3 and 7
             "skip_box_widths": {3: 8, 7: 6},  # Box 3 has width 8, Box 7 has width 6
             "fill_right_to_left": True  # Fill from right to left
         },

        "Pendapatan Suami / Isteri": {
            "text": "1000",
            "x": 46,
            "y": 430,
            "size": 9,
            "format_decimal": True,  # Apply decimal formatting
            "fill_sequential": True,
            "box_width": 12,
            "box_spacing": 0.3,
            "boxes_per_row": 9,  # 9 boxes total
            "row_height": 15,
            "max_rows": 1,
            "skip_boxes": [3, 7],  # Skip boxes 3 and 7
            "skip_box_widths": {3: 8, 7: 6},  # Box 3 has width 8, Box 7 has width 6
            "fill_right_to_left": True  # Fill from right to left
        },

        "Lain-lain Pendapatan": {
            "text": "500",
            "x": 185,
            "y": 405,
            "size": 9,
            "format_decimal": True,  # Apply decimal formatting
            "fill_sequential": True,
            "box_width": 12,
            "box_spacing": 0.3,
            "boxes_per_row": 9,  # 9 boxes total
            "row_height": 15,
            "max_rows": 1,
            "skip_boxes": [3, 7],  # Skip boxes 3 and 7
            "skip_box_widths": {3: 8, 7: 6},  # Box 3 has width 8, Box 7 has width 6
            "fill_right_to_left": True  # Fill from right to left
        },

        "Jumlah Pendapatan": {
            "text": "10500",
            "x": 185,
            "y": 445,
            "size": 9,
            "format_decimal": True,  # Apply decimal formatting
            "fill_sequential": True,
            "box_width": 12,
            "box_spacing": 0.3,
            "boxes_per_row": 9,  # 9 boxes total
            "row_height": 15,
            "max_rows": 1,
            "skip_boxes": [3, 7],  # Skip boxes 3 and 7
            "skip_box_widths": {3: 8, 7: 6},  # Box 3 has width 8, Box 7 has width 6
            "fill_right_to_left": True  # Fill from right to left
        },

        # PERBELANJAAN (B) / EXPENSES (B)

         "Sara Hidup": {
             "text": "3000",
             "x": 337,
             "y": 396,
             "size": 9,
             "format_decimal": True,  # Apply decimal formatting
             "fill_sequential": True,
             "box_width": 12,
             "box_spacing": 0.3,
             "boxes_per_row": 9,  # 9 boxes total
             "row_height": 15,
             "max_rows": 1,
             "skip_boxes": [3, 7],  # Skip boxes 3 and 7
             "skip_box_widths": {3: 8, 7: 6},  # Box 3 has width 8, Box 7 has width 6
             "fill_right_to_left": True  # Fill from right to left
         },

         "Lain-lain Perbelanjaan": {
             "text": "500",
             "x": 337,
             "y": 425,
             "size": 9,
             "format_decimal": True,  # Apply decimal formatting
             "fill_sequential": True,
             "box_width": 12,
             "box_spacing": 0.3,
             "boxes_per_row": 9,  # 9 boxes total
             "row_height": 15,
             "max_rows": 1,
             "skip_boxes": [3, 7],  # Skip boxes 3 and 7
             "skip_box_widths": {3: 8, 7: 6},  # Box 3 has width 8, Box 7 has width 6
             "fill_right_to_left": True  # Fill from right to left
         },

         "Jumlah Perbelanjaan": {
             "text": "3500",
             "x": 439,
             "y": 445,
             "size": 9,
             "format_decimal": True,  # Apply decimal formatting
             "fill_sequential": True,
             "box_width": 12,
             "box_spacing": 0.3,
             "boxes_per_row": 9,  # 9 boxes total
             "row_height": 15,
             "max_rows": 1,
             "skip_boxes": [3, 7],  # Skip boxes 3 and 7
             "skip_box_widths": {3: 8, 7: 6},  # Box 3 has width 8, Box 7 has width 6
             "fill_right_to_left": True  # Fill from right to left
         },

         "Jumlah Ansuran Bulanan": {
             "text": "2000",
             "x": 465,
             "y": 398,
             "size": 9,
             "format_decimal": True,  # Apply decimal formatting
             "fill_sequential": True,
             "box_width": 12,
             "box_spacing": 0.3,
             "boxes_per_row": 9,  # 9 boxes total
             "row_height": 15,
             "max_rows": 1,
             "skip_boxes": [3, 7],  # Skip boxes 3 and 7
             "skip_box_widths": {3: 8, 7: 6},  # Box 3 has width 8, Box 7 has width 6
             "fill_right_to_left": True  # Fill from right to left
         },

         "Sewa Rumah": {
             "text": "1200",
             "x": 465,
             "y": 422,
             "size": 9,
             "format_decimal": True,  # Apply decimal formatting
             "fill_sequential": True,
             "box_width": 12,
             "box_spacing": 0.3,
             "boxes_per_row": 9,  # 9 boxes total
             "row_height": 15,
             "max_rows": 1,
             "skip_boxes": [3, 7],  # Skip boxes 3 and 7
             "skip_box_widths": {3: 8, 7: 6},  # Box 3 has width 8, Box 7 has width 6
             "fill_right_to_left": True  # Fill from right to left
         },

         "Pendapatan Bersih": {
             "text": "7000",
             "x": 320,
             "y": 462,
             "size": 9,
             "format_decimal": True,  # Apply decimal formatting
             "fill_sequential": True,
             "box_width": 12,
             "box_spacing": 0.3,
             "boxes_per_row": 9,  # 9 boxes total
             "row_height": 15,
             "max_rows": 1,
             "skip_boxes": [3, 7],  # Skip boxes 3 and 7
             "skip_box_widths": {3: 8, 7: 6},  # Box 3 has width 8, Box 7 has width 6
             "fill_right_to_left": True  # Fill from right to left
         },

        # BANK/FINANCING TABLE (Multiple rows possible - showing 1 example)

         "Bank 1 Nama": {
             "text": "Bank Rakyat",
             "x": 30,
             "y": 500,
             "size": 8,
             "use_boxes": False  # Free text in table cell
         },

         "Bank 1 Jenis Pembiayaan": {
             "text": "Personal Loan",
             "x": 150,
             "y": 500,
             "size": 8,
             "use_boxes": False
         },

         "Bank 1 No Akaun": {
             "text": "123456789012",
             "x": 270,
             "y": 500,
             "size": 8,
             "use_boxes": False
         },

         "Bank 1 Bayaran Bulanan": {
             "text": "500",
             "x": 400,
             "y": 500,
             "size": 8,
             "use_boxes": False
         },

         "Bank 1 Baki": {
             "text": "15000",
             "x": 500,
             "y": 500,
             "size": 8,
             "use_boxes": False
         },

         "Bank 2 Nama": {
             "text": "Bank Rakyat",
             "x": 30,
             "y": 510,
             "size": 8,
             "use_boxes": False  # Free text in table cell
         },

         "Bank 2 Jenis Pembiayaan": {
             "text": "Personal Loan",
             "x": 150,
             "y": 510,
             "size": 8,
             "use_boxes": False
         },

         "Bank 2 No Akaun": {
             "text": "123456789012",
             "x": 270,
             "y": 510,
             "size": 8,
             "use_boxes": False
         },

         "Bank 2 Bayaran Bulanan": {
             "text": "500",
             "x": 400,
             "y": 510,
             "size": 8,
             "use_boxes": False
         },

         "Bank 2 Baki": {
             "text": "15000",
             "x": 500,
             "y": 510,
             "size": 8,
             "use_boxes": False
         },

         "Bank 3 Nama": {
             "text": "Bank Rakyat",
             "x": 30,
             "y": 520,
             "size": 8,
             "use_boxes": False  # Free text in table cell
         },

         "Bank 3 Jenis Pembiayaan": {
             "text": "Personal Loan",
             "x": 150,
             "y": 520,
             "size": 8,
             "use_boxes": False
         },

         "Bank 3 No Akaun": {
             "text": "123456789012",
             "x": 270,
             "y": 520,
             "size": 8,
             "use_boxes": False
         },

         "Bank 3 Bayaran Bulanan": {
             "text": "500",
             "x": 400,
             "y": 520,
             "size": 8,
             "use_boxes": False
         },

         "Bank 3 Baki": {
             "text": "15000",
             "x": 500,
             "y": 520,
             "size": 8,
             "use_boxes": False
         },
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
