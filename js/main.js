// ================================================================
//  ██████  统一 main.js  ██████
//  功能：侧边栏切换、前进后退、搜索（动态加载 search-index.json）、私密文件夹解锁
// ================================================================

// ===== 全局搜索数据 =====
let searchData = [];

// ===== 加载搜索索引 =====
async function loadSearchIndex() {
    try {
        const response = await fetch('search-index.json?_=' + Date.now());
        if (response.ok) {
            const data = await response.json();
            // search-index.json 格式: { files: [...], folders: [...] }
            if (data.files && data.folders) {
                searchData = [...data.files, ...data.folders];
                console.log('✅ 搜索索引加载成功，共 ' + searchData.length + ' 项');
                return;
            }
        }
        // 加载失败或格式不对，使用精简后备
        console.warn('⚠️ search-index.json 加载失败，使用硬编码后备数据');
        searchData = getFallbackSearchData();
    } catch (e) {
        console.error('❌ 加载搜索索引出错:', e);
        searchData = getFallbackSearchData();
    }
}

// ===== 硬编码后备数据（仅包含文件夹） =====
function getFallbackSearchData() {
    return [
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
            size: '包含大量文件',
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
        {
            id: 'private_folder',
            name: '私密文件夹',
            displayName: '私密文件夹',
            type: '文件夹',
            category: '密码保护',
            size: '空文件夹',
            path: 'private-folder.html',
            icon: 'private-folder',
            isPrivate: true,
            keywords: ['私密', '密码', '保护', '隐藏']
        }
    ];
}

// ===== 全局状态 =====
window.isPrivateFolderUnlocked = false;

// ===== DOM 加载完成后初始化 =====
document.addEventListener('DOMContentLoaded', async function() {
    // 1. 加载搜索索引（异步）
    await loadSearchIndex();

    // ===== 侧边栏切换 =====
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

    // ===== 前进/后退按钮 =====
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
        forwardButton.addEventListener('click', function() {
            window.history.forward();
        });
    }

    // ===== 搜索框展开/折叠 =====
    const searchToggle = document.getElementById('searchToggle');
    const searchBar = document.getElementById('searchBar');
    const searchInput = document.getElementById('searchInput');
    const searchResults = document.getElementById('searchResults');
    const resultsList = document.getElementById('resultsList');

    if (searchToggle && searchBar) {
        searchToggle.addEventListener('click', function() {
            searchBar.classList.toggle('active');
            if (searchBar.classList.contains('active')) {
                if (searchInput) searchInput.focus();
            } else {
                if (searchResults) searchResults.classList.remove('active');
                if (searchInput) searchInput.value = '';
            }
        });
    }

    // ESC 键关闭搜索
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            if (searchBar && searchBar.classList.contains('active')) {
                searchBar.classList.remove('active');
                if (searchResults) searchResults.classList.remove('active');
                if (searchInput) searchInput.value = '';
            }
        }
    });

    // ===== 搜索逻辑（依赖 searchData） =====
    if (searchInput && searchResults && resultsList) {
        searchInput.addEventListener('input', function() {
            const query = this.value.trim().toLowerCase();
            if (query.length === 0) {
                searchResults.classList.remove('active');
                return;
            }

            // 过滤
            const filtered = searchData.filter(item => {
                const match = 
                    item.name.toLowerCase().includes(query) ||
                    item.displayName.toLowerCase().includes(query) ||
                    item.category.toLowerCase().includes(query) ||
                    (item.keywords && item.keywords.some(k => k.toLowerCase().includes(query)));
                // 私密项：仅当解锁后才显示
                if (item.isPrivate && !window.isPrivateFolderUnlocked) {
                    return false;
                }
                return match;
            });

            if (filtered.length > 0) {
                resultsList.innerHTML = filtered.map(item => {
                    const iconClass = item.icon === 'file' ? 'file-icon' : (item.icon === 'private-folder' ? 'private-folder-icon' : 'folder-icon');
                    const privateBadge = item.isPrivate ? '<span style="background:#FF5722;color:white;padding:2px 6px;border-radius:10px;font-size:10px;margin-left:5px;">私密</span>' : '';
                    return `
                        <a href="${item.path}" style="text-decoration:none;color:inherit;display:block;">
                            <div class="search-result" style="background:${item.isPrivate ? 'rgba(255,87,34,0.1)' : 'rgba(30,30,40,0.9)'};border-radius:8px;padding:15px;margin-bottom:10px;border:1px solid ${item.isPrivate ? 'rgba(255,87,34,0.3)' : 'rgba(255,255,255,0.1)'};">
                                <div class="${iconClass}" style="width:40px;height:40px;margin:0 auto 8px;"></div>
                                <div style="text-align:center;">
                                    <div style="font-weight:bold;color:${item.isPrivate ? '#FF5722' : '#4CAF50'};margin-bottom:4px;">
                                        ${item.displayName}
                                        ${privateBadge}
                                    </div>
                                    <div style="font-size:12px;color:#aaa;">
                                        ${item.type} | ${item.category} | ${item.size}
                                    </div>
                                    <div style="font-size:11px;color:#888;margin-top:4px;">
                                        路径: ${item.path}
                                    </div>
                                </div>
                            </div>
                        </a>
                    `;
                }).join('');
                searchResults.classList.add('active');
            } else {
                resultsList.innerHTML = `
                    <div style="color:#aaa;padding:30px;text-align:center;background:rgba(30,30,40,0.5);border-radius:8px;border:1px dashed rgba(255,255,255,0.2);">
                        <i class="fas fa-search" style="font-size:24px;margin-bottom:10px;display:block;"></i>
                        <p>未找到 "<strong style="color:#fff;">${query}</strong>" 相关结果</p>
                        <p style="font-size:12px;margin-top:10px;">提示：私密文件夹内的内容在解锁前不会显示</p>
                    </div>
                `;
                searchResults.classList.add('active');
            }
        });
    }
});

// ===== 密码弹窗逻辑（由 resources.html 调用） =====
// 此部分已在 resources.html 中内联，不再重复
