# PO-Translator 打包说明

## 打包步骤

1. 确保安装了所有依赖包：
   ```bash
   pip install -r requirements.txt
   ```

2. 安装 PyInstaller：
   ```bash
   pip install pyinstaller
   ```

3. 运行打包脚本：
   ```bash
   python build.py
   ```

## 打包后的使用方法

1. 在 `dist/po-translator` 目录下找到 `po-translator.exe`
2. 在与exe文件同级的目录下创建 `.env` 配置文件，内容参考 `.env.example`
3. 双击运行 `po-translator.exe` 即可开始翻译

## .env 配置文件说明

- `TARGET_LANG`：目标语言（如 zh 表示中文）
- `MODEL`：使用的模型名称（kimi, deepseek, qwen, glm, openai 等）
- `API_KEY`：API密钥
- `BATCH_MAX_CHARTS`：批次最大字符数
- `MAX_RETRIES`：最大重试次数
- `FROM_DIR`：源目录（待翻译的po文件所在目录）
- `TO_DIR`：输出目录（翻译后的po文件输出目录）

## 注意事项

1. 打包后的程序需要与 `.env` 配置文件在同一目录下
2. 确保 `FROM_DIR` 指定的目录存在并包含 `.po` 文件
3. 程序运行后会自动创建 `TO_DIR` 指定的输出目录
4. 翻译日志将保存在运行目录下的 `logs/translation.log` 文件中