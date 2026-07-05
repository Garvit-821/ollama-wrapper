"""
VISION AI Assistant - Surfing Test Verification Script
"""
from modules.web_search import web_search, read_webpage

def test_web_search():
    print("Testing programmatic DuckDuckGo search...")
    query = "artificial intelligence"
    results = web_search(query)
    
    # Check that we got back results and that they are structured as text
    assert results is not None
    assert "Title:" in results
    assert "URL:" in results
    assert "Snippet:" in results
    print("  [PASS] Web search programmatically returns results.") 
    
    # Extract first URL to test page reader
    lines = results.split("\n")
    url = None
    for line in lines:
        if line.startswith("URL:"):
            url = line.split("URL:")[1].strip()
            break
            
    assert url is not None
    print(f"  [INFO] Extracted first search URL: {url}")
    return url

def test_read_webpage(url):
    print(f"Testing webpage reader on: {url}")
    content = read_webpage(url)
    
    assert content is not None
    assert len(content) > 50
    print("  [PASS] Webpage reader successfully extracted text.")
    print(f"  [INFO] Extracted text length: {len(content)} chars.")
    print("  [INFO] Sample text:")
    print(f"  --- \n{content[:300].strip()}\n  ---")

if __name__ == "__main__":
    try:
        url = test_web_search()
        test_read_webpage(url)
        print("\nAll surfing verification tests PASSED!")
    except Exception as e:
        print(f"\nVerification failed: {e}")
        import sys
        sys.exit(1)
