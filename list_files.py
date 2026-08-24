import os

print("--- Project Files List ---")
files = [f for f in os.listdir(".") if f.endswith(".py") or f.endswith(".html") or f.endswith(".json")]
for f in files:
    print(f"- {f}")
