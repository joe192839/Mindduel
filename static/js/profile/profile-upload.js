document.addEventListener('DOMContentLoaded', function() {
    const profileUpload = document.getElementById('profile-upload');
    if (profileUpload) {
        profileUpload.addEventListener('change', function(e) {
            if (e.target.files && e.target.files[0]) {
                const formData = new FormData();
                formData.append('profile_photo', e.target.files[0]);
                
                fetch('/accounts/update-profile-photo/', {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        window.location.reload();
                    } else {
                        console.error('Error uploading profile photo:', data.error);
                    }
                })
                .catch(error => console.error('Error:', error));
            }
        });
    }
});