import sys
import pandas as pd
import lxml.html as html
from bs4 import BeautifulSoup
import requests
import os

def extract_post(post, parent_id=None):
    """Extract a post and its replies recursively."""
    post_id = post.get('data-postid')
    
    # Get author and date
    author_date = post.xpath('.//div[contains(@class, "d2l-textblock-secondary")]')
    if author_date:
        author_text = author_date[0].text.strip()
        author = author_text.split('posted')[0].strip()
        date = author_text.split('posted')[1].strip()
    else:
        author = "Unknown Author"
        date = "Unknown Date"
    
    # Get content
    html_block = post.xpath('.//d2l-more-less//d2l-htmlblock-untrusted//d2l-html-block')
    if not html_block:
        html_block = post.xpath('.//d2l-more-less//d2l-html-block')
    
    content = ""
    if html_block and 'html' in html_block[0].attrib:
        raw_html = html_block[0].attrib['html']
        soup = BeautifulSoup(raw_html, 'html.parser')
        content = soup.get_text()
        content = content.strip()
        content = '\n'.join(line.strip() for line in content.splitlines() if line.strip())
    
    # Create base post data
    post_data = {
        'post_id': post_id,
        'parent_id': parent_id,
        'author': author,
        'date': date,
        'content': content,
        'level': len(post.getparent().xpath('ancestor::div[contains(@class, "d2l-le-disc-post")]'))
    }
    
    # Find replies (nested posts)
    replies = []
    # Check for replies in the thread counts section
    reply_counts = post.xpath('.//div[contains(@class, "d2l-thread-reply-counts")]')
    if reply_counts:
        reply_count = reply_counts[0].xpath('.//div[contains(@class, "d2l-textblock-secondary") and contains(text(), "Replies")]')
        if reply_count:
            count_text = reply_count[0].text.strip()
            reply_count = int(count_text.split()[0])
            if reply_count > 0:
                # If there are replies, we need to visit the thread page
                thread_url = post.xpath('.//a[contains(@class, "d2l-linkheading-link")]/@href')
                if thread_url:
                    thread_url = thread_url[0]
                    print(f"\nFound thread with replies: {thread_url}")
                    # For now, just note that we found a thread with replies
                    post_data['thread_url'] = thread_url
                    post_data['has_replies'] = True
    
    return [post_data]

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <html_file>")
        sys.exit(1)
    
    html_file = sys.argv[1]
    print(f"\nAnalyzing HTML file: {html_file}")
    
    # Parse the HTML file
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    tree = html.fromstring(html_content)
    
    # Find all post containers
    posts = tree.xpath('//div[contains(@class, "d2l-le-disc-post")]')
    print(f"\nFound {len(posts)} top-level post containers")
    
    # Process each post
    all_posts = []
    for i, post in enumerate(posts, 1):
        print(f"\nProcessing post {i} (ID: {post.get('data-postid')})")
        post_data = extract_post(post)
        all_posts.extend(post_data)
        
        # If this post has replies, print its thread URL
        if post_data[0].get('has_replies'):
            thread_url = post_data[0].get('thread_url')
            print(f"Thread URL: {thread_url}")
            print(f"Full URL would be: https://your-domain.com{thread_url}")
    
    # Convert to DataFrame
    df = pd.DataFrame(all_posts)
    
    # Save to CSV
    csv_file = os.path.join('data', 'discussion_threads.csv')
    df.to_csv(csv_file, index=False)
    print(f"\nTotal posts (including replies) extracted: {len(df)}")
    print(f"\nSaved discussion threads to {csv_file}")
    
    # Print sample of data
    print("\nSample of extracted data:")
    print(df.head())


if __name__ == "__main__":
    main()
    print("\nNo posts were extracted. Check the HTML structure.")
