import sys
from .cli.commands import cli
from .core.exceptions import PDFToolError


def main():
    try:
        cli()
    except PDFToolError as e:
        print(f"PDF Tool Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
