import os
import json

def generate_schema(env_file=".env", schema_file="schema.json"):
    schema = {}
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            key, _, value = line.partition("=")
            schema[key] = {"required": True, "default": value}
    with open(schema_file, "w") as f:
        json.dump(schema, f, indent=2)
    print(f"✅ Schema saved to {schema_file}")

def validate_schema(schema_file="schema.json", env_file=".env"):
    with open(schema_file) as f:
        schema = json.load(f)
    with open(env_file) as f:
        env_vars = dict(line.strip().split("=", 1) for line in f if "=" in line and not line.startswith("#"))
    missing = [key for key, props in schema.items() if props.get("required") and key not in env_vars]
    if missing:
        print(f"❌ Missing variables: {', '.join(missing)}")
    else:
        print("✅ All required variables are present")

def check_unused(env_file=".env", project_path="."):
    with open(env_file) as f:
        env_vars = [line.strip().split("=")[0] for line in f if "=" in line and not line.startswith("#")]
    unused = []
    for var in env_vars:
        found = False
        for root, _, files in os.walk(project_path):
            for file in files:
                if file.endswith((".py", ".txt", ".md")):
                    with open(os.path.join(root, file)) as f:
                        if var in f.read():
                            found = True
                            break
            if found:
                break
        if not found:
            unused.append(var)
    if unused:
        print(f"⚠️ Unused variables: {', '.join(unused)}")
    else:
        print("✅ No unused variables found")
