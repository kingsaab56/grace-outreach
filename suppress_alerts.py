import os

with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Globally override window.alert so popups never show up under any circumstance
global_override = """
<script>
    // Global alert suppression override
    window.alert = function(msg) {
        console.log("Suppressed Alert:", msg);
    };
</script>
</head>
"""

if "</head>" in html:
    html = html.replace("</head>", global_override)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("✔ Global alert suppressor injected successfully!")
