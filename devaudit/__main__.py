"""Allow `python -m devaudit` to behave exactly like the `devaudit` console script."""

from devaudit.cli import main

if __name__ == "__main__":
    main()
