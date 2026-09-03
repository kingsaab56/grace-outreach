import os

with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Fix CSS padding and min-height on metric cards so green tags are fully visible
css_fix = """
<style>
    .panel-card, div[style*="background: var(--bg-card)"] {
        overflow: visible !important;
        padding-bottom: 24px !important;
    }
</style>
</head>
"""

if "</head>" in html:
    html = html.replace("</head>", css_fix)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("✔ Card layout padding patched successfully!")
