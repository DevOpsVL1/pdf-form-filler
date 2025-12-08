"""
PDF Form Filler Web Platform - Production Version
Transforms PDF form fillers into a modern web application

Features:
- Automatic UPPERCASE conversion
- Real-time character limit validation
- User-friendly web interface
- Production-ready error handling
"""

from flask import Flask, render_template, request, send_file, jsonify, flash
import os
import io
import logging
from datetime import datetime
import secrets

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Ensure directories exist
os.makedirs('outputs', exist_ok=True)
os.makedirs('logs', exist_ok=True)


# =============================================================================
# CHARACTER LIMITS CONFIGURATION
# =============================================================================

CIF1_LIMITS = {
    'ic_number': 12,
    'old_ic_number': 12,
    'name_ic': 84,
    'date_of_birth': 10,
    'num_dependents': 2,
    'country_origin_other': 30,
    'education_other': 30,
    'ownership_type_other': 30,
    'mother_maiden_name': 42,
    'residential_address': 84,
    'residential_postcode': 5,
    'residential_city': 15,
    'residential_state': 25,
    'residence_years': 2,
    'correspondence_address': 63,
    'correspondence_postcode': 5,
    'correspondence_city': 15,
    'correspondence_state': 25,
    'tel_home': 10,
    'tel_office': 10,
    'tel_mobile': 10,
    'fax': 10,
    'email': 30,
    'employer_name': 42,
    'employer_address': 63,
    'date_started_work': 10,
    'position': 8,
    'position_grade': 8,
    'employment_status': 20,
}

PEMBIAYAAN_LIMITS = {
    'ic_number': 12,
    'name': 80,
    'address': 80,
    'postcode': 5,
    'city': 15,
    'state': 25,
    'tel_home': 10,
    'tel_mobile': 10,
    'email': 30,
    'employer_name': 40,
    'employer_address': 80,
    'monthly_income': 10,
    'financing_amount': 10,
    'financing_period': 3,
    'financing_tenure': 3,
    'membership_number': 14,
    'repayment_method_other': 30,
    'financing_type_other': 30,
    'spouse_name': 63,
    'spouse_dob': 10,
    'spouse_ic_new': 12,
    'spouse_ic_old': 8,
    'spouse_phone': 10,
    'spouse_employer_name_address': 80,
    'spouse_employer_postcode': 5,
    'spouse_employer_city_state': 40,
    'spouse_employer_office_phone': 10,
    'reference_name': 80,
    'reference_address': 80,
    'reference_postcode': 5,
    'reference_city_state': 40,
    'reference_ic': 12,
    'reference_occupation': 40,
    'reference_relationship': 40,
    'reference_mobile': 10,
    'reference_home': 10,
    'reference_office': 10,
    'monthly_salary': 10,
    'spouse_income': 10,
    'other_income': 10,
    'total_income': 10,
    'cost_of_living': 10,
    'other_expenses': 10,
    'total_expenses': 10,
    'total_monthly_installments': 10,
    'house_rental': 10,
    'net_income': 10,
    'bank1_name': 40,
    'bank1_type': 40,
    'bank1_account': 20,
    'bank1_monthly_payment': 10,
    'bank1_balance': 10,
    'bank2_name': 40,
    'bank2_type': 40,
    'bank2_account': 20,
    'bank2_monthly_payment': 10,
    'bank2_balance': 10,
    'bank3_name': 40,
    'bank3_type': 40,
    'bank3_account': 20,
    'bank3_monthly_payment': 10,
    'bank3_balance': 10,
}


# =============================================================================
# ROUTES
# =============================================================================

@app.route('/')
def index():
    """Landing page with form selection"""
    return render_template('index.html')


@app.route('/cif1')
def cif1_form():
    """CIF-1 form page"""
    return render_template('cif1_form.html', limits=CIF1_LIMITS)


@app.route('/pembiayaan')
def pembiayaan_form():
    """Personal Financing form page"""
    return render_template('pembiayaan_form.html', limits=PEMBIAYAAN_LIMITS)


@app.route('/api/generate/cif1', methods=['POST'])
def generate_cif1():
    """Generate CIF-1 PDF from user input"""
    try:
        data = request.get_json()
        logger.info("Received CIF-1 form submission")
        logger.debug(f"Form data keys: {list(data.keys())}")
        
        # Convert to uppercase (except emails)
        data = convert_to_uppercase(data, preserve=['email'])
        
        # Validate data
        errors = validate_cif1_data(data)
        if errors:
            logger.warning(f"CIF-1 validation failed: {errors}")
            return jsonify({'success': False, 'errors': errors}), 400
        
        # Generate PDF
        logger.info("Starting PDF generation...")
        from form_fillers.cif1_filler import generate_cif1_pdf
        pdf_buffer = generate_cif1_pdf(data)
        logger.info("PDF generation completed successfully")
        
        # Create filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        name = data.get('name_ic', 'FORM')[:20].replace(' ', '_')
        filename = f'CIF1_{name}_{timestamp}.pdf'
        
        logger.info(f"✓ Successfully generated: {filename}")
        
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except ImportError as e:
        logger.error(f"✗ Import error: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Module import failed: {str(e)}'
        }), 500
    except FileNotFoundError as e:
        logger.error(f"✗ File not found: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'PDF template not found. Please ensure BORANG_CIF-1.pdf is in templates/ folder.'
        }), 500
    except Exception as e:
        logger.error(f"✗ Error generating CIF-1 PDF: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Failed to generate PDF: {str(e)}'
        }), 500


@app.route('/api/generate/pembiayaan', methods=['POST'])
def generate_pembiayaan():
    """Generate Personal Financing PDF from user input"""
    try:
        data = request.get_json()
        logger.info("Received Pembiayaan form submission")
        logger.debug(f"Form data keys: {list(data.keys())}")
        
        # Convert to uppercase
        data = convert_to_uppercase(data, preserve=['email'])
        
        # Validate data
        errors = validate_pembiayaan_data(data)
        if errors:
            logger.warning(f"Pembiayaan validation failed: {errors}")
            return jsonify({'success': False, 'errors': errors}), 400
        
        # Generate PDF
        logger.info("Starting PDF generation...")
        from form_fillers.pembiayaan_filler import generate_pembiayaan_pdf
        pdf_buffer = generate_pembiayaan_pdf(data)
        logger.info("PDF generation completed successfully")
        
        # Create filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        name = data.get('name', 'FORM')[:20].replace(' ', '_')
        filename = f'PEMBIAYAAN_{name}_{timestamp}.pdf'
        
        logger.info(f"✓ Successfully generated: {filename}")
        
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except ImportError as e:
        logger.error(f"✗ Import error: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Module import failed: {str(e)}'
        }), 500
    except FileNotFoundError as e:
        logger.error(f"✗ File not found: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'PDF template not found. Please ensure BORANG_PEMBIAYAAN_PERIBADI.pdf is in templates/ folder.'
        }), 500
    except Exception as e:
        logger.error(f"✗ Error generating Pembiayaan PDF: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Failed to generate PDF: {str(e)}'
        }), 500


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def convert_to_uppercase(data, preserve=None):
    """
    Convert all string values to uppercase
    
    Args:
        data: Dictionary of form data
        preserve: List of field names to preserve (not uppercase)
    
    Returns:
        Dictionary with uppercased values
    """
    preserve = preserve or []
    result = {}
    
    for key, value in data.items():
        if key in preserve or not isinstance(value, str):
            result[key] = value
        else:
            result[key] = value.upper()
    
    return result


def validate_cif1_data(data):
    """Validate CIF-1 form data"""
    errors = []
    
    # Required fields
    if not data.get('ic_number'):
        errors.append('IC Number is required')
    elif len(data['ic_number']) > CIF1_LIMITS['ic_number']:
        errors.append(f'IC Number exceeds {CIF1_LIMITS["ic_number"]} characters')
    
    if not data.get('name_ic'):
        errors.append('Name (as per IC) is required')
    elif len(data['name_ic']) > CIF1_LIMITS['name_ic']:
        errors.append(f'Name exceeds {CIF1_LIMITS["name_ic"]} characters')
    
    # Validate IC format (digits only, with or without dashes)
    ic = data.get('ic_number', '').replace('-', '')
    if ic and not ic.isdigit():
        errors.append('IC Number must contain only digits')
    
    # Validate phone numbers
    for field in ['tel_home', 'tel_office', 'tel_mobile', 'fax']:
        phone = data.get(field, '').replace('-', '')
        if phone and not phone.isdigit():
            errors.append(f'{field.replace("_", " ").title()} must contain only digits')
    
    # Validate email
    email = data.get('email', '')
    if email and '@' not in email:
        errors.append('Invalid email format')
    
    # Check all field limits
    for field, limit in CIF1_LIMITS.items():
        value = data.get(field, '')
        if value and len(str(value)) > limit:
            field_name = field.replace('_', ' ').title()
            errors.append(f'{field_name} exceeds {limit} characters')
    
    return errors


def validate_pembiayaan_data(data):
    """Validate Personal Financing form data"""
    errors = []
    
    # Required fields
    if not data.get('ic_number'):
        errors.append('IC Number is required')
    
    if not data.get('name'):
        errors.append('Name is required')
    
    # Validate IC format
    ic = data.get('ic_number', '').replace('-', '')
    if ic and not ic.isdigit():
        errors.append('IC Number must contain only digits')
    
    # Validate numeric fields
    numeric_fields = ['monthly_income', 'financing_amount', 'financing_period']
    for field in numeric_fields:
        value = data.get(field, '')
        if value:
            try:
                float(str(value).replace(',', ''))
            except ValueError:
                field_name = field.replace('_', ' ').title()
                errors.append(f'{field_name} must be a valid number')
    
    # Check all field limits
    for field, limit in PEMBIAYAAN_LIMITS.items():
        value = data.get(field, '')
        if value and len(str(value)) > limit:
            field_name = field.replace('_', ' ').title()
            errors.append(f'{field_name} exceeds {limit} characters')
    
    return errors


# =============================================================================
# ERROR HANDLERS
# =============================================================================

@app.errorhandler(413)
def file_too_large(e):
    """Handle file size exceeded"""
    return jsonify({
        'success': False,
        'error': 'File size exceeds 16MB limit'
    }), 413


@app.errorhandler(500)
def internal_error(e):
    """Handle internal server errors"""
    logger.error(f"Internal error: {str(e)}", exc_info=True)
    return jsonify({
        'success': False,
        'error': 'An internal error occurred. Please try again.'
    }), 500


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return render_template('404.html'), 404


# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    print("="*80)
    print("PDF FORM FILLER PLATFORM - PRODUCTION VERSION")
    print("="*80)
    print("\n✓ Server starting...")
    print("✓ Access platform at: http://localhost:5000")
    print("✓ CIF-1 Form: http://localhost:5000/cif1")
    print("✓ Pembiayaan Form: http://localhost:5000/pembiayaan")
    print("\nPress CTRL+C to stop\n")
    print("="*80)
    
    app.run(debug=False, host='0.0.0.0', port=5000)
