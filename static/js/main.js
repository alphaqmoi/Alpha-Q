document.addEventListener('DOMContentLoaded', function() {
    // File upload handling
    const fileInput = document.getElementById('model_files');
    const fileList = document.getElementById('file_list');
    const uploadForm = document.getElementById('upload_form');
    const authForm = document.getElementById('auth_form');
    
    // Update file list when files are selected
    if (fileInput) {
        fileInput.addEventListener('change', function() {
            fileList.innerHTML = '';
            
            if (this.files.length > 0) {
                for (let i = 0; i < this.files.length; i++) {
                    const file = this.files[i];
                    const fileSize = formatFileSize(file.size);
                    
                    const fileItem = document.createElement('div');
                    fileItem.className = 'file-item';
                    fileItem.innerHTML = `
                        <span>${file.name}</span>
                        <span class="badge bg-secondary">${fileSize}</span>
                    `;
                    fileList.appendChild(fileItem);
                }
            } else {
                fileList.innerHTML = '<p class="text-muted">No files selected</p>';
            }
        });
    }
    
    // Show loading spinner when submitting forms
    if (uploadForm) {
        uploadForm.addEventListener('submit', function() {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Uploading...';
            }
        });
    }
    
    if (authForm) {
        authForm.addEventListener('submit', function() {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Authenticating...';
            }
        });
    }
    
    // Toggle new repository options
    const isNewRepoCheckbox = document.getElementById('is_new_repo');
    const repoVisibilityGroup = document.getElementById('repo_visibility_group');
    
    if (isNewRepoCheckbox && repoVisibilityGroup) {
        isNewRepoCheckbox.addEventListener('change', function() {
            repoVisibilityGroup.style.display = this.checked ? 'block' : 'none';
        });
        
        // Initialize visibility on page load
        repoVisibilityGroup.style.display = isNewRepoCheckbox.checked ? 'block' : 'none';
    }
    
    // Helper function to format file size
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    // Enable tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });
    
    // Auto-close alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            if (alert.parentNode) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 5000);
    });
});
