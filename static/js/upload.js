// Handle file upload UI feedback
function handleFileUpload(formId, fileInputId) {
    const form = document.getElementById(formId);
    const fileInput = document.getElementById(fileInputId);
    
    // Exit if elements don't exist
    if (!form || !fileInput) return;
    
    const submitBtn = form.querySelector('button[type="submit"]');
    if (!submitBtn) return;
    
    fileInput.addEventListener('change', function() {
        const files = this.files;
        if (files && files.length > 0) {
            const fileList = Array.from(files).map(file => file.name).join(', ');
            const feedback = document.createElement('div');
            feedback.className = 'mt-2 text-info';
            feedback.textContent = `Selected: ${fileList}`;
            
            // Remove any existing feedback
            const existingFeedback = fileInput.parentElement.querySelector('.text-info');
            if (existingFeedback) {
                existingFeedback.remove();
            }
            
            fileInput.parentElement.appendChild(feedback);
        }
    });
    
    form.addEventListener('submit', function(e) {
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Uploading...';
        }
    });
}

// Initialize upload handlers when the document is ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize upload handlers only if we're on a page with upload forms
    const outlineForm = document.getElementById('outline-form');
    const documentsForm = document.getElementById('documents-form');
    
    if (outlineForm) {
        handleFileUpload('outline-form', 'outline');
    }
    if (documentsForm) {
        handleFileUpload('documents-form', 'documents');
    }
});
