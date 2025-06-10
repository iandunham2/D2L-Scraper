import os
import re
import csv
from bs4 import BeautifulSoup
import pandas as pd
import glob

class DiscussionProcessor:
    def __init__(self, base_dir='.'):
        self.base_dir = base_dir
        self.output_file = os.path.join(self.base_dir, 'processed_discussions.csv')
        self.all_posts = []

    def process_html_file(self, filename):
        """Process a single HTML file and extract discussion posts and replies."""
        with open(filename, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find the main post and replies
        posts = []
        post_container = soup.find('div', id='threadDataList')
        if post_container:
            # Find main post
            main_post = post_container.find('div', class_='d2l-htmlblock-untrusted')
            if main_post:
                # Extract author from profile handle
                author_handle = post_container.find('div', class_='d2l-user-profile-handle')
                if author_handle:
                    # Get the actual name from the profile handle
                    name_element = author_handle.find('span', class_='d2l-offscreen')
                    if name_element:
                        author_name = name_element.text.replace('View profile card for ', '').strip()
                    else:
                        author_name = "Unknown Author"
                else:
                    author_name = "Unknown Author"
                
                # Get post content from the HTML block
                post_content = post_container.find('div', class_='d2l-htmlblock-untrusted')
                if post_content:
                    post_text = post_content.find('d2l-html-block').get('html')
                    if not post_text:
                        post_text = post_content.text.strip()
                    post_text = ' '.join(post_text.split())
                else:
                    post_text = ""
            
                # Add main post
                posts.append({
                    'author': author_name,
                    'post': post_text,
                    'replies': []
                })
                
                # Find replies
                reply_containers = post_container.find_all('div', class_='d2l-discussion-post-content')
                for reply in reply_containers:
                    # Extract reply author
                    reply_author_handle = reply.find('div', class_='d2l-user-profile-handle')
                    if reply_author_handle:
                        name_element = reply_author_handle.find('span', class_='d2l-offscreen')
                        if name_element:
                            reply_author = name_element.text.replace('View profile card for ', '').strip()
                        else:
                            reply_author = "Unknown Author"
                    else:
                        reply_author = "Unknown Author"
                    
                    # Get reply content from HTML block
                    reply_content = reply.find('div', class_='d2l-htmlblock-untrusted')
                    if reply_content:
                        reply_text = reply_content.find('d2l-html-block').get('html')
                        if not reply_text:
                            reply_text = reply_content.text.strip()
                        reply_text = ' '.join(reply_text.split())
                    else:
                        reply_text = reply.text.strip()
                    
                    # Add reply to the main post's replies list
                    posts[0]['replies'].append({
                        'author': reply_author,
                        'reply': reply_text
                    })
        
        return posts

    def process_all_files(self):
        """Process all HTML files and write to CSV."""
        # Get list of HTML files
        html_files = sorted(glob.glob('post_page_*.html'))
        
        # Process files and collect posts
        all_posts = []
        for filename in html_files:
            print(f"Processing file: {filename}")
            posts = self.process_html_file(filename)
            all_posts.extend(posts)
        
        # Write to CSV
        with open('processed_discussions.csv', 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Author', 'Post', 'Reply']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            
            # Process all posts
            for post in all_posts:
                # Write main post
                writer.writerow({
                    'Author': post['author'],
                    'Post': post['post'],
                    'Reply': ''
                })
                
                # Write replies
                for reply in post['replies']:
                    writer.writerow({
                        'Author': reply['author'],
                        'Post': '',
                        'Reply': reply['reply']
                    })

        print(f"Saved {len(all_posts)} posts to {os.path.abspath('processed_discussions.csv')}")

if __name__ == "__main__":
    processor = DiscussionProcessor()
    processor.process_all_files()
