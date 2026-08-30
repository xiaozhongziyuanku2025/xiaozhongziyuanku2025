const fs = require('fs');
const path = require('path');

// 解码 Base64 文件名（URL-safe）
function decodeBase64FileName(encoded) {
    if (!encoded) return encoded;
    let base64 = encoded.replace(/-/g, '+').replace(/_/g, '/');
    while (base64.length % 4) base64 += '=';
    try {
        return decodeURIComponent(escape(atob(base64)));
    } catch {
        return encoded;
    }
}

// 读取 assets.json（由工作流先下载）
const assetsPath = path.join(__dirname, '../assets.json');
if (!fs.existsSync(assetsPath)) {
    console.error('❌ assets.json 不存在，请先下载 Release assets');
    process.exit(1);
}

const assets = JSON.parse(fs.readFileSync(assetsPath, 'utf8'));

// 构建 files 数组
const files = assets.map(asset => {
    const decoded = decodeBase64FileName(asset.name);
    const sizeMB = (asset.size / 1024 / 1024).toFixed(1);
    return {
        id: 'file_' + asset.id,
        name: asset.name,
        displayName: decoded,
        type: '文件',
        category: 'EXE应用程序',
        size: sizeMB + ' MB',
        path: 'windows-virus.html',
        icon: 'file',
        isPrivate: false,
        keywords: decoded.split(/[._\- ]/).filter(w => w.length > 2)
    };
});

// 固定的文件夹数据
const folders = [
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

const searchIndex = { files, folders };
fs.writeFileSync('search-index.json', JSON.stringify(searchIndex, null, 2));
console.log('✅ search-index.json 已生成，共 ' + files.length + ' 个文件，' + folders.length + ' 个文件夹');
