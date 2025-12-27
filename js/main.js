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
    
    // 修复的搜索功能
    const searchToggle = document.getElementById('searchToggle');
    const searchBar = document.getElementById('searchBar');
    const searchInput = document.getElementById('searchInput');
    const searchResults = document.getElementById('searchResults');
    
    if (searchToggle && searchBar && searchInput && searchResults) {
        searchToggle.addEventListener('click', function() {
            searchBar.classList.toggle('active');
            if (searchBar.classList.contains('active')) {
                searchInput.focus();
            } else {
                searchResults.classList.remove('active');
            }
        });
        
        // 实际搜索功能
        searchInput.addEventListener('input', function() {
            const query = this.value.trim().toLowerCase();
            const resultsList = document.getElementById('resultsList');
            
            if (query.length === 0) {
                searchResults.classList.remove('active');
                return;
            }
            
            if (resultsList) {
                resultsList.innerHTML = '';
                
                // 搜索所有文件（包括跨页面文件）
                const allFileItems = [
                    {
                        name: '000.exe.rar',
                        displayName: '000.exe',
                        size: '111 KB',
                        type: 'EXE应用程序',
                        category: 'Windows病毒库',
                        path: 'windows-virus.html'
                    }
                    // 未来可以添加更多文件
                ];
                
                let foundItems = 0;
                
                allFileItems.forEach(file => {
                    if (file.displayName.toLowerCase().includes(query) || 
                        file.name.toLowerCase().includes(query)) {
                        const resultItem = document.createElement('a');
                        resultItem.href = file.path;
                        resultItem.className = 'download-link';
                        resultItem.innerHTML = `
                            <div class="file-item" data-name="${file.name}">
                                <div class="file-icon"></div>
                                <div class="file-name">${file.displayName}</div>
                                <div class="file-details">大小: ${file.size} | 类型: ${file.type}</div>
                            </div>
                        `;
                        resultsList.appendChild(resultItem);
                        foundItems++;
                    }
                });
                
                if (foundItems > 0) {
                    searchResults.classList.add('active');
                } else {
                    resultsList.innerHTML = '<p style="color:#aaa; padding:20px; text-align:center;">未找到相关文件</p>';
                    searchResults.classList.add('active');
                }
            }
        });
        
        // ESC键关闭搜索
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                if (searchBar.classList.contains('active')) {
                    searchBar.classList.remove('active');
                    searchResults.classList.remove('active');
                    searchInput.value = '';
                }
            }
        });
    }
});
