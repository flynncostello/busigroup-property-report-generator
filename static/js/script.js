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

    // Handle form submission with improved validation and loading animation
    const form = document.querySelector('form');
    const loadingOverlay = document.getElementById('loading-overlay');
    const loadingMessage = document.getElementById('loading-message');
    
    if (form) {
        form.addEventListener('submit', function(e) {
            console.log('Form submission initiated');
            
            // Don't show loading state for reset button click
            if (e.submitter && e.submitter.formAction && e.submitter.formAction.includes('/reset')) {
                console.log('Reset button clicked, skipping validation');
                return; // Allow reset to proceed normally
            }
            
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
                console.log('Validation error: No business type selected');
            } else if (!secondLine) {
                isValid = false;
                errorMessage = 'Please enter the report title.';
                console.log('Validation error: No report title entered');
            } else if (!thirdLine) {
                isValid = false;
                errorMessage = 'Please enter the location.';
                console.log('Validation error: No location entered');
            } else if (!reportDate) {
                isValid = false;
                errorMessage = 'Please enter the report date.';
                console.log('Validation error: No date entered');
            } else if (!file) {
                isValid = false;
                errorMessage = 'Please select an Excel or CSV file.';
                console.log('Validation error: No file selected');
            } else if (file) {
                // Check file extension
                const fileExt = file.name.split('.').pop().toLowerCase();
                if (!['xlsx', 'xls', 'csv'].includes(fileExt)) {
                    isValid = false;
                    errorMessage = 'Please select a valid Excel (.xlsx, .xls) or CSV file.';
                    console.log('Validation error: Invalid file type');
                }
            }
            
            if (!isValid) {
                e.preventDefault(); // Only prevent submission if invalid
                showNotification(errorMessage, 'error');
                return;
            }
            
            console.log('Form validation passed, starting report generation');
            
            // Show loading overlay with animated progress messages
            showLoading();
            
            // CRITICAL: Don't call preventDefault() here - let the form submit normally
            // This was the key issue in your original code
            console.log('Allowing form to submit normally to server');
            
            // Set up a timeout to hide loading if the download takes too long
            setTimeout(() => {
                hideLoading();
                console.log('Load timeout reached, hiding loading overlay');
                showNotification('Report generation complete. If download didn\'t start, please check the browser download area.', 'success');
            }, 60000); // 60 seconds timeout for larger files
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
    
    // Function to show loading overlay with animated messages
    function showLoading() {
        if (!loadingOverlay) return;
        
        // Show loading overlay
        loadingOverlay.classList.add('active');
        
        // Array of loading messages to cycle through
        const messages = [
            "Processing your data...",
            "Analyzing property information...",
            "Creating report layout...",
            "Generating PDF report...",
            "Almost done, preparing download..."
        ];
        
        let messageIndex = 0;
        
        // Update message immediately
        if (loadingMessage) {
            loadingMessage.textContent = messages[messageIndex];
        }
        
        // Cycle through messages every 3 seconds
        const messageInterval = setInterval(() => {
            messageIndex = (messageIndex + 1) % messages.length;
            
            if (loadingMessage) {
                // Fade out
                loadingMessage.style.opacity = 0;
                
                // Change text and fade in
                setTimeout(() => {
                    loadingMessage.textContent = messages[messageIndex];
                    loadingMessage.style.opacity = 1;
                }, 100);
            }
        }, 1000);
        
        // Store interval ID in window object to clear it later
        window.loadingMessageInterval = messageInterval;
    }
    
    // Hide loading overlay and clear message interval
    function hideLoading() {
        if (!loadingOverlay) return;
        
        loadingOverlay.classList.remove('active');
        
        // Clear message interval if exists
        if (window.loadingMessageInterval) {
            clearInterval(window.loadingMessageInterval);
            window.loadingMessageInterval = null;
        }
    }
    
    // Handle events for floating labels in input fields
    const inputs = document.querySelectorAll('.input-container input');
    
    inputs.forEach(input => {
        // Check initial state
        if (input.value.trim() !== '') {
            input.classList.add('has-content');
        }
        
        // Handle input events
        input.addEventListener('input', function() {
            if (this.value.trim() !== '') {
                this.classList.add('has-content');
            } else {
                this.classList.remove('has-content');
            }
        });
    });
});