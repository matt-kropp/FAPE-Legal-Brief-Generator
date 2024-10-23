// Handle file upload UI feedback
function handleFileUpload(formId, fileInputId) {
    const form = document.getElementById(formId);
    const fileInput = document.getElementById(fileInputId);
    
    // Only proceed if both elements exist
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
    handleFileUpload('outline-form', 'outline');
    handleFileUpload('documents-form', 'documents');
});
