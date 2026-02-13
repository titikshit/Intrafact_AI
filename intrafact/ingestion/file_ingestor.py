import hashlib
from pathlib import Path
from intrafact.config import RAW_DATA_DIR, PROCESSED_DATA_DIR
import pypdf
from typing import List, Dict, Optional

def calculate_file_hash(content: str) -> str:
    """
    Calculates the SHA256 hash of the given content string.
    """
    return hashlib.sha256(content.encode("utf-8")).hexdigest()

def extract_text_from_pdf(filepath: Path) -> str:
    """
    Reads a PDF file and converts it to a single string of text.
    """
    text_content = []
    try:
        with open(filepath, 'rb') as f:
            reader = pypdf.PdfReader(f)
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    text_content.append(text)
        
        return "\n".join(text_content)
    except Exception as e:
        print(f"   ⚠️ Error reading PDF {filepath.name}: {e}")
        return ""

def extract_text_from_txt(filepath: Path) -> str:
    """
    Reads a text file with multiple encoding fallbacks.
    """
    encodings = ['utf-8', 'latin-1', 'cp1252', 'ascii']
    
    for encoding in encodings:
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
        except Exception as e:
            print(f"   ⚠️ Error reading file {filepath.name}: {e}")
            return ""
    
    print(f"   ⚠️ Could not decode {filepath.name} with any encoding")
    return ""

def get_file_content(filepath: Path) -> Optional[str]:
    """
    Routes to appropriate extraction method based on file extension.
    """
    suffix = filepath.suffix.lower()
    
    if suffix == '.pdf':
        return extract_text_from_pdf(filepath)
    elif suffix in ['.txt', '.md', '.csv', '.json', '.log', '.xml', '.html']:
        return extract_text_from_txt(filepath)
    else:
        print(f"   ⚠️ Unsupported file type: {filepath.name}")
        return None

def check_if_processed(file_hash: str, file_name: str) -> bool:
    """
    Checks if a file with this hash actually exists in the processed folder.
    Returns True only if BOTH the hash matches AND the file physically exists.
    """
    # Check if processed directory exists
    if not PROCESSED_DATA_DIR.exists():
        PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
        return False
    
    # Look for any file with matching hash in the filename or metadata
    # This assumes processed files are named with hash (adjust based on your system)
    processed_files = list(PROCESSED_DATA_DIR.glob("*"))
    
    for processed_file in processed_files:
        # Check if this file's name contains the hash
        if file_hash in processed_file.name:
            return True
        
        # Alternative: check metadata file if you store hash separately
        # You might need to adjust this based on how your system stores metadata
    
    return False

def ingestor() -> List[Dict]:
    """
    Reads all supported files from the raw data directory and returns a list 
    of data objects for the normalization layer.
    """
    # 1. Ensure directories exist
    if not RAW_DATA_DIR.exists():
        print(f"❌ Directory not found: {RAW_DATA_DIR}")
        return []
    
    if not PROCESSED_DATA_DIR.exists():
        PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created processed directory: {PROCESSED_DATA_DIR}")
    
    # 2. Get all files in the directory (excluding hidden files)
    files = [f for f in RAW_DATA_DIR.glob("*") if f.is_file() and not f.name.startswith('.')]
    
    if not files:
        print(f"⚠️ No files found in {RAW_DATA_DIR}")
        return []
    
    print(f"📂 Found {len(files)} file(s) in raw directory")
    
    collected_data = []

    for file_path in files:
        try:
            # 3. Extract content based on file type
            content = get_file_content(file_path)
            
            if not content:
                print(f"   ⏭️ Skipping {file_path.name} (empty or unsupported)")
                continue
            
            if len(content.strip()) == 0:
                print(f"   ⏭️ Skipping {file_path.name} (no text content)")
                continue
            
            # 4. Calculate hash
            file_hash = calculate_file_hash(content)
            
            # 5. CRITICAL FIX: Check if file is actually processed (not just hash exists)
            if check_if_processed(file_hash, file_path.name):
                print(f"   ✓ Already processed: {file_path.name}")
                continue
            
            # 6. Create standardized data object
            data_item = {
                "raw_text": content,
                "metadata": {
                    "file_name": file_path.name,
                    "file_path": str(file_path),
                    "file_type": file_path.suffix.lower(),
                    "source_type": "local_file",
                    "file_hash": file_hash,
                    "file_size": file_path.stat().st_size
                }
            }
            
            collected_data.append(data_item)
            print(f"   ✅ Collected: {file_path.name} ({len(content)} chars)")
            
        except Exception as e:
            print(f"   ❌ Failed to process {file_path.name}: {e}")
            continue

    print(f"\n📊 Total files to process: {len(collected_data)}")
    return collected_data

if __name__ == "__main__":
    result = ingestor()
    print(f"\nIngested {len(result)} documents")