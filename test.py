from datatypeplus import (
    FlexString,
    NList,
    EvolveList,
    FlexDict,
    EvolveDict,
    Signal,
    Computed,
    Effect,
    FlexTree,
    info,
)

print("=== Testing datatypeplus v2.0.0 ===")
info()
print("\n" + "=" * 40 + "\n")

# --- 1. FlexString Tests ---
print("--- 1. FlexString Tests ---")
fs = FlexString("  hello world  ").strip().title().replace("World", "Python")
print("Fluent Chaining:", fs)

fs.to_snake()
print("Snake Case:", fs)

fs.to_camel()
print("Camel Case:", fs)

fs.slugify()
print("Slugify:", fs)

print("Parse Float:", FlexString("3.14159").to_float())
print()

# --- 2. NList Tests ---
print("--- 2. NList Tests ---")
nl = NList(
    axes={
        "City": ["NY", "LA", "CHI"],
        "Year": [2024, 2025, 2026],
        "Metric": ["Revenue", "Profit"]
    },
    default=0
)
nl["NY", 2026, "Revenue"] = 5000
nl["LA", 2026, "Revenue"] = 3500

print("Single lookup (NY 2026 Revenue):", nl["NY", 2026, "Revenue"])
sub_nl = nl["NY":"LA", 2026, :]
print("Sub-NList slice shape:", sub_nl.shape)
print("NList Total Sum:", nl.sum())
print()

# --- 3. Signal / Computed / Effect Tests ---
print("--- 3. Signal / Computed / Effect Tests ---")
count = Signal(10)
double_count = Computed(lambda: count.get() * 2)

logs = []
Effect(lambda: logs.append(f"Count changed to {double_count.get()}"))

count.set(25)
print("Effect log 1:", logs[0])
print("Effect log 2:", logs[1])
print()

# --- 4. EvolveList Tests ---
print("--- 4. EvolveList Tests ---")
el = EvolveList([10, 20, 0])
el[2].computed_from([el[0], el[1]], lambda a, b: a + b)
print("Computed element el[2] (10+20):", el[2].value)

with el.batch():
    el[0] = 50
    el[1] = 50
print("Batch update el[2] (50+50):", el[2].value)
print()

# --- 5. FlexDict & EvolveDict Tests ---
print("--- 5. FlexDict & EvolveDict Tests ---")
fd = FlexDict()
fd.user.profile.name = "Alice"
print("Auto-vivified FlexDict:", fd.to_dict())
print("Flattened Dict:", fd.flatten())

ed = EvolveDict({"status": "idle"})
ed.when(lambda: ed["status"] == "active").do(lambda: print("Trigger: System is ACTIVE!"))
ed["status"] = "active"
print()

# --- 6. FlexTree Tests ---
print("--- 6. FlexTree Tests ---")
root = FlexTree("root", value="root_val")
n1 = root.add_child("config")
leaf = n1.add_child("database", value="postgres://localhost")

found = root.find("/root/config/database")
print("Found tree node path:", found.path if found else "Not found")
print("Node value:", found.value if found else None)
print()

print("=== All v2.0.0 Tests Completed Successfully! ===")