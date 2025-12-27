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
    
    // 全局状态：私密文件夹是否解锁
    window.isPrivateFolderUnlocked = false;
    
    // 修复的搜索功能 - 支持搜索文件和文件夹
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
        
        // 搜索数据库 - 包含所有文件和文件夹
        const searchDatabase = [
            // 公共文件和文件夹
            {
                id: 'file_001',
                name: '000.exe.rar',
                displayName: '000.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '111 KB',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,  // 公开文件
                keywords: ['000', 'exe', '病毒', 'windows']
            },
            {
                id: 'folder_001',
                name: '小众资源库',
                displayName: '小众资源库',
                type: '文件夹',
                category: '主文件夹',
                size: '包含子文件夹',
                path: 'main-resources.html',
                icon: 'folder',
                isPrivate: false,
                keywords: ['小众', '资源库', '主要', '文件夹']
            },
            {
                id: 'folder_002',
                name: 'Windows病毒库',
                displayName: 'Windows病毒库',
                type: '文件夹',
                category: '子文件夹',
                size: '包含1个文件',
                path: 'windows-virus.html',
                icon: 'folder',
                isPrivate: false,
                keywords: ['windows', '病毒库', '病毒', '样本']
            },
            {
                id: 'folder_003',
                name: '资源库',
                displayName: '资源库',
                type: '文件夹',
                category: '根目录',
                size: '包含2个文件夹',
                path: 'resources.html',
                icon: 'folder',
                isPrivate: false,
                keywords: ['资源库', '首页', '根目录']
            },
            // 私密文件夹（未解锁时隐藏）
            {
                id: 'private_folder',
                name: '私密文件夹',
                displayName: '私密文件夹',
                type: '文件夹',
                category: '密码保护',
                size: '空文件夹',
                path: 'private-folder.html',
                icon: 'private-folder',
                isPrivate: true,  // 私密文件夹
                keywords: ['私密', '密码', '保护', '隐藏']
            },
            // 私密文件夹内的文件（未解锁时隐藏）
            {
                id: 'private_file_001',
                name: 'secret-document.pdf',
                displayName: '机密文档.pdf',
                type: '文件',
                category: 'PDF文档',
                size: '2.5 MB',
                path: 'private-folder.html',
                icon: 'file',
                isPrivate: true,  // 私密文件
                requiresUnlock: true,  // 需要解锁才能访问
                keywords: ['机密', '文档', '秘密', '内部']
            },
            {
                id: 'private_file_002',
                name: 'confidential-data.zip',
                displayName: '机密数据.zip',
                type: '文件',
                category: '压缩文件',
                size: '15.3 MB',
                path: 'private-folder.html',
                icon: 'file',
                isPrivate: true,  // 私密文件
                requiresUnlock: true,
                keywords: ['机密', '数据', '压缩', '内部']
            }
        ];
        
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
                
                let foundItems = 0;
                
                // 搜索所有项目和文件夹
                searchDatabase.forEach(item => {
                    // 检查是否匹配搜索词
                    const matchesSearch = 
                        item.name.toLowerCase().includes(query) || 
                        item.displayName.toLowerCase().includes(query) ||
                        item.category.toLowerCase().includes(query) ||
                        item.keywords.some(keyword => keyword.toLowerCase().includes(query));
                    
                    // 根据解锁状态决定是否显示
                    let shouldShow = false;
                    
                    if (item.isPrivate) {
                        // 私密项目：未解锁时不显示
                        if (window.isPrivateFolderUnlocked) {
                            shouldShow = matchesSearch;
                        } else {
                            shouldShow = false; // 完全隐藏
                        }
                    } else {
                        // 公开项目：始终显示
                        shouldShow = matchesSearch;
                    }
                    
                    if (shouldShow) {
                        const resultItem = document.createElement('a');
                        resultItem.href = item.path;
                        resultItem.className = 'search-result-item';
                        resultItem.style.display = 'block';
                        resultItem.style.textDecoration = 'none';
                        resultItem.style.color = 'inherit';
                        
                        // 根据类型设置图标
                        let iconHTML = '';
                        if (item.icon === 'file') {
                            iconHTML = '<div class="file-icon" style="margin: 0 auto 8px;"></div>';
                        } else if (item.icon === 'private-folder') {
                            iconHTML = '<div class="private-folder-icon" style="width: 40px; height: 40px; margin: 0 auto 8px;"></div>';
                        } else {
                            iconHTML = '<div class="folder-icon" style="width: 40px; height: 40px; margin: 0 auto 8px;"></div>';
                        }
                        
                        // 私密文件特殊标记
                        const privateBadge = item.isPrivate ? 
                            '<span style="background: #FF5722; color: white; padding: 2px 6px; border-radius: 10px; font-size: 10px; margin-left: 5px;">私密</span>' : '';
                        
                        resultItem.innerHTML = `
                            <div class="search-result" style="
                                background: ${item.isPrivate ? 'rgba(255, 87, 34, 0.1)' : 'rgba(30, 30, 40, 0.9)'};
                                border-radius: 8px;
                                padding: 15px;
                                margin-bottom: 10px;
                                border: 1px solid ${item.isPrivate ? 'rgba(255, 87, 34, 0.3)' : 'rgba(255, 255, 255, 0.1)'};
                                transition: all 0.3s;
                                cursor: pointer;
                            ">
                                ${iconHTML}
                                <div style="text-align: center;">
                                    <div style="font-weight: bold; color: ${item.isPrivate ? '#FF5722' : '#4CAF50'}; margin-bottom: 4px;">
                                        ${item.displayName}
                                        ${privateBadge}
                                    </div>
                                    <div style="font-size: 12px; color: #aaa;">
                                        <span>${item.type}</span> | 
                                        <span>${item.category}</span> | 
                                        <span>${item.size}</span>
                                    </div>
                                    <div style="font-size: 11px; color: #888; margin-top: 4px;">
                                        路径: ${item.path}
                                    </div>
                                </div>
                            </div>
                        `;
                        
                        // 悬停效果
                        resultItem.addEventListener('mouseenter', function() {
                            this.querySelector('.search-result').style.transform = 'translateY(-2px)';
                            this.querySelector('.search-result').style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.3)';
                            this.querySelector('.search-result').style.borderColor = item.isPrivate ? 
                                'rgba(255, 87, 34, 0.5)' : 'rgba(76, 175, 80, 0.5)';
                        });
                        
                        resultItem.addEventListener('mouseleave', function() {
                            this.querySelector('.search-result').style.transform = 'none';
                            this.querySelector('.search-result').style.boxShadow = 'none';
                            this.querySelector('.search-result').style.borderColor = item.isPrivate ? 
                                'rgba(255, 87, 34, 0.3)' : 'rgba(255, 255, 255, 0.1)';
                        });
                        
                        resultsList.appendChild(resultItem);
                        foundItems++;
                    }
                });
                
                if (foundItems > 0) {
                    searchResults.classList.add('active');
                } else {
                    resultsList.innerHTML = `
                        <div style="
                            color: #aaa; 
                            padding: 30px; 
                            text-align: center;
                            background: rgba(30, 30, 40, 0.5);
                            border-radius: 8px;
                            border: 1px dashed rgba(255, 255, 255, 0.2);
                        ">
                            <i class="fas fa-search" style="font-size: 24px; margin-bottom: 10px; display: block;"></i>
                            <p>未找到 "<strong style="color: #fff;">${query}</strong>" 相关结果</p>
                            <p style="font-size: 12px; margin-top: 10px;">
                                提示：私密文件夹内的内容在解锁前不会显示在搜索结果中
                            </p>
                        </div>
                    `;
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
        
        // 点击页面其他地方关闭搜索
        document.addEventListener('click', function(e) {
            if (searchResults.classList.contains('active') && 
                !searchResults.contains(e.target) && 
                !searchBar.contains(e.target) && 
                e.target !== searchToggle) {
                searchResults.classList.remove('active');
            }
        });
    }
});
