const { app, BrowserWindow, ipcMain, dialog, shell } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');
const os = require('os');

// 配置文件路径
const configPath = path.join(os.homedir(), '.agentorchestra', 'config.json');
const configDir = path.dirname(configPath);

// 确保配置目录存在
if (!fs.existsSync(configDir)) {
  fs.mkdirSync(configDir, { recursive: true });
}

let mainWindow;
let backendProcess = null;

// 支持的模型配置
const SUPPORTED_MODELS = {
  openai: {
    name: 'OpenAI',
    icon: '🤖',
    models: ['gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo', 'gpt-3.5-turbo'],
    baseUrl: 'https://api.openai.com/v1',
    requiresKey: true
  },
  anthropic: {
    name: 'Anthropic Claude',
    icon: '🧠',
    models: ['claude-3-5-sonnet-20241022', 'claude-3-opus-20240229', 'claude-3-sonnet-20240229', 'claude-3-haiku-20240307'],
    baseUrl: 'https://api.anthropic.com',
    requiresKey: true
  },
  ollama: {
    name: 'Ollama (本地)',
    icon: '🦙',
    models: ['llama3.2', 'llama3.1', 'mistral', 'qwen2.5', 'phi4', 'deepseek-r1'],
    baseUrl: 'http://localhost:11434',
    requiresKey: false
  },
  // 国产大模型
  baidu: {
    name: '百度文心一言',
    icon: '🇨🇳',
    models: ['ERNIE-Bot-4', 'ERNIE-Bot', 'ERNIE-Bot-turbo', 'ERNIE-Speed'],
    baseUrl: 'https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat',
    requiresKey: true
  },
  alibaba: {
    name: '阿里通义千问',
    icon: '🇨🇳',
    models: ['qwen-max', 'qwen-plus', 'qwen-turbo', 'qwen-long'],
    baseUrl: 'https://dashscope.aliyuncs.com/api/v1',
    requiresKey: true
  },
  zhipu: {
    name: '智谱AI (GLM)',
    icon: '🇨🇳',
    models: ['glm-4', 'glm-4-plus', 'glm-4-flash', 'glm-4v'],
    baseUrl: 'https://open.bigmodel.cn/api/paas/v4',
    requiresKey: true
  },
  moonshot: {
    name: '月之暗面 (Kimi)',
    icon: '🇨🇳',
    models: ['moonshot-v1-8k', 'moonshot-v1-32k', 'moonshot-v1-128k'],
    baseUrl: 'https://api.moonshot.cn/v1',
    requiresKey: true
  },
  deepseek: {
    name: 'DeepSeek',
    icon: '🇨🇳',
    models: ['deepseek-chat', 'deepseek-reasoner'],
    baseUrl: 'https://api.deepseek.com/v1',
    requiresKey: true
  }
};

// 创建主窗口
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 900,
    minHeight: 600,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      enableRemoteModule: true
    },
    icon: path.join(__dirname, 'assets', 'icon.png'),
    show: false,
    titleBarStyle: 'default'
  });

  // 加载本地HTML文件
  mainWindow.loadFile('index.html');

  // 窗口准备好后显示
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
    stopBackend();
  });
}

// 读取配置
function loadConfig() {
  try {
    if (fs.existsSync(configPath)) {
      const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
      return config;
    }
  } catch (error) {
    console.error('加载配置失败:', error);
  }
  return {
    selectedProvider: 'openai',
    apiKeys: {},
    baseUrls: {},
    selectedModels: {}
  };
}

// 保存配置
function saveConfig(config) {
  try {
    fs.writeFileSync(configPath, JSON.stringify(config, null, 2));
    return true;
  } catch (error) {
    console.error('保存配置失败:', error);
    return false;
  }
}

// 启动后端服务
async function startBackend(config) {
  if (backendProcess) {
    console.log('后端服务已在运行');
    return true;
  }

  return new Promise((resolve, reject) => {
    const backendPath = path.join(__dirname, '..', 'backend');
    const pythonCmd = process.platform === 'win32' ? 'python' : 'python3';
    
    // 设置环境变量
    const env = {
      ...process.env,
      LLM_PROVIDER: config.selectedProvider,
      OPENAI_API_KEY: config.apiKeys.openai || '',
      ANTHROPIC_API_KEY: config.apiKeys.anthropic || '',
      BAIDU_API_KEY: config.apiKeys.baidu || '',
      ALIBABA_API_KEY: config.apiKeys.alibaba || '',
      ZHIPU_API_KEY: config.apiKeys.zhipu || '',
      MOONSHOT_API_KEY: config.apiKeys.moonshot || '',
      DEEPSEEK_API_KEY: config.apiKeys.deepseek || '',
      OLLAMA_BASE_URL: config.baseUrls.ollama || 'http://localhost:11434',
      SELECTED_MODEL: config.selectedModels[config.selectedProvider] || ''
    };

    console.log('启动后端服务...');
    
    backendProcess = spawn(pythonCmd, ['-m', 'uvicorn', 'app.main:app', '--host', '0.0.0.0', '--port', '8000'], {
      cwd: backendPath,
      env: env,
      stdio: 'pipe'
    });

    let started = false;

    backendProcess.stdout.on('data', (data) => {
      console.log(`后端输出: ${data}`);
      if (data.toString().includes('Uvicorn running')) {
        started = true;
        resolve(true);
      }
    });

    backendProcess.stderr.on('data', (data) => {
      console.error(`后端错误: ${data}`);
    });

    backendProcess.on('error', (error) => {
      console.error('启动后端失败:', error);
      if (!started) {
        reject(error);
      }
    });

    backendProcess.on('close', (code) => {
      console.log(`后端进程退出，代码: ${code}`);
      backendProcess = null;
    });

    // 超时处理
    setTimeout(() => {
      if (!started) {
        reject(new Error('启动后端服务超时'));
      }
    }, 30000);
  });
}

// 停止后端服务
function stopBackend() {
  if (backendProcess) {
    console.log('停止后端服务...');
    if (process.platform === 'win32') {
      spawn('taskkill', ['/pid', backendProcess.pid, '/f', '/t']);
    } else {
      backendProcess.kill('SIGTERM');
    }
    backendProcess = null;
  }
}

// IPC 处理程序

// 获取支持的模型列表
ipcMain.handle('get-supported-models', () => {
  return SUPPORTED_MODELS;
});

// 加载配置
ipcMain.handle('load-config', () => {
  return loadConfig();
});

// 保存配置
ipcMain.handle('save-config', (event, config) => {
  return saveConfig(config);
});

// 启动后端
ipcMain.handle('start-backend', async (event, config) => {
  try {
    await startBackend(config);
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

// 停止后端
ipcMain.handle('stop-backend', () => {
  stopBackend();
  return { success: true };
});

// 测试API连接
ipcMain.handle('test-connection', async (event, config) => {
  try {
    const provider = SUPPORTED_MODELS[config.selectedProvider];
    if (!provider) {
      return { success: false, error: '未知的提供商' };
    }

    // 构建测试请求的URL
    let testUrl = config.baseUrls[config.selectedProvider] || provider.baseUrl;
    
    // 根据不同提供商构建测试请求
    const fetch = (await import('node-fetch')).default;
    
    let headers = {
      'Content-Type': 'application/json'
    };

    // 添加认证头
    if (provider.requiresKey && config.apiKeys[config.selectedProvider]) {
      if (config.selectedProvider === 'anthropic') {
        headers['x-api-key'] = config.apiKeys[config.selectedProvider];
      } else if (config.selectedProvider === 'baidu') {
        // 百度需要特殊处理
        headers['Authorization'] = `Bearer ${config.apiKeys[config.selectedProvider]}`;
      } else {
        headers['Authorization'] = `Bearer ${config.apiKeys[config.selectedProvider]}`;
      }
    }

    // 简单的连接测试
    let response;
    try {
      if (config.selectedProvider === 'ollama') {
        // 测试Ollama连接
        response = await fetch(`${testUrl}/api/tags`, {
          method: 'GET',
          timeout: 5000
        });
      } else {
        // 其他API简单测试
        response = await fetch(testUrl, {
          method: 'GET',
          headers: headers,
          timeout: 10000
        });
      }
      
      if (response.ok || response.status === 401 || response.status === 403) {
        // 401/403 表示连接成功，只是需要认证
        return { success: true, message: '连接成功' };
      } else {
        return { success: false, error: `HTTP ${response.status}: ${response.statusText}` };
      }
    } catch (fetchError) {
      return { success: false, error: `连接失败: ${fetchError.message}` };
    }
  } catch (error) {
    return { success: false, error: error.message };
  }
});

// 打开外部链接
ipcMain.handle('open-external', (event, url) => {
  shell.openExternal(url);
});

// 应用就绪
app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  stopBackend();
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

// 应用退出前清理
app.on('before-quit', () => {
  stopBackend();
});
