import re

filepath = 'd:/web_arlenys/index.html'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Remove language toggle button from desktop nav
nav_btn_pattern = r'<button\s*id="lang-toggle-btn".*?</button>'
content = re.sub(nav_btn_pattern, '', content, flags=re.DOTALL)

# Remove language toggle button from mobile nav
mob_btn_pattern = r'<button\s*id="mobile-lang-toggle".*?</button>'
content = re.sub(mob_btn_pattern, '', content, flags=re.DOTALL)

# Remove CSS rules for languages
css_rules = r'      html\[lang="en"\] \.es-content \{[\s\S]*?display:\s*inline;\s*\}'
content = re.sub(css_rules, '', content)

css_rules2 = r'      html\[lang="es"\] \.en-content \{[\s\S]*?display:\s*inline;\s*\}'
content = re.sub(css_rules2, '', content)

# Remove `<span class="es-content">...</span>` blocks
es_span_pattern = r'<span\s+class="es-content"[^>]*>.*?</span>'
# But what if there are nested elements? We know there aren't in this specific project, it's just text.
# Let's remove them non-greedily. But some spans are multi-line.
es_span_pattern = re.compile(r'<span class="es-content".*?</span>', re.DOTALL)
content = re.sub(es_span_pattern, '', content)

# Unwrap `<span class="en-content">...</span>`
en_span_pattern = re.compile(r'<span class="en-content"[^>]*>(.*?)</span>', re.DOTALL)
content = re.sub(en_span_pattern, r'\1', content)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Language processing complete.")
