/**
 * Personal Financing Form JavaScript
 * Handles character counting, uppercase conversion, and form submission
 */

$(document).ready(function() {
    initCharacterCounters();
    initUppercaseConversion();
    $('#pembiayaanForm').on('submit', handleFormSubmit);
});

function initCharacterCounters() {
    $('input[data-limit], textarea[data-limit]').each(function() {
        const $field = $(this);
        const limit = parseInt($field.data('limit'));
        const $counter = $field.siblings('.char-counter');
        
        $field.on('input', function() {
            const currentLength = $field.val().length;
            $counter.text(`${currentLength}/${limit} characters`);
            
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

function initUppercaseConversion() {
    $('input[type="text"], textarea').not('[name="email"]').on('input', function() {
        const $field = $(this);
        const cursorPos = this.selectionStart;
        const value = $field.val();
        const uppercased = value.toUpperCase();
        
        if (value !== uppercased) {
            $field.val(uppercased);
            this.setSelectionRange(cursorPos, cursorPos);
        }
    });
}

function handleFormSubmit(e) {
    e.preventDefault();
    
    const formData = {};
    $('#pembiayaanForm').serializeArray().forEach(function(field) {
        if (field.name === 'email') {
            formData[field.name] = field.value;
        } else {
            formData[field.name] = field.value.toUpperCase();
        }
    });
    
    if (!formData.ic_number || !formData.name) {
        showError('Please fill in all required fields (IC Number and Name)');
        return;
    }
    
    const icNumber = formData.ic_number.replace(/-/g, '');
    if (!/^\d{12}$/.test(icNumber)) {
        showError('IC Number must be 12 digits');
        return;
    }
    
    if (formData.email && !isValidEmail(formData.email)) {
        showError('Please enter a valid email address');
        return;
    }
    
    $('#generateBtn').prop('disabled', true);
    $('#loadingSpinner').show();
    $('#errorAlert').hide();
    
    console.log('Submitting Pembiayaan form with data:', formData);
    
    $.ajax({
        url: '/api/generate/pembiayaan',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(formData),
        xhrFields: {
            responseType: 'blob'
        },
        success: function(blob) {
            console.log('PDF generation successful, blob size:', blob.size);
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `PEMBIAYAAN_${formData.name.substring(0, 20).replace(/\s+/g, '_')}_${Date.now()}.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            showSuccess('PDF generated successfully!');
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

function showError(message) {
    $('#errorAlert').html('<i class="bi bi-exclamation-triangle-fill"></i> ' + message).show();
    $('html, body').animate({ scrollTop: $('#errorAlert').offset().top - 100 }, 500);
}

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

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}
