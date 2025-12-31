# PO-Translator Windows 可执行文件使用说明

## 简介

PO-Translator 是一个基于大语言模型（LLM）的自动化翻译工具，专门用于处理 `.po` 文件的国际化（i18n）和本地化（l10n）任务。

## 使用步骤

### 1. 下载并解压

1. 下载打包好的 `po-translator` 目录
2. 将其解压到你想要的目录（例如 `C:\po-translator`）

### 2. 创建配置文件

1. 在 `po-translator.exe` 同级目录下创建 `.env` 文件
2. 编辑 `.env` 文件，内容如下：

```bash
# .env 配置文件示例
TARGET_LANG=zh
MODEL=qwen
API_KEY=your_api_key_here
BATCH_MAX_CHARTS=2000
MAX_RETRIES=3
FROM_DIR=po_files
TO_DIR=po_files_translated
```

**配置说明：**

- `TARGET_LANG`：目标语言（如 zh 表示中文）
- `MODEL`：使用的模型名称（kimi, deepseek, qwen, glm, openai 等）
- `API_KEY`：API密钥
- `BATCH_MAX_CHARTS`：批次最大字符数
- `MAX_RETRIES`：最大重试次数
- `FROM_DIR`：源目录（待翻译的po文件所在目录）
- `TO_DIR`：输出目录（翻译后的po文件输出目录）

### 3. 准备待翻译的文件

1. 在程序运行目录下创建 `po_files` 目录（或使用配置文件中指定的目录名）
2. 将需要翻译的 `.po` 文件放入该目录

### 4. 运行程序

双击运行 `po-translator.exe`，程序将开始翻译过程。

### 5. 查看结果

翻译完成后，结果将保存在配置文件中指定的输出目录（默认为 `po_files_translated`）中。

## 安全说明

本程序使用PyInstaller打包，所有Python源代码（包括 [config.py](file://f:\WorkSpace\Python\po-translator\config.py) 和 [rate_limiter.py](file://f:\WorkSpace\Python\po-translator\rate_limiter.py)）都已被编译并嵌入到可执行文件中，不会以明文形式暴露。

- 源代码文件（.py）已编译为字节码并嵌入到exe文件中
- 程序运行时不会在系统中释放源码文件
- 所有核心逻辑都已编译，反编译需要专业的工具和知识

## 注意事项

1. 确保 `.env` 配置文件与 `po-translator.exe` 在同一目录下
2. 确保API密钥正确配置
3. 翻译日志将保存在运行目录下的 `logs/translation.log` 文件中
4. 如果程序无法运行，请检查 `.env` 文件配置是否正确

## 故障排除

### 程序无法启动

1. 检查 `.env` 文件是否存在
2. 检查 `.env` 文件中的配置是否正确
3. 确保FROM_DIR和TO_DIR目录存在或有写入权限

### 翻译失败

1. 检查API密钥是否正确
2. 检查网络连接是否正常
3. 查看 `logs/translation.log` 中的错误信息

## 更新配置

如需更改配置，只需修改 `.env` 文件中的相应参数，然后重新运行程序即可。