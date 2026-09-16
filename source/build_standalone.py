"""Package the same invitation screen as an offline, double-clickable HTML file."""
from pathlib import Path
root = Path(__file__).resolve().parent
html = (root / 'static/index.html').read_text()
html = html.replace('<link rel="stylesheet" href="/style.css">',
                    '<style>' + (root / 'static/style.css').read_text() + '</style>')
html = html.replace('<script src="/app.js"></script>',
                    '<script>' + (root / 'static/app.js').read_text() + '</script>')
(root / 'invitation.html').write_text(html)
