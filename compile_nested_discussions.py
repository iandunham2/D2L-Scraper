import os
import glob
import csv
import re
from bs4 import BeautifulSoup

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
OUTPUT_FILE = os.path.join(DATA_DIR, 'nested_discussions.csv')


def extract_posts(file_path):
    """Extract main post and replies from a Brightspace discussion HTML file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        html = f.read()
    soup = BeautifulSoup(html, 'html.parser')
    blocks = soup.find_all('div', class_='d2l-htmlblock-untrusted')
    if not blocks:
        return None

    def get_text(block):
        html_attr = block.find('d2l-html-block')
        if not html_attr:
            return ''
        html_content = html_attr.get('html', '')
        return BeautifulSoup(html_content, 'html.parser').get_text(separator=' ', strip=True)

    def get_author(block):
        span = block.find_previous('span', string=re.compile('View profile card'))
        if span:
            return span.get_text().replace('View profile card for', '').strip()
        return ''

    main_author = get_author(blocks[0])
    main_post = get_text(blocks[0])
    replies = []
    for block in blocks[1:]:
        reply_author = get_author(block)
        reply_text = get_text(block)
        if reply_author or reply_text:
            replies.append(f"{reply_author}: {reply_text}")

    return {
        'Author': main_author,
        'Post': main_post,
        'Replies': replies
    }


def compile_discussions():
    html_files = sorted(glob.glob(os.path.join(DATA_DIR, 'post_page_*.html')))
    discussions = []
    max_replies = 0
    for file_path in html_files:
        data = extract_posts(file_path)
        if data:
            discussions.append(data)
            if len(data['Replies']) > max_replies:
                max_replies = len(data['Replies'])

    fieldnames = ['Author', 'Post'] + [f'Reply_{i+1}' for i in range(max_replies)]

    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for disc in discussions:
            row = {
                'Author': disc['Author'],
                'Post': disc['Post'],
            }
            for i in range(max_replies):
                row[f'Reply_{i+1}'] = disc['Replies'][i] if i < len(disc['Replies']) else ''
            writer.writerow(row)

    print(f"Saved {len(discussions)} discussions to {OUTPUT_FILE}")


if __name__ == '__main__':
    compile_discussions()
