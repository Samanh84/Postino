document.addEventListener('DOMContentLoaded', function() {
    const copyBtn = document.getElementById('copy-tracking-code');
    const codeBox = document.getElementById('tracking-code-box');
    const msg = document.getElementById('copy-msg');

    if (!copyBtn || !codeBox || !msg) return;

    copyBtn.addEventListener('click', async () => {
        try {
            // استفاده از Clipboard API
            await navigator.clipboard.writeText(codeBox.textContent.trim());

            // نمایش پیام کوتاه
            msg.style.display = 'block';
            setTimeout(() => {
                msg.style.display = 'none';
            }, 2000);
        } catch (err) {
            // اگر Clipboard API پشتیبانی نشد یا خطا رخ داد
            alert('خطا در کپی کردن کد رهگیری. لطفاً دستی کپی کنید.');
            console.error('Copy failed', err);
        }
    });
});
