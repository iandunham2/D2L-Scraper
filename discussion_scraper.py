import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os

class BrightspaceDiscussionScraper:
    def __init__(self, username, password, course_url):
        self.username = username
        self.password = password
        self.course_url = course_url
        self.session = requests.Session()
        
    def login(self):
        """
        Attempt to login to Brightspace
        """
        try:
            # First get the login page to get any required cookies
            login_url = "https://kennesaw.view.usg.edu/d2l/lp/auth/login/login.d2l"
            response = self.session.get(login_url)
            
            # Extract any necessary form data from the login page
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Create login payload
            payload = {
                'userName': self.username,
                'password': self.password,
                'action': 'login'
            }
            
            # Submit login
            response = self.session.post(login_url, data=payload)
            
            # Check if login was successful
            if response.status_code == 200:
                print("Login successful")
                return True
            else:
                print(f"Login failed with status code: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Login failed: {str(e)}")
            return False
            
    def get_discussions(self):
        """
        Get discussion posts from the course
        """
        try:
            # Navigate to discussions page
            discussions_url = f"{self.course_url}/discussions"
            response = self.session.get(discussions_url)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find all discussion threads
                threads = soup.find_all('div', class_='d2l-discussion-thread')
                
                discussions = []
                for thread in threads:
                    thread_data = {
                        'title': thread.find('h3', class_='d2l-discussion-thread-title').text.strip(),
                        'author': thread.find('span', class_='d2l-discussion-thread-author').text.strip(),
                        'date': thread.find('span', class_='d2l-discussion-thread-date').text.strip(),
                        'posts': []
                    }
                    
                    # Find all posts in the thread
                    posts = thread.find_all('div', class_='d2l-discussion-post')
                    for post in posts:
                        post_data = {
                            'author': post.find('span', class_='d2l-discussion-post-author').text.strip(),
                            'date': post.find('span', class_='d2l-discussion-post-date').text.strip(),
                            'content': post.find('div', class_='d2l-discussion-post-content').text.strip()
                        }
                        thread_data['posts'].append(post_data)
                    
                    discussions.append(thread_data)
                
                return discussions
                
            else:
                print(f"Failed to get discussions page: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Error getting discussions: {str(e)}")
            return []
            
    def save_to_csv(self, discussions, output_file):
        """
        Save discussions to CSV file
        """
        try:
            posts_list = []
            for thread in discussions:
                for post in thread['posts']:
                    posts_list.append({
                        'Thread Title': thread['title'],
                        'Thread Author': thread['author'],
                        'Thread Date': thread['date'],
                        'Post Author': post['author'],
                        'Post Date': post['date'],
                        'Post Content': post['content']
                    })
            
            df = pd.DataFrame(posts_list)
            df.to_csv(output_file, index=False, encoding='utf-8')
            print(f"Data saved to {output_file}")
            
        except Exception as e:
            print(f"Error saving to CSV: {str(e)}")
            
    def run(self):
        """
        Main execution method
        """
        try:
            if self.login():
                discussions = self.get_discussions()
                if discussions:
                    output_file = f"brightspace_discussions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                    self.save_to_csv(discussions, output_file)
                else:
                    print("No discussions found")
            
        except Exception as e:
            print(f"Error during execution: {str(e)}")
            
if __name__ == "__main__":
    # Initialize scraper
    scraper = BrightspaceDiscussionScraper(
        username="idunham",
        password="Asherelliot0192pqow!",
        course_url="https://kennesaw.view.usg.edu/d2l/home/3428449"
    )
    
    print("Starting Brightspace Discussion Scraper...")
    scraper.run()
