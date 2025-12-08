// Handle conditional "Others" fields for both CIF-1 and Pembiayaan forms
document.addEventListener('DOMContentLoaded', function() {
    
    // CIF-1 Form Conditionals
    // Country of Origin
    const countryRadios = document.getElementsByName('country_origin');
    const countryOtherField = document.getElementById('countryOtherField');
    if (countryRadios.length > 0 && countryOtherField) {
        countryRadios.forEach(radio => {
            radio.addEventListener('change', function() {
                countryOtherField.style.display = this.value === 'LAIN-LAIN' ? 'block' : 'none';
            });
        });
    }
    
    // Education
    const educationRadios = document.getElementsByName('education');
    const educationOtherField = document.getElementById('educationOtherField');
    if (educationRadios.length > 0 && educationOtherField) {
        educationRadios.forEach(radio => {
            radio.addEventListener('change', function() {
                educationOtherField.style.display = this.value === 'LAIN-LAIN' ? 'block' : 'none';
            });
        });
    }
    
    // Ownership Type
    const ownershipRadios = document.getElementsByName('ownership_type');
    const ownershipOtherField = document.getElementById('ownershipOtherField');
    if (ownershipRadios.length > 0 && ownershipOtherField) {
        ownershipRadios.forEach(radio => {
            radio.addEventListener('change', function() {
                ownershipOtherField.style.display = this.value === 'LAIN-LAIN' ? 'block' : 'none';
            });
        });
    }
    
    // Pembiayaan Form Conditionals
    // Repayment Method
    const repaymentRadios = document.getElementsByName('repayment_method');
    const repaymentOtherField = document.getElementById('repaymentOtherField');
    if (repaymentRadios.length > 0 && repaymentOtherField) {
        repaymentRadios.forEach(radio => {
            radio.addEventListener('change', function() {
                repaymentOtherField.style.display = this.value === 'LAIN-LAIN / OTHERS' ? 'block' : 'none';
            });
        });
    }
    
    // Financing Type
    const financingTypeRadios = document.getElementsByName('financing_type');
    const financingTypeOtherField = document.getElementById('financingTypeOtherField');
    if (financingTypeRadios.length > 0 && financingTypeOtherField) {
        financingTypeRadios.forEach(radio => {
            radio.addEventListener('change', function() {
                financingTypeOtherField.style.display = this.value === 'LAIN-LAIN / OTHERS' ? 'block' : 'none';
            });
        });
    }
});
