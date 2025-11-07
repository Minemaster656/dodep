document.addEventListener('DOMContentLoaded', function() {
    const tabs = document.querySelectorAll('.tab');
    const loginTab = document.getElementById('tab-header-login');
    const registerTab = document.getElementById('tab-header-register');
    const loginInput = document.getElementById('login');
    const nameInput = document.getElementById('name');
    const passwordInput = document.getElementById('password');
    const showPasswordButton = document.getElementById('show-password-button');

    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            tabs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');

            if (this.dataset.tab === 'login') {
                nameInput.classList.add('hidden');
            } else {
                nameInput.classList.remove('hidden');
            }
        });
    });

    showPasswordButton.addEventListener('click', function() {
        if (passwordInput.type === 'password') {
            passwordInput.type = 'text';
        } else {
            passwordInput.type = 'password';
        }
    });

    // Initialize
    if (loginTab.classList.contains('active')) {
        nameInput.classList.add('hidden');
    }
});