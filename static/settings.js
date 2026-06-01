document.getElementById('profile-photo-input')?.addEventListener('change', async function () {
    const file = this.files?.[0];
    const status = document.getElementById('upload-status');
    if (!file) return;

    if (file.size > 5 * 1024 * 1024) {
        if (status) status.textContent = 'File too large. Max 5MB.';
        return;
    }

    const preview = document.getElementById('profile-preview');
    const headerAvatar = document.getElementById('header-avatar');
    const objectUrl = URL.createObjectURL(file);
    if (preview) preview.src = objectUrl;
    if (headerAvatar) headerAvatar.src = objectUrl;

    if (status) status.textContent = 'Uploading...';

    const formData = new FormData();
    formData.append('profile_photo', file);

    try {
        const response = await fetch('/settings/upload-photo', {
            method: 'POST',
            body: formData,
            credentials: 'same-origin',
        });
        if (response.redirected) {
            window.location.href = response.url;
            return;
        }
        if (response.ok) {
            window.location.reload();
            return;
        }
        if (status) status.textContent = 'Upload failed. Please try again.';
    } catch {
        if (status) status.textContent = 'Upload failed. Check your connection.';
    } finally {
        this.value = '';
    }
});
