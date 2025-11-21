"""
Configure Custom Search Paths for Python Venv Detection

This tool allows you to add custom directories where DevAudit should search
for Python virtual environments.

Usage:
    python configure_venv_paths.py
"""

from pathlib import Path

def main():
    config_dir = Path.home() / ".devaudit"
    config_file = config_dir / "venv_search_paths.txt"

    print("=" * 80)
    print("DevAudit - Configure Python Venv Search Paths")
    print("=" * 80)
    print()
    print("This tool helps DevAudit find ALL your Python virtual environments.")
    print("By default, DevAudit searches common development directories like:")
    print("  - ~/dev, ~/dev_files, ~/projects, ~/code")
    print("  - ~/Documents/GitHub, ~/Documents/projects")
    print("  - Desktop/projects, OneDrive/projects")
    print()
    print("If you have projects in other locations, add them here!")
    print()

    # Create config directory if it doesn't exist
    config_dir.mkdir(parents=True, exist_ok=True)

    # Load existing paths
    existing_paths = []
    if config_file.exists():
        content = config_file.read_text(encoding='utf-8')
        for line in content.split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                existing_paths.append(line)

    # Show existing paths
    if existing_paths:
        print("Current custom search paths:")
        for i, path in enumerate(existing_paths, 1):
            print(f"  {i}. {path}")
        print()
    else:
        print("No custom search paths configured yet.")
        print()

    # Menu
    while True:
        print("\nOptions:")
        print("  1. Add a new search path")
        print("  2. Remove a search path")
        print("  3. View all paths")
        print("  4. Exit")
        print()

        choice = input("Enter your choice (1-4): ").strip()

        if choice == "1":
            # Add new path
            print()
            path_str = input("Enter directory path to scan (e.g., C:\\my_projects): ").strip()

            if not path_str:
                print("[ERROR] Path cannot be empty!")
                continue

            path = Path(path_str)
            if not path.exists():
                print(f"[WARNING] Path does not exist: {path}")
                confirm = input("Add anyway? (y/n): ").strip().lower()
                if confirm != 'y':
                    continue

            if str(path) in existing_paths:
                print(f"[INFO] Path already in list: {path}")
                continue

            existing_paths.append(str(path))
            print(f"[OK] Added: {path}")

        elif choice == "2":
            # Remove path
            if not existing_paths:
                print("\n[INFO] No paths to remove!")
                continue

            print("\nCurrent paths:")
            for i, path in enumerate(existing_paths, 1):
                print(f"  {i}. {path}")

            try:
                idx = int(input("\nEnter number to remove (0 to cancel): ").strip())
                if idx == 0:
                    continue
                if 1 <= idx <= len(existing_paths):
                    removed = existing_paths.pop(idx - 1)
                    print(f"[OK] Removed: {removed}")
                else:
                    print("[ERROR] Invalid number!")
            except ValueError:
                print("[ERROR] Please enter a valid number!")

        elif choice == "3":
            # View all paths
            print("\n" + "=" * 80)
            print("All Search Paths (Default + Custom)")
            print("=" * 80)
            print("\nDefault paths (always scanned):")
            print("  - ~/dev, ~/dev_files, ~/projects, ~/code, ~/repos, ~/work, ~/workspace")
            print("  - ~/Documents/GitHub, ~/Documents/projects, ~/Documents/dev")
            print("  - ~/Desktop/projects, ~/OneDrive/projects")
            print()

            if existing_paths:
                print("Custom paths:")
                for i, path in enumerate(existing_paths, 1):
                    print(f"  {i}. {path}")
            else:
                print("No custom paths configured.")
            print()

        elif choice == "4":
            # Exit
            break

        else:
            print("[ERROR] Invalid choice! Please enter 1-4.")

    # Save paths
    print("\nSaving configuration...")
    content = "# DevAudit Python Venv Search Paths\n"
    content += "# Add one directory path per line\n"
    content += "# Lines starting with # are comments\n\n"
    content += "\n".join(existing_paths)

    config_file.write_text(content, encoding='utf-8')
    print(f"[OK] Configuration saved to: {config_file}")
    print("\nNext time you run a DevAudit scan, these paths will be included!")
    print()
    print("=" * 80)

if __name__ == "__main__":
    main()
