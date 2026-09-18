from pathlib import Path
from config import DOCUMENTS_DIR

if __name__ == "__main__":
    files = list(DOCUMENTS_DIR.glob("*.md"))
    print(f"Prepared {len(files)} local documents for demo retrieval.")
    for path in files:
        print(f"- {path.name}")
