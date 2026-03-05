import sys
from .client import run

def main():
    if len(sys.argv) < 3:
        print("Usage: disposable run '<script>'")
        return

    command = sys.argv[1]

    if command != "run":
        print("Unknown command")
        return

    script = sys.argv[2]

    result = run(script)

    print(result)

if __name__ == "__main__":
    main()
