"""
Personal Financing Form Filler - User Data Integration
Wraps the base Pembiayaan filling logic to accept user input from web form
"""

import io
import os
import tempfile


def generate_pembiayaan_pdf(data):
    """
    Generate filled Personal Financing PDF from user data
    
    Args:
        data: Dictionary containing form fields (already in UPPERCASE)
    
    Returns:
        BytesIO buffer containing the filled PDF
    """
    # Import base filling function
    from form_fillers.pembiayaan_base import fill_pdf_with_overlay
    
    # Build field mapping from user data
    field_data = build_field_mapping(data)
    
    # Use relative path that works on any OS
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)  # Go up one level from form_fillers/
    input_pdf = os.path.join(project_root, 'templates', 'BORANG_PEMBIAYAAN_PERIBADI.pdf')
    
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


def build_field_mapping(data):
    """
    Build field mapping dictionary from user input data
    
    Args:
        data: Dictionary from web form (all values in UPPERCASE)
    
    Returns:
        Dictionary matching the format expected by fill_pdf_with_overlay
    """
    field_mapping = {}
    
    # Helper function to check if field has actual value
    def has_value(field_name):
        """Check if field exists and has non-empty value"""
        value = data.get(field_name)
        return value and str(value).strip()  # Not None, not empty, not just whitespace
    
    # ===========================================
    # TOP SECTION - FINANCING DETAILS
    # ===========================================
    
    # Financing Amount (Jumlah Pembiayaan)
    if has_value('financing_amount'):
        field_mapping["Jumlah Pembiayaan"] = {
            "text": data['financing_amount'],
            "x": 180,
            "y": 75,
            "size": 9,
            "fill_sequential": True,
            "box_width": 12,
            "box_spacing": 0.4,
            "boxes_per_row": 7,
            "row_height": 15,
            "max_rows": 1,
            "skip_boxes": [4],
            "fill_right_to_left": True
        }
    
    # Tenure in months (Tempoh)
    if has_value('financing_tenure'):
        field_mapping["Tempoh (bulan)"] = {
            "text": data['financing_tenure'],
            "x": 180,
            "y": 92,
            "size": 9,
            "fill_sequential": True,
            "box_width": 12,
            "box_spacing": 0.4,
            "boxes_per_row": 3,
            "row_height": 15,
            "max_rows": 1,
            "fill_right_to_left": True
        }
    
    # Membership Number (No. Anggota)
    if has_value('membership_number'):
        field_mapping["No. Anggota / Membership No."] = {
            "text": data['membership_number'],
            "x": 180,
            "y": 107,
            "size": 9,
            "fill_sequential": True,
            "box_width": 12,
            "box_spacing": 0.7,
            "boxes_per_row": 14,
            "row_height": 15,
            "max_rows": 1,
            "skip_boxes": [1, 2, 3, 7],
            "fill_right_to_left": True
        }
    
    # Repayment Method (Cara Bayaran Balik)
    if has_value('repayment_method'):
        field_mapping["Cara Bayaran Balik"] = {
            "text": data['repayment_method'],
            "is_checkbox": True,
            "size": 10,
            "checkbox_options": {
                "BIRO": {"x": 384, "y": 78},
                "GAJIAN / SALARY": {"x": 410, "y": 78},
                "TUNAI / CASH": {"x": 469, "y": 78},
                "LAIN-LAIN / OTHERS": {"x": 384, "y": 87}
            }
        }
    
    # Repayment Method - Others
    if has_value('repayment_method_other'):
        field_mapping["Cara Bayaran Balik Lain-lain"] = {
            "text": data['repayment_method_other'],
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
            "conditional_value": "LAIN-LAIN / OTHERS"
        }
    
    # Financing Type (Jenis Pembiayaan)
    if has_value('financing_type'):
        field_mapping["Jenis Pembiayaan"] = {
            "text": data['financing_type'],
            "is_checkbox": True,
            "size": 10,
            "checkbox_options": {
                "PERSENDIRIAN AL-AMAL": {"x": 384, "y": 96},
                "LESTARI": {"x": 469, "y": 96},
                "LAIN-LAIN / OTHERS": {"x": 384, "y": 104}
            }
        }
    
    # Financing Type - Others
    if has_value('financing_type_other'):
        field_mapping["Jenis Pembiayaan Lain-lain"] = {
            "text": data['financing_type_other'],
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
            "conditional_value": "LAIN-LAIN / OTHERS"
        }
    
    # ===========================================
    # SECTION D - SPOUSE INFORMATION
    # ===========================================
    
    # Spouse Name (Nama Suami/Isteri)
    if has_value('spouse_name'):
        field_mapping["Nama Suami/Isteri"] = {
            "text": data['spouse_name'],
            "x": 32,
            "y": 144,
            "size": 9,
            "use_boxes": True,
            "box_width": 12,
            "box_spacing": 0.7,
            "boxes_per_row": 21,
            "row_height": 15,
            "max_rows": 3
        }
    
    # Spouse Date of Birth (Tarikh Lahir Pasangan)
    if has_value('spouse_dob'):
        field_mapping["Tarikh Lahir Pasangan"] = {
            "text": data['spouse_dob'],
            "x": 117,
            "y": 189,
            "size": 9,
            "is_date": True,
            "box_width": 12,
            "box_spacing": 0.7,
            "separator_width": 6,
            "separator_char": "-"
        }
    
    # Spouse IC Number - New (No. Kad Pengenalan Pasangan Baru)
    if has_value('spouse_ic_new'):
        field_mapping["No. Kad Pengenalan Pasangan Baru"] = {
            "text": data['spouse_ic_new'],
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
        }
    
    # Spouse IC Number - Old (No. Kad Pengenalan Pasangan Lama)
    if has_value('spouse_ic_old'):
        field_mapping["No. Kad Pengenalan Pasangan Lama"] = {
            "text": data['spouse_ic_old'],
            "x": 32,
            "y": 246,
            "size": 9,
            "use_boxes": True,
            "box_width": 12,
            "box_spacing": 0.9,
            "boxes_per_row": 8,
            "row_height": 15,
            "max_rows": 1
        }
    
    # Spouse Phone (No. Tel. Pasangan)
    if has_value('spouse_phone'):
        field_mapping["No. Tel. Pasangan"] = {
            "text": data['spouse_phone'],
            "x": 149,
            "y": 246,
            "size": 9,
            "is_conditional_phone": True,
            "box_width": 12,
            "box_spacing": 0.4,
            "phone_space_separator_width": 7,
            "phone_space_position": 3,
            "phone_check_position": 1,
            "phone_check_value": "1"
        }
    
    # Spouse Employer Name & Address (Nama & Alamat Majikan Pasangan)
    if has_value('spouse_employer_name_address'):
        field_mapping["Nama & Alamat Majikan Pasangan"] = {
            "text": data['spouse_employer_name_address'],
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
        }
    
    # Spouse Employer Postcode (Poskod Pasangan)
    if has_value('spouse_employer_postcode'):
        field_mapping["Poskod Pasangan"] = {
            "text": data['spouse_employer_postcode'],
            "x": 32,
            "y": 322,
            "size": 9,
            "use_boxes": True,
            "box_width": 12,
            "box_spacing": 0.4,
            "boxes_per_row": 6,
            "row_height": 15,
            "max_rows": 1
        }
    
    # Spouse Employer Office Phone (No. Tel. Pejabat Pasangan)
    if has_value('spouse_employer_office_phone'):
        field_mapping["No. Tel. Pejabat Pasangan"] = {
            "text": data['spouse_employer_office_phone'],
            "x": 148,
            "y": 323,
            "size": 9,
            "is_phone": True,
            "box_width": 12,
            "box_spacing": 0.5,
            "phone_space_separator_width": 7,
            "phone_space_position": 2,
            "phone_leading_space": True
        }
    
    # Spouse Employer City/State (Bandar / Negeri Pasangan)
    if has_value('spouse_employer_city_state'):
        field_mapping["Bandar / Negeri Pasangan"] = {
            "text": data['spouse_employer_city_state'],
            "x": 32,
            "y": 346,
            "size": 9,
            "use_boxes": True,
            "box_width": 12,
            "box_spacing": 0.8,
            "boxes_per_row": 21,
            "row_height": 15,
            "max_rows": 1
        }
    
    # ===========================================
    # SECTION E - REFERENCE INFORMATION
    # ===========================================
    
    # Reference Name (Nama Perujuk)
    if has_value('reference_name'):
        field_mapping["Nama Perujuk"] = {
            "text": data['reference_name'],
            "x": 309,
            "y": 144,
            "size": 9,
            "use_boxes": True,
            "box_width": 12,
            "box_spacing": 0.7,
            "boxes_per_row": 21,
            "row_height": 15,
            "max_rows": 2
        }
    
    # Reference Address (Alamat Kediaman Perujuk)
    if has_value('reference_address'):
        field_mapping["Alamat Kediaman Perujuk"] = {
            "text": data['reference_address'],
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
        }
    
    # Reference Postcode (Poskod Perujuk)
    if has_value('reference_postcode'):
        field_mapping["Poskod Perujuk"] = {
            "text": data['reference_postcode'],
            "x": 310,
            "y": 230,
            "size": 9,
            "use_boxes": True,
            "box_width": 12,
            "box_spacing": 0.4,
            "boxes_per_row": 6,
            "row_height": 15,
            "max_rows": 1
        }
    
    # Reference City/State (Bandar / Negeri Perujuk)
    if has_value('reference_city_state'):
        field_mapping["Bandar / Negeri Perujuk"] = {
            "text": data['reference_city_state'],
            "x": 385,
            "y": 230,
            "size": 9,
            "use_boxes": True,
            "box_width": 12,
            "box_spacing": 1,
            "boxes_per_row": 20,
            "row_height": 15,
            "max_rows": 1
        }
    
    # Reference IC Number (No. Kad Pengenalan Perujuk)
    if has_value('reference_ic'):
        field_mapping["No. Kad Pengenalan Perujuk"] = {
            "text": data['reference_ic'],
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
        }
    
    # Reference Occupation (Pekerjaan Perujuk)
    if has_value('reference_occupation'):
        field_mapping["Pekerjaan Perujuk"] = {
            "text": data['reference_occupation'],
            "x": 309,
            "y": 274,
            "size": 9,
            "use_boxes": True,
            "box_width": 12,
            "box_spacing": 0.7,
            "boxes_per_row": 20,
            "row_height": 15,
            "max_rows": 1
        }
    
    # Reference Relationship (Hubungan Perujuk)
    if has_value('reference_relationship'):
        field_mapping["Hubungan Perujuk"] = {
            "text": data['reference_relationship'],
            "x": 309,
            "y": 297,
            "size": 9,
            "use_boxes": True,
            "box_width": 12,
            "box_spacing": 0.7,
            "boxes_per_row": 20,
            "row_height": 15,
            "max_rows": 1
        }
    
    # Reference Mobile Phone (No. Untuk Dihubungi Perujuk Tel Bimbit)
    if has_value('reference_mobile'):
        field_mapping["No. Untuk Dihubungi Perujuk Tel Bimbit"] = {
            "text": data['reference_mobile'],
            "x": 385,
            "y": 320,
            "size": 9,
            "is_conditional_phone": True,
            "box_width": 12,
            "box_spacing": 0.5,
            "phone_space_separator_width": 7,
            "phone_space_position": 3,
            "phone_check_position": 1,
            "phone_check_value": "1"
        }
    
    # Reference Home Phone (No. Untuk Dihubungi Perujuk Rumah)
    if has_value('reference_home'):
        field_mapping["No. Untuk Dihubungi Perujuk Rumah"] = {
            "text": data['reference_home'],
            "x": 385,
            "y": 333,
            "size": 9,
            "is_conditional_phone": True,
            "box_width": 12,
            "box_spacing": 0.5,
            "phone_space_separator_width": 7,
            "phone_space_position": 3,
            "phone_check_position": 1,
            "phone_check_value": "1"
        }
    
    # Reference Office Phone (No. Untuk Dihubungi Perujuk Pejabat)
    if has_value('reference_office'):
        field_mapping["No. Untuk Dihubungi Perujuk Pejabat"] = {
            "text": data['reference_office'],
            "x": 385,
            "y": 347,
            "size": 9,
            "is_conditional_phone": True,
            "box_width": 12,
            "box_spacing": 0.5,
            "phone_space_separator_width": 7,
            "phone_space_position": 3,
            "phone_check_position": 1,
            "phone_check_value": "1"
        }
    
    # ===========================================
    # SECTION F - FINANCIAL BACKGROUND
    # ===========================================
    
    # Monthly Salary (Gaji Bulanan Asas)
    if has_value('monthly_salary'):
        field_mapping["Gaji Bulanan Asas"] = {
            "text": data['monthly_salary'],
            "x": 46,
            "y": 405,
            "size": 9,
            "format_decimal": True,
            "fill_sequential": True,
            "box_width": 12,
            "box_spacing": 0.3,
            "boxes_per_row": 9,
            "row_height": 15,
            "max_rows": 1,
            "skip_boxes": [3, 7],
            "skip_box_widths": {3: 8, 7: 6},
            "fill_right_to_left": True
        }
    
    # Spouse Income (Pendapatan Suami / Isteri)
    if has_value('spouse_income'):
        field_mapping["Pendapatan Suami / Isteri"] = {
            "text": data['spouse_income'],
            "x": 46,
            "y": 430,
            "size": 9,
            "format_decimal": True,
            "fill_sequential": True,
            "box_width": 12,
            "box_spacing": 0.3,
            "boxes_per_row": 9,
            "row_height": 15,
            "max_rows": 1,
            "skip_boxes": [3, 7],
            "skip_box_widths": {3: 8, 7: 6},
            "fill_right_to_left": True
        }
    
    # Other Income (Lain-lain Pendapatan)
    if has_value('other_income'):
        field_mapping["Lain-lain Pendapatan"] = {
            "text": data['other_income'],
            "x": 185,
            "y": 405,
            "size": 9,
            "format_decimal": True,
            "fill_sequential": True,
            "box_width": 12,
            "box_spacing": 0.3,
            "boxes_per_row": 9,
            "row_height": 15,
            "max_rows": 1,
            "skip_boxes": [3, 7],
            "skip_box_widths": {3: 8, 7: 6},
            "fill_right_to_left": True
        }
    
    # Total Income (Jumlah Pendapatan)
    if has_value('total_income'):
        field_mapping["Jumlah Pendapatan"] = {
            "text": data['total_income'],
            "x": 185,
            "y": 445,
            "size": 9,
            "format_decimal": True,
            "fill_sequential": True,
            "box_width": 12,
            "box_spacing": 0.3,
            "boxes_per_row": 9,
            "row_height": 15,
            "max_rows": 1,
            "skip_boxes": [3, 7],
            "skip_box_widths": {3: 8, 7: 6},
            "fill_right_to_left": True
        }
    
    # Cost of Living (Sara Hidup)
    if has_value('cost_of_living'):
        field_mapping["Sara Hidup"] = {
            "text": data['cost_of_living'],
            "x": 337,
            "y": 396,
            "size": 9,
            "format_decimal": True,
            "fill_sequential": True,
            "box_width": 12,
            "box_spacing": 0.3,
            "boxes_per_row": 9,
            "row_height": 15,
            "max_rows": 1,
            "skip_boxes": [3, 7],
            "skip_box_widths": {3: 8, 7: 6},
            "fill_right_to_left": True
        }
    
    # Other Expenses (Lain-lain Perbelanjaan)
    if has_value('other_expenses'):
        field_mapping["Lain-lain Perbelanjaan"] = {
            "text": data['other_expenses'],
            "x": 337,
            "y": 425,
            "size": 9,
            "format_decimal": True,
            "fill_sequential": True,
            "box_width": 12,
            "box_spacing": 0.3,
            "boxes_per_row": 9,
            "row_height": 15,
            "max_rows": 1,
            "skip_boxes": [3, 7],
            "skip_box_widths": {3: 8, 7: 6},
            "fill_right_to_left": True
        }
    
    # Total Expenses (Jumlah Perbelanjaan)
    if has_value('total_expenses'):
        field_mapping["Jumlah Perbelanjaan"] = {
            "text": data['total_expenses'],
            "x": 439,
            "y": 445,
            "size": 9,
            "format_decimal": True,
            "fill_sequential": True,
            "box_width": 12,
            "box_spacing": 0.3,
            "boxes_per_row": 9,
            "row_height": 15,
            "max_rows": 1,
            "skip_boxes": [3, 7],
            "skip_box_widths": {3: 8, 7: 6},
            "fill_right_to_left": True
        }
    
    # Total Monthly Installments (Jumlah Ansuran Bulanan)
    if has_value('total_monthly_installments'):
        field_mapping["Jumlah Ansuran Bulanan"] = {
            "text": data['total_monthly_installments'],
            "x": 465,
            "y": 398,
            "size": 9,
            "format_decimal": True,
            "fill_sequential": True,
            "box_width": 12,
            "box_spacing": 0.3,
            "boxes_per_row": 9,
            "row_height": 15,
            "max_rows": 1,
            "skip_boxes": [3, 7],
            "skip_box_widths": {3: 8, 7: 6},
            "fill_right_to_left": True
        }
    
    # House Rental (Sewa Rumah)
    if has_value('house_rental'):
        field_mapping["Sewa Rumah"] = {
            "text": data['house_rental'],
            "x": 465,
            "y": 422,
            "size": 9,
            "format_decimal": True,
            "fill_sequential": True,
            "box_width": 12,
            "box_spacing": 0.3,
            "boxes_per_row": 9,
            "row_height": 15,
            "max_rows": 1,
            "skip_boxes": [3, 7],
            "skip_box_widths": {3: 8, 7: 6},
            "fill_right_to_left": True
        }
    
    # Net Income (Pendapatan Bersih)
    if has_value('net_income'):
        field_mapping["Pendapatan Bersih"] = {
            "text": data['net_income'],
            "x": 320,
            "y": 462,
            "size": 9,
            "format_decimal": True,
            "fill_sequential": True,
            "box_width": 12,
            "box_spacing": 0.3,
            "boxes_per_row": 9,
            "row_height": 15,
            "max_rows": 1,
            "skip_boxes": [3, 7],
            "skip_box_widths": {3: 8, 7: 6},
            "fill_right_to_left": True
        }
    
    # ===========================================
    # BANK/FINANCING TABLE (3 rows)
    # ===========================================
    
    # Bank 1
    if has_value('bank1_name'):
        field_mapping["Bank 1 Nama"] = {
            "text": data['bank1_name'],
            "x": 30,
            "y": 500,
            "size": 8,
            "use_boxes": False
        }
    
    if has_value('bank1_type'):
        field_mapping["Bank 1 Jenis Pembiayaan"] = {
            "text": data['bank1_type'],
            "x": 150,
            "y": 500,
            "size": 8,
            "use_boxes": False
        }
    
    if has_value('bank1_account'):
        field_mapping["Bank 1 No Akaun"] = {
            "text": data['bank1_account'],
            "x": 270,
            "y": 500,
            "size": 8,
            "use_boxes": False
        }
    
    if has_value('bank1_monthly_payment'):
        field_mapping["Bank 1 Bayaran Bulanan"] = {
            "text": data['bank1_monthly_payment'],
            "x": 400,
            "y": 500,
            "size": 8,
            "use_boxes": False
        }
    
    if has_value('bank1_balance'):
        field_mapping["Bank 1 Baki"] = {
            "text": data['bank1_balance'],
            "x": 500,
            "y": 500,
            "size": 8,
            "use_boxes": False
        }
    
    # Bank 2
    if has_value('bank2_name'):
        field_mapping["Bank 2 Nama"] = {
            "text": data['bank2_name'],
            "x": 30,
            "y": 510,
            "size": 8,
            "use_boxes": False
        }
    
    if has_value('bank2_type'):
        field_mapping["Bank 2 Jenis Pembiayaan"] = {
            "text": data['bank2_type'],
            "x": 150,
            "y": 510,
            "size": 8,
            "use_boxes": False
        }
    
    if has_value('bank2_account'):
        field_mapping["Bank 2 No Akaun"] = {
            "text": data['bank2_account'],
            "x": 270,
            "y": 510,
            "size": 8,
            "use_boxes": False
        }
    
    if has_value('bank2_monthly_payment'):
        field_mapping["Bank 2 Bayaran Bulanan"] = {
            "text": data['bank2_monthly_payment'],
            "x": 400,
            "y": 510,
            "size": 8,
            "use_boxes": False
        }
    
    if has_value('bank2_balance'):
        field_mapping["Bank 2 Baki"] = {
            "text": data['bank2_balance'],
            "x": 500,
            "y": 510,
            "size": 8,
            "use_boxes": False
        }
    
    # Bank 3
    if has_value('bank3_name'):
        field_mapping["Bank 3 Nama"] = {
            "text": data['bank3_name'],
            "x": 30,
            "y": 520,
            "size": 8,
            "use_boxes": False
        }
    
    if has_value('bank3_type'):
        field_mapping["Bank 3 Jenis Pembiayaan"] = {
            "text": data['bank3_type'],
            "x": 150,
            "y": 520,
            "size": 8,
            "use_boxes": False
        }
    
    if has_value('bank3_account'):
        field_mapping["Bank 3 No Akaun"] = {
            "text": data['bank3_account'],
            "x": 270,
            "y": 520,
            "size": 8,
            "use_boxes": False
        }
    
    if has_value('bank3_monthly_payment'):
        field_mapping["Bank 3 Bayaran Bulanan"] = {
            "text": data['bank3_monthly_payment'],
            "x": 400,
            "y": 520,
            "size": 8,
            "use_boxes": False
        }
    
    if has_value('bank3_balance'):
        field_mapping["Bank 3 Baki"] = {
            "text": data['bank3_balance'],
            "x": 500,
            "y": 520,
            "size": 8,
            "use_boxes": False
        }
    
    return field_mapping
