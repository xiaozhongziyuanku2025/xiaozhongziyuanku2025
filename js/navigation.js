// 前进后退按钮功能
document.addEventListener('DOMContentLoaded', function() {
    const backButton = document.getElementById('backButton');
    const forwardButton = document.getElementById('forwardButton');
    
    if (backButton) {
        if (window.history.length > 1) {
            backButton.classList.add('active');
            backButton.addEventListener('click', function() {
                window.history.back();
            });
        }
    }
    
    if (forwardButton) {
        forwardButton.classList.remove('active');
    }
});
