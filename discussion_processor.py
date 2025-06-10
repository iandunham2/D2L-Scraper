import os
import csv
from bs4 import BeautifulSoup
import glob
import re
import html
import json
from datetime import datetime
from typing import List, Dict, Optional
import glob

class DiscussionProcessor:
    def __init__(self):
        pass

    def clean_text(self, text):
        """Clean text by removing HTML tags, entities, and extra whitespace."""
        if not text:
            return ""
        # Replace HTML entities
        text = text.replace('&#39;', "'")
        text = text.replace('&#160;', ' ')
        text = text.replace('&quot;', '"')
        text = text.replace('&amp;', '&')
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text

    def extract_post_content(self, container):
        """Extract post content from container."""
        if not container:
            return ''
        
        # Find the content div
        content_div = container.find('div', class_='d2l-htmlblock-untrusted')
        if content_div:
            # Find the d2l-html-block element
            html_block = content_div.find('d2l-html-block')
            if html_block:
                # Get the HTML content from the 'html' attribute
                html_content = html_block.get('html', '')
                if html_content:
                    # Parse the HTML content to extract text
                    from bs4 import BeautifulSoup
                    inner_soup = BeautifulSoup(html_content, 'html.parser')
                    return self.clean_text(inner_soup.get_text())
        
        return ''

    def extract_author_name(self, container):
        """Extract author name from post container. For main post, look in page title section."""
        # First try the page title section for main post
        page_title = container.find('h2', class_='d2l-page-title')
        if page_title:
            print(f"Found page title: {page_title}")
            # Look for the profile handle in the page title section
            profile_handle = page_title.find_previous_sibling('div', class_='d2l-user-profile-handle')
            if profile_handle:
                print(f"Found profile handle: {profile_handle}")
                # Look for the profile card text
                profile_card = profile_handle.find('span', class_='d2l-offscreen')
                if profile_card:
                    print(f"Found profile card: {profile_card.text}")
                    # Extract the author name from the profile card text
                    text = profile_card.text.strip()
                    if "View profile card for" in text:
                        # Extract the name from the profile card text
                        author_name = text.replace("View profile card for ", "").strip()
                        print(f"Extracted author from profile card: {author_name}")
                        return author_name

        # If not found in page title section, try the thread status section
        status_section = container.find('div', class_='d2l-thread-statuses-container')
        if status_section:
            print(f"Found status section: {status_section}")
            # Look for the text block that contains the author name
            text_block = status_section.find('div', class_='d2l-textblock d2l-textblock-secondary vui-emphasis')
            if text_block:
                print(f"Found text block: {text_block.text}")
                # Extract the author name from the text (it's the first part before "posted")
                text = text_block.text.strip()
                if "posted" in text:
                    # Split on "posted" and take the first part
                    author_name = text.split(" posted ")[0]
                    # Clean up the author name
                    print(f"Extracted author from status: {author_name}")
                    return author_name.strip().rstrip(',. ').strip()

        # If still not found, try the profile handle
        profile_handle = container.find('div', class_='d2l-user-profile-handle')
        if profile_handle:
            print(f"Found profile handle: {profile_handle}")
            # Look for the profile card text
            profile_card = profile_handle.find('span', class_='d2l-offscreen')
            if profile_card:
                print(f"Found profile card: {profile_card.text}")
                # Extract the author name from the profile card text
                text = profile_card.text.strip()
                if "View profile card for" in text:
                    # Extract the name from the profile card text
                    author_name = text.replace("View profile card for ", "").strip()
                    print(f"Extracted author from profile card: {author_name}")
                    return author_name

            # If no profile card found, try the alt text in the profile image
            img = profile_handle.find('img')
            if img and 'alt' in img.attrs:
                print(f"Found profile image alt: {img['alt']}")
                return img['alt'].strip()
            
            # If no alt text, try the profile handle ID
            if 'data-d2l-pid' in profile_handle.attrs:
                pid = profile_handle['data-d2l-pid']
                print(f"Found profile handle ID: {pid}")
                # Try to find the profile handle with this ID
                handle_with_pid = container.find('div', {'class': 'd2l-user-profile-handle', 'data-d2l-pid': pid})
                if handle_with_pid:
                    # Look for the profile card text again
                    profile_card = handle_with_pid.find('span', class_='d2l-offscreen')
                    if profile_card:
                        print(f"Found profile card from PID: {profile_card.text}")
                        text = profile_card.text.strip()
                        if "View profile card for" in text:
                            author_name = text.replace("View profile card for ", "").strip()
                            print(f"Extracted author from PID profile card: {author_name}")
                            return author_name

        # If still not found, try to find author in post header
        post_header = container.find('div', class_='d2l-discussions-post-header')
        if post_header:
            print(f"Found post header: {post_header}")

    def process_html_file(self, filename):
        """Process a single HTML file and extract posts and replies."""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                html_content = f.read()
            soup = BeautifulSoup(html_content, 'html.parser')
            if 'topic_page' in filename:
                return []
            main_post = {}
            # Look for post content in either d2l-htmlblock or d2l-htmlblock-untrusted
            main_content = soup.find('div', class_=lambda x: x and ('d2l-htmlblock' in x or 'd2l-htmlblock-untrusted' in x))
            if main_content:
                # Clean the text by removing HTML tags and extra whitespace
                text = main_content.get_text().strip()
                if text:
                    main_post['post'] = self.clean_text(text)
                else:
                    print(f"Found empty main post content in {filename}")
                
                # Find the author name in the profile handle
                profile_handle = soup.find('div', class_='d2l-user-profile-handle-image')
                if profile_handle:
                    # Look for the offscreen text that contains the author name
                    offscreen_text = profile_handle.find('span', class_='d2l-offscreen')
                    if offscreen_text:
                        text = offscreen_text.text.strip()
                        if "View profile card for" in text:
                            # Extract the name from the text
                            author_name = text.replace("View profile card for", "").strip()
                            main_post['author'] = author_name
                            print(f"Found main post author: {main_post['author']}")
                        else:
                            print(f"No author name in offscreen text: {text}")
                    else:
                        print("No offscreen text found in profile handle")
                else:
                    print("No profile handle found")
            else:
                print("No main post content found")

            post_container = soup.find('div', id='threadDataList')
            if not post_container:
                print(f"No post container found in {filename}")
                return []

            replies = []
            reply_containers = post_container.find_all('div', class_='d2l-le-disc-reply')
            for reply_container in reply_containers:
                reply_author = self.extract_author_name(reply_container)
                reply_text = self.extract_post_content(reply_container)
                if reply_text and reply_author:  # Only include replies with both author and content
                    replies.append({'author': reply_author, 'post': self.clean_text(reply_text)})
                elif reply_text:
                    print(f"Found reply with no author in {filename}")
                elif reply_author:
                    print(f"Found reply with no content in {filename}")

            # Combine main post and replies
            if main_post and 'author' in main_post:
                main_post['replies'] = replies
                return [main_post]
            else:
                print(f"Skipping {filename} due to missing author")
                return []

        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")
            return []

                                ])

        # Read and sort the CSV
        with open(filename, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            sorted_rows = sorted(reader, key=lambda x: (x['Post Author'], x['Reply Author']))

        # Write sorted CSV
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Post Author', 'Post Content', 'Reply Author', 'Reply Content', 'Main Post ID'])
            for row in sorted_rows:
                writer.writerow([
                    row['Post Author'],
                    row['Post Content'],
                    row['Reply Author'],
                    row['Reply Content'],
                    row['Main Post ID']
                ])

        return posts

if __name__ == "__main__":
    import sys
    import os
    
    # Get the directory containing the script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, "data")
    
    # Process all HTML files in the data directory
    html_files = glob.glob(os.path.join(data_dir, "*.html"))
    
    if not html_files:
        print("No HTML files found in the data directory")
        sys.exit(1)

    processor = DiscussionProcessor()
    all_posts = []
    
    # Process each file
    for filename in html_files:
        print(f"Processing {filename}...")
        posts = processor.process_html_file(filename)
        all_posts.extend(posts)
    
    # Write all posts to a single CSV file
    output_file = os.path.join(script_dir, "all_discussions.csv")
    
    # First write all posts and replies
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Post Author', 'Post Content', 'Reply Author', 'Reply Content', 'Main Post ID'])
        
        for post in all_posts:
            # Write main post
            if 'author' in post and 'post' in post:
                writer.writerow([
                    post['author'],
                    post['post'],
                    '',  # Empty reply author for main post
                    '',  # Empty reply content for main post
                    post['author']  # Main post ID (using author as unique identifier)
                ])
                
                # Write replies
                if 'replies' in post:
                    for reply in post['replies']:
                        if 'author' in reply and 'post' in reply:
                            writer.writerow([
                                '',  # Empty post author for reply
                                '',  # Empty post content for reply
                                reply['author'],
                                reply['post'],
                                post['author']  # Main post ID
                            ])

    # Read and sort the CSV
    with open(output_file, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        sorted_rows = sorted(reader, key=lambda x: (x['Post Author'], x['Reply Author']))

    # Write sorted CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Post Author', 'Post Content', 'Reply Author', 'Reply Content', 'Main Post ID'])
        for row in sorted_rows:
            writer.writerow([
                row['Post Author'],
                row['Post Content'],
                row['Reply Author'],
                row['Reply Content'],
                row['Main Post ID']
            ])
    
    print(f"Processed {len(all_posts)} posts and wrote to {output_file}")
