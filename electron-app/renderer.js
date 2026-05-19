// 渲染进程脚本
const { ipcRenderer, shell } = require('electron');

// 全局状态
let supportedModels = {};
let currentConfig = {
  selectedProvider: '',
  apiKeys: {},
  baseUrls: {},
  selectedModels: {}
};
let isServiceRunning = false;

// 初始化
async function init() {
  try {
    // 获取支持的模型
    supportedModels = await ipcRenderer.invoke('get-supported-models');
    
    // 加载配置
    currentConfig = await ipcRenderer.invoke('load-config');
    
    // 渲染提供商卡片
    renderProviderCards();
    
    // 如果有已保存的配置，显示它
    if (currentConfig.selectedProvider) {
      selectProvider(currentConfig.selectedProvider);
      updateCurrentConfigDisplay();
    }
    
    addLog('配置加载完成', 'info');
  } catch (error) {
    addLog(`初始化失败: ${error.message}`, 'error');
  }
}

// 渲染提供商卡片
function renderProviderCards() {
  const grid = document.getElementById('providerGrid');
  grid.innerHTML = '';
  
  Object.entries(supportedModels).forEach(([key, provider]) => {
    const card = document.createElement('div');
    card.className = 'provider-card';
    card.dataset.provider = key;
    card.onclick = () => selectProvider(key);
    
    let tag = '';
    if (key === 'ollama') {
      tag = '<span class="tag local">本地</span>';
    } else if (['baidu', 'alibaba', 'zhipu', 'moonshot', 'deepseek'].includes(key)) {
      tag = '<span class="tag china">国产</span>';
    }
    
    card.innerHTML = `
      <div class="icon">${provider.icon}</div>
      <div class="name">${provider.name}</div>
      ${tag}
    `;
    
    grid.appendChild(card);
  });
}

// 选择提供商
function selectProvider(providerKey) {
  currentConfig.selectedProvider = providerKey;
  
  // 更新卡片样式
  document.querySelectorAll('.provider-card').forEach(card => {
    card.classList.toggle('active', card.dataset.provider === providerKey);
  });
  
  // 显示配置区域
  const configSection = document.getElementById('configSection');
  configSection.classList.remove('hidden');
  
  const provider = supportedModels[providerKey];
  
  // 更新模型选择
  const modelSelect = document.getElementById('modelSelect');
  modelSelect.innerHTML = provider.models.map(model => 
    `<option value="${model}" ${currentConfig.selectedModels[providerKey] === model ? 'selected' : ''}>${model}</option>`
  ).join('');
  
  // 显示/隐藏API Key输入
  const apiKeyGroup = document.getElementById('apiKeyGroup');
  if (provider.requiresKey) {
    apiKeyGroup.classList.remove('hidden');
    document.getElementById('apiKeyInput').value = currentConfig.apiKeys[providerKey] || '';
  } else {
    apiKeyGroup.classList.add('hidden');
  }
  
  // 设置Base URL
  document.getElementById('baseUrlInput').value = currentConfig.baseUrls[providerKey] || '';
  
  // 清除测试结果
  document.getElementById('testResult').innerHTML = '';
}

// 测试连接
async function testConnection() {
  const testBtn = document.getElementById('testBtn');
  const resultDiv = document.getElementById('testResult');
  
  // 更新配置对象
  updateConfigFromUI();
  
  testBtn.disabled = true;
  testBtn.innerHTML = '<span class="loading"></span> 测试中...';
  resultDiv.innerHTML = '';
  
  try {
    addLog(`正在测试 ${supportedModels[currentConfig.selectedProvider].name} 连接...`, 'info');
    
    const result = await ipcRenderer.invoke('test-connection', currentConfig);
    
    if (result.success) {
      resultDiv.innerHTML = `<div class="test-result success">✅ 连接成功！${result.message || ''}</div>`;
      addLog('连接测试成功', 'success');
    } else {
      resultDiv.innerHTML = `<div class="test-result error">❌ ${result.error}</div>`;
      addLog(`连接测试失败: ${result.error}`, 'error');
    }
  } catch (error) {
    resultDiv.innerHTML = `<div class="test-result error">❌ 测试出错: ${error.message}</div>`;
    addLog(`测试出错: ${error.message}`, 'error');
  } finally {
    testBtn.disabled = false;
    testBtn.innerHTML = '🔗 测试连接';
  }
}

// 保存配置
async function saveConfiguration() {
  const saveBtn = document.getElementById('saveBtn');
  
  // 更新配置对象
  updateConfigFromUI();
  
  saveBtn.disabled = true;
  saveBtn.innerHTML = '<span class="loading"></span> 保存中...';
  
  try {
    const success = await ipcRenderer.invoke('save-config', currentConfig);
    
    if (success) {
      addLog('配置保存成功', 'success');
      updateCurrentConfigDisplay();
      
      // 显示成功提示
      const resultDiv = document.getElementById('testResult');
      resultDiv.innerHTML = `<div class="test-result success">✅ 配置已保存！</div>`;
      
      setTimeout(() => {
        resultDiv.innerHTML = '';
      }, 3000);
    } else {
      addLog('配置保存失败', 'error');
    }
  } catch (error) {
    addLog(`保存出错: ${error.message}`, 'error');
  } finally {
    saveBtn.disabled = false;
    saveBtn.innerHTML = '💾 保存配置';
  }
}

// 从UI更新配置对象
function updateConfigFromUI() {
  const provider = currentConfig.selectedProvider;
  
  currentConfig.selectedModels[provider] = document.getElementById('modelSelect').value;
  
  if (supportedModels[provider].requiresKey) {
    currentConfig.apiKeys[provider] = document.getElementById('apiKeyInput').value.trim();
  }
  
  const baseUrl = document.getElementById('baseUrlInput').value.trim();
  if (baseUrl) {
    currentConfig.baseUrls[provider] = baseUrl;
  } else {
    delete currentConfig.baseUrls[provider];
  }
}

// 更新当前配置显示
function updateCurrentConfigDisplay() {
  const display = document.getElementById('currentConfig');
  
  if (!currentConfig.selectedProvider) {
    display.textContent = '未配置';
    return;
  }
  
  const provider = supportedModels[currentConfig.selectedProvider];
  const model = currentConfig.selectedModels[currentConfig.selectedProvider] || provider.models[0];
  const hasKey = currentConfig.apiKeys[currentConfig.selectedProvider] ? '已设置' : '未设置';
  
  display.innerHTML = `
    <strong>提供商:</strong> ${provider.name}<br>
    <strong>模型:</strong> ${model}<br>
    <strong>API Key:</strong> ${provider.requiresKey ? hasKey : '不需要'}
  `;
}

// 启动服务
async function startService() {
  const startBtn = document.getElementById('startBtn');
  const stopBtn = document.getElementById('stopBtn');
  const openWebBtn = document.getElementById('openWebBtn');
  
  if (!currentConfig.selectedProvider) {
    addLog('请先选择并配置模型提供商', 'error');
    return;
  }
  
  startBtn.disabled = true;
  startBtn.innerHTML = '<span class="loading"></span> 启动中...';
  
  try {
    addLog('正在启动后端服务...', 'info');
    
    const result = await ipcRenderer.invoke('start-backend', currentConfig);
    
    if (result.success) {
      isServiceRunning = true;
      updateStatusUI(true);
      addLog('后端服务启动成功', 'success');
      
      // 启用停止按钮和打开Web按钮
      stopBtn.disabled = false;
      openWebBtn.disabled = false;
    } else {
      addLog(`启动失败: ${result.error}`, 'error');
      startBtn.disabled = false;
      startBtn.innerHTML = '▶️ 启动服务';
    }
  } catch (error) {
    addLog(`启动出错: ${error.message}`, 'error');
    startBtn.disabled = false;
    startBtn.innerHTML = '▶️ 启动服务';
  }
}

// 停止服务
async function stopService() {
  const startBtn = document.getElementById('startBtn');
  const stopBtn = document.getElementById('stopBtn');
  const openWebBtn = document.getElementById('openWebBtn');
  
  stopBtn.disabled = true;
  stopBtn.innerHTML = '<span class="loading"></span> 停止中...';
  
  try {
    addLog('正在停止后端服务...', 'info');
    
    await ipcRenderer.invoke('stop-backend');
    
    isServiceRunning = false;
    updateStatusUI(false);
    addLog('后端服务已停止', 'info');
    
    // 重置按钮状态
    startBtn.disabled = false;
    startBtn.innerHTML = '▶️ 启动服务';
    stopBtn.disabled = true;
    stopBtn.innerHTML = '⏹️ 停止服务';
    openWebBtn.disabled = true;
  } catch (error) {
    addLog(`停止出错: ${error.message}`, 'error');
    stopBtn.disabled = false;
    stopBtn.innerHTML = '⏹️ 停止服务';
  }
}

// 更新状态UI
function updateStatusUI(running) {
  const indicator = document.getElementById('statusIndicator');
  const statusText = document.getElementById('statusText');
  const startBtn = document.getElementById('startBtn');
  
  if (running) {
    indicator.classList.remove('stopped');
    indicator.classList.add('running');
    statusText.textContent = '服务运行中 (http://localhost:8000)';
    startBtn.innerHTML = '✅ 服务已启动';
  } else {
    indicator.classList.remove('running');
    indicator.classList.add('stopped');
    statusText.textContent = '服务未启动';
    startBtn.innerHTML = '▶️ 启动服务';
  }
}

// 打开Web界面
function openWebInterface() {
  shell.openExternal('http://localhost:8000');
  addLog('已打开 Web 界面', 'info');
}

// 添加日志
function addLog(message, type = 'info') {
  const container = document.getElementById('logsContainer');
  const time = new Date().toLocaleTimeString('zh-CN');
  
  const entry = document.createElement('div');
  entry.className = 'log-entry';
  entry.innerHTML = `
    <span class="log-time">[${time}]</span>
    <span class="log-${type}">${message}</span>
  `;
  
  container.appendChild(entry);
  container.scrollTop = container.scrollHeight;
  
  // 限制日志数量
  while (container.children.length > 50) {
    container.removeChild(container.firstChild);
  }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', init);
