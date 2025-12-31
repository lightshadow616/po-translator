import polib
import json
from json import JSONDecodeError
from tqdm import tqdm
import os
from openai import OpenAI
from config import *
from rate_limiter import RateLimiter


class AiTranslator:
    def __init__(self, config, api_key):
        self.config = config
        self.client = OpenAI(
            api_key=api_key,
            base_url=config['base_url'],
        )
        self.prompt = config['prompt']
        self.rate_limiter = RateLimiter(config.get('rpm', 60), 60)

    def translate_text(self, text):
        @self.rate_limiter
        def limited_chat(msgs):
            return self.client.chat.completions.create(
                model=self.config['model'],
                messages=msgs,
                stream=False,
                response_format={"type": "json_object"},
                temperature=self.config.get('temperature', 1)
            )

        for attempt in range(MAX_RETRIES):
            messages = [
                {"role": "system", "content": self.prompt},
                {"role": "user", "content": text},
            ]
            completion_contents = []
            try:
                while True:
                    completion = limited_chat(messages)
                    messages.append(completion.choices[0].message)
                    completion_contents.append(completion.choices[0].message.content)
                    if completion.choices[0].finish_reason != "length":
                        break

                return ''.join(completion_contents)
            except Exception as e:
                logger.error(f"尝试 {attempt + 1} 次失败：{e}")
                if attempt >= MAX_RETRIES - 1:
                    logger.error("已达到最大重试次数。返回空。")
                    raise e  # 重新抛出异常以便调用方知道错误

        return ''


class PoWalkTranslator:
    def __init__(self, translator: AiTranslator, src: str, dest: str = None):
        self.translator = translator
        self.src = src
        self.dest = dest

    def run(self):
        if not os.path.exists(self.src):
            logger.error(f"源目录不存在: {self.src}")
            return
            
        for root, dirs, files in os.walk(self.src):
            logger.info(f"正在翻译目录{root}")
            for file in files:
                if file.endswith(".po"):
                    file_path = os.path.join(root, file)
                    new_file_path = file_path.replace(self.src, self.dest) if self.dest else file_path
                    try:
                        self.translate_po_file(file_path, new_file_path)
                    except Exception as e:
                        logger.error(f"翻译文件失败 {file_path}: {e}")

    def translate_po_file(self, file_path, new_file_path=None):
        logger.info(f"正在翻译: {file_path}")

        try:
            # 尝试使用不同编码读取PO文件，并检查返回值
            po = polib.pofile(file_path, encoding='utf-8')
            # 检查polib是否成功解析了文件
            if po is None:
                logger.error(f"polib返回了None: {file_path}")
                return
        except Exception as e:
            logger.error(f"使用UTF-8读取PO文件失败 {file_path}: {e}")
            try:
                # 尝试使用其他编码
                po = polib.pofile(file_path, encoding='gbk')
                if po is None:
                    logger.error(f"使用GBK编码polib返回了None: {file_path}")
                    return
            except Exception as e2:
                logger.error(f"使用GBK编码读取PO文件也失败 {file_path}: {e2}")
                return

        # 确保PO对象确实是一个POFile对象
        if not hasattr(po, '__iter__') or not hasattr(po, 'save'):
            logger.error(f"PO对象格式不正确: {file_path}")
            return

        # 筛选未翻译的条目 - 只有msgstr完全为空的条目才需要翻译
        # 这会正确处理长字符串格式，因为即使是多行的空字符串，join后也是空的
        try:
            untranslated_entries = [entry for entry in po if not entry.msgstr and not entry.obsolete]
        except Exception as e:
            logger.error(f"筛选未翻译条目失败 {file_path}: {e}")
            return

        if not untranslated_entries:
            logger.info("没有需要翻译的条目，跳过翻译。")
            # 即使没有需要翻译的内容，也要保存文件（复制原文件到目标位置）
            to_file_path = new_file_path or file_path
            self.ensure_directory_exists(to_file_path)
            try:
                po.save(to_file_path)
                logger.info(f"已保存文件到: {to_file_path}\n")
            except Exception as e:
                logger.error(f"保存文件失败 {to_file_path}: {e}")
            return

        # 处理批次
        batches = []
        current_batch = []
        current_length = 0

        for entry in untranslated_entries:
            if current_length + len(entry.msgid) > BATCH_MAX_CHARTS:
                batches.append(current_batch)
                current_batch = []
                current_length = 0
            current_batch.append(entry)
            current_length += len(entry.msgid)

        if current_batch:
            batches.append(current_batch)

        # 按批次翻译
        for batch in tqdm(batches, desc="翻译进度"):
            batch_map = {str(index): entry.msgid for index, entry in enumerate(batch)}
            content = json.dumps(batch_map, ensure_ascii=False)
            try:
                translated_content = self.translator.translate_text(content)
            except Exception as e:
                logger.error(f"翻译批次失败: {e}")
                continue
                
            try:
                translated_batch_map = json.loads(translated_content)
            except JSONDecodeError as e:
                logger.error(e.msg)
                logger.error("可能是翻译的条目过多，丢失该部分翻译，请尝试修改 BATCH_MAX_CHARTS 配置重新运行")
                translated_batch_map = ''

            if not translated_content:
                logger.info(f"翻译失败原文: {content}")
                logger.warning("警告: 批次翻译失败，保持原有的空翻译")
                continue

            # 更新翻译
            for key, value in translated_batch_map.items():
                msgid, msgstr = batch_map[key], value
                entry = po.find(msgid)
                if entry:
                    if entry.msgid_plural:
                        entry.msgstr_plural['0'] = msgstr
                        entry.msgstr_plural['1'] = msgstr
                    else:
                        entry.msgstr = msgstr

        # 保存翻译文件
        to_file_path = new_file_path or file_path
        self.ensure_directory_exists(to_file_path)
        try:
            po.save(to_file_path)
            logger.info(f"已保存翻译后的文件到: {to_file_path}\n")
        except Exception as e:
            logger.error(f"保存文件失败 {to_file_path}: {e}")


    @staticmethod
    def ensure_directory_exists(file_path):
        """
        确保文件路径的目录存在，如果不存在则创建。
        :param file_path: 目标文件的完整路径
        """
        directory = os.path.dirname(file_path)
        if directory:  # 如果路径中包含目录
            os.makedirs(directory, exist_ok=True)


if __name__ == "__main__":
    try:
        # 检查环境变量是否正确加载
        if not MODEL or not API_KEY:
            logger.error("缺少必要的环境变量配置，请检查 .env 文件")
            print("缺少必要的环境变量配置，请检查 .env 文件")
            input("按任意键退出...")
            exit(1)
            
        translator = AiTranslator(MODEL_CONFIG, API_KEY)
        po_walk_translator = PoWalkTranslator(translator, FROM_DIR, TO_DIR)
        po_walk_translator.run()
    except Exception as e:
        logger.error(f"程序运行出错: {e}")
        print(f"程序运行出错: {e}")
        input("按任意键退出...")
        exit(1)