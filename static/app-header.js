document.addEventListener('DOMContentLoaded', () => {
    const toggle = document.getElementById('notif-toggle');
    const dropdown = document.getElementById('notif-dropdown');
    const badge = document.getElementById('notif-badge');
    const markAllForm = document.getElementById('mark-all-read-form');

    if (!toggle || !dropdown) return;

    toggle.addEventListener('click', (e) => {
        e.stopPropagation();
        dropdown.classList.toggle('hidden');
        const isOpen = !dropdown.classList.contains('hidden');
        toggle.setAttribute('aria-expanded', String(isOpen));
    });

    document.addEventListener('click', (e) => {
        if (!dropdown.contains(e.target) && !toggle.contains(e.target)) {
            dropdown.classList.add('hidden');
            toggle.setAttribute('aria-expanded', 'false');
        }
    });

    dropdown.querySelectorAll('.notif-item.unread .notif-link').forEach((link) => {
        link.addEventListener('click', () => {
            const item = link.closest('.notif-item');
            const id = item?.dataset.id;
            if (id) {
                fetch(`/notifications/mark-read/${id}`, {
                    method: 'POST',
                    headers: { 'X-Requested-With': 'XMLHttpRequest' },
                }).then((r) => r.json()).then((data) => {
                    if (data.ok) {
                        item.classList.remove('unread');
                        updateBadge(data.unread);
                    }
                }).catch(() => {});
            }
        });
    });

    if (markAllForm) {
        markAllForm.addEventListener('submit', (e) => {
            e.preventDefault();
            fetch('/notifications/mark-all-read', {
                method: 'POST',
                headers: { 'X-Requested-With': 'XMLHttpRequest' },
            }).then((r) => r.json()).then((data) => {
                if (data.ok) {
                    dropdown.querySelectorAll('.notif-item').forEach((el) => el.classList.remove('unread'));
                    updateBadge(0);
                    markAllForm.remove();
                }
            }).catch(() => markAllForm.submit());
        });
    }

    function updateBadge(count) {
        if (!badge) return;
        if (count > 0) {
            badge.textContent = count;
            badge.classList.remove('hidden');
        } else {
            badge.classList.add('hidden');
        }
    }
});
