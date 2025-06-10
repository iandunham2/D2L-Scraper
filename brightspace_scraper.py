import os
import glob
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd
from datetime import datetime

class BrightspaceDiscussionScraper:
    def __init__(self, course_url="https://kennesaw.view.usg.edu/d2l/home/3428449"):
        """
        Initialize the scraper with the course URL.
        
        Args:
            course_url (str): The URL of the course to scrape.
        """
        self.course_url = course_url
        self.base_url = course_url
        self.driver = None
        self.cleanup_old_data()
        print(f"\nUsing course URL: {self.course_url}")
        print(f"Using base URL: {self.base_url}")

    def cleanup_old_data(self):
        """Delete any existing data files from previous runs"""
        print("\nCleaning up old data files...")
        try:
            # Delete HTML files
            html_files = glob.glob(os.path.join("data", "*.html"))
            for file in html_files:
                os.remove(file)
                print(f"Deleted: {file}")
            
            # Delete text files
            txt_files = glob.glob(os.path.join("data", "*.txt"))
            for file in txt_files:
                os.remove(file)
                print(f"Deleted: {file}")
            
            print("\nOld data files cleaned up")
        except Exception as e:
            print(f"\nWarning: Error cleaning up old data: {str(e)}")
        
    def setup_driver(self):
        """
        Set up Chrome WebDriver with necessary options
        """
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        
        options = Options()
        options.add_argument('--start-maximized')
        options.add_argument('--disable-notifications')
        options.add_argument('--remote-debugging-port=9222')
        
        # Set up ChromeService
        service = Service()
        
        # Use system Chrome browser
        self.driver = webdriver.Chrome(service=service, options=options)
        
    def login(self):
        """
        Navigate to login page and wait for manual navigation to discussions
        """
        print("Starting Brightspace Discussion Scraper...")
        print("Please have your Duo MFA device ready to approve the push notification.")
        print(f"\nNavigating to: {self.course_url}")
        self.driver.get(self.course_url)
        print("\nPlease log in manually:")
        print("1. Enter your username and password")
        print("2. Approve the Duo MFA push notification on your device")
        input("\nPress Enter after you've logged in...")
        
        # Navigate to discussions page
        discussions_url = f"{self.course_url.replace('/home/', '/le/')}/discussions/List"
        print(f"\nNavigating to discussions page: {discussions_url}")
        self.driver.get(discussions_url)
        print("\nWaiting for discussions page to load...")
        time.sleep(10)
        
        # Add explicit wait for discussion topics
        try:
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='discussion-topic'], a[href*='/discussions/topics/']"))
            )
        except Exception as e:
            print(f"\nError waiting for discussion topics: {str(e)}")
            print(f"\nCurrent URL: {self.driver.current_url}")
            print(f"\nPage title: {self.driver.title}")
            
            # Save error page for debugging
            error_file = f"error_page_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            error_path = os.path.join("data", error_file)
            with open(error_path, 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
            print(f"\nSaved error page to: {error_path}")
        
        # Verify we're on the right page by checking for discussion topics
        try:
            topics = self.driver.find_elements(By.CSS_SELECTOR, "[class*='discussion-topic'], a[href*='/discussions/topics/']")
            if topics:
                print(f"\nFound {len(topics)} discussion topics on the page")
            else:
                print("\nWarning: No discussion topics found - please verify you're on the correct discussions page")
        except Exception as e:
            print(f"\nError verifying discussions page: {str(e)}")
        
        print("\nStarting page collection...")
            

            
    def wait_for_dynamic_content(self):
        """Wait for all dynamic content to load"""
        # Wait for initial load
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "d2l-discussion-post"))
        )
        
        # Wait for AJAX calls to complete
        WebDriverWait(self.driver, 10).until(
            lambda driver: driver.execute_script("return jQuery.active == 0")
        )
        
        # Scroll to bottom to trigger lazy loading
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Wait for content to load
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        
        # Wait for any final AJAX calls
        time.sleep(2)  # Give extra time for all content to load
        
    def collect_discussion_data(self):
        """
        Collect discussion data from Brightspace by navigating through discussions
        """
        try:
            # We're already on the discussions list page
            print("\nStarting from discussions list page...")
            
            # Wait for discussion topics to load
            print("\nWaiting for discussion topics to load...")
            time.sleep(10)  # Give it plenty of time to load
            
            # Find and collect all topic URLs
            selectors = [
                "a[href*='/discussions/topics/']",
                "[class*='discussion-topic']",
                "[class*='discussion-item']",
                "a.d2l-linkheading-link"
            ]
            topic_urls = []
            for selector in selectors:
                try:
                    print(f"\nTrying topic selector: {selector}")
                    topics = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if topics:
                        print(f"Found topics with selector: {selector}")
                        for topic in topics:
                            try:
                                topic_url = topic.get_attribute('href')
                                topic_urls.append(topic_url)
                            except Exception as e:
                                print(f"Error getting topic URL: {str(e)}")
                                continue
                        break
                except Exception as e:
                    print(f"Selector {selector} failed: {str(e)}")
                    continue
            if not topic_urls:
                raise Exception("Could not find any discussion topics")
            
            # Process each topic URL
            for topic_url in topic_urls:
                try:
                    print(f"\nProcessing topic: {topic_url}")
                    # Navigate directly to the topic
                    self.driver.get(topic_url)
                    time.sleep(10)  # Wait for topic page to load
                    
                    # Save the topic page
                    topic_file = f"topic_page_{topic_url.split('/')[-1]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
                    topic_path = os.path.join("data", topic_file)
                    with open(topic_path, 'w', encoding='utf-8') as f:
                        content_area = self.driver.find_element(By.TAG_NAME, 'body')
                        f.write(content_area.get_attribute('innerHTML'))
                    print(f"\nSaved topic page to: {topic_path}")
                    
                    # Wait for posts to load
                    print("\nWaiting for posts to load...")
                    time.sleep(10)  # Give it time to load
                    
                    # Find posts within this topic
                    print("\nFinding posts...")
                    post_selectors = [
                        "a[href*='/discussions/posts/']",
                        "[class*='discussion-post']",
                        "[class*='discussion-reply']",
                        "a.d2l-linkheading-link"
                    ]
                    
                    posts = []
                    for selector in post_selectors:
                        try:
                            print(f"\nTrying post selector: {selector}")
                            posts = self.driver.find_elements(By.CSS_SELECTOR, selector)
                            if posts:
                                print(f"Found posts with selector: {selector}")
                                break
                        except Exception as e:
                            print(f"Post selector {selector} failed: {str(e)}")
                            continue
                    
                    if not posts:
                        print("\nNo posts found in this topic")
                        continue
                    
                    # First collect all post URLs
                    post_urls = []
                    for post in posts:
                        try:
                            post_url = post.get_attribute('href')
                            post_urls.append(post_url)
                        except Exception as e:
                            print(f"\nError getting post URL: {str(e)}")
                            continue
                    
                    # Process each post URL
                    for post_url in post_urls:
                        try:
                            print(f"\nProcessing post: {post_url}")
                            
                            # Navigate to the post
                            self.driver.get(post_url)
                            time.sleep(10)  # Wait for post page to load
                            
                            # Wait for post content and replies to load
                            print("\nWaiting for post content and replies to load...")
                            time.sleep(10)  # Give it time to load
                            
                            # Save the post page with replies
                            post_file = f"post_page_{post_url.split('/')[-1]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
                            post_path = os.path.join("data", post_file)
                            with open(post_path, 'w', encoding='utf-8') as f:
                                content_area = self.driver.find_element(By.TAG_NAME, 'body')
                                f.write(content_area.get_attribute('innerHTML'))
                            print(f"\nSaved post page with replies to: {post_path}")
                            
                            # Print the content directly to console
                            print("\nPost Content:")
                            print(content_area.text)
                            
                            # Save topic information in a separate file
                            topic_file = f"topic_{topic_url.split('/')[-1]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                            topic_path = os.path.join("data", topic_file)
                            with open(topic_path, 'a', encoding='utf-8') as f:
                                f.write(f"\nPost URL: {post_url}\n")
                                f.write(f"Post Content:\n{content_area.text}\n\n")
                            
                        except Exception as e:
                            print(f"\nError processing post: {str(e)}")
                            continue
                    
                    # Go back to discussions list
                    self.driver.back()
                    time.sleep(5)  # Wait for page to reload
                    
                except Exception as e:
                    print(f"\nError processing topic: {str(e)}")
                    continue
            
            print("\nSuccessfully completed post collection")
            
        except Exception as e:
            print(f"\nError collecting discussion data: {str(e)}")
            # Save error page source
            error_file = f"error_page_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            error_path = os.path.join("data", error_file)
            with open(error_path, 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
            print(f"Saved error page source to: {error_path}")
            raise
        
    def cleanup(self):
        """
        Close the browser
        """
        if self.driver:
            self.driver.quit()
            
    def run(self):
        """
        Main execution method
        """
        try:
            self.setup_driver()
            self.login()
            self.collect_discussion_data()
            
        except Exception as e:
            print(f"Error during execution: {str(e)}")
            
        finally:
            self.cleanup()

if __name__ == "__main__":
    # Initialize scraper with course URL
    scraper = BrightspaceDiscussionScraper(
        course_url="https://kennesaw.view.usg.edu/d2l/home/3428449"
    )
    
    print("Starting Brightspace Discussion Scraper...")
    print("Please have your Duo MFA device ready to approve the push notification.")
    scraper.run()
