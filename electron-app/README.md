# AgentOrchestra 桌面版

AI 多智能体协作平台桌面应用程序，支持多种大语言模型配置。

## 功能特性

- 🎼 **多智能体协作** - 5个专业智能体协同工作
- 🤖 **多模型支持** - 支持 8+ 种大语言模型
  - OpenAI (GPT-4, GPT-3.5)
  - Anthropic Claude
  - Ollama (本地部署)
  - 百度文心一言
  - 阿里通义千问
  - 智谱AI (GLM)
  - 月之暗面 Kimi
  - DeepSeek
- ⚙️ **可视化配置** - 图形界面配置API密钥和模型参数
- 🔗 **连接测试** - 一键测试API连接状态
- 🖥️ **集成Web界面** - 启动后可直接打开Web管理界面

## 系统要求

- Windows 10/11 (64位)
- Python 3.9+ (用于运行后端服务)
- 4GB+ 内存

## 使用方法

### 1. 启动应用

双击运行 `AgentOrchestra.exe`

### 2. 配置模型

1. 在左侧选择您想要使用的AI模型提供商
2. 选择具体的模型版本
3. 输入API Key（本地Ollama不需要）
4. 点击"测试连接"验证配置
5. 点击"保存配置"

### 3. 启动服务

1. 点击"启动服务"按钮启动后端服务
2. 等待服务状态变为"服务运行中"
3. 点击"打开 Web 界面"访问管理界面

### 4. 使用Web界面

在浏览器中您可以：
- 创建和管理任务
- 与智能体对话
- 查看工作流执行状态
- 配置智能体参数

## 配置文件

配置文件保存在用户目录下：
```
%USERPROFILE%\.agentorchestra\config.json
```

## 支持的模型

### 国际模型
- **OpenAI** - gpt-4o, gpt-4o-mini, gpt-4-turbo, gpt-3.5-turbo
- **Anthropic Claude** - claude-3-5-sonnet, claude-3-opus, claude-3-haiku

### 本地模型
- **Ollama** - llama3.2, llama3.1, mistral, qwen2.5, phi4, deepseek-r1

### 国产模型
- **百度文心一言** - ERNIE-Bot-4, ERNIE-Bot, ERNIE-Bot-turbo
- **阿里通义千问** - qwen-max, qwen-plus, qwen-turbo
- **智谱AI** - glm-4, glm-4-plus, glm-4-flash
- **月之暗面 Kimi** - moonshot-v1-8k, moonshot-v1-32k, moonshot-v1-128k
- **DeepSeek** - deepseek-chat, deepseek-reasoner

## 开发说明

### 项目结构
```
electron-app/
├── main.js          # 主进程
├── index.html       # 配置界面
├── renderer.js      # 渲染进程
├── assets/          # 图标资源
└── package.json     # 项目配置
```

### 打包命令
```bash
# 开发模式运行
npm start

# 打包Windows应用
npm run dist
```

## 技术栈

- **Electron** - 桌面应用框架
- **Node.js** - 后端服务管理
- **Python/FastAPI** - AI后端服务
- **HTML/CSS/JavaScript** - 配置界面

## 许可证

MIT License

## 项目链接

- GitHub: https://github.com/yourusername/AgentOrchestra
- 文档: https://github.com/yourusername/AgentOrchestra#readme
