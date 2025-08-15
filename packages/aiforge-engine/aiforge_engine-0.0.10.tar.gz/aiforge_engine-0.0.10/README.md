# 🚀 AIForge - 智能意图自适应执行引擎  
  
<div align="center">  
  
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/) [![Textual](https://img.shields.io/badge/Textual-4.0.0+%20-purple)](https://textual.textualize.io/) [![FastAPI](https://img.shields.io/badge/FastAPI-0.116.1+%20-red)](https://fastapi.tiangolo.com/) [![SentenceTransformers](https://img.shields.io/badge/SentenceTransformers-5.0.0+%20-pink)](https://www.SBERT.net/)  
[![PyPI version](https://badge.fury.io/py/aiforge-engine.svg?v=10)](https://badge.fury.io/py/aiforge-engine) [![Downloads](https://pepy.tech/badge/aiforge-engine?v=10)](https://pepy.tech/project/aiforge-engine) [![AI Powered](https://img.shields.io/badge/AI-Powered-ff69b4.svg)](#) [![License](https://img.shields.io/badge/license-Apache%202.0-yellow)](./LICENSE) [![Stars](https://img.shields.io/github/stars/iniwap/AIForge?style=social)](https://github.com/iniwap/AIForge)  
[![Development Status](https://img.shields.io/badge/status-alpha-orange.svg)](https://github.com/iniwap/AIForge) [![Development Status](https://img.shields.io/badge/development-active-brightgreen.svg)](https://github.com/iniwap/AIForge)  
  
**将自然语言指令转化为可执行代码的AI驱动自动化引擎**  
  
[🚀 快速开始](#-快速开始) • [🧠 核心功能](#-核心功能) • [⚡ 联系支持](#-联系与支持) • [🌐 应用场景](#-应用场景)  
  
</div>  
  
---  
  
## 🎯 什么是 AIForge？    
> 🚧 **项目状态**: 目前处于全力开发阶段，版本更新比较频繁，敬请关注。 

AIForge 是一个**智能执行引擎**，它消除了自然语言指令与代码执行之间的壁垒。通过先进的指令分析和自适应执行架构，AIForge 提供：  
  
- 🧠 **深度理解** - 多维度指令解析，精准捕获意图  
- ⚡ **即时执行** - 快速代码生成，实时环境交互    
- 🔮 **智能缓存** - 基于语义相似性的智能代码复用  
- 🌊 **自我进化** - 持续学习优化，错误自愈能力  
- 🎭 **多提供商** - AI模型和提供商的无缝切换  
 
> **核心哲学**: *Thought → Code → Reality* - 让思维直接驱动现实世界  

![LOGO](https://raw.githubusercontent.com/iniwap/AIForge/main/logo.jpg)  

## ✨ 核心功能  
  
### 🏗️ 多界面架构  
- **CLI接口** - 直接执行的命令行工具  
- **Python API** - 应用程序的编程集成  
- **Web API** - 基于FastAPI的REST接口  
- **终端GUI** - 交互式文本用户界面  
  
### 🤖 LLM提供商支持  
- **OpenAI** - GPT模型集成  
- **DeepSeek** - 经济高效的AI提供商  
- **OpenRouter** - 多模型访问平台  
- **Ollama** - 本地模型执行  
  
### 🔧 高级执行管理  
- **语义缓存** - 基于指令相似性的智能代码复用  
- **模板系统** - 领域特定的执行模板  
- **搜索集成** - 多引擎搜索能力（百度、Bing、360、搜狗），支持SearXNG集成
- **内容生成** - 专业的内容创建工作流  

### 🌍 多语言支持  
- **全球化指令处理** - 支持12种主要语言的自然语言指令识别  
- **本地化关键词** - 中文、英文、阿拉伯语、德语、西班牙语、法语、印地语、日语、韩语、葡萄牙语、俄语、越南语  
- **智能语言检测** - 自动识别用户指令语言并匹配相应的关键词库  
- **跨语言兼容** - 保持英文关键词通用性的同时提供本地化体验

### 🛡️ 企业级功能  
- **Docker部署** - 同时支持两种部署方式
- **进度跟踪** - 实时执行状态指示器  
- **错误处理** - 全面的异常管理和重试逻辑  
- **配置管理** - 灵活的TOML配置系统  

## 🔐 企业级安全特性  
AIForge提供多层安全保障，确保AI代码安全执行：  

- **沙盒隔离**：进程级隔离执行，完整资源限制  
- **网络安全**：四级策略控制，智能域名过滤    
- **代码分析**：危险模式检测，安全模块导入  
- **统一中间件**：可扩展的安全验证框架

## 🚀 快速开始
    
### 安装部署
    
- 非Docker模式  
```bash  
pip install aiforge-engine    
  
# 包含可选依赖    
pip install aiforge-engine[all]  # 所有功能    
pip install aiforge-engine[gui]  # 终端GUI支持    
pip install aiforge-engine[web]  # Web API支持    
```  
  
- Docker模式  
```bash    
# 1. 安装 AIForge（包含 web 依赖）  
pip install aiforge-engine[web]  
  
# 2. 设置 API 密钥    
echo "OPENROUTER_API_KEY=your-api-key" > .env    
    
# 3. 一键启动    
aiforge-docker start    
    
# 4. 开发模式（热重载）   
aiforge-docker start --dev  

# 5. 源码模式执行时（默认英文）
$env:AIFORGE_LOCALE="zh"; ./aiforge-docker.bat start --dev  # win

./aiforge-docker.sh start --dev  # linux/unix/mac

# 6. 集成SearXNG
aiforge-docker start --dev --searxng

# 7. 查看帮助
$env:AIFORGE_LOCALE="zh"; ./aiforge-docker.bat --help
```  
  
### 基础使用 
- 非Docker模式   
```python  
from aiforge import AIForgeEngine    
  
# 使用API密钥快速开始    
forge = AIForgeEngine(api_key="your-openrouter-apikey")    
  
# 执行自然语言指令    
result = forge("搜索全球股市最新趋势并分析写一篇投资建议")    
print(result)    
```    
  
- Docker模式  
```bash    
# CLI 直接使用    
aiforge "搜索股市趋势并分析"    
    
# 指定提供商     
aiforge --provider deepseek "分析数据"   
```  

### 高级配置  

- 高级参数传递
```python
# 提供商特定配置  
forge = AIForgeEngine(  
    api_key="your-deepseek-key",  
    provider="deepseek",
    locale="en", # ar|de|en|es|fr|hi|ja|ko|pt|ru|vi|zh
    max_rounds=5,
)  

# 复杂任务执行  
result = forge.run(  
    "构建实时数据监控系统",  
    system_prompt="你是一位高级软件架构师"  
)  
```
  
### 配置文件设置  
  
    # aiforge.toml  
    workdir = "aiforge_work"  
    max_tokens = 4096  
    max_rounds = 5  
    default_llm_provider = "openrouter"  
  
    [llm.openrouter]  
    type = "openai"  
    model = "deepseek/deepseek-chat-v3-0324:free"  
    api_key = "your-key"  
    base_url = "https://openrouter.ai/api/v1"  
    timeout = 30  
    max_tokens = 8192  
  
    # 从配置文件加载  
    forge = AIForgeEngine(config_file="aiforge.toml")  
  
## 🎭 应用场景  
  
### 💼 商业智能  
- **市场分析** - 实时数据挖掘与趋势预测  
- **风险评估** - 多维度风险模型构建  
- **决策支持** - 数据驱动的智能决策引擎  
  
### 🔬 研究与开发  
- **数据科学** - 自动化实验设计与分析  
- **模型训练** - 智能超参数优化  
- **研究辅助** - 数据可视化与展示  
  
### 🛠️ 开发加速  
- **原型验证** - 快速MVP构建  
- **API集成** - 智能接口适配  
- **DevOps自动化** - 系统监控与维护  
  
### 🎨 创意实现  
- **内容生成** - 多媒体内容智能创作  
- **数据艺术** - 将数据转化为视觉艺术  
- **交互设计** - 智能UI/UX原型生成  
  
## 🌟 为什么选择 AIForge？  
  
| 特性 | 传统解决方案 | AIForge |  
|------|-------------|---------|  
| 学习曲线 | 数周到数月 | 几分钟上手 |  
| 开发效率 | 线性增长 | 指数级提升 |  
| 错误处理 | 手动调试 | 自动错误恢复 |  
| 可扩展性 | 有限 | 无限可能 |  
| 智能程度 | 静态规则 | 动态学习 |  
  
## 🔮 技术前瞻  
  
AIForge 不仅是工具，更是通往**认知计算时代**的桥梁：  
  
- 🧠 **神经符号融合** - 结合符号推理与神经网络  
- 🌊 **流式思维** - 实时思维流的捕获与执行  
- 🎯 **意图预测** - 基于上下文的需求预判  
- 🔄 **自我进化** - 持续学习的智能体系统  

## 🤝 开发与贡献  
  
    # 开发者设置  
    git clone https://github.com/iniwap/AIForge.git  
    cd AIForge  
    pip install -e ".[dev]"  
  
    # 运行测试  
    pytest tests/  
  
## 📞 联系与支持  
  
- 🌐 **官网**: [aiforge.dev](https://iniwap.github.io/AIForge)  
- 💬 **社区**: [Discord](https://discord.gg/Vp35uSBsrw)  
- 📧 **联系**: iniwaper@gmail.com  
- 🐦 **动态**: [@AIForge](https://twitter.com/iafun_tipixel)  
- 📦 **PyPI**: [aiforge-engine](https://pypi.org/project/aiforge-engine/)  
  
---  
  
<div align="center">  
  
**🌟 重新定义可能性的边界 🌟**  
  
*AIForge - 智能与执行的完美结合*  
  
[立即开始](https://pypi.org/project/aiforge-engine/) | [查看文档](https://iniwap.github.io/AIForge) | [加入社区](https://discord.gg/Vp35uSBsrw)  
  [English](README_EN.md) | [中文](README.md)

</div>