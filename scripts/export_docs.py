import os, zipfile, html
from pathlib import Path
import xml.etree.ElementTree as ET

def extract_blocks(docx_path: Path):
    """Extract ordered content blocks: paragraphs and tables from .docx."""
    with zipfile.ZipFile(docx_path, 'r') as z:
        raw = z.read('word/document.xml').decode('utf-8', errors='ignore')
    ET.register_namespace('w', 'http://schemas.openxmlformats.org/wordprocessingml/2006/main')
    ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    root = ET.fromstring(raw)
    body = root.find('w:body', ns)
    blocks = []
    def text_in(el):
        parts = []
        for t in el.findall('.//w:t', ns):
            parts.append(t.text or '')
        return html.unescape(''.join(parts)).strip()
    if body is not None:
        for child in list(body):
            tag = child.tag.split('}')[-1]
            if tag == 'p':
                txt = text_in(child)
                if txt:
                    blocks.append({'type': 'p', 'text': txt})
            elif tag == 'tbl':
                rows = []
                for tr in child.findall('w:tr', ns):
                    row = []
                    for tc in tr.findall('w:tc', ns):
                        row.append(text_in(tc))
                    while row and row[-1] == '':
                        row.pop()
                    if row:
                        rows.append(row)
                if rows:
                    blocks.append({'type': 'table', 'rows': rows})
    return blocks

def write_md(lines, out_path: Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text('\n'.join(lines), encoding='utf-8')

def write_html_blocks(blocks, out_path: Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    parts = []
    parts.append('<!DOCTYPE html>')
    parts.append('<html lang="zh-CN">')
    parts.append('<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">')
    parts.append('<title>导出文档</title>')
    parts.append('<style>body{font-family:-apple-system,Segoe UI,Roboto,PingFang SC,\"Microsoft YaHei\",Arial,sans-serif;line-height:1.6;padding:24px;max-width:1100px;margin:auto;} p{margin:0.6em 0;} table{border-collapse:collapse;margin:10px 0;min-width:60%} th,td{border:1px solid #d1d5db;padding:6px 10px;vertical-align:top} thead{background:#f3f4f6} tr:nth-child(even){background:#fafafa}</style>')
    parts.append('</head><body>')
    for blk in blocks:
        if blk.get('type') == 'p':
            parts.append('<p>' + html.escape(blk.get('text','')) + '</p>')
        elif blk.get('type') == 'table':
            parts.append('<table><tbody>')
            for row in blk.get('rows', []):
                parts.append('<tr>' + ''.join('<td>{}</td>'.format(html.escape(cell)) for cell in row) + '</tr>')
            parts.append('</tbody></table>')
    parts.append('</body></html>')
    out_path.write_text('\n'.join(parts), encoding='utf-8')

def main():
    docs_dir = Path('docs')
    exports = []
    for docx in docs_dir.glob('*.docx'):
        blocks = extract_blocks(docx)
        lines = [blk['text'] for blk in blocks if blk.get('type')=='p']
        base = docx.stem
        out_md = docs_dir / 'export' / f'{base}.md'
        out_html = docs_dir / 'export' / f'{base}.html'
        write_md(lines, out_md)
        write_html_blocks(blocks, out_html)
        exports.append((str(docx), str(out_md), str(out_html)))
    for e in exports:
        print('Exported:', e[0], '->', e[1], ';', e[2])

if __name__ == '__main__':
    main()
