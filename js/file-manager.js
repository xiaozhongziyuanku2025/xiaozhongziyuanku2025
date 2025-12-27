// 文件管理系统
class FileManager {
    constructor() {
        this.files = [];
        this.categories = new Set();
        this.init();
    }
    
    init() {
        console.log('文件管理器初始化完成');
        this.loadSampleData();
    }
    
    loadSampleData() {
        this.files = [
            {
                id: 'file_001',
                name: '000.exe',
                displayName: '000.exe',
                filename: '000.exe.rar',
                size: '111 KB',
                type: 'EXE应用程序',
                category: 'Windows病毒库',
                path: 'Windows病毒库/000.exe.rar',
                description: 'Windows病毒样本',
                uploadDate: '2024-01-01',
                tags: ['病毒', 'Windows', '样本']
            }
        ];
        
        this.categories.add('Windows病毒库');
        this.categories.add('私密文件夹');
    }
    
    getAllFiles() {
        return this.files;
    }
    
    getFilesByCategory(category) {
        return this.files.filter(file => file.category === category);
    }
    
    getAllCategories() {
        return Array.from(this.categories);
    }
    
    searchFiles(keyword) {
        const searchTerm = keyword.toLowerCase();
        return this.files.filter(file => {
            return file.name.toLowerCase().includes(searchTerm) ||
                   file.displayName.toLowerCase().includes(searchTerm) ||
                   file.description.toLowerCase().includes(searchTerm) ||
                   file.tags.some(tag => tag.toLowerCase().includes(searchTerm));
        });
    }
    
    addFile(fileData) {
        const newFile = {
            id: 'file_' + (this.files.length + 1).toString().padStart(3, '0'),
            ...fileData
        };
        
        this.files.push(newFile);
        
        if (fileData.category) {
            this.categories.add(fileData.category);
        }
        
        console.log('文件添加成功:', newFile);
        return newFile;
    }
    
    getFileDetails(fileId) {
        return this.files.find(file => file.id === fileId) || null;
    }
}

const fileManager = new FileManager();
window.FileManager = FileManager;
window.fileManager = fileManager;
