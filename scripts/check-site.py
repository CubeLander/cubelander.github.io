"""Check published HTML, internal links, article exports and discovery documents."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import xml.etree.ElementTree as ET

ROOT = Path('_site')


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.path, self.links, self.ids = path, [], set()
        self.h1 = 0
        self.lang = self.canonical = self.description = False
        self.feed(path.read_text())

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            assert attrs['id'] not in self.ids, f'Duplicate ID: {self.path}: {attrs["id"]}'
            self.ids.add(attrs['id'])
        if tag == 'h1':
            self.h1 += 1
        if tag == 'html':
            self.lang = attrs.get('lang') == 'zh-CN'
        if tag == 'link' and attrs.get('rel') == 'canonical':
            self.canonical = attrs['href'].startswith('https://cubelander.github.io/')
        if tag == 'meta' and attrs.get('name') == 'description':
            self.description = bool(attrs.get('content'))
        for name in ('href', 'src'):
            if name in attrs:
                self.links.append(attrs[name])


pages = {path: Page(path) for path in ROOT.rglob('*.html')}
assert pages, 'No HTML generated'
for path, page in pages.items():
    assert page.h1 == 1, f'Expected one h1: {path}'
    assert page.lang and page.canonical and page.description, f'Missing metadata: {path}'
    assert 'main' in page.ids, f'Missing skip-link target: {path}'
    assert '{{' not in path.read_text(), f'Unrendered template: {path}'
    for link in page.links:
        url = urlsplit(link)
        if url.scheme or url.netloc:
            assert url.scheme == 'https', f'Unexpected external URL: {link}'
            continue
        target = ROOT / unquote(url.path).lstrip('/') if url.path.startswith('/') else path.parent / unquote(url.path)
        if not url.path:
            target = path
        if target.is_dir():
            target /= 'index.html'
        assert target.exists(), f'Broken link in {path}: {link}'
        if url.fragment and target in pages:
            assert unquote(url.fragment) in pages[target].ids, f'Broken anchor: {path}: {link}'

taxi = ROOT / 'taxi/index.html'
assert taxi.read_bytes() == Path('public/taxi/index.html').read_bytes(), 'Taxi export must pass through unchanged'
assert '/taxi/' in (ROOT / 'index.html').read_text(), 'Missing taxi navigation'
public = taxi.read_text()
assert '公开展示版' in public
assert not any(token in public.lower() for token in ('/users/', 'file://', 'mailto:', '学号', '班级')), 'Private material in taxi export'

sources = list(Path('src/posts').glob('*.md'))
assert sources, 'No articles'
for source in sources:
    slug = source.stem
    assert (ROOT / 'notes' / slug / 'index.html').exists(), f'Missing article: {slug}'
    raw = (ROOT / 'text' / source.name).read_text()
    assert len(raw) > 500 and raw.startswith('# '), f'Incomplete Markdown export: {slug}'
    assert 'https://github.com/vLLM-HUST/BetterScale/blob/' in raw, f'Missing raw provenance: {slug}'

feed = ET.parse(ROOT / 'feed.xml')
assert len(feed.findall('{http://www.w3.org/2005/Atom}entry')) == len(sources)
ET.parse(ROOT / 'sitemap.xml')
assert (ROOT / '.nojekyll').exists()
assert 'sitemap.xml' in (ROOT / 'robots.txt').read_text()
print(f'PASS: {len(pages)} HTML pages, {len(sources)} article exports, local links/anchors, Atom and sitemap.')
