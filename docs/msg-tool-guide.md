# msg-tool模式使用指南

## 概述

msg-tool模式是GalTransl DumpInjector项目新增的功能模式，集成了msg-tool工具的强大功能，为用户提供对更多游戏引擎类型的支持。

## 安装和配置

### 1. 获取msg-tool工具

- 从官方仓库下载最新版本的msg-tool: https://github.com/msg-tool/msg-tool
- 将`msg-tool.exe`文件放置在GalTransl DumpInjector项目的根目录中

### 2. 验证安装

启动应用后，点击菜单栏中的"工具" -> "检查msg-tool状态"来验证工具是否正确安装。

## 支持的游戏引擎

### Artemis系列
- **artemis**: 支持AST文件格式
- **artemis-asb**: 支持ASB和IET文件格式  
- **artemis-txt**: 支持通用文本脚本格式

### BGI/Ethornell系列
- **bgi/ethornell**: 支持通用脚本格式
- **bgi-bp/ethornell-bp**: 支持特殊BP脚本格式

### CatSystem2系列
- **cat-system**: 支持CST场景脚本
- **cat-system-cstl**: 支持I18N国际化文件

### 其他支持的引擎
- **circus**: 支持MES脚本文件
- **entis-gls**: 支持XML脚本格式
- **escude**: 支持BIN脚本文件
- **ex-hibit**: 支持RLD脚本文件
- **favorite**: 支持DAT脚本文件
- **innocent-grey**: 支持TXT脚本格式
- **kirikiri**: 支持KS脚本文件

## 使用流程

### 文本提取流程

1. **选择输入文件夹**
   - 在"日文脚本文件夹"中选择包含游戏脚本文件的目录

2. **选择输出文件夹**
   - 在"日文JSON保存文件夹"中选择用于保存提取的JSON文件的目录

3. **选择引擎类型**
   - 从下拉菜单中选择对应的游戏引擎类型
   - 如果不确定，可以选择"自动检测"让工具自动识别

4. **执行提取**
   - 点击"提取脚本到JSON"按钮开始提取过程
   - 在输出窗口中可以实时查看提取进度和结果

### 文本注入流程

1. **选择输入文件夹**
   - "日文脚本文件夹": 原始游戏脚本文件夹
   - "译文JSON文件夹": 包含翻译后JSON文件的文件夹

2. **选择输出文件夹**
   - "译文脚本保存文件夹": 用于保存注入后脚本文件的目录

3. **配置注入选项**
   - **GBK编码注入**: 启用后使用`--encoding cp932`参数，适用于需要GBK编码的场景
   - **SJIS替换模式**: 启用汉字到日文汉字的映射替换功能

4. **执行注入**
   - 点击"注入JSON回脚本"按钮开始注入过程
   - 在输出窗口中可以实时查看注入进度和结果

## 高级功能

### GBK编码支持

当启用"GBK编码注入"选项时，msg-tool将使用`--encoding cp932`参数，这对于某些需要特殊编码处理的游戏非常有用。

### SJIS字符替换

SJIS替换功能可以将中文汉字映射为对应的日文汉字，确保在日文游戏中的正确显示：

- **空值替换**: 如果SJIS替换字符输入框为空，将进行全量字符替换
- **指定字符替换**: 输入特定字符后，只替换这些指定的字符

## 故障排除

### 常见问题

**问题**: 提示"msg-tool工具不可用"
**解决方案**: 确保msg-tool.exe文件位于项目根目录中，并且具有执行权限

**问题**: 引擎自动检测失败
**解决方案**: 手动选择对应的引擎类型，或检查脚本文件格式是否受支持

**问题**: 提取或注入过程中出现编码错误
**解决方案**: 尝试启用GBK编码选项，或检查原始脚本文件的编码格式

### 调试技巧

1. **查看实时输出**: 输出窗口会显示msg-tool的详细执行信息
2. **检查工具状态**: 使用菜单中的状态检查功能验证工具可用性
3. **逐步操作**: 先进行小规模测试，确认参数配置正确后再处理完整项目

## 技术细节

### 命令行参数映射

msg-tool模式使用以下命令行参数：

**提取命令**:
```
msg-tool export --output-format json --recursive [--script-type ENGINE] INPUT_PATH OUTPUT_PATH
```

**注入命令**:
```
msg-tool import [--script-type ENGINE] [--encoding cp932] --recursive SCRIPT_PATH JSON_PATH OUTPUT_PATH
```

### 配置文件

msg-tool相关的配置会保存在`config/default_config.ini`的以下部分：

```ini
[MsgToolPaths]
msgtool_script_jp_folder = 
msgtool_json_jp_folder = 
msgtool_json_cn_folder = 
msgtool_script_cn_folder = 

[MsgToolSettings]
msgtool_selected_engine = 自动检测
msgtool_use_gbk_encoding = false
msgtool_sjis_replacement = false
msgtool_sjis_chars = 
```

## 最佳实践

1. **备份原始文件**: 在进行任何操作前，务必备份原始游戏脚本文件
2. **逐步测试**: 先用小量文件测试，确认配置正确后再批量处理
3. **验证结果**: 注入完成后，验证游戏是否能正常运行和显示
4. **保存配置**: 成功的配置会自动保存，下次使用时会自动加载

## 与VNTextPatch模式的对比

| 特性 | VNTextPatch模式 | msg-tool模式 |
|------|-----------------|--------------|
| 支持引擎数量 | 相对较少 | 更多更广泛 |
| 配置复杂度 | 简单 | 中等 |
| 功能特性 | 成熟稳定 | 功能丰富 |
| 社区支持 | 广泛 | 快速发展 |
| 学习曲线 | 低 | 中等 |

选择哪种模式取决于你要处理的游戏引擎类型和个人偏好。

---

如有问题或建议，请在项目的Issue页面提交反馈。