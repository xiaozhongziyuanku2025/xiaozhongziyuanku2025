// 侧边栏切换功能
document.addEventListener('DOMContentLoaded', function() {
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
                if (searchInput) searchInput.focus();
            } else {
                if (searchResults) searchResults.classList.remove('active');
            }
        });
        
        if (searchInput) {
            searchInput.addEventListener('input', function() {
                const query = this.value.trim().toLowerCase();
                const resultsList = document.getElementById('resultsList');
                
                if (query.length === 0) {
                    if (searchResults) searchResults.classList.remove('active');
                    return;
                }
                
                if (resultsList) {
                    resultsList.innerHTML = '';
                    const allFileItems = document.querySelectorAll('.file-item');
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
});
