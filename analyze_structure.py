from lxml import etree
import json

# Read and parse the HTML file
with open('discussion_page_20250606_154115.html', 'r', encoding='utf-8') as f:
    tree = etree.parse(f, etree.HTMLParser())

# Analyze the structure
structure = {}

def analyze_element(element, level=0):
    tag = element.tag
    if tag == 'script' or tag == 'style':
        return
    
    # Get element attributes
    attrs = dict(element.attrib)
    
    # Get text content
    text = element.text.strip() if element.text else ''
    
    # Get children
    children = []
    for child in element:
        child_data = analyze_element(child, level + 1)
        if child_data:
            children.append(child_data)
    
    # Create structure entry
    entry = {
        'tag': tag,
        'attributes': attrs,
        'text': text[:100] + '...' if len(text) > 100 else text,
        'children': children
    }
    
    # Print structure for debugging
    print('  ' * level + f"{tag}: {attrs}")
    if text:
        print('  ' * (level + 1) + f"Text: {text[:50]}")
    
    return entry

# Find all post containers
post_containers = tree.xpath('//div[contains(@class, "d2l-le-disc-post")]')
print(f"\nFound {len(post_containers)} post containers")

# Analyze the first post container in detail
if post_containers:
    print("\nAnalyzing first post container structure:")
    structure = analyze_element(post_containers[0])
    
    # Save structure analysis
    with open('structure_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(structure, f, indent=2)

# Find all more-less elements
more_less_elements = tree.xpath('//d2l-more-less')
print(f"\nFound {len(more_less_elements)} more-less elements")

# Find all HTML block elements
html_blocks = tree.xpath('//d2l-html-block')
print(f"\nFound {len(html_blocks)} HTML blocks")

# Print attributes of HTML blocks
for block in html_blocks:
    print("\nHTML Block Attributes:")
    print(json.dumps(dict(block.attrib), indent=2))
    
    # Try to decode the HTML content
    if 'html' in block.attrib:
        raw_html = block.attrib['html']
        print("\nRaw HTML content:")
        print(raw_html[:200] + '...')  # Print first 200 chars
        
        # Try different decoding approaches
        try:
            decoded = raw_html.encode().decode('unicode_escape')
            print("\nDecoded content:")
            print(decoded[:200] + '...')  # Print first 200 chars
        except Exception as e:
            print(f"Error decoding: {e}")
