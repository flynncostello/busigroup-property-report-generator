/*
 * Property Report Generator - Enhanced UI Interactions
 * This file handles all client-side interactions including form validation,
 * file uploads, sheet selection, and error handling with popup messages.
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

    // Get references to all important elements
    const fileInput = document.getElementById('file');
    const fileUploadText = document.getElementById('file-upload-text');
    const fileUploadIcon = document.getElementById('file-upload-icon');
    const fileName = document.getElementById('file-name');
    const fileSize = document.getElementById('file-size');
    const sheetSelectionContainer = document.getElementById('sheet-selection-container');
    const sheetSelect = document.getElementById('sheet_name');
    const sheetLoading = document.getElementById('sheet-loading');
    const generateBtn = document.getElementById('generateBtn');
    
    // Initially disable generate button until all requirements are met
    generateBtn.disabled = true;
    
    // Handle file input change event
    if (fileInput) {
        fileInput.addEventListener('change', function() {
            if (fileInput.files.length > 0) {
                const file = fileInput.files[0];
                const fileSizeValue = formatFileSize(file.size);
                
                console.log('File selected:', file.name, '(', fileSizeValue, ')');
                
                // Update UI to show selected file information
                fileName.textContent = file.name;
                fileSize.textContent = fileSizeValue;
                fileUploadText.textContent = 'File selected';
                fileUploadIcon.innerHTML = '<i class="fas fa-check-circle"></i>';
                
                // Validate file type
                const fileExt = file.name.split('.').pop().toLowerCase();
                if (!['xlsx', 'xls', 'csv'].includes(fileExt)) {
                    showErrorPopup('Please select a valid Excel (.xlsx, .xls) or CSV file.');
                    resetFileInput();
                    return;
                }
                
                // If it's an Excel file, automatically fetch sheet names
                if (fileExt === 'xlsx' || fileExt === 'xls') {
                    getSheetNames(file);
                } else {
                    // For CSV files, hide sheet selection and update button state
                    sheetSelectionContainer.style.display = 'none';
                    updateGenerateButtonState();
                }
            } else {
                resetFileInput();
            }
        });
    }
    
    // Handle sheet selection change
    if (sheetSelect) {
        sheetSelect.addEventListener('change', function() {
            updateGenerateButtonState();
        });
    }
    
    /**
     * Function to get sheet names from Excel file
     * Sends the file to the backend and populates the dropdown with available sheets
     */
    function getSheetNames(file) {
        sheetLoading.style.display = 'block';
        sheetSelectionContainer.style.display = 'block';
        
        const formData = new FormData();
        formData.append('file', file);
        
        fetch('/get_sheet_names', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            sheetLoading.style.display = 'none';
            
            if (data.error) {
                console.error('Error getting sheet names:', data.error);
                showErrorPopup(data.error);
                sheetSelectionContainer.style.display = 'none';
                return;
            }
            
            // Clear existing options and add new ones
            sheetSelect.innerHTML = '<option value="">Select a sheet...</option>';
            
            // Add each sheet name to the dropdown
            data.sheet_names.forEach(sheetName => {
                const option = document.createElement('option');
                option.value = sheetName;
                option.textContent = sheetName;
                sheetSelect.appendChild(option);
            });
            
            console.log('Sheet names loaded:', data.sheet_names);
        })
        .catch(error => {
            console.error('Error fetching sheet names:', error);
            sheetLoading.style.display = 'none';
            showErrorPopup('Error loading sheet names. Please try again.');
            sheetSelectionContainer.style.display = 'none';
        });
    }
    
    /**
     * Function to update the state of the generate button
     * Only enables the button when all required conditions are met
     */
    function updateGenerateButtonState() {
        const file = fileInput.files[0];
        const fileExt = file ? file.name.split('.').pop().toLowerCase() : '';
        
        // Check if all required fields are filled
        if (!file) {
            generateBtn.disabled = true;
            return;
        }
        
        // For Excel files, check if sheet is selected
        if ((fileExt === 'xlsx' || fileExt === 'xls') && !sheetSelect.value) {
            generateBtn.disabled = true;
            return;
        }
        
        // Enable button if all conditions are met
        generateBtn.disabled = false;
    }
    
    /**
     * Function to reset file input UI to initial state
     */
    function resetFileInput() {
        fileName.textContent = 'No file selected';
        fileSize.textContent = '';
        fileUploadText.textContent = 'Choose Excel/CSV file';
        fileUploadIcon.innerHTML = '<i class="fas fa-cloud-upload-alt"></i>';
        if (fileInput) fileInput.value = '';
        sheetSelectionContainer.style.display = 'none';
        sheetSelect.innerHTML = '<option value="">Select a sheet...</option>';
        generateBtn.disabled = true;
    }
    
    /**
     * Format file size in human-readable format
     */
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // Get references to modal elements
    const form = document.getElementById('reportForm');
    const confirmationModal = document.getElementById('confirmationModal');
    const confirmGenerate = document.getElementById('confirmGenerate');
    const cancelGenerate = document.getElementById('cancelGenerate');
    const loadingOverlay = document.getElementById('loading-overlay');
    const successOverlay = document.getElementById('success-overlay');
    const closeSuccessBtn = document.getElementById('closeSuccessBtn');
    
    // Handle generate button click
    if (generateBtn) {
        generateBtn.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Validate form fields before showing confirmation
            const formValidation = validateForm();
            if (formValidation.isValid) {
                // All fields are valid, show confirmation modal
                confirmationModal.classList.add('show');
            } else {
                // Show specific error popup for missing fields
                showErrorPopup(formValidation.errorMessage);
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
    
    /**
     * Function to create and show error popup modal
     * This creates a dynamic modal that displays error messages to the user
     */
    function showErrorPopup(message) {
        // Check if error modal already exists, if not create it
        let errorModal = document.getElementById('errorModal');
        if (!errorModal) {
            createErrorModal();
            errorModal = document.getElementById('errorModal');
        }
        
        // Update the error message
        const errorMessage = document.getElementById('errorMessage');
        errorMessage.textContent = message;
        
        // Show the error modal
        errorModal.classList.add('show');
        
        console.log('Error popup shown:', message);
    }
    
    /**
     * Function to create error modal dynamically
     * Creates a popup window specifically for displaying error messages
     */
    function createErrorModal() {
        const modalHtml = `
            <div id="errorModal" class="modal">
                <div class="modal-content">
                    <div class="modal-header" style="background-color: #f0506e;">
                        <h3><i class="fas fa-exclamation-triangle"></i> Error</h3>
                    </div>
                    <div class="modal-body">
                        <p id="errorMessage"></p>
                    </div>
                    <div class="modal-footer">
                        <button id="closeErrorBtn" class="btn btn-primary">
                            <i class="fas fa-check"></i> OK
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        // Insert modal into the page
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        
        // Add event listener for close button
        document.getElementById('closeErrorBtn').addEventListener('click', function() {
            document.getElementById('errorModal').classList.remove('show');
        });
        
        // Close modal when clicking outside
        document.getElementById('errorModal').addEventListener('click', function(e) {
            if (e.target === this) {
                this.classList.remove('show');
            }
        });
    }
    
    /**
     * Comprehensive form validation function
     * Checks all required fields and returns specific error messages
     */
    function validateForm() {
        // Get all form values
        const businessType = document.querySelector('input[name="business_type"]:checked');
        const secondLine = document.getElementById('second_line').value.trim();
        const thirdLine = document.getElementById('third_line').value.trim();
        const reportDate = document.getElementById('report_date').value.trim();
        const file = document.getElementById('file').files[0];
        const fileExt = file ? file.name.split('.').pop().toLowerCase() : '';
        const sheetName = document.getElementById('sheet_name').value;
        
        // Check each field and return specific error messages
        if (!businessType) {
            return { isValid: false, errorMessage: 'Please select a business type (BusiVet or BusiHealth).' };
        }
        
        if (!secondLine) {
            return { isValid: false, errorMessage: 'Please enter the report title.' };
        }
        
        if (!thirdLine) {
            return { isValid: false, errorMessage: 'Please enter the location.' };
        }
        
        if (!reportDate) {
            return { isValid: false, errorMessage: 'Please enter the report date.' };
        }
        
        if (!file) {
            return { isValid: false, errorMessage: 'Please select an Excel or CSV file.' };
        }
        
        // Check file extension
        if (!['xlsx', 'xls', 'csv'].includes(fileExt)) {
            return { isValid: false, errorMessage: 'Please select a valid Excel (.xlsx, .xls) or CSV file.' };
        }
        
        // For Excel files, check if sheet is selected
        if ((fileExt === 'xlsx' || fileExt === 'xls') && !sheetName) {
            return { isValid: false, errorMessage: 'Please select a sheet from the dropdown.' };
        }
        
        // All validations passed
        return { isValid: true, errorMessage: null };
    }
    
    /**
     * Submit the form programmatically with proper error handling
     * This function communicates with the backend and handles different response types
     */
    function submitForm() {
        console.log('Submitting form...');
        
        // Create a form data object for submission
        const formData = new FormData(form);
        
        // Submit form using fetch API with custom headers to identify AJAX requests
        fetch('/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',  // This tells the backend this is an AJAX request
                'Accept': 'application/json, application/pdf'  // We accept both JSON (errors) and PDF (success)
            }
        })
        .then(response => {
            console.log('Response status:', response.status);
            console.log('Response content-type:', response.headers.get('content-type'));
            
            // Check if the response indicates an error (4xx or 5xx status codes)
            if (!response.ok) {
                // The response is an error, try to parse it as JSON
                const contentType = response.headers.get('content-type');
                if (contentType && contentType.includes('application/json')) {
                    // It's a JSON error response
                    return response.json().then(errorData => {
                        console.log('Received JSON error:', errorData);
                        throw new Error(errorData.error || 'Unknown error occurred');
                    });
                } else {
                    // It's not JSON, probably an HTML error page
                    return response.text().then(htmlText => {
                        console.log('Received non-JSON error response');
                        throw new Error('Server error occurred');
                    });
                }
            }
            
            // Check if the response is actually a PDF file
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/pdf')) {
                console.log('Received PDF response');
                return response.blob();
            } else {
                // If it's not a PDF and not an error, something unexpected happened
                console.error('Unexpected response type:', contentType);
                throw new Error('Invalid response format');
            }
        })
        .then(blob => {
            if (!blob) return; // Skip if no blob (shouldn't happen)
            
            console.log('Processing PDF download...');
            
            // Create a download link for the PDF
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            
            // Create a meaningful filename for the download
            const businessType = document.querySelector('input[name="business_type"]:checked').value;
            const thirdLine = document.getElementById('third_line').value.trim();
            const reportDate = document.getElementById('report_date').value.trim();
            const filename = `Property_Report_${thirdLine.replace(/\s+/g, '_')}_${reportDate.replace(/\s+/g, '_')}.pdf`;
            
            a.href = url;
            a.download = filename;
            a.style.display = 'none';
            document.body.appendChild(a);
            
            // Start the download
            a.click();
            
            // Clean up resources
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            // Hide loading overlay and show success message after a small delay
            setTimeout(() => {
                loadingOverlay.classList.remove('active');
                // Show success message
                successOverlay.classList.add('active');
                console.log('PDF download initiated successfully');
            }, 1000);
        })
        .catch(error => {
            console.error('Error during form submission:', error);
            
            // Hide loading overlay
            loadingOverlay.classList.remove('active');
            
            // Show error popup with the specific error message
            showErrorPopup(error.message);
        });
    }

    // Reset button functionality
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

    /**
     * Reset all form fields to their default state
     */
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
        
        // Reset file input and sheet selection
        resetFileInput();
        
        // Reset input styling for floating labels
        const inputs = document.querySelectorAll('.input-container input');
        inputs.forEach(input => {
            if (input.value.trim() === '') {
                input.classList.remove('has-content');
            } else {
                input.classList.add('has-content');
            }
        });
    }
    
    /**
     * Function to show notification/flash message
     * This is used for non-error messages like success notifications
     */
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
        
        // Create new message element
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
        // Check initial state for floating labels
        if (input.value.trim() !== '') {
            input.classList.add('has-content');
        }
        
        // Handle input events for real-time label updates
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

    // Update generate button state when any form field changes
    document.querySelectorAll('input, select').forEach(element => {
        element.addEventListener('change', updateGenerateButtonState);
        element.addEventListener('input', updateGenerateButtonState);
    });

});