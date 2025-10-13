import json, os, datetime, ast

schedule_file = 'docs/data/calendar.json'
today = datetime.date.today().isoformat()

# 取环境变量
committer = os.environ.get('COMMITTER_NAME', 'unknown')

# 获取本次 push 改动的文件列表（md 文件）
files_env = os.environ.get('COMMIT_FILES', '[]')
try:
    files_nested = json.loads(files_env)
except Exception:
    files_nested = []
# 拉平成一维
files = []
for sub in files_nested:
    if isinstance(sub, list):
        files.extend(sub)
    elif isinstance(sub, str):
        files.append(sub)

# 只取 md 文件
md_files = [f for f in files if f.endswith('.md')]

def to_mkdocs_url(path):
    # 去掉前导 docs/
    if path.startswith('docs/'):
        path = path[len('docs/'):]
        # 去掉 .md 后缀
    if path.endswith('.md'):
        path = path[:-3]
    return path

urls = [to_mkdocs_url(p) for p in md_files]

# 读取 schedule
if os.path.exists(schedule_file):
    with open(schedule_file, encoding='utf-8') as f:
        events = json.load(f)
else:
    events = []

# 先找当天该人的 pending 事件
# pending_index = None
# for idx, ev in enumerate(events):
#     if ev.get('date') == today and ev.get('title') == committer and ev.get('status') == 'pending':
#         pending_index = idx
#         break

# if pending_index is not None and urls:
#     # 用第一条 md 文件更新现有事件
#     events[pending_index]['status'] = 'done'
#     events[pending_index]['url'] = urls[0]
#     used = 1
# else:
#     used = 0

used = 0

# 对剩余的 md 文件新增事件
for url in urls[used:]:
    events.append({
        'date': today,
        'title': committer,
        'desc': '',
        'status': 'done',
        'url': url
    })

# 写回
os.makedirs(os.path.dirname(schedule_file), exist_ok=True)
# with open(schedule_file, 'w', encoding='utf-8') as f:
#     json.dump(events, f, ensure_ascii=False, indent=2)

# 手动写，保证单个字典不换行，字典之间换行
with open(schedule_file, 'w', encoding='utf-8') as f:
    f.write('[\n')
    for i, ev in enumerate(events):
        json.dump(ev, f, ensure_ascii=False, separators=(',', ':'))
        if i < len(events) - 1:
            f.write(',\n')
        else:
            f.write('\n')
    f.write(']\n')
