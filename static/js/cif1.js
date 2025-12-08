/**
 * CIF-1 Form JavaScript
 * Handles character counting, uppercase conversion, and form submission
 */

$(document).ready(function() {
    // Initialize character counters for all fields
    initCharacterCounters();
    
    // Initialize uppercase conversion
    initUppercaseConversion();
    
    // Handle form submission
    $('#cif1Form').on('submit', handleFormSubmit);
});

/**
 * Initialize character counters for all input fields
 */
function initCharacterCounters() {
    $('input[data-limit], textarea[data-limit]').each(function() {
        const $field = $(this);
        const limit = parseInt($field.data('limit'));
        const $counter = $field.siblings('.char-counter');
        
        // Update counter on input
        $field.on('input', function() {
            const currentLength = $field.val().length;
            $counter.text(`${currentLength}/${limit} characters`);
            
            // Change color based on usage
            if (currentLength > limit) {
                $counter.removeClass('text-muted text-warning').addClass('text-danger');
                $field.addClass('is-invalid');
            } else if (currentLength > limit * 0.9) {
                $counter.removeClass('text-muted text-danger').addClass('text-warning');
                $field.removeClass('is-invalid');
            } else {
                $counter.removeClass('text-warning text-danger').addClass('text-muted');
                $field.removeClass('is-invalid');
            }
        });
    });
}

/**
 * Initialize automatic uppercase conversion for text fields
 * Excludes email field
 */
function initUppercaseConversion() {
    $('input[type="text"], textarea').not('[name="email"]').on('input', function() {
        const $field = $(this);
        const cursorPos = this.selectionStart;
        const value = $field.val();
        const uppercased = value.toUpperCase();
        
        if (value !== uppercased) {
            $field.val(uppercased);
            // Restore cursor position
            this.setSelectionRange(cursorPos, cursorPos);
        }
    });
}

/**
 * Handle form submission
 * Validates data and sends to API
 */
function handleFormSubmit(e) {
    e.preventDefault();
    
    // Collect form data
    const formData = {};
    $('#cif1Form').serializeArray().forEach(function(field) {
        // Convert to uppercase except for email
        if (field.name === 'email') {
            formData[field.name] = field.value;
        } else {
            formData[field.name] = field.value.toUpperCase();
        }
    });
    
    // Validate required fields
    if (!formData.ic_number || !formData.name_ic) {
        showError('Please fill in all required fields (IC Number and Name)');
        return;
    }
    
    // Validate IC number format
    const icNumber = formData.ic_number.replace(/-/g, '');
    if (!/^\d{12}$/.test(icNumber)) {
        showError('IC Number must be 12 digits');
        return;
    }
    
    // Validate email if provided
    if (formData.email && !isValidEmail(formData.email)) {
        showError('Please enter a valid email address');
        return;
    }
    
    // Show loading spinner
    $('#generateBtn').prop('disabled', true);
    $('#loadingSpinner').show();
    $('#errorAlert').hide();
    
    console.log('Submitting CIF-1 form with data:', formData);
    
    // Send to API
    $.ajax({
        url: '/api/generate/cif1',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(formData),
        xhrFields: {
            responseType: 'blob' // Important for PDF download
        },
        success: function(blob) {
            console.log('PDF generation successful, blob size:', blob.size);
            // Create download link
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `CIF1_${formData.name_ic.substring(0, 20).replace(/\s+/g, '_')}_${Date.now()}.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            // Show success message
            showSuccess('PDF generated successfully!');
            
            // Reset button
            $('#generateBtn').prop('disabled', false);
            $('#loadingSpinner').hide();
        },
        error: function(xhr) {
            console.error('PDF generation failed:', xhr.status, xhr.statusText);
            console.error('Response:', xhr.response);
            let errorMessage = 'Failed to generate PDF. Please try again.';
            
            // When responseType is blob, we need to read the blob as text to get error JSON
            if (xhr.responseType === 'blob' && xhr.response instanceof Blob) {
                const reader = new FileReader();
                reader.onload = function() {
                    try {
                        const errorData = JSON.parse(reader.result);
                        if (errorData.errors) {
                            errorMessage = errorData.errors.join('<br>');
                        } else if (errorData.error) {
                            errorMessage = errorData.error;
                        }
                    } catch (e) {
                        errorMessage = 'Server error. Please check your input and try again.';
                    }
                    showError(errorMessage);
                };
                reader.readAsText(xhr.response);
            } else if (xhr.responseJSON) {
                if (xhr.responseJSON.errors) {
                    errorMessage = xhr.responseJSON.errors.join('<br>');
                } else if (xhr.responseJSON.error) {
                    errorMessage = xhr.responseJSON.error;
                }
                showError(errorMessage);
            } else {
                showError(errorMessage);
            }
            
            $('#generateBtn').prop('disabled', false);
            $('#loadingSpinner').hide();
        }
    });
}

/**
 * Show error message
 */
function showError(message) {
    $('#errorAlert').html('<i class="bi bi-exclamation-triangle-fill"></i> ' + message).show();
    $('html, body').animate({ scrollTop: $('#errorAlert').offset().top - 100 }, 500);
}

/**
 * Show success message
 */
function showSuccess(message) {
    const successHtml = `
        <div class="alert alert-success alert-dismissible fade show mt-3" role="alert">
            <i class="bi bi-check-circle-fill"></i> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    $(successHtml).insertAfter('#errorAlert');
    setTimeout(function() {
        $('.alert-success').fadeOut();
    }, 5000);
}

/**
 * Validate email format
 */
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}
