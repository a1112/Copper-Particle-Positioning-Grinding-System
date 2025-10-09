import re, html
from pathlib import Path

def load_lines(paths):
    lines = []
    for p in paths:
        text = Path(p).read_text(encoding='utf-8', errors='ignore')
        # Split by lines, keep non-empty lines
        for ln in text.splitlines():
            s = ln.strip()
            if s:
                lines.append(s)
    return lines

TOPICS = {
    '通信协议': [
        '通信协议','通讯协议','协议','TCP','UDP','WebSocket','HTTP','请求','响应','报文','帧格式','CRC','校验','端口'
    ],
    '系统架构': [
        '系统架构','总体架构','整体架构','架构','结构','模块','分层','流程','组件','部署','拓扑'
    ],
    '接口说明': [
        '接口说明','接口','API','HTTP','REST','WebSocket','端点','路径','参数','返回','状态码'
    ],
}

SRC = [
    'docs/export/铜粒子定位磨削系统软件开发文档.md',
    'docs/export/铜粒子设备软件使用说明书.md',
]

lines = load_lines(SRC)

out_dir = Path('docs/export')
out_dir.mkdir(parents=True, exist_ok=True)

results = {k: [] for k in TOPICS}

for idx, ln in enumerate(lines):
    for topic, kws in TOPICS.items():
        if any(k in ln for k in kws):
            # Capture the line and some context around it
            start = max(0, idx-3)
            end = min(len(lines), idx+4)
            block = '\n'.join(lines[start:end])
            results[topic].append(block)

# Deduplicate while preserving order
for topic in results:
    seen = set()
    uniq = []
    for blk in results[topic]:
        if blk not in seen:
            uniq.append(blk)
            seen.add(blk)
    results[topic] = uniq

# Write MD and HTML for each topic
for topic in results:
    md_path = out_dir / f'{topic}.md'
    html_path = out_dir / f'{topic}.html'
    md_text = f'# {topic}\n\n' + '\n\n---\n\n'.join(results[topic]) + '\n'
    md_path.write_text(md_text, encoding='utf-8')
    # Simple HTML wrapper
    parts = [
        '<!DOCTYPE html>',
        '<html lang="zh-CN">',
        '<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
        f'<title>{html.escape(topic)}</title>',
        '<style>body{font-family:-apple-system,Segoe UI,Roboto,PingFang SC,\"Microsoft YaHei\",Arial,sans-serif;line-height:1.6;padding:24px;max-width:900px;margin:auto;} h1{margin:0.6em 0 0.2em} .blk{margin:1em 0; padding:0.6em 0; border-top:1px solid #eee}</style>',
        '</head><body>',
        f'<h1>{html.escape(topic)}</h1>'
    ]
    for blk in results[topic]:
        parts.append('<div class="blk">' + '<br>'.join(html.escape(l) for l in blk.split('\n')) + '</div>')
    parts.append('</body></html>')
    html_path.write_text('\n'.join(parts), encoding='utf-8')

print('EXTRACTED:', ', '.join(f'{k}({len(results[k])}块)' for k in results))
