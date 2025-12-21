// 全局变量
let currentLevel = 0;
let historyStack = [];
let forwardStack = [];
let isPrivateFolderUnlocked = false;
let privateFolderPassword = "123456"; // 简单密码方便记忆

// DOM 元素
const navToggle = document.getElementById('navToggle');
const sidebar = document.getElementById('sidebar');
const sidebarOverlay = document.getElementById('sidebarOverlay');
const navLinks = document.querySelectorAll('.nav-link');
const sections = document.querySelectorAll('.section');
const folders = document.querySelectorAll('.folder');
const folderContents = document.querySelectorAll('.folder-content');
const breadcrumb = document.getElementById('breadcrumb');
const backButton = document.getElementById('backButton');
const forwardButton = document.getElementById('forwardButton');
const searchToggle = document.getElementById('searchToggle');
const searchBar = document.getElementById('searchBar');
const searchInput = document.getElementById('searchInput');
const searchResults = document.getElementById('searchResults');
const resultsList = document.getElementById('resultsList');
const passwordModal = document.getElementById('passwordModal');
const passwordInput = document.getElementById('passwordInput');
const passwordSubmit = document.getElementById('passwordSubmit');
const passwordCancel = document.getElementById('passwordCancel');
const passwordError = document.getElementById('passwordError');
const privateFolders = document.querySelectorAll('.private-folder');

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    // 默认显示"关于作者"页面
    showSection('about');
    
    // 导航菜单切换
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const target = this.getAttribute('data-target');
            
            // 更新导航菜单
            navLinks.forEach(l => l.classList.remove('active'));
            this.classList.add('active');
            
            // 显示对应部分
            showSection(target);
            
            // 在移动设备上关闭侧边栏
            closeSidebar();
            
            // 如果是资源库，重置为首页
            if (target === 'resources') {
                resetResourcesToHome();
            }
        });
    });
    
    // 侧边栏切换
    navToggle.addEventListener('click', function() {
        toggleSidebar();
    });
    
    // 点击遮罩层关闭侧边栏
    sidebarOverlay.addEventListener('click', function() {
        closeSidebar();
    });
    
    // 文件夹点击事件
    folders.forEach(folder => {
        folder.addEventListener('click', function() {
            const folderName = this.getAttribute('data-folder');
            const level = parseInt(this.getAttribute('data-level'));
            
            // 检查是否是私密文件夹
            if (this.classList.contains('private-folder')) {
                if (!isPrivateFolderUnlocked) {
                    // 显示密码输入模态框
                    passwordModal.classList.add('active');
                    passwordInput.focus();
                    return;
                }
            }
            
            // 更新当前层级
            currentLevel = level;
            
            // 添加到历史记录
            historyStack.push({
                level: currentLevel,
                folderName: folderName
            });
            
            // 清空前进栈
            forwardStack = [];
            
            // 更新导航按钮状态
            updateNavButtons();
            
            // 显示对应文件夹内容
            showFolderContent(folderName, level);
            
            // 更新面包屑导航
            updateBreadcrumb(folderName, level);
        });
    });
    
    // 面包屑导航点击事件
    breadcrumb.addEventListener('click', function(e) {
        if (e.target.classList.contains('breadcrumb-item')) {
            const level = parseInt(e.target.getAttribute('data-level'));
            const folderName = e.target.getAttribute('data-folder');
            
            // 检查是否是私密文件夹层级
            if (level > 0 && folderName === 'private') {
                if (!isPrivateFolderUnlocked) {
                    // 显示密码输入模态框
                    passwordModal.classList.add('active');
                    passwordInput.focus();
                    return;
                }
            }
            
            // 更新当前层级
            currentLevel = level;
            
            // 添加到历史记录
            historyStack.push({
                level: currentLevel,
                folderName: folderName || 'root'
            });
            
            // 清空前进栈
            forwardStack = [];
            
            // 更新导航按钮状态
            updateNavButtons();
            
            // 显示对应文件夹内容
            showFolderContent(folderName || 'root', level);
            
            // 更新面包屑导航
            updateBreadcrumb(folderName || 'root', level);
        }
    });
    
    // 后退按钮
    backButton.addEventListener('click', function() {
        if (historyStack.length > 1) {
            // 将当前状态保存到前进栈
            forwardStack.push(historyStack.pop());
            
            // 获取上一个状态
            const prevState = historyStack[historyStack.length - 1];
            
            // 更新当前层级
            currentLevel = prevState.level;
            
            // 更新导航按钮状态
            updateNavButtons();
            
            // 显示对应文件夹内容
            showFolderContent(prevState.folderName, prevState.level);
            
            // 更新面包屑导航
            updateBreadcrumb(prevState.folderName, prevState.level);
        }
    });
    
    // 前进按钮
    forwardButton.addEventListener('click', function() {
        if (forwardStack.length > 0) {
            // 获取下一个状态
            const nextState = forwardStack.pop();
            
            // 添加到历史记录
            historyStack.push(nextState);
            
            // 更新当前层级
            currentLevel = nextState.level;
            
            // 更新导航按钮状态
            updateNavButtons();
            
            // 显示对应文件夹内容
            showFolderContent(nextState.folderName, nextState.level);
            
            // 更新面包屑导航
            updateBreadcrumb(nextState.folderName, nextState.level);
        }
    });
    
    // 搜索功能
    searchToggle.addEventListener('click', function() {
        searchBar.classList.toggle('active');
        if (searchBar.classList.contains('active')) {
            searchInput.focus();
        } else {
            searchResults.classList.remove('active');
        }
    });
    
    searchInput.addEventListener('input', function() {
        const query = this.value.trim().toLowerCase();
        
        if (query.length === 0) {
            searchResults.classList.remove('active');
            return;
        }
        
        // 执行搜索
        performSearch(query);
    });
    
    // 密码输入功能
    passwordSubmit.addEventListener('click', function() {
        const inputPassword = passwordInput.value.trim();
        
        if (inputPassword === privateFolderPassword) {
            // 密码正确
            isPrivateFolderUnlocked = true;
            passwordModal.classList.remove('active');
            passwordInput.value = '';
            passwordError.style.display = 'none';
            
            // 自动打开私密文件夹
            const privateFolder = document.querySelector('.private-folder');
            if (privateFolder) {
                const folderName = privateFolder.getAttribute('data-folder');
                const level = parseInt(privateFolder.getAttribute('data-level'));
                
                // 更新当前层级
                currentLevel = level;
                
                // 添加到历史记录
                historyStack.push({
                    level: currentLevel,
                    folderName: folderName
                });
                
                // 清空前进栈
                forwardStack = [];
                
                // 更新导航按钮状态
                updateNavButtons();
                
                // 显示对应文件夹内容
                showFolderContent(folderName, level);
                
                // 更新面包屑导航
                updateBreadcrumb(folderName, level);
            }
        } else {
            // 密码错误
            passwordError.style.display = 'block';
            passwordInput.value = '';
            passwordInput.focus();
        }
    });
    
    passwordCancel.addEventListener('click', function() {
        passwordModal.classList.remove('active');
        passwordInput.value = '';
        passwordError.style.display = 'none';
    });
    
    // 按ESC键关闭密码模态框和侧边栏
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            if (passwordModal.classList.contains('active')) {
                passwordModal.classList.remove('active');
                passwordInput.value = '';
                passwordError.style.display = 'none';
            }
            if (sidebar.classList.contains('active')) {
                closeSidebar();
            }
        }
    });
    
    // 初始更新导航按钮状态
    updateNavButtons();
});

// 显示指定部分
function showSection(targetId) {
    sections.forEach(section => {
        section.classList.remove('active');
        if (section.id === targetId) {
            section.classList.add('active');
        }
    });
}

// 切换侧边栏
function toggleSidebar() {
    if (window.innerWidth <= 768) {
        sidebar.classList.toggle('active');
        sidebarOverlay.classList.toggle('active');
    }
}

// 关闭侧边栏
function closeSidebar() {
    if (window.innerWidth <= 768) {
        sidebar.classList.remove('active');
        sidebarOverlay.classList.remove('active');
    }
}

// 重置资源库到首页
function resetResourcesToHome() {
    currentLevel = 0;
    historyStack = [{
        level: currentLevel,
        folderName: 'root'
    }];
    forwardStack = [];
    
    // 更新导航按钮状态
    updateNavButtons();
    
    // 显示首页内容
    showFolderContent('root', 0);
    
    // 更新面包屑导航
    updateBreadcrumb('root', 0);
}

// 显示文件夹内容
function showFolderContent(folderName, level) {
    // 隐藏所有文件夹内容
    folderContents.forEach(content => {
        content.classList.remove('active');
    });
    
    // 显示对应文件夹内容
    let targetContentId = '';
    
    if (level === 0 || folderName === 'root') {
        targetContentId = 'folder-level-0'; // 首页
    } else if (folderName === 'main') {
        targetContentId = 'folder-level-1'; // 小众资源库
    } else if (folderName === 'private') {
        targetContentId = 'folder-level-private'; // 私密文件夹
    }
    
    if (targetContentId) {
        const targetContent = document.getElementById(targetContentId);
        if (targetContent) {
            targetContent.classList.add('active');
        }
    }
    
    // 隐藏搜索结果
    searchResults.classList.remove('active');
}

// 更新面包屑导航
function updateBreadcrumb(folderName, level) {
    // 清空面包屑
    breadcrumb.innerHTML = '';
    
    // 添加首页
    const homeItem = document.createElement('div');
    homeItem.className = 'breadcrumb-item';
    homeItem.setAttribute('data-level', '0');
    homeItem.setAttribute('data-folder', 'root');
    homeItem.textContent = '首页';
    breadcrumb.appendChild(homeItem);
    
    // 如果当前层级大于0，添加当前文件夹（跳过"资源库"层级）
    if (level > 0 && folderName !== 'root') {
        // 添加当前文件夹
        const currentItem = document.createElement('div');
        currentItem.className = 'breadcrumb-item';
        currentItem.setAttribute('data-level', level.toString());
        currentItem.setAttribute('data-folder', folderName);
        
        // 处理文件夹名称显示
        let displayName = folderName;
        if (folderName === 'main') {
            displayName = '小众资源库';
        } else if (folderName === 'private') {
            displayName = '私密文件夹';
        }
        
        currentItem.textContent = displayName;
        breadcrumb.appendChild(currentItem);
    }
}

// 更新导航按钮状态
function updateNavButtons() {
    // 后退按钮
    if (historyStack.length > 1) {
        backButton.classList.add('active');
    } else {
        backButton.classList.remove('active');
    }
    
    // 前进按钮
    if (forwardStack.length > 0) {
        forwardButton.classList.add('active');
    } else {
        forwardButton.classList.remove('active');
    }
}

// 执行搜索
function performSearch(query) {
    // 清空搜索结果
    resultsList.innerHTML = '';
    
    // 获取所有文件项
    const allFileItems = document.querySelectorAll('.file-item');
    let foundItems = 0;
    
    // 搜索逻辑
    allFileItems.forEach(item => {
        const fileName = item.getAttribute('data-name');
        const isPrivate = item.getAttribute('data-private') === 'true';
        
        // 检查是否匹配搜索词
        if (fileName && fileName.toLowerCase().includes(query)) {
            // 如果是私密文件且未解锁，则跳过
            if (isPrivate && !isPrivateFolderUnlocked) {
                return;
            }
            
            // 创建搜索结果项
            const resultItem = item.cloneNode(true);
            resultsList.appendChild(resultItem);
            foundItems++;
        }
    });
    
    // 显示搜索结果
    if (foundItems > 0) {
        searchResults.classList.add('active');
    } else {
        searchResults.classList.remove('active');
    }
}
