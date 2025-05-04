/*
 * Property Report Generator - Enhanced UI Interactions
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Property Report Generator initialized');
    
    // Set default date to current date in format "DD Month YYYY"
    const reportDateInput = document.getElementById('report_date');
    if (reportDateInput && !reportDateInput.value) {
        const now = new Date();
        const months = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ];
        const formattedDate = `${now.getDate()} ${months[now.getMonth()]} ${now.getFullYear()}`;
        reportDateInput.value = formattedDate;
        console.log('Default date set to:', formattedDate);
        
        // Trigger the not-placeholder-shown state for styling
        reportDateInput.dispatchEvent(new Event('input'));
    }

    // Handle file input change for improved file upload experience
    const fileInput = document.getElementById('file');
    const fileUploadText = document.getElementById('file-upload-text');
    const fileUploadIcon = document.getElementById('file-upload-icon');
    const fileName = document.getElementById('file-name');
    const fileSize = document.getElementById('file-size');
    
    if (fileInput) {
        fileInput.addEventListener('change', function() {
            if (fileInput.files.length > 0) {
                const file = fileInput.files[0];
                const fileSizeValue = formatFileSize(file.size);
                
                console.log('File selected:', file.name, '(', fileSizeValue, ')');
                
                // Update UI to show selected file
                fileName.textContent = file.name;
                fileSize.textContent = fileSizeValue;
                fileUploadText.textContent = 'File selected';
                fileUploadIcon.innerHTML = '<i class="fas fa-check-circle"></i>';
                
                // Validate file type
                const fileExt = file.name.split('.').pop().toLowerCase();
                if (!['xlsx', 'xls', 'csv'].includes(fileExt)) {
                    showNotification('Please select a valid Excel (.xlsx, .xls) or CSV file.', 'error');
                    resetFileInput();
                }
            } else {
                resetFileInput();
            }
        });
    }
    
    // Function to reset file input UI
    function resetFileInput() {
        fileName.textContent = 'No file selected';
        fileSize.textContent = '';
        fileUploadText.textContent = 'Choose Excel/CSV file';
        fileUploadIcon.innerHTML = '<i class="fas fa-cloud-upload-alt"></i>';
        if (fileInput) fileInput.value = '';
    }
    
    // Format file size in human-readable format
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // Handle form submission with confirmation and loading animation
    const form = document.getElementById('reportForm');
    const generateBtn = document.getElementById('generateBtn');
    const confirmationModal = document.getElementById('confirmationModal');
    const confirmGenerate = document.getElementById('confirmGenerate');
    const cancelGenerate = document.getElementById('cancelGenerate');
    const loadingOverlay = document.getElementById('loading-overlay');
    const successOverlay = document.getElementById('success-overlay');
    const closeSuccessBtn = document.getElementById('closeSuccessBtn');
    
    // Show confirmation modal when Generate Report button is clicked
    if (generateBtn) {
        generateBtn.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Validate form fields before showing confirmation
            if (validateForm()) {
                // Show confirmation modal
                confirmationModal.classList.add('show');
            }
        });
    }
    
    // Handle confirmation button click
    if (confirmGenerate) {
        confirmGenerate.addEventListener('click', function() {
            // Hide confirmation modal
            confirmationModal.classList.remove('show');
            
            // Show loading overlay
            loadingOverlay.classList.add('active');
            
            // Submit the form
            submitForm();
        });
    }
    
    // Handle cancel button click
    if (cancelGenerate) {
        cancelGenerate.addEventListener('click', function() {
            // Hide confirmation modal
            confirmationModal.classList.remove('show');
        });
    }
    
    // Close success message
    if (closeSuccessBtn) {
        closeSuccessBtn.addEventListener('click', function() {
            successOverlay.classList.remove('active');
        });
    }
    
    // Validate form fields
    function validateForm() {
        // Validate form fields
        const businessType = document.querySelector('input[name="business_type"]:checked');
        const secondLine = document.getElementById('second_line').value.trim();
        const thirdLine = document.getElementById('third_line').value.trim();
        const reportDate = document.getElementById('report_date').value.trim();
        const file = document.getElementById('file').files[0];
        
        let isValid = true;
        let errorMessage = '';
        
        // Validation logic
        if (!businessType) {
            isValid = false;
            errorMessage = 'Please select a business type.';
        } else if (!secondLine) {
            isValid = false;
            errorMessage = 'Please enter the report title.';
        } else if (!thirdLine) {
            isValid = false;
            errorMessage = 'Please enter the location.';
        } else if (!reportDate) {
            isValid = false;
            errorMessage = 'Please enter the report date.';
        } else if (!file) {
            isValid = false;
            errorMessage = 'Please select an Excel or CSV file.';
        } else if (file) {
            // Check file extension
            const fileExt = file.name.split('.').pop().toLowerCase();
            if (!['xlsx', 'xls', 'csv'].includes(fileExt)) {
                isValid = false;
                errorMessage = 'Please select a valid Excel (.xlsx, .xls) or CSV file.';
            }
        }
        
        if (!isValid) {
            showNotification(errorMessage, 'error');
        }
        
        return isValid;
    }
    
    // Submit the form programmatically and handle download completion
    function submitForm() {
        console.log('Submitting form...');
        
        // Create a hidden iframe to track download completion
        const downloadFrame = document.createElement('iframe');
        downloadFrame.style.display = 'none';
        document.body.appendChild(downloadFrame);
        
        // Create a form data object for submission
        const formData = new FormData(form);
        
        // Submit form using fetch API
        fetch('/', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Server responded with an error');
            }
            return response.blob();
        })
        .then(blob => {
            // Create a download link
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            
            // Extract filename from Content-Disposition header if possible
            // Otherwise create a default name
            const businessType = document.querySelector('input[name="business_type"]:checked').value;
            const thirdLine = document.getElementById('third_line').value.trim();
            const reportDate = document.getElementById('report_date').value.trim();
            const filename = `Property_Report_${thirdLine.replace(/\s+/g, '_')}_${reportDate.replace(/\s+/g, '_')}.pdf`;
            
            a.href = url;
            a.download = filename;
            a.style.display = 'none';
            document.body.appendChild(a);
            
            // Start download
            a.click();
            
            // Clean up
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            // Hide loading overlay after a small delay to ensure download started
            setTimeout(() => {
                loadingOverlay.classList.remove('active');
                
                // Show success message
                successOverlay.classList.add('active');
            }, 1000);
        })
        .catch(error => {
            console.error('Error during form submission:', error);
            
            // Hide loading overlay
            loadingOverlay.classList.remove('active');
            
            // Show error notification
            showNotification('An error occurred while generating the report. Please try again.', 'error');
        });
    }

    // Reset button functionality - clear form fields without page reload
    const resetBtn = document.getElementById('resetBtn');
    if (resetBtn) {
        resetBtn.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Reset all form fields
            resetForm();
            
            // Show success notification
            showNotification('Form has been reset', 'success');
            
            // Send the reset signal to server
            fetch('/reset', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            }).then(response => {
                console.log('Reset request sent to server');
            }).catch(error => {
                console.error('Error sending reset request:', error);
            });
        });
    }

    // Reset all form fields
    function resetForm() {
        // Reset text inputs
        document.getElementById('second_line').value = '';
        document.getElementById('third_line').value = '';
        
        // Reset date to current date
        const now = new Date();
        const months = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ];
        document.getElementById('report_date').value = `${now.getDate()} ${months[now.getMonth()]} ${now.getFullYear()}`;
        
        // Reset business type to BusiVet
        document.getElementById('busivet').checked = true;
        
        // Reset file input
        resetFileInput();
        
        // Reset input styling
        const inputs = document.querySelectorAll('.input-container input');
        inputs.forEach(input => {
            if (input.value.trim() === '') {
                input.classList.remove('has-content');
            } else {
                input.classList.add('has-content');
            }
        });
    }
    
    // Function to show notification/flash message
    function showNotification(message, type = 'error') {
        console.log(`Showing ${type} message: ${message}`);
        
        // Check if flash messages container exists
        let flashContainer = document.querySelector('.flash-messages');
        
        // Create container if it doesn't exist
        if (!flashContainer) {
            flashContainer = document.createElement('div');
            flashContainer.className = 'flash-messages';
            
            // Insert at the top of the content
            const content = document.querySelector('.content');
            content.insertBefore(flashContainer, content.firstChild);
        }
        
        // Clear existing messages
        flashContainer.innerHTML = '';
        
        // Create new message
        const messageElement = document.createElement('div');
        messageElement.className = `flash-message ${type}`;
        
        // Add icon based on message type
        const icon = document.createElement('i');
        icon.className = type === 'error' ? 'fas fa-exclamation-circle' : 'fas fa-check-circle';
        messageElement.appendChild(icon);
        
        // Add message text
        const textNode = document.createTextNode(` ${message}`);
        messageElement.appendChild(textNode);
        
        // Add to container
        flashContainer.appendChild(messageElement);
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            messageElement.classList.add('fade-out');
            
            // Remove after fade animation
            setTimeout(() => {
                messageElement.remove();
                
                // Remove container if empty
                if (flashContainer.children.length === 0) {
                    flashContainer.remove();
                }
                
                console.log('Flash message hidden');
            }, 300);
            
        }, 5000);
    }
    
    // Handle events for floating labels in input fields
    const inputs = document.querySelectorAll('.input-container input');

    inputs.forEach(input => {
        // Check initial state
        if (input.value.trim() !== '') {
            input.classList.add('has-content');
        }
        
        // Handle input events
        input.addEventListener('input', function () {
            if (this.value.trim() !== '') {
                this.classList.add('has-content');
            } else {
                this.classList.remove('has-content');
            }
        });
        
        // Handle blur event to reset state if needed
        input.addEventListener('blur', function () {
            if (this.value.trim() === '') {
                this.classList.remove('has-content');
            }
        });
    });

});