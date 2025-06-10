from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd
from datetime import datetime
import json
import os

class BrightspaceDiscussionScraper:
    def __init__(self, username, password, course_url):
        """
        Initialize the scraper with login credentials and course URL
        """
        self.username = username
        self.password = password
        self.course_url = course_url
        self.driver = None
        
    def setup_driver(self):
        """
        Set up Chrome WebDriver with necessary options
        """
        options = Options()
        options.add_argument('--start-maximized')
        options.add_argument('--disable-notifications')
        
        # Use system Chrome browser
        self.driver = webdriver.Chrome(options=options)
        
    def login(self):
        """
        Navigate to login page and enter credentials
        """
        print("Opening Chrome browser...")
        self.driver.get(self.course_url)
        
        print("Please log in manually:")
        print("1. Enter your username and password")
        print("2. Approve the Duo MFA push notification on your device")
        print("3. Wait for the browser to navigate to the course page")
        
        # Wait for user to complete login
        input("Press Enter after you've completed the login process...")
        
        # Verify we're on the course page
        print("Verifying course page...")
        try:
            # Check for course navigation elements
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "d2l-navigation"))
            )
            print("Successfully logged in and on course page!")
            
            # Wait for user to navigate to discussions
            print("\nPlease navigate manually to the discussions page.")
            print("Once you're on the discussions page:")
            print("1. The page should show all discussion threads")
            print("2. Each thread should have posts")
            print("3. You should see the full discussion content")
            
            input("\nPress Enter when you're on the discussions page...")
            
            # Print page information for debugging
            print("\nPage Information:")
            print(f"Current URL: {self.driver.current_url}")
            
            print("\nPage Elements:")
            # Print all elements with their tags and classes
            elements = self.driver.find_elements(By.XPATH, "//*")
            for idx, element in enumerate(elements, 1):
                try:
                    tag = element.tag_name
                    classes = element.get_attribute("class")
                    id = element.get_attribute("id")
                    text = element.text.strip()[:50]  # First 50 chars of text
                    print(f"{idx}. Tag: {tag}, Classes: {classes}, ID: {id}, Text: '{text}'")
                except:
                    continue
            
            print("\nPlease review the elements above and identify:")
            print("1. The container element for discussion threads")
            print("2. The elements for individual discussion posts")
            print("3. Any buttons needed to expand threads")
            
            input("\nPress Enter after reviewing the elements...")
            
        except Exception as e:
            print(f"Warning: Could not verify course page: {str(e)}")
            print("Please make sure you're logged in and on the correct course page.")
            input("Press Enter to continue if you're sure you're on the correct page...")
            
    def collect_discussion_data(self):
        """
        Collect discussion posts data from the current page
        """
        discussions = []
        
        try:
            print("\nDetailed page analysis:")
            print(f"Current URL: {self.driver.current_url}")
            
            # First, collect all topic links
            print("\nCollecting topic links...")
            topics = []
            
            # Wait for topics to load (using explicit wait)
            try:
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "tr.d2l-grid-row"))
                )
                
                # Get all topic rows
                topic_rows = self.driver.find_elements(By.CSS_SELECTOR, "tr.d2l-grid-row")
                print(f"Found {len(topic_rows)} topic rows")
                
                # Process only the first topic
                if topic_rows:
                    row = topic_rows[0]
                    try:
                        print("\nProcessing first topic")
                        
                        # Get topic title and link
                        title_element = row.find_element(By.CSS_SELECTOR, "h3.d2l-heading-3")
                        title = title_element.find_element(By.CSS_SELECTOR, "a.d2l-linkheading-link").text.strip()
                        topic_link = title_element.find_element(By.CSS_SELECTOR, "a.d2l-linkheading-link").get_attribute('href')
                        
                        # Get post count
                        post_count_element = row.find_element(By.CSS_SELECTOR, "[id^='topicPostsCountPlaceholderId']")
                        post_count = post_count_element.text.strip()
                        
                        # Store topic info
                        topic_data = {
                            'title': title,
                            'link': topic_link,
                            'post_count': post_count
                        }
                        topics.append(topic_data)
                        print(f"Found topic: {title} with {post_count} posts")
                        
                    except Exception as e:
                        print(f"Error processing first topic: {str(e)}")
                        return discussions
                
            except TimeoutException:
                print("\nTimed out waiting for topics to load. Trying alternative selector...")
                try:
                    # Try with table row last selector
                    WebDriverWait(self.driver, 20).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "tr.d2l-table-row-last"))
                    )
                    
                    # Get all topic rows
                    topic_rows = self.driver.find_elements(By.CSS_SELECTOR, "tr.d2l-table-row-last")
                    print(f"Found {len(topic_rows)} topic rows with alternative selector")
                    
                    # Process only the first topic
                    if topic_rows:
                        row = topic_rows[0]
                        try:
                            print("\nProcessing first topic")
                            
                            # Get topic title and link
                            title_element = row.find_element(By.CSS_SELECTOR, "h3.d2l-heading-3")
                            title = title_element.find_element(By.CSS_SELECTOR, "a.d2l-linkheading-link").text.strip()
                            topic_link = title_element.find_element(By.CSS_SELECTOR, "a.d2l-linkheading-link").get_attribute('href')
                            
                            # Get post count
                            post_count_element = row.find_element(By.CSS_SELECTOR, "[id^='topicPostsCountPlaceholderId']")
                            post_count = post_count_element.text.strip()
                            
                            # Store topic info
                            topic_data = {
                                'title': title,
                                'link': topic_link,
                                'post_count': post_count
                            }
                            topics.append(topic_data)
                            print(f"Found topic: {title} with {post_count} posts")
                            
                        except Exception as e:
                            print(f"Error processing first topic: {str(e)}")
                            return discussions
                    
                except TimeoutException:
                    print("\nTimed out with both selectors. Please check if you're on the correct page.")
                    return discussions
            
            if not topics:
                print("\nNo discussion topics found. Please check:")
                print("1. You're on the correct discussions page")
                print("2. There are discussion threads visible")
                print("3. The page structure might have changed")
                return discussions
                
            print(f"\nFound 1 topic. Processing it...")
            
            # Process the single topic
            topic = topics[0]
            try:
                print(f"\nProcessing topic: {topic['title']}")
                print(f"Navigating to: {topic['link']}")
                
                # Navigate to topic page
                self.driver.get(topic['link'])
                
                # First try with explicit wait
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div.d2l-discussion-post"))
                    )
                    print("Found posts using primary selector")
                    
                except TimeoutException:
                    print("Primary selector timed out, trying alternative selectors...")
                    
                    # Save complete page content for analysis
                    print("\nSaving complete page content for analysis...")
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    page_source = self.driver.page_source
                    
                    # Save HTML source
                    page_file = f"discussion_page_{timestamp}.html"
                    page_path = os.path.join("data", page_file)
                    with open(page_path, "w", encoding="utf-8") as f:
                        f.write(page_source)
                    print(f"Saved HTML source to {page_path}")
                    
                    # Save DOM structure using JavaScript
                    print("\nSaving DOM structure...")
                    script = """
                        function getDOMStructure(element, depth = 0) {
                            const result = {
                                tag: element.tagName,
                                classes: element.className,
                                id: element.id,
                                text: element.textContent.trim().substring(0, 200),
                                children: [],
                                attributes: {}
                            };
                            
                            // Get all attributes
                            const attrs = element.attributes;
                            for (let i = 0; i < attrs.length; i++) {
                                result.attributes[attrs[i].name] = attrs[i].value;
                            }
                            
                            // Get children
                            const children = element.children;
                            for (let i = 0; i < children.length; i++) {
                                result.children.push(getDOMStructure(children[i], depth + 1));
                            }
                            
                            return result;
                        }
                        
                        return getDOMStructure(document.body);
                    """
                    dom_structure = self.driver.execute_script(script)
                    
                    # Save DOM structure to JSON
                    with open(f"dom_structure_{timestamp}.json", "w", encoding="utf-8") as f:
                        json.dump(dom_structure, f, indent=2)
                    print(f"Saved DOM structure to dom_structure_{timestamp}.json")
                    
                    # Print some statistics about the page
                    print("\nPage statistics:")
                    total_elements = len(self.driver.find_elements(By.XPATH, "//*"))
                    total_divs = len(self.driver.find_elements(By.TAG_NAME, "div"))
                    print(f"Total elements: {total_elements}")
                    print(f"Total div elements: {total_divs}")
                    print(f"Total text content length: {len(page_source)}")
                    
                    # Look for discussion-related elements
                    print("\nLooking for discussion-related elements...")
                    script = """
                        let elements = [];
                        let allElements = document.getElementsByTagName('*');
                        for (let el of allElements) {
                            if (el.className) {
                                let classes = el.className.split(' ');
                                if (classes.some(cls => cls.includes('discussion') || 
                                                    cls.includes('post') || 
                                                    cls.includes('message'))) {
                                    elements.push({
                                        tag: el.tagName,
                                        classes: el.className,
                                        text: el.textContent.trim().substring(0, 200),
                                        attributes: Object.fromEntries(Array.from(el.attributes).map(attr => [attr.name, attr.value]))
                                    });
                                }
                            }
                        }
                        return elements;
                    """
                    discussion_elements = self.driver.execute_script(script)
                    print(f"\nFound {len(discussion_elements)} discussion-related elements")
                    
                    # Save discussion elements to file
                    with open(f"discussion_elements_{timestamp}.json", "w", encoding="utf-8") as f:
                        json.dump(discussion_elements, f, indent=2)
                    print(f"Saved discussion elements to discussion_elements_{timestamp}.json")
                    
                    # Try alternative post selectors with more variations
                    post_selectors = [
                        "div.d2l-le-disc-post",
                        "div.d2l-le-disc-post-border",
                        "div.d2l-le-disc-post-content",
                        "div.d2l_le_discussions_threadlistitem_subject",
                        "d2l-more-less",
                        "d2l-htmlblock-untrusted",
                        "div.d2l-textblock-secondary"
                    ]
                    
                    # Try to find posts using the exact structure we found in the HTML
                    try:
                        # First try to find the main post container
                        post_containers = self.driver.find_elements(By.CSS_SELECTOR, "div.d2l-le-disc-post")
                        print(f"\nFound {len(post_containers)} post containers")
                        
                        if post_containers:
                            # For each post container, try to find the content
                            for post in post_containers:
                                try:
                                    # Get the post content container
                                    content_container = post.find_element(By.CSS_SELECTOR, ".d2l-le-disc-posrev")
                                    
                                    # Get author and date
                                    author_date = content_container.find_element(By.CSS_SELECTOR, ".d2l-textblock-secondary")
                                    print(f"\nFound author/date: {author_date.text}")
                                    
                                    # Get the actual post content
                                    post_content = content_container.find_element(By.CSS_SELECTOR, "d2l-more-less")
                                    content = post_content.find_element(By.CSS_SELECTOR, "d2l-htmlblock-untrusted")
                                    print(f"\nFound content: {content.text[:200]}...")
                                    
                                    # Process the post
                                    posts.append({
                                        'author': author_date.text.split('posted')[0].strip(),
                                        'date': author_date.text.split('posted')[1].strip(),
                                        'content': content.text
                                    })
                                    
                                except Exception as e:
                                    print(f"Error processing post: {str(e)}")
                                    continue
                        
                    except Exception as e:
                        print(f"Error finding posts: {str(e)}")
                        
                    # If we didn't find posts, try the alternative selectors
                    if not posts:
                        print("\nNo posts found with main structure, trying alternative selectors...")
                        for selector in post_selectors:
                            try:
                                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                                print(f"\nChecking selector: {selector}")
                                print(f"Found {len(elements)} elements")
                                
                                if elements:
                                    # Print details of first element
                                    first = elements[0]
                                    print(f"\nFirst element details:")
                                    print(f"Classes: {first.get_attribute('class')}")
                                    print(f"Text: {first.text.strip()[:200]}")
                                    print(f"Attributes: {first.get_attribute('outerHTML')[:200]}")
                                    
                                    # Try to find author and date
                                    author = first.find_elements(By.CSS_SELECTOR, ".d2l-user-profile-handle")
                                    date = first.find_elements(By.CSS_SELECTOR, "abbr.d2l-fuzzydate")
                                    print(f"Found {len(author)} author elements")
                                    print(f"Found {len(date)} date elements")
                                    
                                    # Try alternative selectors for author and date
                                    if not author:
                                        print("Trying alternative author selectors...")
                                        author_selectors = [
                                            ".d2l-discussion-post-author",
                                            ".d2l-discussion-message-author",
                                            ".d2l-discussion-post-username",
                                            ".d2l-discussion-message-username",
                                            "[class*='author']",
                                            "[class*='username']",
                                            ".d2l-le-disc-post-author",
                                            ".d2l-textblock-secondary"
                                        ]
                                        for auth_sel in author_selectors:
                                            auth_elem = first.find_elements(By.CSS_SELECTOR, auth_sel)
                                            if auth_elem:
                                                print(f"Found author with selector {auth_sel}")
                                                author = auth_elem
                                                break
                                    
                                    if not date:
                                        print("Trying alternative date selectors...")
                                        date_selectors = [
                                            ".d2l-discussion-post-date",
                                            ".d2l-discussion-message-date",
                                            ".d2l-discussion-post-timestamp",
                                            ".d2l-discussion-message-timestamp",
                                            "[class*='date']",
                                            "[class*='timestamp']",
                                            "[class*='posted']",
                                            "[class*='replied']",
                                            "time",
                                            ".d2l-textblock-secondary"
                                        ]
                                        for date_sel in date_selectors:
                                            date_elem = first.find_elements(By.CSS_SELECTOR, date_sel)
                                            if date_elem:
                                                print(f"Found date with selector {date_sel}")
                                                date = date_elem
                                                break
                                    
                                    posts = elements
                                    print(f"Using selector {selector} with {len(posts)} posts")
                                    break
                            except Exception as e:
                                print(f"Error with selector {selector}: {str(e)}")
                                continue
                    
                    posts = []
                    for selector in post_selectors:
                        try:
                            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                            print(f"\nChecking selector: {selector}")
                            print(f"Found {len(elements)} elements")
                            
                            if elements:
                                # Print details of first element
                                first = elements[0]
                                print(f"\nFirst element details:")
                                print(f"Classes: {first.get_attribute('class')}")
                                print(f"Text: {first.text.strip()[:200]}")
                                print(f"Attributes: {first.get_attribute('outerHTML')[:200]}")
                                
                                # Try to find author and date
                                author = first.find_elements(By.CSS_SELECTOR, ".d2l-user-profile-handle")
                                date = first.find_elements(By.CSS_SELECTOR, "abbr.d2l-fuzzydate")
                                print(f"Found {len(author)} author elements")
                                print(f"Found {len(date)} date elements")
                                
                                # Try alternative selectors for author and date
                                if not author:
                                    print("Trying alternative author selectors...")
                                    author_selectors = [
                                        ".d2l-discussion-post-author",
                                        ".d2l-discussion-message-author",
                                        ".d2l-discussion-post-username",
                                        ".d2l-discussion-message-username",
                                        "[class*='author']",
                                        "[class*='username']",
                                        ".d2l-discussion-message-username",
                                        ".d2l-discussion-post-username",
                                        ".d2l-le-discussions-threadlistitem-author"
                                    ]
                                    for auth_sel in author_selectors:
                                        auth_elem = first.find_elements(By.CSS_SELECTOR, auth_sel)
                                        if auth_elem:
                                            print(f"Found author with selector {auth_sel}")
                                            author = auth_elem
                                            break
                                
                                if not date:
                                    print("Trying alternative date selectors...")
                                    date_selectors = [
                                        ".d2l-discussion-post-date",
                                        ".d2l-discussion-message-date",
                                        ".d2l-discussion-post-timestamp",
                                        ".d2l-discussion-message-timestamp",
                                        "[class*='date']",
                                        "[class*='timestamp']",
                                        "[class*='posted']",
                                        "[class*='replied']",
                                        "time"
                                    ]
                                    for date_sel in date_selectors:
                                        date_elem = first.find_elements(By.CSS_SELECTOR, date_sel)
                                        if date_elem:
                                            print(f"Found date with selector {date_sel}")
                                            date = date_elem
                                            break
                                
                                posts = elements
                                print(f"Using selector {selector} with {len(posts)} posts")
                                break
                        except Exception as e:
                            print(f"Error with selector {selector}: {str(e)}")
                            continue
                        
                    if not posts:
                        print("\nNo posts found with any selector")
                        print("\nChecking for iframe content...")
                        iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
                        print(f"Found {len(iframes)} iframes")
                        for i, iframe in enumerate(iframes):
                            try:
                                self.driver.switch_to.frame(iframe)
                                iframe_posts = self.driver.find_elements(By.CSS_SELECTOR, "div.d2l-discussion-post")
                                print(f"\nChecking iframe {i+1}")
                                print(f"Found {len(iframe_posts)} posts in iframe")
                                if iframe_posts:
                                    posts = iframe_posts
                                    print(f"Found posts in iframe {i+1}")
                                    break
                            except Exception as e:
                                print(f"Error checking iframe {i+1}: {str(e)}")
                            finally:
                                self.driver.switch_to.default_content()
                        
                        if not posts:
                            print("\nNo posts found in iframes either")
                            print("\nChecking for dynamic content loading...")
                            # Wait for any potential dynamic content
                            time.sleep(5)
                            # Try one more time with primary selector
                            try:
                                WebDriverWait(self.driver, 5).until(
                                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.d2l-discussion-post"))
                                )
                                posts = self.driver.find_elements(By.CSS_SELECTOR, "div.d2l-discussion-post")
                                print(f"\nFound {len(posts)} posts after waiting for dynamic content")
                            except:
                                print("No posts found after waiting for dynamic content")
                                
                            if not posts:
                                print("\nFinal attempt with full page source analysis...")
                                page_source = self.driver.page_source
                                if "d2l-discussion-post" in page_source:
                                    print("Found discussion post class in page source but couldn't locate elements")
                                else:
                                    print("No discussion post class found in page source")
                                    
                                print("\nCurrent URL:", self.driver.current_url)
                                print("\nPage title:", self.driver.title)
                                
                            return discussions
                
                # Process each post
                post_data = []
                for post in posts:
                    try:
                        # Get post details
                        author = post.find_element(By.CSS_SELECTOR, ".d2l-user-profile-handle").text.strip()
                        date = post.find_element(By.CSS_SELECTOR, "abbr.d2l-fuzzydate").text.strip()
                        content = post.find_element(By.CSS_SELECTOR, ".d2l-discussion-post-content").text.strip()
                        
                        post_data.append({
                            'author': author,
                            'date': date,
                            'content': content
                        })
                        print(f"Processed post by {author}")
                        
                    except Exception as e:
                        print(f"Error processing post: {str(e)}")
                        continue
                    
                # Add to discussions
                discussion = {
                    'title': topic['title'],
                    'post_count': topic['post_count'],
                    'posts': post_data
                }
                discussions.append(discussion)
                
            except TimeoutException as e:
                print(f"\nTimed out waiting for posts in {topic['title']}")
                return discussions
            except Exception as e:
                print(f"Error processing topic {topic['title']}: {str(e)}")
                return discussions
                
        except Exception as e:
            print(f"Error collecting discussion data: {str(e)}")
            raise
            
        return discussions
        
    def save_to_csv(self, discussions, output_file):
        """
        Save discussion data to a CSV file
        """
        posts_list = []
        for discussion in discussions:
            for post in discussion['posts']:
                posts_list.append({
                    'Topic': discussion['title'],
                    'Author': post['author'],
                    'Date': post['date'],
                    'Content': post['content']
                })
        
        df = pd.DataFrame(posts_list)
        df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"Data saved to {output_file}")
        
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
            
            # Collect and save data
            discussions = self.collect_discussion_data()
            if discussions:
                filename = f"brightspace_discussions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                output_file = os.path.join("data", filename)
                print(f"Saving discussions to {output_file}...")
                self.save_to_csv(discussions, output_file)
                print(f"Successfully saved discussions to {output_file}")
            else:
                print("No discussions found")
                
        except Exception as e:
            print(f"Error during execution: {str(e)}")
            
        finally:
            self.cleanup()

if __name__ == "__main__":
    # Initialize scraper
    scraper = BrightspaceDiscussionScraper(
        username="idunham",
        password="Asherelliot0192pqow!",
        course_url="https://kennesaw.view.usg.edu/d2l/home/3428449"
    )
    
    print("Starting Brightspace Discussion Scraper...")
    scraper.run()
