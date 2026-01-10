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
        
        // 搜索数据库 - 包含所有文件和文件夹（187个Windows病毒文件已添加）
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
                isPrivate: false,
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
                size: '包含187个文件',
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
                isPrivate: true,
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
                isPrivate: true,
                requiresUnlock: true,
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
                isPrivate: true,
                requiresUnlock: true,
                keywords: ['机密', '数据', '压缩', '内部']
            },
            
            // ==================== Windows病毒库文件 (187个) ====================
            // 第1组 (1-30)
            {
                id: 'virus_001',
                name: '0KBAttack.exe.rar',
                displayName: '0KBAttack.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['0KBAttack', '攻击', '病毒', 'exe']
            },
            {
                id: 'virus_002',
                name: '000.exe.rar',
                displayName: '000.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '111 KB',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['000', 'exe', '病毒']
            },
            {
                id: 'virus_003',
                name: '16-9计算器.exe.rar',
                displayName: '16-9计算器.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['计算器', '16-9', '病毒', 'exe']
            },
            {
                id: 'virus_004',
                name: '45.exe.rar',
                displayName: '45.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['45', 'exe', '病毒']
            },
            {
                id: 'virus_005',
                name: '49.exe.rar',
                displayName: '49.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['49', 'exe', '病毒']
            },
            {
                id: 'virus_006',
                name: '666.exe.rar',
                displayName: '666.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['666', 'exe', '病毒', '恶魔']
            },
            {
                id: 'virus_007',
                name: 'Abantes.exe.rar',
                displayName: 'Abantes.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['Abantes', 'exe', '病毒']
            },
            {
                id: 'virus_008',
                name: 'AdvancedTex.exe.rar',
                displayName: 'AdvancedTex.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['AdvancedTex', '高级', '文本', '病毒']
            },
            {
                id: 'virus_009',
                name: 'Airoutix.exe.rar',
                displayName: 'Airoutix.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['Airoutix', '空气', '病毒', 'exe']
            },
            {
                id: 'virus_010',
                name: 'Argon.exe.rar',
                displayName: 'Argon.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['Argon', '氩', '化学', '病毒']
            },
            {
                id: 'virus_011',
                name: 'Argon-safety.exe.rar',
                displayName: 'Argon-safety.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['Argon', '安全', 'safety', '病毒']
            },
            {
                id: 'virus_012',
                name: 'auspicious.exe.rar',
                displayName: 'auspicious.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['auspicious', '吉祥', '病毒', 'exe']
            },
            {
                id: 'virus_013',
                name: 'avif.exe.rar',
                displayName: 'avif.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['avif', '图片格式', '病毒', 'exe']
            },
            {
                id: 'virus_014',
                name: 'avif.GDIOnly.exe.rar',
                displayName: 'avif.GDIOnly.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['avif', 'GDIOnly', '图形', '病毒']
            },
            {
                id: 'virus_015',
                name: 'bad_apple.exe.rar',
                displayName: 'bad_apple.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['bad apple', '坏苹果', '病毒', 'exe']
            },
            {
                id: 'virus_016',
                name: 'BUG32.exe.rar',
                displayName: 'BUG32.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['BUG32', 'bug', '错误', '病毒']
            },
            {
                id: 'virus_017',
                name: 'ChilledWindows(无害).exe.rar',
                displayName: 'ChilledWindows(无害).exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['ChilledWindows', '无害', '冷却', '病毒']
            },
            {
                id: 'virus_018',
                name: 'ChorumeDestructive.exe.rar',
                displayName: 'ChorumeDestructive.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['ChorumeDestructive', '破坏性', '病毒', 'exe']
            },
            {
                id: 'virus_019',
                name: 'DcRAT.exe.rar',
                displayName: 'DcRAT.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['DcRAT', '远程控制', '木马', '病毒']
            },
            {
                id: 'virus_020',
                name: 'Dead Fish.exe.rar',
                displayName: 'Dead Fish.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['Dead Fish', '死鱼', '病毒', 'exe']
            },
            {
                id: 'virus_021',
                name: 'Death.exe.rar',
                displayName: 'Death.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['Death', '死亡', '病毒', 'exe']
            },
            {
                id: 'virus_022',
                name: 'denoweniw0-safety.exe.rar',
                displayName: 'denoweniw0-safety.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['denoweniw0', '安全', 'safety', '病毒']
            },
            {
                id: 'virus_023',
                name: 'denoweniw0.exe.rar',
                displayName: 'denoweniw0.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['denoweniw0', '病毒', 'exe']
            },
            {
                id: 'virus_024',
                name: 'Dichloromethylhexane.exe.rar',
                displayName: 'Dichloromethylhexane.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['Dichloromethylhexane', '化学', '二氯', '病毒']
            },
            {
                id: 'virus_025',
                name: 'Dicolactor.exe.rar',
                displayName: 'Dicolactor.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['Dicolactor', '病毒', 'exe']
            },
            {
                id: 'virus_026',
                name: 'dimethylamine.exe.rar',
                displayName: 'dimethylamine.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['dimethylamine', '二甲胺', '化学', '病毒']
            },
            {
                id: 'virus_027',
                name: 'dimethylamine-safety.exe.rar',
                displayName: 'dimethylamine-safety.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['dimethylamine', '安全', 'safety', '病毒']
            },
            {
                id: 'virus_028',
                name: 'DISK MURDERER 2.0.bat.rar',
                displayName: 'DISK MURDERER 2.0.bat',
                type: '文件',
                category: 'BAT批处理文件',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['DISK MURDERER', '磁盘杀手', '批处理', 'bat']
            },
            {
                id: 'virus_029',
                name: 'Disk Terminator.exe.rar',
                displayName: 'Disk Terminator.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['Disk Terminator', '磁盘终结者', '病毒', 'exe']
            },
            {
                id: 'virus_030',
                name: 'Disunited.exe.rar',
                displayName: 'Disunited.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['Disunited', '分离', '病毒', 'exe']
            },
            // 第2组 (31-60)
            {
                id: 'virus_031',
                name: 'ED54 SpeedHacker.exe.rar',
                displayName: 'ED54 SpeedHacker.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['ED54', 'SpeedHacker', '速度黑客', '病毒']
            },
            {
                id: 'virus_032',
                name: 'effectsnamoxider（升级版）.exe.rar',
                displayName: 'effectsnamoxider（升级版）.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['effectsnamoxider', '升级版', '病毒', 'exe']
            },
            {
                id: 'virus_033',
                name: 'FakeMrsMajor3.0.exe.rar',
                displayName: 'FakeMrsMajor3.0.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['FakeMrsMajor', '假', '病毒', '3.0']
            },
            {
                id: 'virus_034',
                name: 'FormBook窃密木马.exe.rar',
                displayName: 'FormBook窃密木马.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['FormBook', '窃密', '木马', '病毒']
            },
            {
                id: 'virus_035',
                name: 'GameSetup（熊猫烧香）.exe.rar',
                displayName: 'GameSetup（熊猫烧香）.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['GameSetup', '熊猫烧香', '病毒', '经典']
            },
            {
                id: 'virus_036',
                name: 'grass脱盒v1.2.exe.rar',
                displayName: 'grass脱盒v1.2.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['grass', '脱盒', 'v1.2', '病毒']
            },
            {
                id: 'virus_037',
                name: 'HappyTime(快乐时光病毒).vbs.rar',
                displayName: 'HappyTime(快乐时光病毒).vbs',
                type: '文件',
                category: 'VBS脚本文件',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['HappyTime', '快乐时光', 'vbs', '脚本病毒']
            },
            {
                id: 'virus_038',
                name: 'HBRSB.exe.rar',
                displayName: 'HBRSB.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['HBRSB', '病毒', 'exe']
            },
            {
                id: 'virus_039',
                name: 'Heptoxide.exe.rar',
                displayName: 'Heptoxide.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['Heptoxide', '七氧化物', '化学', '病毒']
            },
            {
                id: 'virus_040',
                name: 'Heptoxide-safety.exe.rar',
                displayName: 'Heptoxide-safety.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['Heptoxide', '安全', 'safety', '病毒']
            },
            {
                id: 'virus_041',
                name: 'hexoputon - destructive.exe.rar',
                displayName: 'hexoputon - destructive.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['hexoputon', 'destructive', '破坏性', '病毒']
            },
            {
                id: 'virus_042',
                name: 'hexoputon - safety.exe.rar',
                displayName: 'hexoputon - safety.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['hexoputon', '安全', 'safety', '病毒']
            },
            {
                id: 'virus_043',
                name: 'HipsMain（火绒安全病毒2.0）.exe.rar',
                displayName: 'HipsMain（火绒安全病毒2.0）.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['HipsMain', '火绒安全', '病毒', '2.0']
            },
            {
                id: 'virus_044',
                name: 'HMCL_Virus.exe.rar',
                displayName: 'HMCL_Virus.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['HMCL', 'Virus', '我的世界', '病毒']
            },
            {
                id: 'virus_045',
                name: 'hollywoodium.exe.rar',
                displayName: 'hollywoodium.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['hollywoodium', '好莱坞', '病毒', 'exe']
            },
            {
                id: 'virus_046',
                name: 'hollywoodium-safety.exe.rar',
                displayName: 'hollywoodium-safety.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['hollywoodium', '安全', 'safety', '病毒']
            },
            {
                id: 'virus_047',
                name: 'Holzer.exe.rar',
                displayName: 'Holzer.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['Holzer', '病毒', 'exe']
            },
            {
                id: 'virus_048',
                name: 'hydrogen.exe.rar',
                displayName: 'hydrogen.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['hydrogen', '氢', '化学', '病毒']
            },
            {
                id: 'virus_049',
                name: 'ico.exe.rar',
                displayName: 'ico.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['ico', '图标', '病毒', 'exe']
            },
            {
                id: 'virus_050',
                name: 'ico_GDIOnly.exe.rar',
                displayName: 'ico_GDIOnly.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['ico', 'GDIOnly', '图标', '病毒']
            },
            {
                id: 'virus_051',
                name: 'IKUN-KILLER.exe.rar',
                displayName: 'IKUN-KILLER.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['IKUN', 'KILLER', '杀手', '病毒']
            },
            {
                id: 'virus_052',
                name: 'incaseformat.exe.rar',
                displayName: 'incaseformat.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['incaseformat', '格式化', '病毒', 'exe']
            },
            {
                id: 'virus_053',
                name: 'Info_Update(Harmless).exe.rar',
                displayName: 'Info_Update(Harmless).exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['Info_Update', '无害', 'Harmless', '病毒']
            },
            {
                id: 'virus_054',
                name: 'jfif.exe.rar',
                displayName: 'jfif.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['jfif', '图片格式', '病毒', 'exe']
            },
            {
                id: 'virus_055',
                name: 'JJY.exe.rar',
                displayName: 'JJY.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['JJY', '病毒', 'exe']
            },
            {
                id: 'virus_056',
                name: 'jpg.exe.rar',
                displayName: 'jpg.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['jpg', '图片格式', '病毒', 'exe']
            },
            {
                id: 'virus_057',
                name: 'JSONx64-safety.exe.rar',
                displayName: 'JSONx64-safety.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['JSON', 'x64', '安全', 'safety', '病毒']
            },
            {
                id: 'virus_058',
                name: 'JSONx64.exe.rar',
                displayName: 'JSONx64.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['JSON', 'x64', '病毒', 'exe']
            },
            {
                id: 'virus_059',
                name: 'JSONx86-safety.exe.rar',
                displayName: 'JSONx86-safety.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['JSON', 'x86', '安全', 'safety', '病毒']
            },
            {
                id: 'virus_060',
                name: 'JSONx86.exe.rar',
                displayName: 'JSONx86.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['JSON', 'x86', '病毒', 'exe']
            },
            // 第3组 (61-90)
            {
                id: 'virus_061',
                name: 'Lost.exe.rar',
                displayName: 'Lost.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['Lost', '丢失', '病毒', 'exe']
            },
            {
                id: 'virus_062',
                name: 'M0dules.exe.rar',
                displayName: 'M0dules.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['M0dules', '模块', '病毒', 'exe']
            },
            {
                id: 'virus_063',
                name: 'M0dules_GDIOnly.exe.rar',
                displayName: 'M0dules_GDIOnly.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['M0dules', 'GDIOnly', '模块', '病毒']
            },
            {
                id: 'virus_064',
                name: 'Mandela.exe.rar',
                displayName: 'Mandela.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['Mandela', '曼德拉', '病毒', 'exe']
            },
            {
                id: 'virus_065',
                name: 'Microsoft Paint15.1.1.exe.rar',
                displayName: 'Microsoft Paint15.1.1.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['Microsoft Paint', '画图', '15.1.1', '病毒']
            },
            {
                id: 'virus_066',
                name: 'Microsoft Paint15.3.2.exe.rar',
                displayName: 'Microsoft Paint15.3.2.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['Microsoft Paint', '画图', '15.3.2', '病毒']
            },
            {
                id: 'virus_067',
                name: 'ModifiedEnternalred.exe.rar',
                displayName: 'ModifiedEnternalred.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['ModifiedEnternalred', '修改', '永恒红', '病毒']
            },
            {
                id: 'virus_068',
                name: 'ModifiedEnternalred-safety.exe.rar',
                displayName: 'ModifiedEnternalred-safety.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['ModifiedEnternalred', '安全', 'safety', '病毒']
            },
            {
                id: 'virus_069',
                name: 'ModifiedPurgatorium.exe.rar',
                displayName: 'ModifiedPurgatorium.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['ModifiedPurgatorium', '修改', '炼狱', '病毒']
            },
            {
                id: 'virus_070',
                name: 'Monoxidex64.exe.rar',
                displayName: 'Monoxidex64.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['Monoxide', '一氧化物', 'x64', '病毒']
            },
            {
                id: 'virus_071',
                name: 'Monoxidex86.exe.rar',
                displayName: 'Monoxidex86.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['Monoxide', '一氧化物', 'x86', '病毒']
            },
            {
                id: 'virus_072',
                name: 'MrsMajor 2.0.exe.rar',
                displayName: 'MrsMajor 2.0.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['MrsMajor', '夫人', '2.0', '病毒']
            },
            {
                id: 'virus_073',
                name: 'MrsMajor 3.0.exe.rar',
                displayName: 'MrsMajor 3.0.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['MrsMajor', '夫人', '3.0', '病毒']
            },
            {
                id: 'virus_074',
                name: 'Musubi.exe.rar',
                displayName: 'Musubi.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['Musubi', '饭团', '病毒', 'exe']
            },
            {
                id: 'virus_075',
                name: 'nepotonod.exe.rar',
                displayName: 'nepotonod.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['nepotonod', '病毒', 'exe']
            },
            {
                id: 'virus_076',
                name: 'Office 2023专业增强版Setup(易语言程序).exe.rar',
                displayName: 'Office 2023专业增强版Setup(易语言程序).exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['Office 2023', '专业增强版', '易语言', '病毒']
            },
            {
                id: 'virus_077',
                name: 'Oganesson.exe.rar',
                displayName: 'Oganesson.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['Oganesson', 'Og', '化学元素', '病毒']
            },
            {
                id: 'virus_078',
                name: 'Oganesson.harmless.exe.rar',
                displayName: 'Oganesson.harmless.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['Oganesson', '无害', 'harmless', '病毒']
            },
            {
                id: 'virus_079',
                name: 'PAINT.exe.rar',
                displayName: 'PAINT.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['PAINT', '画图', '病毒', 'exe']
            },
            {
                id: 'virus_080',
                name: 'Parasite 2.0.exe.rar',
                displayName: 'Parasite 2.0.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['Parasite', '寄生虫', '2.0', '病毒']
            },
            {
                id: 'virus_081',
                name: 'PasswordHacker.exe.rar',
                displayName: 'PasswordHacker.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['PasswordHacker', '密码黑客', '病毒', 'exe']
            },
            {
                id: 'virus_082',
                name: 'PCManager·报废.exe.rar',
                displayName: 'PCManager·报废.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['PCManager', '报废', '病毒', 'exe']
            },
            {
                id: 'virus_083',
                name: 'pcTNT.exe.rar',
                displayName: 'pcTNT.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['pcTNT', 'TNT', '炸药', '病毒']
            },
            {
                id: 'virus_084',
                name: 'Pertechnetate.exe.rar',
                displayName: 'Pertechnetate.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['Pertechnetate', '高锝酸盐', '化学', '病毒']
            },
            {
                id: 'virus_085',
                name: 'Pet.exe.rar',
                displayName: 'Pet.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['Pet', '宠物', '病毒', 'exe']
            },
            {
                id: 'virus_086',
                name: 'PhantasmA.exe.rar',
                displayName: 'PhantasmA.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['PhantasmA', '幻象', '病毒', 'exe']
            },
            {
                id: 'virus_087',
                name: 'Phosgene.exe.rar',
                displayName: 'Phosgene.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['Phosgene', '光气', '化学', '病毒']
            },
            {
                id: 'virus_088',
                name: 'PlayingWithCitlali.exe.rar',
                displayName: 'PlayingWithCitlali.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['PlayingWithCitlali', '玩耍', '病毒', 'exe']
            },
            {
                id: 'virus_089',
                name: 'png.exe.rar',
                displayName: 'png.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['png', '图片格式', '病毒', 'exe']
            },
            {
                id: 'virus_090',
                name: 'png_GDIOnly.exe.rar',
                displayName: 'png_GDIOnly.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['png', 'GDIOnly', '图片', '病毒']
            },
            // 第4组 (91-120)
            {
                id: 'virus_091',
                name: 'png_Win8-11_GDIOnly.exe.rar',
                displayName: 'png_Win8-11_GDIOnly.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['png', 'Win8-11', 'GDIOnly', '病毒']
            },
            {
                id: 'virus_092',
                name: 'q2oic2i0b.exe.rar',
                displayName: 'q2oic2i0b.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['q2oic2i0b', '随机名', '病毒', 'exe']
            },
            {
                id: 'virus_093',
                name: 'Quadrioxide.exe.rar',
                displayName: 'Quadrioxide.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['Quadrioxide', '四氧化物', '化学', '病毒']
            },
            {
                id: 'virus_094',
                name: 'quantizer.exe.rar',
                displayName: 'quantizer.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['quantizer', '量化器', '病毒', 'exe']
            },
            {
                id: 'virus_095',
                name: 'radiance_harmful.exe.rar',
                displayName: 'radiance_harmful.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['radiance', 'harmful', '有害', '病毒']
            },
            {
                id: 'virus_096',
                name: 'radiance_harmless.exe.rar',
                displayName: 'radiance_harmless.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['radiance', 'harmless', '无害', '病毒']
            },
            {
                id: 'virus_097',
                name: 'Ramnit蠕虫病毒.vbs.rar',
                displayName: 'Ramnit蠕虫病毒.vbs',
                type: '文件',
                category: 'VBS脚本文件',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['Ramnit', '蠕虫病毒', 'vbs', '脚本']
            },
            {
                id: 'virus_098',
                name: 'RedEye.exe.rar',
                displayName: 'RedEye.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['RedEye', '红眼', '病毒', 'exe']
            },
            {
                id: 'virus_099',
                name: 'REMCOS远控.exe.rar',
                displayName: 'REMCOS远控.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['REMCOS', '远控', '远程控制', '病毒']
            },
            {
                id: 'virus_100',
                name: 'Ripples.exe.rar',
                displayName: 'Ripples.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['Ripples', '涟漪', '病毒', 'exe']
            },
            {
                id: 'virus_101',
                name: 'RoobDesktopAssistant(摧毁者).exe.rar',
                displayName: 'RoobDesktopAssistant(摧毁者).exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['RoobDesktopAssistant', '摧毁者', '病毒', 'exe']
            },
            {
                id: 'virus_102',
                name: 'Rover.exe.rar',
                displayName: 'Rover.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['Rover', '漫游者', '病毒', 'exe']
            },
            {
                id: 'virus_103',
                name: 'Rover beta1.2.exe.rar',
                displayName: 'Rover beta1.2.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['Rover', 'beta1.2', '测试版', '病毒']
            },
            {
                id: 'virus_104',
                name: 'salinewin.exe.rar',
                displayName: 'salinewin.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['salinewin', '盐水', '病毒', 'exe']
            },
            {
                id: 'virus_105',
                name: 'salinewin-safety.exe.rar',
                displayName: 'salinewin-safety.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['salinewin', '安全', 'safety', '病毒']
            },
            {
                id: 'virus_106',
                name: 'SecurityVirus(安全者).exe.rar',
                displayName: 'SecurityVirus(安全者).exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['SecurityVirus', '安全者', '病毒', 'exe']
            },
            {
                id: 'virus_107',
                name: 'Spark.exe.rar',
                displayName: 'Spark.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['Spark', '火花', '病毒', 'exe']
            },
            {
                id: 'virus_108',
                name: 'SparkPro.exe.rar',
                displayName: 'SparkPro.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['SparkPro', '火花专业版', '病毒', 'exe']
            },
            {
                id: 'virus_109',
                name: 'Sulfoxide.exe.rar',
                displayName: 'Sulfoxide.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['Sulfoxide', '亚砜', '化学', '病毒']
            },
            {
                id: 'virus_110',
                name: 'Sustain Epic.exe.rar',
                displayName: 'Sustain Epic.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['Sustain Epic', '持续史诗', '病毒', 'exe']
            },
            {
                id: 'virus_111',
                name: 'Synaptics.exe.rar',
                displayName: 'Synaptics.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['Synaptics', '突触', '病毒', 'exe']
            },
            {
                id: 'virus_112',
                name: 'SystemKiller.exe.rar',
                displayName: 'SystemKiller.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['SystemKiller', '系统杀手', '病毒', 'exe']
            },
            {
                id: 'virus_113',
                name: 'SystemKiller_x32.exe.rar',
                displayName: 'SystemKiller_x32.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['SystemKiller', 'x32', '32位', '病毒']
            },
            {
                id: 'virus_114',
                name: 'SystemKiller_x64.exe.rar',
                displayName: 'SystemKiller_x64.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['SystemKiller', 'x64', '64位', '病毒']
            },
            {
                id: 'virus_115',
                name: 'Technetium.exe.rar',
                displayName: 'Technetium.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['Technetium', '锝', '化学元素', '病毒']
            },
            {
                id: 'virus_116',
                name: 'Technetium-safety.exe.rar',
                displayName: 'Technetium-safety.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['Technetium', '安全', 'safety', '病毒']
            },
            {
                id: 'virus_117',
                name: 'tendows.exe.rar',
                displayName: 'tendows.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['tendows', '十窗', '病毒', 'exe']
            },
            {
                id: 'virus_118',
                name: 'Tera Bonus.exe.rar',
                displayName: 'Tera Bonus.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['Tera Bonus', '太拉奖励', '病毒', 'exe']
            },
            {
                id: 'virus_119',
                name: 'Tera Bonus-GDIOnly.exe.rar',
                displayName: 'Tera Bonus-GDIOnly.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['Tera Bonus', 'GDIOnly', '病毒', 'exe']
            },
            {
                id: 'virus_120',
                name: 'Termi_1.2.exe.rar',
                displayName: 'Termi_1.2.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['Termi', '1.2', '终端', '病毒']
            },
            // 第5组 (121-150)
            {
                id: 'virus_121',
                name: 'Terminator3.1.exe.rar',
                displayName: 'Terminator3.1.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['Terminator', '终结者', '3.1', '病毒']
            },
            {
                id: 'virus_122',
                name: 'Tetroxidex64.exe.rar',
                displayName: 'Tetroxidex64.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['Tetroxide', '四氧化物', 'x64', '病毒']
            },
            {
                id: 'virus_123',
                name: 'Tetroxidex86.exe.rar',
                displayName: 'Tetroxidex86.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['Tetroxide', '四氧化物', 'x86', '病毒']
            },
            {
                id: 'virus_124',
                name: 'tin.exe.rar',
                displayName: 'tin.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['tin', '锡', '化学元素', '病毒']
            },
            {
                id: 'virus_125',
                name: 'trichloromethane.exe.rar',
                displayName: 'trichloromethane.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['trichloromethane', '三氯甲烷', '化学', '病毒']
            },
            {
                id: 'virus_126',
                name: 'trichloromethane-safety.exe.rar',
                displayName: 'trichloromethane-safety.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['trichloromethane', '安全', 'safety', '病毒']
            },
            {
                id: 'virus_127',
                name: 'Tubejamming.exe.rar',
                displayName: 'Tubejamming.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['Tubejamming', '管阻塞', '病毒', 'exe']
            },
            {
                id: 'virus_128',
                name: 'Undulations.exe.rar',
                displayName: 'Undulations.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['Undulations', '波动', '病毒', 'exe']
            },
            {
                id: 'virus_129',
                name: 'Unfixable.exe.rar',
                displayName: 'Unfixable.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['Unfixable', '无法修复', '病毒', 'exe']
            },
            {
                id: 'virus_130',
                name: 'u某病毒1.1（作者一流）.exe.rar',
                displayName: 'u某病毒1.1（作者一流）.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['u某病毒', '1.1', '作者一流', '病毒']
            },
            {
                id: 'virus_131',
                name: 'VIDAR.exe.rar',
                displayName: 'VIDAR.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['VIDAR', '病毒', 'exe']
            },
            {
                id: 'virus_132',
                name: 'warp.exe.rar',
                displayName: 'warp.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['warp', '扭曲', '病毒', 'exe']
            },
            {
                id: 'virus_133',
                name: 'Wewe_1.3.exe.rar',
                displayName: 'Wewe_1.3.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['Wewe', '1.3', '病毒', 'exe']
            },
            {
                id: 'virus_134',
                name: 'Windows-advanced-Winkiller-NoDisk-NoBOOT-Pro.exe.rar',
                displayName: 'Windows-advanced-Winkiller-NoDisk-NoBOOT-Pro.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['Windows-advanced-Winkiller', 'NoDisk', 'NoBOOT', '病毒']
            },
            {
                id: 'virus_135',
                name: 'WINKILLER.exe.rar',
                displayName: 'WINKILLER.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['WINKILLER', '窗口杀手', '病毒', 'exe']
            },
            {
                id: 'virus_136',
                name: 'WinKiller 2.0.0.2f.exe.rar',
                displayName: 'WinKiller 2.0.0.2f.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['WinKiller', '2.0.0.2f', '病毒', 'exe']
            },
            {
                id: 'virus_137',
                name: 'WinRGBDestructive.exe.rar',
                displayName: 'WinRGBDestructive.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['WinRGBDestructive', 'RGB破坏', '病毒', 'exe']
            },
            {
                id: 'virus_138',
                name: 'YellowSkull 2.0.exe.rar',
                displayName: 'YellowSkull 2.0.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['YellowSkull', '黄骷髅', '2.0', '病毒']
            },
            {
                id: 'virus_139',
                name: 'yesgntgfrf.exe.rar',
                displayName: 'yesgntgfrf.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['yesgntgfrf', '随机名', '病毒', 'exe']
            },
            {
                id: 'virus_140',
                name: 'yesgntgfrf-safety.exe.rar',
                displayName: 'yesgntgfrf-safety.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['yesgntgfrf', '安全', 'safety', '病毒']
            },
            {
                id: 'virus_141',
                name: 'Zoxazolamine.exe.rar',
                displayName: 'Zoxazolamine.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['Zoxazolamine', '佐沙唑胺', '化学', '病毒']
            },
            {
                id: 'virus_142',
                name: '《与雾雨魔理沙一起偷重要的东西》游戏外挂win7版.exe.rar',
                displayName: '《与雾雨魔理沙一起偷重要的东西》游戏外挂win7版.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['与雾雨魔理沙', '游戏外挂', 'win7', '病毒']
            },
            {
                id: 'virus_143',
                name: '《与雾雨魔理沙一起偷重要的东西》游戏外挂win8.x版.exe.rar',
                displayName: '《与雾雨魔理沙一起偷重要的东西》游戏外挂win8.x版.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['与雾雨魔理沙', '游戏外挂', 'win8.x', '病毒']
            },
            {
                id: 'virus_144',
                name: '《与雾雨魔理沙一起偷重要的东西》游戏外挂win10+版.exe.rar',
                displayName: '《与雾雨魔理沙一起偷重要的东西》游戏外挂win10+版.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['与雾雨魔理沙', '游戏外挂', 'win10+', '病毒']
            },
            {
                id: 'virus_145',
                name: '【php.shell病毒】东莞市机电工程学校机房电脑壁纸.jpg.rar',
                displayName: '【php.shell病毒】东莞市机电工程学校机房电脑壁纸.jpg',
                type: '文件',
                category: 'JPG图片文件',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['php.shell病毒', '东莞', '机房壁纸', 'jpg']
            },
            {
                id: 'virus_146',
                name: '【Synaptics】HMCL(2).exe.rar',
                displayName: '【Synaptics】HMCL(2).exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['Synaptics', 'HMCL', '我的世界', '病毒']
            },
            {
                id: 'virus_147',
                name: '奥利给病毒.exe.rar',
                displayName: '奥利给病毒.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['奥利给', '网络用语', '病毒', 'exe']
            },
            {
                id: 'virus_148',
                name: '病名は愛だつた.A.exe.rar',
                displayName: '病名は愛だつた.A.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['病名は愛だつた', '日语', 'A版', '病毒']
            },
            {
                id: 'virus_149',
                name: '病名は愛だつた.B.exe.rar',
                displayName: '病名は愛だつた.B.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['病名は愛だつた', '日语', 'B版', '病毒']
            },
            {
                id: 'virus_150',
                name: '不乖巧的毒.exe.rar',
                displayName: '不乖巧的毒.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['不乖巧', '毒', '病毒', 'exe']
            },
            // 第6组 (151-180)
            {
                id: 'virus_151',
                name: '钉钉(呵呵一笑).exe.rar',
                displayName: '钉钉(呵呵一笑).exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['钉钉', '呵呵一笑', '办公软件', '病毒']
            },
            {
                id: 'virus_152',
                name: '高考成绩查询.exe.rar',
                displayName: '高考成绩查询.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['高考成绩', '查询', '病毒', 'exe']
            },
            {
                id: 'virus_153',
                name: '高能弹窗.exe.rar',
                displayName: '高能弹窗.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['高能', '弹窗', '病毒', 'exe']
            },
            {
                id: 'virus_154',
                name: '黑人抬棺病毒，第七版编译2.0.exe.rar',
                displayName: '黑人抬棺病毒，第七版编译2.0.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['黑人抬棺', '第七版', '2.0', '病毒']
            },
            {
                id: 'virus_155',
                name: '滑稽病毒.exe.rar',
                displayName: '滑稽病毒.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['滑稽', '表情', '病毒', 'exe']
            },
            {
                id: 'virus_156',
                name: '灰鸽子后门木马.exe.rar',
                displayName: '灰鸽子后门木马.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['灰鸽子', '后门木马', '病毒', 'exe']
            },
            {
                id: 'virus_157',
                name: '火绒危险.exe.rar',
                displayName: '火绒危险.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['火绒', '危险', '杀毒软件', '病毒']
            },
            {
                id: 'virus_158',
                name: '金坷垃病毒最终完成版3.0.exe.rar',
                displayName: '金坷垃病毒最终完成版3.0.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['金坷垃', '最终完成版', '3.0', '病毒']
            },
            {
                id: 'virus_159',
                name: '老帝病毒.exe.rar',
                displayName: '老帝病毒.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['老帝', '病毒', 'exe']
            },
            {
                id: 'virus_160',
                name: '卢本伟病毒.exe.rar',
                displayName: '卢本伟病毒.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['卢本伟', '主播', '病毒', 'exe']
            },
            {
                id: 'virus_161',
                name: '迷你世界.exe.rar',
                displayName: '迷你世界.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['迷你世界', '游戏', '病毒', 'exe']
            },
            {
                id: 'virus_162',
                name: '迷你世界超级外挂.exe.rar',
                displayName: '迷你世界超级外挂.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['迷你世界', '超级外挂', '病毒', 'exe']
            },
            {
                id: 'virus_163',
                name: '某科学的超virus.exe.rar',
                displayName: '某科学的超virus.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['某科学的', '超virus', '病毒', 'exe']
            },
            {
                id: 'virus_164',
                name: '潘嘎之交.exe.rar',
                displayName: '潘嘎之交.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['潘嘎之交', '网络梗', '病毒', 'exe']
            },
            {
                id: 'virus_165',
                name: '如何吸旺仔牛奶.exe.rar',
                displayName: '如何吸旺仔牛奶.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['如何吸', '旺仔牛奶', '病毒', 'exe']
            },
            {
                id: 'virus_166',
                name: '赛博灯泡病毒.exe.rar',
                displayName: '赛博灯泡病毒.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['赛博', '灯泡', '病毒', 'exe']
            },
            {
                id: 'virus_167',
                name: '斯大林病毒.exe.rar',
                displayName: '斯大林病毒.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['斯大林', '苏联', '病毒', 'exe']
            },
            {
                id: 'virus_168',
                name: '王境泽病毒.exe.rar',
                displayName: '王境泽病毒.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['王境泽', '真香', '病毒', 'exe']
            },
            {
                id: 'virus_169',
                name: '王境泽病毒(2.0版).exe.rar',
                displayName: '王境泽病毒(2.0版).exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['王境泽', '2.0版', '病毒', 'exe']
            },
            {
                id: 'virus_170',
                name: '喜之郎鬼畜v2.0.exe.rar',
                displayName: '喜之郎鬼畜v2.0.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['喜之郎', '鬼畜', 'v2.0', '病毒']
            },
            {
                id: 'virus_171',
                name: '喜之郎鬼畜病毒v3.0.exe.rar',
                displayName: '喜之郎鬼畜病毒v3.0.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['喜之郎', '鬼畜病毒', 'v3.0', '病毒']
            },
            {
                id: 'virus_172',
                name: '仙女CXK.exe.rar',
                displayName: '仙女CXK.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['仙女', 'CXK', '病毒', 'exe']
            },
            {
                id: 'virus_173',
                name: '印尼宽带病毒.exe.rar',
                displayName: '印尼宽带病毒.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['印尼', '宽带', '病毒', 'exe']
            },
            {
                id: 'virus_174',
                name: '硬件病毒(XP运行).exe.rar',
                displayName: '硬件病毒(XP运行).exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['硬件病毒', 'XP运行', '病毒', 'exe']
            },
            {
                id: 'virus_175',
                name: '俞飞鸿病毒1.4.exe.rar',
                displayName: '俞飞鸿病毒1.4.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['俞飞鸿', '1.4', '病毒', 'exe']
            },
            {
                id: 'virus_176',
                name: '原神.exe.rar',
                displayName: '原神.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['原神', '游戏', '病毒', 'exe']
            },
            {
                id: 'virus_177',
                name: '再见，世界.exe.rar',
                displayName: '再见，世界.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['再见', '世界', '病毒', 'exe']
            },
            {
                id: 'virus_178',
                name: '浙江温州病毒（滑稽制作）.exe.rar',
                displayName: '浙江温州病毒（滑稽制作）.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['浙江温州', '滑稽制作', '病毒', 'exe']
            },
            {
                id: 'virus_179',
                name: '支付宝集福增强工具.exe.rar',
                displayName: '支付宝集福增强工具.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['支付宝', '集福', '增强工具', '病毒']
            },
            {
                id: 'virus_180',
                name: '中华黑豹升级版.exe.rar',
                displayName: '中华黑豹升级版.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['中华黑豹', '升级版', '病毒', 'exe']
            },
            // 第7组 (181-187)
            {
                id: 'virus_181',
                name: '中华黑豹增强版.exe.rar',
                displayName: '中华黑豹增强版.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['中华黑豹', '增强版', '病毒', 'exe']
            },
            {
                id: 'virus_182',
                name: 'ë.exe.rar',
                displayName: 'ë.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['ë', '拉丁字母', '病毒', 'exe']
            },
            {
                id: 'virus_183',
                name: 'ß.exe.rar',
                displayName: 'ß.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['ß', '德语字母', '病毒', 'exe']
            },
            {
                id: 'virus_184',
                name: 'ü.exe.rar',
                displayName: 'ü.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['ü', '德语字母', '病毒', 'exe']
            },
            {
                id: 'virus_185',
                name: 'π.exe.rar',
                displayName: 'π.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['π', '圆周率', '数学', '病毒']
            },
            {
                id: 'virus_186',
                name: 'ю.exe.rar',
                displayName: 'ю.exe',
                type: '文件',
                category: 'EXE应用程序',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['ю', '俄语字母', '病毒', 'exe']
            },
            {
                id: 'virus_187',
                name: '点开必看.txt',
                displayName: '点开必看.txt',
                type: '文件',
                category: '文本文件',
                size: '未知',
                path: 'windows-virus.html',
                icon: 'file',
                isPrivate: false,
                keywords: ['点开必看', '说明', 'txt', '文本']
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
                        (item.keywords && item.keywords.some(keyword => keyword.toLowerCase().includes(query)));
                    
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