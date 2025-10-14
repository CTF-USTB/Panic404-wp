import json
import os
import datetime

schedule_file = 'docs/data/calendar.json'
today = datetime.date.today().isoformat()

# === 获取环境变量 ===
committer = os.environ.get('COMMITTER_NAME', 'unknown')
# 新增文件（added）
added_env = os.environ.get('ADDED_FILES', '[]')
# 重命名文件（renamed）
renamed_env = os.environ.get('RENAMED_PAIRS', '[]')


def parse_list(env_str):
    """解析 JSON 数组为 Python 列表"""
    try:
        return json.loads(env_str)
    except Exception:
        return []


added_files = parse_list(added_env)
renamed_pairs = parse_list(renamed_env)

# 只取 Markdown 文件
added_md = [f for f in added_files if isinstance(f, str) and f.endswith('.md')]
renamed_pairs = [p for p in renamed_pairs if isinstance(p, dict)
                 and p.get('old', '').endswith('.md')
                 and p.get('new', '').endswith('.md')]


def to_mkdocs_url(path: str) -> str:
    """将 docs/xxx.md 转为 mkdocs URL"""
    if path.startswith('docs/'):
        path = path[len('docs/'):]
    if path.endswith('.md'):
        path = path[:-3]
    return path


# === 读取现有事件文件 ===
if os.path.exists(schedule_file):
    with open(schedule_file, encoding='utf-8') as f:
        events = json.load(f)
else:
    events = []

# === 更新重命名文件 ===
if renamed_pairs:
    print(f"Processing renamed pairs: {renamed_pairs}")
    for pair in renamed_pairs:
        old_url = to_mkdocs_url(pair['old'])
        new_url = to_mkdocs_url(pair['new'])

        # 尝试在现有 events 中找到旧 URL
        updated = False
        for ev in events:
            if ev.get('url') == old_url:
                ev['url'] = new_url
                # ev['date'] = today
                # ev['title'] = committer + " (rename)"
                updated = True
                break

        # 若旧 URL 不存在，则补充新事件
        # 非预料情况
        if not updated:
            events.append({
                'date': today,
                'title': committer,
                'desc': '',
                'status': 'done',
                'url': new_url
            })

# === 处理新增文件 ===
if added_md:
    print(f"Adding events for: {added_md}")
    for path in added_md:
        url = to_mkdocs_url(path)
        events.append({
            'date': today,
            'title': committer,
            'desc': '',
            'status': 'done',
            'url': url
        })

# === 写回 JSON（单行字典形式） ===
os.makedirs(os.path.dirname(schedule_file), exist_ok=True)
with open(schedule_file, 'w', encoding='utf-8') as f:
    f.write('[\n')
    for i, ev in enumerate(events):
        json.dump(ev, f, ensure_ascii=False, separators=(',', ':'))
        if i < len(events) - 1:
            f.write(',\n')
        else:
            f.write('\n')
    f.write(']\n')

print(f"Updated {len(events)} events in {schedule_file}")
