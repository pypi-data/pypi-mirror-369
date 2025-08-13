import argparse
from .core import generate_schema, validate_schema, check_unused

def main():
    parser = argparse.ArgumentParser(description="Check and validate .env files")
    parser.add_argument("--generate-schema", action="store_true", help="Generate schema from .env")
    parser.add_argument("--schema", help="Path to schema.json")
    parser.add_argument("--check-unused", action="store_true", help="Check unused variables")
    parser.add_argument("--path", help="Path to scan for unused variables")
    parser.add_argument("--env", default=".env", help="Path to .env file")
    args = parser.parse_args()

    if args.generate_schema:
        generate_schema(env_file=args.env)
    elif args.schema:
        validate_schema(schema_file=args.schema, env_file=args.env)
    elif args.check_unused:
        check_unused(env_file=args.env, project_path=args.path or ".")
    else:
        parser.print_help()
