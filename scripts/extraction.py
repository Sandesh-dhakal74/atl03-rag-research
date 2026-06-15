import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unstructured.partition.pdf import partition_pdf
from src.rag.config import ATL03_USER_GUIDE

def extract(pdf_path):
    print(f"Extracting: {pdf_path}")
    
    elements = partition_pdf(
        filename=str(pdf_path),
        strategy="fast",
    )
    
    print(f"\nTotal elements found: {len(elements)}")
    print(f"\n--- First 20 elements ---\n")
    
    for elem in elements[:20]:
        print(f"Type: {elem.category}")
        print(f"Text: {elem.text[:100]}")
        print(f"Page: {elem.metadata.page_number}")
        print("---")

if __name__ == "__main__":
    extract(ATL03_USER_GUIDE)