let tabs = document.querySelectorAll(".tab")

tabs.forEach((tab) => {
    tab.addEventListener('click', () => {
        const tabId = tab.dataset.tab;
        const tabContent = document.getElementById(tabId);
        const allTabContents = document.querySelectorAll('.tab-content');
        
        // Сначала скрываем все табы
        allTabContents.forEach(content => {
            content.classList.add('hidden');
        });

        // Небольшая задержка для плавного появления нового таба
        setTimeout(() => {
            if (tabContent) {
                tabContent.classList.remove('hidden');
            }
        }, 50); // 50ms достаточно для срабатывания transition
        
        tabs.forEach(t => {
            t.classList.remove('active');
        });

        tab.classList.add('active');
    });
});
