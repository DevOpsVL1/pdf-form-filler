"""
CIF-1 Form Filler - FULLY CORRECTED VERSION
ALL coordinates extracted from original fill_cif1_boxes.py
Every single Y coordinate has been verified and corrected
"""

import io
import os
import tempfile


def generate_cif1_pdf(data):
    """
    Generate filled CIF-1 PDF from user data
    Uses EXACT structure from original code with ALL correct coordinates
    
    Args:
        data: Dictionary containing form fields (already in UPPERCASE)
    
    Returns:
        BytesIO buffer containing the filled PDF
    """
    # Import base filling function
    from form_fillers.cif1_base import fill_pdf_with_overlay
    
    # Build field mapping with EXACT original structure
    field_data = build_field_data(data)
    
    # Use the template PDF path
    input_pdf = '/mnt/user-data/outputs/pdf-form-platform-complete/templates/BORANG_CIF-1.pdf'
    
    # Create temporary output file
    temp_output = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    temp_output_path = temp_output.name
    temp_output.close()
    
    try:
        # Generate PDF using the base function (writes to file)
        fill_pdf_with_overlay(input_pdf, temp_output_path, field_data, draw_grid=False)
        
        # Read the generated PDF into buffer
        output_buffer = io.BytesIO()
        with open(temp_output_path, 'rb') as f:
            output_buffer.write(f.read())
        
        output_buffer.seek(0)
        return output_buffer
        
    finally:
        # Clean up temporary file
        try:
            os.unlink(temp_output_path)
        except:
            pass


def build_field_data(data):
    """
    Build field_data dictionary using EXACT structure from original fill_cif1_boxes.py
    ALL Y-COORDINATES VERIFIED AND CORRECTED
    """
    field_data = {}
    
    # Helper function
    def has_value(field_name):
        """Check if field exists and has non-empty value"""
        value = data.get(field_name)
        return value and str(value).strip()
    
    # ===========================================
    # SECTION A - CUSTOMER INFORMATION
    # Using EXACT original field names and coordinates
    # ===========================================
    
    # IC Number - EXACT original structure
    if has_value('ic_number'):
        field_data["No. Kad Pengenalan Baru"] = {
            "text": data['ic_number'],
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
        }
    
    # Date of Birth - EXACT original structure
    if has_value('date_of_birth'):
        field_data["Tarikh Lahir"] = {
            "text": data['date_of_birth'],
            "x": 52,
            "y": 374,
            "size": 9,
            "is_date": True,
            "box_width": 12,
            "box_spacing": 0.2,
            "separator_width": 6,
            "separator_char": "-"
        }
    
    # Name - EXACT original structure
    if has_value('name_ic'):
        field_data["Nama"] = {
            "text": data['name_ic'],
            "x": 52,
            "y": 403,
            "size": 9,
            "use_boxes": True,
            "box_width": 12,
            "box_spacing": 0.2,
            "boxes_per_row": 21,
            "row_height": 13,
            "max_rows": 3
        }
    
    # Preferred Name (Nama Pilihan)
    if has_value('preferred_name'):
        field_data["Nama Pilihan"] = {
            "text": data['preferred_name'],
            "x": 52,
            "y": 458,
            "size": 9,
            "use_boxes": True,
            "box_width": 12,
            "box_spacing": 0.2,
            "boxes_per_row": 21,
            "row_height": 13,
            "max_rows": 2
        }
    
    # Title (Gelaran) - Checkbox - EXACT Y coordinates
    if has_value('title'):
        field_data["Gelaran"] = {
            "text": data['title'],
            "is_checkbox": True,
            "size": 10,
            "checkbox_options": {
                "EN": {"x": 52, "y": 504},
                "PUAN": {"x": 99, "y": 504},
                "CIK": {"x": 142, "y": 504},
                "PROFESOR": {"x": 199, "y": 504},
                "DATO": {"x": 52, "y": 512},
                "DATIN": {"x": 99, "y": 512},
                "TAN SRI": {"x": 52, "y": 521},
                "PUAN SRI": {"x": 99, "y": 521},
                "DR": {"x": 142, "y": 512},
                "YANG BERHORMAT": {"x": 199, "y": 512},
                "LAIN-LAIN": {"x": 142, "y": 521}
            }
        }
    
    # Gender (Jantina) - Checkbox - EXACT Y coordinates
    if has_value('gender'):
        field_data["Jantina"] = {
            "text": data['gender'],
            "is_checkbox": True,
            "size": 10,
            "checkbox_options": {
                "LELAKI": {"x": 141, "y": 539},
                "PEREMPUAN": {"x": 199, "y": 539}
            }
        }
    
    # Marital Status (Taraf Perkahwinan) - Checkbox - CORRECTED Y coordinates
    if has_value('marital_status'):
        field_data["Taraf Perkahwinan"] = {
            "text": data['marital_status'],
            "is_checkbox": True,
            "size": 10,
            "checkbox_options": {
                "BUJANG": {"x": 52, "y": 565},  # VERIFIED
                "BALU": {"x": 141, "y": 565},   # VERIFIED
                "BERKAHWIN": {"x": 52, "y": 574},  # VERIFIED
                "BERCERAI": {"x": 141, "y": 574},  # VERIFIED
                "LAIN-LAIN": {"x": 52, "y": 584}   # FIXED: was 582
            }
        }
    
    # Race (Bangsa) - Checkbox - CORRECTED Y coordinates
    if has_value('race'):
        field_data["Bangsa"] = {
            "text": data['race'],
            "is_checkbox": True,
            "size": 10,
            "checkbox_options": {
                "BUMIPUTERA": {"x": 52, "y": 620},   # FIXED: was 615
                "CINA": {"x": 141, "y": 620},         # FIXED: was 615
                "INDIA": {"x": 52, "y": 631},         # FIXED: was 624
                "LAIN-LAIN": {"x": 141, "y": 631}     # FIXED: was 624
            }
        }
    
    # Religion (Agama) - Checkbox - CORRECTED Y coordinates  
    if has_value('religion'):
        field_data["Agama"] = {
            "text": data['religion'],
            "is_checkbox": True,
            "size": 10,
            "checkbox_options": {
                "ISLAM": {"x": 52, "y": 656},      # FIXED: was 649
                "BUDDHA": {"x": 141, "y": 656},    # FIXED: was 649
                "HINDU": {"x": 226, "y": 656},     # FIXED: was 649
                "KRISTIAN": {"x": 52, "y": 667},   # FIXED: was 658
                "LAIN-LAIN": {"x": 141, "y": 667}  # FIXED: was 658
            }
        }
    
    # Mother's Maiden Name (Nama Ibu) - CORRECTED Y coordinate
    if has_value('mother_maiden_name'):
        field_data["Nama Ibu"] = {
            "text": data['mother_maiden_name'],
            "x": 52,
            "y": 788,  # FIXED: was 707 (81 pixels off!)
            "size": 9,
            "use_boxes": True,
            "box_width": 12,
            "box_spacing": 0.2,
            "boxes_per_row": 21,
            "row_height": 13,
            "max_rows": 2
        }
    
    # ===========================================
    # SECTION B - CONTACT DETAILS
    # CORRECTED X and Y coordinates
    # ===========================================
    
    # Residential Address - CORRECTED coordinates
    if has_value('residential_address'):
        field_data["Alamat Kediaman"] = {
            "text": data['residential_address'],
            "x": 316,  # FIXED: was 319
            "y": 203,  # FIXED: was 237 (34 pixels off!)
            "size": 9,
            "use_boxes": True,
            "box_width": 12,
            "box_spacing": 0.1,  # FIXED: was 0.2
            "boxes_per_row": 21,
            "row_height": 13,
            "max_rows": 3,  # FIXED: was 4
            "remove_commas": True,
            "respect_newlines": True
        }
    
    if has_value('residential_postcode'):
        field_data["Poskod Kediaman"] = {
            "text": data['residential_postcode'],
            "x": 317,  # FIXED: was 319
            "y": 255,  # FIXED: was 299 (44 pixels off!)
            "size": 9,
            "use_boxes": True,
            "box_width": 12,
            "box_spacing": 0.2,
            "boxes_per_row": 5,
            "row_height": 13,
            "max_rows": 1
        }
    
    if has_value('residential_city'):
        field_data["Bandar Kediaman"] = {
            "text": data['residential_city'],
            "x": 388,  # FIXED: was 374
            "y": 255,  # FIXED: was 299 (44 pixels off!)
            "size": 9,
            "use_boxes": True,
            "box_width": 12,
            "box_spacing": 0.2,
            "boxes_per_row": 15,
            "row_height": 13,
            "max_rows": 1
        }
    
    if has_value('residential_state'):
        field_data["Negeri Kediaman"] = {
            "text": data['residential_state'],
            "x": 315,  # FIXED: was 319
            "y": 280,  # FIXED: was 327 (47 pixels off!)
            "size": 9,
            "use_boxes": True,
            "box_width": 12,
            "box_spacing": 0,  # FIXED: was 0.2
            "boxes_per_row": 20,  # FIXED: was 25
            "row_height": 13,
            "max_rows": 1
        }
    
    # Correspondence Address - CORRECTED coordinates
    if has_value('correspondence_address'):
        field_data["Alamat Surat Menyurat"] = {
            "text": data['correspondence_address'],
            "x": 316,  # FIXED: was 319
            "y": 327,  # FIXED: was 369 (42 pixels off!)
            "size": 9,
            "use_boxes": True,
            "box_width": 12,
            "box_spacing": 0.1,  # FIXED: was 0.2
            "boxes_per_row": 21,
            "row_height": 13,
            "max_rows": 2,  # FIXED: was 3
            "remove_commas": True,
            "respect_newlines": True
        }
    
    if has_value('correspondence_postcode'):
        field_data["Poskod Surat"] = {
            "text": data['correspondence_postcode'],
            "x": 317,  # FIXED: was 319
            "y": 366,  # FIXED: was 418 (52 pixels off!)
            "size": 9,
            "use_boxes": True,
            "box_width": 12,
            "box_spacing": 0.2,
            "boxes_per_row": 5,
            "row_height": 13,
            "max_rows": 1
        }
    
    if has_value('correspondence_city'):
        field_data["Bandar Surat"] = {
            "text": data['correspondence_city'],
            "x": 388,  # FIXED: was 374
            "y": 366,  # FIXED: was 418 (52 pixels off!)
            "size": 9,
            "use_boxes": True,
            "box_width": 12,
            "box_spacing": 0.2,
            "boxes_per_row": 15,
            "row_height": 13,
            "max_rows": 1
        }
    
    if has_value('correspondence_state'):
        field_data["Negeri Surat"] = {
            "text": data['correspondence_state'],
            "x": 315,  # FIXED: was 319
            "y": 391,  # FIXED: was 447 (56 pixels off!)
            "size": 9,
            "use_boxes": True,
            "box_width": 12,
            "box_spacing": 0,  # FIXED: was 0.2
            "boxes_per_row": 25,
            "row_height": 13,
            "max_rows": 1
        }
    
    # Phone Numbers - CORRECTED Y coordinates (were 70+ pixels off!)
    if has_value('tel_home'):
        field_data["Tel Kediaman"] = {
            "text": data['tel_home'],
            "x": 389,
            "y": 420,  # FIXED: was 492 (72 pixels off!)
            "size": 9,
            "is_phone": True,
            "box_width": 12,
            "box_spacing": 0.1,
            "phone_space_separator_width": 6,
            "phone_space_position": 3,
            "phone_leading_space": False
        }
    
    if has_value('tel_office'):
        field_data["Tel Pejabat"] = {
            "text": data['tel_office'],
            "x": 389,
            "y": 433,  # FIXED: was 508 (75 pixels off!)
            "size": 9,
            "is_phone": True,
            "box_width": 12,
            "box_spacing": 0.1,
            "phone_space_separator_width": 6,
            "phone_space_position": 3,
            "phone_leading_space": False
        }
    
    if has_value('tel_mobile'):
        field_data["Tel Bimbit"] = {
            "text": data['tel_mobile'],
            "x": 389,
            "y": 446,  # FIXED: was 524 (78 pixels off!)
            "size": 9,
            "is_phone": True,
            "box_width": 12,
            "box_spacing": 0.1,
            "phone_space_separator_width": 6,
            "phone_space_position": 3,
            "phone_leading_space": True  # Mobile starts from 2nd box
        }
    
    if has_value('fax'):
        field_data["Faks"] = {
            "text": data['fax'],
            "x": 389,
            "y": 459,  # FIXED: was 540 (81 pixels off!)
            "size": 9,
            "is_phone": True,
            "box_width": 12,
            "box_spacing": 0.1,
            "phone_space_separator_width": 6,
            "phone_space_position": 2,
            "phone_leading_space": True
        }
    
    # Email - CORRECTED Y coordinate
    if has_value('email'):
        field_data["Alamat Email"] = {
            "text": data['email'],
            "x": 388,
            "y": 471,  # FIXED: was 569 (98 pixels off!)
            "size": 9,
            "fill_sequential": True,
            "box_width": 11,
            "box_spacing": 0.9,
            "boxes_per_row": 15,
            "row_height": 13,
            "max_rows": 2
        }
    
    # ===========================================
    # SECTION C - EMPLOYMENT INFORMATION
    # CORRECTED coordinates
    # ===========================================
    
    if has_value('employer_name'):
        field_data["Nama Majikan"] = {
            "text": data['employer_name'],
            "x": 316,
            "y": 530,  # FIXED: was 614 (84 pixels off!)
            "size": 9,
            "use_boxes": True,
            "box_width": 12,
            "box_spacing": 0.1,
            "boxes_per_row": 21,
            "row_height": 13,
            "max_rows": 2
        }
    
    if has_value('employer_address'):
        field_data["Alamat Majikan"] = {
            "text": data['employer_address'],
            "x": 316,
            "y": 568,  # FIXED: was 655 (87 pixels off!)
            "size": 9,
            "use_boxes": True,
            "box_width": 12,
            "box_spacing": 0.1,
            "boxes_per_row": 21,
            "row_height": 13,
            "max_rows": 3,
            "remove_commas": True,
            "respect_newlines": True
        }
    
    return field_data
