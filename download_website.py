import os
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import re

class WebsiteTextExtractor:
    def __init__(self, root_url, output_dir= "extracted_text", max_pages=100):
        """
        Initialize the website text extractor.
        
        :param root_url: The starting URL of the website
        :param output_dir: Directory to save extracted text
        :param max_pages: Maximum number of pages to extract
        """
        output_dir = root_url.replace("https://", "").replace(".", "_")
        self.root_url = root_url
        self.base_domain = urlparse(root_url).netloc
        self.output_dir = output_dir
        self.max_pages = max_pages
        self.visited_urls = set()
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

    def is_valid_url(self, url):
        """
        Check if the URL is valid and within the same domain.
        
        :param url: URL to validate
        :return: Boolean indicating if URL is valid
        """
        parsed_url = urlparse(url)
        return (parsed_url.netloc == self.base_domain or 
                parsed_url.netloc == '') and \
               parsed_url.scheme in ['http', 'https']

    def download_page(self, url):
        """
        Download the content of a single page.
        
        :param url: URL of the page to download
        :return: Downloaded content or None
        """
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error downloading {url}: {e}")
            return None

    def extract_clean_text(self, html_content):
        """
        Extract clean, readable text from HTML content with Markdown-like formatting.
        
        :param html_content: HTML content to parse
        :return: Extracted and cleaned text with formatting
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script, style, and navigation elements
        for script in soup(["script", "style", "nav", "header", "footer"]):
            script.decompose()
        
        # Helper function to convert HTML to Markdown-like formatting
        def convert_tag(tag):
            if tag.name == 'h1':
                return f"\n# {tag.get_text(strip=True)}\n"
            elif tag.name == 'h2':
                return f"\n## {tag.get_text(strip=True)}\n"
            elif tag.name == 'h3':
                return f"\n### {tag.get_text(strip=True)}\n"
            elif tag.name == 'h4':
                return f"\n#### {tag.get_text(strip=True)}\n"
            elif tag.name == 'h5':
                return f"\n##### {tag.get_text(strip=True)}\n"
            elif tag.name == 'h6':
                return f"\n###### {tag.get_text(strip=True)}\n"
            elif tag.name == 'strong' or tag.name == 'b':
                return f"**{tag.get_text(strip=True)}**"
            elif tag.name == 'em' or tag.name == 'i':
                return f"*{tag.get_text(strip=True)}*"
            elif tag.name == 'ul':
                return '\n' + '\n'.join(f"- {li.get_text(strip=True)}" for li in tag.find_all('li')) + '\n'
            elif tag.name == 'ol':
                return '\n' + '\n'.join(f"{i+1}. {li.get_text(strip=True)}" for i, li in enumerate(tag.find_all('li'))) + '\n'
            elif tag.name == 'blockquote':
                return f"\n> {tag.get_text(strip=True)}\n"
            elif tag.name == 'code':
                return f"`{tag.get_text(strip=True)}`"
            elif tag.name == 'pre':
                return f"\n```\n{tag.get_text(strip=True)}\n```\n"
            elif tag.name == 'p':
                return f"\n{tag.get_text(strip=True)}\n"
            return tag.get_text(strip=True)
        
        # Process the document with formatting
        formatted_text = []
        for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 
                                      'p', 'strong', 'b', 'em', 'i', 
                                      'ul', 'ol', 'blockquote', 
                                      'code', 'pre']):
            formatted_text.append(convert_tag(element))
        
        # Join and clean up text
        text = '\n'.join(formatted_text)
        text = re.sub(r'\n{3,}', '\n\n', text).strip()
        
        # Optional: Add some basic length filtering
        return text if len(text) > 100 else ''

    def save_text(self, url, text):
        """
        Save extracted text to a file.
        
        :param url: URL of the page
        :param text: Extracted text content
        """
        # Create filename from URL
        parsed_url = urlparse(url)
        path = parsed_url.path.strip('/')
        
        # Handle homepage or root
        if not path:
            path = 'index'
        
        # Replace invalid filename characters
        safe_path = path.replace('/', '_').replace('\\', '_')
        
        # Ensure unique filename
        filename = os.path.join(self.output_dir, f"{safe_path}.md")
        
        # Ensure unique filename if exists
        counter = 1
        while os.path.exists(filename):
            filename = os.path.join(self.output_dir, f"{safe_path}_{counter}.md")
            counter += 1
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(text)

    def extract_links(self, html_content, base_url):
        """
        Extract all links from HTML content.
        
        :param html_content: HTML content to parse
        :param base_url: Base URL for resolving relative links
        :return: Set of unique links
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        links = set()
        
        for a_tag in soup.find_all('a', href=True):
            link = urljoin(base_url, a_tag['href'])
            parsed_link = urlparse(link)
            
            # Remove fragment identifiers
            link = parsed_link._replace(fragment='').geturl()
            
            if self.is_valid_url(link):
                links.add(link)
        
        return links

    def extract_website_text(self):
        """
        Extract text from entire website starting from root URL.
        """
        to_visit = {self.root_url}
        
        while to_visit and len(self.visited_urls) < self.max_pages:
            current_url = to_visit.pop()
            
            if current_url in self.visited_urls:
                continue
            
            print(f"Extracting text from: {current_url}")
            
            content = self.download_page(current_url)
            
            if content:
                # Extract clean text
                text = self.extract_clean_text(content)
                
                # Save text if it's not empty
                if text:
                    self.save_text(current_url, text)
                
                self.visited_urls.add(current_url)
                
                # Extract and add new links
                new_links = self.extract_links(content, current_url)
                to_visit.update(link for link in new_links 
                                if link not in self.visited_urls)
        
        print(f"Extracted text from {len(self.visited_urls)} pages.")

def main():
    # Example usage
    root_url = 'https://likeminds.community'  # Replace with your target website
    extractor = WebsiteTextExtractor(root_url, max_pages=50)
    extractor.extract_website_text()

if __name__ == '__main__':
    main()


#self.output_dir = root_url.replace("https://", "").replace(".", "_")