// 侧边栏切换功能
const navToggle = document.getElementById('navToggle');
const sidebar = document.getElementById('sidebar');
const sidebarOverlay = document.getElementById('sidebarOverlay');

if (navToggle && sidebar && sidebarOverlay) {
    navToggle.addEventListener('click', function() {
        if (window.innerWidth <= 768) {
            sidebar.classList.toggle('active');
            sidebarOverlay.classList.toggle('active');
        }
    });
    
    sidebarOverlay.addEventListener('click', function() {
        if (window.innerWidth <= 768) {
            sidebar.classList.remove('active');
            sidebarOverlay.classList.remove('active');
        }
    });
    
    // ESC键关闭侧边栏
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && sidebar.classList.contains('active')) {
            sidebar.classList.remove('active');
            sidebarOverlay.classList.remove('active');
        }
    });
}

// 搜索功能
const searchToggle = document.getElementById('searchToggle');
const searchBar = document.getElementById('searchBar');
const searchInput = document.getElementById('searchInput');
const searchResults = document.getElementById('searchResults');

if (searchToggle && searchBar) {
    searchToggle.addEventListener('click', function() {
        searchBar.classList.toggle('active');
        if (searchBar.classList.contains('active')) {
            searchInput.focus();
        } else {
            if (searchResults) searchResults.classList.remove('active');
        }
    });
    
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const query = this.value.trim().toLowerCase();
            
            if (query.length === 0) {
                if (searchResults) searchResults.classList.remove('active');
                return;
            }
            
            // 简单搜索实现
            const allFileItems = document.querySelectorAll('.file-item');
            const resultsList = document.getElementById('resultsList');
            
            if (resultsList) {
                resultsList.innerHTML = '';
                let foundItems = 0;
                
                allFileItems.forEach(item => {
                    const fileName = item.getAttribute('data-name');
                    if (fileName && fileName.toLowerCase().includes(query)) {
                        const resultItem = item.cloneNode(true);
                        resultsList.appendChild(resultItem);
                        foundItems++;
                    }
                });
                
                if (foundItems > 0 && searchResults) {
                    searchResults.classList.add('active');
                } else if (searchResults) {
                    searchResults.classList.remove('active');
                }
            }
        });
    }
}

// 导航按钮状态
function updateNavButtons() {
    const backButton = document.getElementById('backButton');
    const forwardButton = document.getElementById('forwardButton');
    
    if (backButton) {
        if (window.history.length > 1) {
            backButton.classList.add('active');
        } else {
            backButton.classList.remove('active');
        }
    }
    
    if (forwardButton) {
        forwardButton.classList.remove('active'); // 简单实现
    }
}

// 页面加载时更新导航按钮
document.addEventListener('DOMContentLoaded', updateNavButtons);
window.addEventListener('popstate', updateNavButtons);
