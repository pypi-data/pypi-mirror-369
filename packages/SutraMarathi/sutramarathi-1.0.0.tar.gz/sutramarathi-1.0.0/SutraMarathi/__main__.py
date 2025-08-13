# sutramarathi/__main__.py

import sys
from .interpreter import run_sutra_file

def main():
    if len(sys.argv) != 2:
        print("वापर: sutramarathi <file.sm>")
        sys.exit(1)

    file_path = sys.argv[1]
    run_sutra_file(file_path)

if __name__ == "__main__":
    main()
