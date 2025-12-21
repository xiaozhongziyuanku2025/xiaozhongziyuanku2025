// 前进后退按钮功能
const backButton = document.getElementById('backButton');
const forwardButton = document.getElementById('forwardButton');

if (backButton) {
    backButton.addEventListener('click', function() {
        window.history.back();
    });
}

if (forwardButton) {
    forwardButton.addEventListener('click', function() {
        window.history.forward();
    });
}

// 侧边栏导航链接激活状态
document.addEventListener('DOMContentLoaded', function() {
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        const linkHref = link.getAttribute('href');
        if (linkHref === currentPage || 
            (currentPage === '' && linkHref === 'index.html')) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });
});
