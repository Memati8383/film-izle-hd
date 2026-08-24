/**
 * Film İzle HD - Ortak JS Fonksiyonlari
 * Toast notification, paylasilan yardimcilar.
 */

/* Toast Notification Sistemi */
function showToast(message, type = 'info', duration = 3000) {
    let container = document.getElementById('toastContainer');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toastContainer';
        container.style.cssText = 'position:fixed;top:80px;right:20px;z-index:999999;display:flex;flex-direction:column;gap:10px;pointer-events:none;';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    const colors = {
        info: { bg: '#1a1a2e', border: '#6366f1', icon: 'fas fa-circle-info' },
        success: { bg: '#0d2818', border: '#46d369', icon: 'fas fa-circle-check' },
        error: { bg: '#2d0a0a', border: '#e50914', icon: 'fas fa-circle-exclamation' },
        warning: { bg: '#2d2a0a', border: '#fbbf24', icon: 'fas fa-triangle-exclamation' }
    };
    const c = colors[type] || colors.info;

    toast.style.cssText = `background:${c.bg};border:1px solid ${c.border};border-radius:10px;padding:14px 20px;color:#fff;font-family:'Inter',sans-serif;font-size:14px;font-weight:500;display:flex;align-items:center;gap:10px;box-shadow:0 8px 30px rgba(0,0,0,0.6);pointer-events:auto;transform:translateX(120%);transition:transform 0.3s cubic-bezier(0.4,0,0.2,1),opacity 0.3s;opacity:0;max-width:380px;backdrop-filter:blur(10px);`;
    toast.innerHTML = `<i class="${c.icon}" style="color:${c.border};font-size:18px;flex-shrink:0;"></i><span>${message}</span>`;

    container.appendChild(toast);
    requestAnimationFrame(() => {
        toast.style.transform = 'translateX(0)';
        toast.style.opacity = '1';
    });

    setTimeout(() => {
        toast.style.transform = 'translateX(120%)';
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

/* Ortak alert yerine kullanilan fonksiyonlar */
function alertSuccess(msg) { showToast(msg, 'success'); }
function alertError(msg) { showToast(msg, 'error', 4000); }
function alertInfo(msg) { showToast(msg, 'info'); }
function alertWarning(msg) { showToast(msg, 'warning', 4000); }
