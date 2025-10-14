import json
from mkdocs.plugins import BasePlugin

class AuthorFromJSONPlugin(BasePlugin):
    def on_config(self, config):
        # 只加载一次 JSON 文件
        with open('docs/data/calendar.json', 'r', encoding='utf-8') as f:
            self.events = json.load(f)
        return config

    def on_page_markdown(self, markdown, page, config, files):
        # page.file.src_path 是相对 docs/ 的路径
        # 去掉 .md 后缀再比较
        src_path = page.file.src_path.replace("\\", "/")
        src_path_no_ext = src_path[:-3] if src_path.endswith('.md') else src_path
        for event in self.events:
            if event['url'] == src_path_no_ext:
                author = event['title']
                markdown += f"\n\n<p style=\"text-align: right;\">\nby. {author}\n</p>\n"
                break
        return markdown