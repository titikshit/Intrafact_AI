import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve()
while not (PROJECT_ROOT / ".git").exists():
    PROJECT_ROOT = PROJECT_ROOT.parent

RAW_DATA_PATH = PROJECT_ROOT / "data/raw/manual"


DISPLAY_PATH = RAW_DATA_PATH.relative_to(PROJECT_ROOT)


def file_ingestor():

    if not os.path.exists(RAW_DATA_PATH):
        print(f"no folder {DISPLAY_PATH} found")
        return
    
    files = os.listdir(RAW_DATA_PATH)
    print(f"There are {len(files)} files in {DISPLAY_PATH}")

    for file in files:
        full_path =  os.path.join(RAW_DATA_PATH, file)

        with open(full_path,"r",encoding = "utf-8") as f:
            content = f.read()
            print(f"file name: {file}")
            print(f"File content:\n{content}")
            print("-" * 30)

if __name__ == "--main__":
    file_ingestor()

   
