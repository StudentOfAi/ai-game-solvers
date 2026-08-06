import os
import sys

# Path to the file we want to verify
FILE_PATH = "/Users/clawd/Desktop/ai-game-solvers/pacman-ai/index.html"

def verify():
    if not os.path.exists(FILE_PATH):
        print(f"❌ Error: File {FILE_PATH} does not exist.")
        sys.exit(1)
    
    with open(FILE_PATH, 'r') as f:
        content = f.read()
        
    # Verification 1: Check for required HTML tags
    required_tags = ["<!DOCTYPE html>", "<body>", "<canvas>", "<script>"]
    for tag in required_tags:
        if tag not in content:
            print(f"❌ Error: Missing {tag}")
            sys.exit(1)

    # Verification 2: Check for existence of critical CSS/JS IDs
    required_ids = ["gameCanvas", "stats-box", "status-text"]
    for id_el in required_ids:
        if f"id='{id_el}'" not in content and f"id=\"{id_el}\"" not in content:
            print(f"❌ Error: Missing ID {id_el}")
            sys.exit(1)

    # Verification 3: Check for common classes/consts from the original logic
    required_logic = ["MASY_TEMPLATE", "KMP", "bruteForce"]
    # Note: We look for strings that appear in the JS part
    found_all = True
    for item in required_logic:
        if item.upper() not in content.upper():
             print(f"⚠️ Warning: {item} not found in source.")
             found_all = False
           
    if found_all:
        print("✅ Verification Successful: index.html exists and contains core game infrastructure.")
    else:
        sys.exit(1)

if __name__ == "__main__":
    verify()
