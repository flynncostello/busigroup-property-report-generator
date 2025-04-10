/*
 * Main JavaScript for Property Report Generator
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
    }

    // Handle file input change to show selected filename
    const fileInput = document.getElementById('file');
    const fileFeedback = document.getElementById('file-feedback');
    
    if (fileInput && fileFeedback) {
        fileInput.addEventListener('change', function() {
            if (fileInput.files.length > 0) {
                const fileName = fileInput.files[0].name;
                const fileSize = (fileInput.files[0].size / 1024).toFixed(2) + ' KB';
                console.log('File selected:', fileName, '(', fileSize, ')');
                
                // Display filename and validate type
                fileFeedback.textContent = fileName;
                
                // Check if it's a valid file type
                const fileExt = fileName.split('.').pop().toLowerCase();
                if (!['xlsx', 'xls', 'csv'].includes(fileExt)) {
                    showFlashMessage('Please select a valid Excel (.xlsx, .xls) or CSV file.', 'error');
                    fileInput.value = ''; // Clear the file input
                    fileFeedback.textContent = 'No file selected';
                    fileFeedback.classList.add('error');
                } else {
                    fileFeedback.classList.remove('error');
                }
            } else {
                fileFeedback.textContent = 'No file selected';
                fileFeedback.classList.remove('error');
            }
        });
    }

    // Form submission validation and loading state
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', function(e) {
            console.log('Form submission initiated');
            
            // Don't show loading state for reset button click
            if (e.submitter && e.submitter.formAction && e.submitter.formAction.includes('/reset')) {
                console.log('Reset button clicked, skipping validation');
                return;
            }
            
            // Validate form fields
            const businessType = document.querySelector('input[name="business_type"]:checked');
            const secondLine = document.getElementById('second_line').value.trim();
            const thirdLine = document.getElementById('third_line').value.trim();
            const reportDate = document.getElementById('report_date').value.trim();
            const file = document.getElementById('file').files[0];
            
            let isValid = true;
            let errorMessage = '';
            
            if (!businessType) {
                isValid = false;
                errorMessage = 'Please select a business type.';
                console.log('Validation error: No business type selected');
            } else if (!secondLine) {
                isValid = false;
                errorMessage = 'Please enter the report title line.';
                console.log('Validation error: No report title entered');
            } else if (!thirdLine) {
                isValid = false;
                errorMessage = 'Please enter the location line.';
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
                const fileName = file.name.toLowerCase();
                if (!fileName.endsWith('.xlsx') && !fileName.endsWith('.xls') && !fileName.endsWith('.csv')) {
                    isValid = false;
                    errorMessage = 'Please select a valid Excel (.xlsx, .xls) or CSV file.';
                    console.log('Validation error: Invalid file type');
                }
            }
            
            if (!isValid) {
                e.preventDefault();
                showFlashMessage(errorMessage, 'error');
                return;
            }
            
            console.log('Form validation passed, starting report generation');
            
            // Create loading indicator
            showLoadingOverlay('Generating property report, please wait...');
        });
    }
    
    // Function to show flash message
    function showFlashMessage(message, type = 'error') {
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
        messageElement.textContent = message;
        
        // Add to container
        flashContainer.appendChild(messageElement);
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            messageElement.remove();
            
            // Remove container if empty
            if (flashContainer.children.length === 0) {
                flashContainer.remove();
            }
            
            console.log('Flash message auto-hidden');
        }, 5000);
    }
    
    // Function to show loading overlay
    function showLoadingOverlay(message) {
        console.log('Showing loading overlay with message:', message);
        
        // Add loading class to body
        document.body.classList.add('loading');
        
        // Create loading overlay
        const loadingOverlay = document.createElement('div');
        loadingOverlay.className = 'loading-overlay';
        
        // Add spinner and message
        loadingOverlay.innerHTML = `
            <div class="loading-spinner"></div>
            <div class="loading-text">${message}</div>
        `;
        
        // Add to body
        document.body.appendChild(loadingOverlay);
    }
});