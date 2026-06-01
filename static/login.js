document.querySelector('.toggle-pwd')?.addEventListener('click', function () {
    const input = document.getElementById('password');
    const icon = this.querySelector('i');
    if (!input) return;
    const show = input.type === 'password';
    input.type = show ? 'text' : 'password';
    icon.classList.toggle('ph-eye', !show);
    icon.classList.toggle('ph-eye-slash', show);
});

document.querySelectorAll('.theme-btn').forEach((btn, i) => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.theme-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
    });
});
