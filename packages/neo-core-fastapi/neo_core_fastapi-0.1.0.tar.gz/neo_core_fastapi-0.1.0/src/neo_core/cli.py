"""Command line interface for neo-core-fastapi."""

import argparse
import sys
from typing import List, Optional


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        prog="neo-core",
        description="Neo Core FastAPI - Core library for FastAPI applications",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="neo-core-fastapi 0.1.0",
    )
    
    subparsers = parser.add_subparsers(
        dest="command",
        help="Available commands",
        metavar="COMMAND",
    )
    
    # Init command
    init_parser = subparsers.add_parser(
        "init",
        help="Initialize a new neo-core project",
    )
    init_parser.add_argument(
        "name",
        help="Project name",
    )
    init_parser.add_argument(
        "--template",
        choices=["basic", "full"],
        default="basic",
        help="Project template (default: basic)",
    )
    
    # Database commands
    db_parser = subparsers.add_parser(
        "db",
        help="Database management commands",
    )
    db_subparsers = db_parser.add_subparsers(
        dest="db_command",
        help="Database commands",
    )
    
    # Database init
    db_subparsers.add_parser(
        "init",
        help="Initialize database with Alembic",
    )
    
    # Database migrate
    migrate_parser = db_subparsers.add_parser(
        "migrate",
        help="Create a new migration",
    )
    migrate_parser.add_argument(
        "-m", "--message",
        required=True,
        help="Migration message",
    )
    
    # Database upgrade
    upgrade_parser = db_subparsers.add_parser(
        "upgrade",
        help="Upgrade database to latest migration",
    )
    upgrade_parser.add_argument(
        "revision",
        nargs="?",
        default="head",
        help="Target revision (default: head)",
    )
    
    # Database downgrade
    downgrade_parser = db_subparsers.add_parser(
        "downgrade",
        help="Downgrade database",
    )
    downgrade_parser.add_argument(
        "revision",
        help="Target revision",
    )
    
    return parser


def handle_init_command(args: argparse.Namespace) -> int:
    """Handle the init command."""
    print(f"Initializing neo-core project: {args.name}")
    print(f"Template: {args.template}")
    print("\nProject initialization is not yet implemented.")
    print("Please refer to the documentation for manual setup.")
    return 0


def handle_db_command(args: argparse.Namespace) -> int:
    """Handle database commands."""
    if not args.db_command:
        print("Error: No database command specified")
        return 1
    
    if args.db_command == "init":
        print("Initializing database with Alembic...")
        print("\nDatabase initialization is not yet implemented.")
        print("Please run: alembic init alembic")
        
    elif args.db_command == "migrate":
        print(f"Creating migration: {args.message}")
        print("\nMigration creation is not yet implemented.")
        print(f"Please run: alembic revision --autogenerate -m '{args.message}'")
        
    elif args.db_command == "upgrade":
        print(f"Upgrading database to: {args.revision}")
        print("\nDatabase upgrade is not yet implemented.")
        print(f"Please run: alembic upgrade {args.revision}")
        
    elif args.db_command == "downgrade":
        print(f"Downgrading database to: {args.revision}")
        print("\nDatabase downgrade is not yet implemented.")
        print(f"Please run: alembic downgrade {args.revision}")
    
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args(argv)
    
    if not args.command:
        parser.print_help()
        return 0
    
    try:
        if args.command == "init":
            return handle_init_command(args)
        elif args.command == "db":
            return handle_db_command(args)
        else:
            print(f"Unknown command: {args.command}")
            return 1
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 130
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())