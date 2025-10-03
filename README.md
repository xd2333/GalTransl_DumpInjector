# GalTransl DumpInjector - 重构版本

[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](https://github.com/your-repo/GalTransl_DumpInjector)
[![Python](https://img.shields.io/badge/python-3.7+-green.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)

GalTransl DumpInjector 是一个用于游戏翻译文本提取和注入的GUI工具。本项目是对原版单体应用的完全重构，采用模块化架构提高可维护性和可扩展性。

## ✨ 特性

### 🔧 三模式支持
- **VNTextPatch模式** - 使用VNTextPatch工具进行自动提取和注入
- **msg-tool模式** - 使用msg-tool工具支持更广泛的游戏引擎类型 
- **正则表达式模式** - 使用自定义正则表达式灵活处理各种脚本格式

### 🎮 msg-tool引擎支持
- **Artemis系列**: artemis (AST), artemis-asb (ASB/IET), artemis-txt (通用文本)
- **BGI/Ethornell系列**: bgi/ethornell (通用脚本), bgi-bp (特殊BP脚本)
- **CatSystem2系列**: cat-system (CST场景脚本), cat-system-cstl (I18N文件)
- **其他引擎**: circus, entis-gls, escude, ex-hibit, favorite, innocent-grey, kirikiri

### 🌐 多编码支持
- UTF-8、GBK、SJIS等多种字符编码
- 自动编码检测和转换
- SJIS扩展字符处理

### 🔄 SJIS字符替换
- 汉字到日文汉字的智能映射
- 可选择性替换或全量替换
- 生成替换配置信息

### 💻 现代化界面
- 基于ttkbootstrap的现代主题
- 实时输出显示和进度反馈
- 可复用的GUI组件

### 📁 配置管理
- 自动保存和恢复设置
- 支持默认配置和用户配置
- 配置导入导出功能

## 📦 安装

### 环境要求
- Python 3.7+
- tkinter (通常随Python安装)

### 外部工具要求
- **VNTextPatch**: 用于VNTextPatch模式，必须放置在项目根目录的VNTextPatch文件夹中
- **msg-tool**: 用于msg-tool模式，必须将msg-tool.exe放置在项目根目录中

### 依赖安装
```bash
pip install -r requirements.txt
```

### 依赖项
- `ttkbootstrap>=1.10.1` - 现代化的tkinter主题
- `chardet>=5.0.0` - 字符编码检测

## 🚀 使用方法

### 启动应用
```bash
python src/main.py
```

### VNTextPatch模式

1. **文本提取**
   - 选择日文脚本文件夹
   - 选择JSON保存文件夹
   - 选择引擎（可选，默认自动判断）
   - 点击“提取脚本到JSON”

2. **文本注入**
   - 选择译文JSON文件夹
   - 选择输出脚本文件夹
   - 配置编码选项：
     - GBK编码注入
     - SJIS替换模式
   - 点击“注入JSON回脚本”

### msg-tool模式

1. **文本提取**
   - 选择日文脚本文件夹
   - 选择JSON保存文件夹
   - 选择引擎（支持Artemis、BGI、CatSystem2等）
   - 点击“提取脚本到JSON”

2. **文本注入**
   - 选择译文JSON文件夹
   - 选择输出脚本文件夹
   - 配置选项：
     - GBK编码注入 (--encoding cp932)
     - SJIS替换模式
   - 点击“注入JSON回脚本”

### 正则表达式模式

1. **配置正则表达式**
   - 输入正文提取正则表达式（必须包含捕获组）
   - 输入人名提取正则表达式（可选）
   - 选择日文脚本编码

2. **文本提取**
   - 选择日文脚本文件夹和JSON保存文件夹
   - 点击"提取脚本到JSON"

3. **文本注入**
   - 选择日文JSON文件夹、译文JSON文件夹和输出文件夹
   - 选择中文脚本编码
   - 配置SJIS替换模式（可选）
   - 点击"注入JSON回脚本"

## 🏗️ 项目架构

### 目录结构
```
GalTransl_DumpInjector/
├── src/                    # 源代码
│   ├── gui/               # GUI界面层
│   │   ├── widgets/       # 可复用组件
│   │   ├── main_window.py # 主窗口
│   │   ├── vntext_tab.py  # VNTextPatch标签页
│   │   └── regex_tab.py   # 正则表达式标签页
│   ├── core/              # 核心业务逻辑
│   │   ├── vntext_processor.py    # VNTextPatch处理器
│   │   ├── regex_processor.py     # 正则表达式处理器
│   │   ├── sjis_handler.py        # SJIS字符处理
│   │   └── file_operations.py     # 文件操作
│   ├── models/            # 数据模型
│   │   ├── config.py      # 配置管理
│   │   └── translation_data.py    # 翻译数据
│   ├── utils/             # 工具函数
│   │   ├── encoding_utils.py      # 编码工具
│   │   ├── command_executor.py    # 命令执行
│   │   └── validators.py          # 输入验证
│   └── main.py            # 应用入口
├── config/                # 配置文件
│   └── default_config.ini
├── resources/             # 资源文件
│   └── hanzi2kanji_table.txt
├── tests/                 # 测试文件
└── requirements.txt       # 依赖管理
```

### 架构设计原则
- **分层架构**: GUI层、业务逻辑层、数据层清晰分离
- **模块化**: 功能按模块组织，便于维护和扩展
- **可测试**: 业务逻辑与界面分离，便于单元测试
- **可配置**: 集中的配置管理，支持个性化设置

## 🔧 开发

### 运行测试
```bash
python tests/test_runner.py
```

### 代码检查
所有核心模块都通过了语法检查，无编译错误。

## 📋 从原版迁移

重构版本与原版功能完全兼容：

### 保持兼容的功能
- ✅ 相同的用户界面布局
- ✅ 兼容的配置文件格式
- ✅ 相同的VNTextPatch工具调用
- ✅ 相同的SJIS字符替换逻辑

### 新增的改进
- 🆕 模块化代码架构
- 🆕 完善的错误处理
- 🆕 实时输出显示
- 🆕 进度条反馈
- 🆕 配置导入导出
- 🆕 主题切换支持

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目。

### 开发指南
1. Fork 本仓库
2. 创建特性分支
3. 提交更改
4. 运行测试确保代码质量
5. 提交Pull Request

## 📜 更新日志

### v2.0.0 (重构版本)
- 🔄 完全重构为模块化架构
- ➕ 添加完善的错误处理和用户反馈
- ➕ 新增配置管理和状态保存
- ➕ 实现可复用的GUI组件
- ➕ 添加单元测试支持
- 🐛 修复原版中的各种潜在问题

### v1.1 (原版)
- 基础的VNTextPatch和正则表达式模式
- 简单的GUI界面
- SJIS字符替换功能

## 📄 许可证

本项目基于 MIT 许可证开源 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 👨‍💻 作者

- **cx2333** - 原作者
- **重构团队** - 架构重构和优化

## 🙏 致谢

- 感谢原版GalTransl DumpInjector的创作者
- 感谢VNTextPatch工具的开发者
- 感谢所有贡献者和用户的反馈

---

如果这个项目对你有帮助，请给个⭐️支持一下！