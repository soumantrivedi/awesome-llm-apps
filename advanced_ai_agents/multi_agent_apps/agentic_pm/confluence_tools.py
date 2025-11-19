"""
Confluence Integration Tools for Agentic PM
Provides tools for publishing reports and documents to Confluence Wiki
"""

import os
import requests
import re
from typing import Dict, List, Optional, Any
from datetime import datetime


class ConfluenceTools:
    """Tools for interacting with Confluence API"""
    
    def __init__(self, confluence_url: str, email: str, api_token: str):
        if not all([confluence_url, email, api_token]):
            raise ValueError("Confluence URL, email, and API token are required")
        self.confluence_url = confluence_url.rstrip('/')
        self.email = email
        self.api_token = api_token
        self.auth = (email, api_token)
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    
    def get_space(self, space_key: str) -> Dict:
        """Get Confluence space information"""
        url = f"{self.confluence_url}/rest/api/space/{space_key}"
        response = requests.get(url, headers=self.headers, auth=self.auth)
        response.raise_for_status()
        return response.json()
    
    def create_space(self, key: str, name: str, description: Optional[str] = None) -> Dict:
        """Create a new Confluence space"""
        url = f"{self.confluence_url}/rest/api/space"
        
        payload = {
            "key": key,
            "name": name,
            "type": "global"
        }
        
        if description:
            payload["description"] = {
                "plain": {
                    "value": description,
                    "representation": "plain"
                }
            }
        
        response = requests.post(url, json=payload, headers=self.headers, auth=self.auth)
        response.raise_for_status()
        return response.json()
    
    def create_page(self, space_key: str, title: str, content: str,
                   parent_id: Optional[str] = None, content_format: str = "storage") -> Dict:
        """
        Create a new Confluence page
        
        Args:
            space_key: The space key where the page will be created
            title: Page title
            content: Page content (can be markdown, HTML, or Confluence storage format)
            parent_id: Optional parent page ID for hierarchical structure
            content_format: Content format - "storage" (Confluence), "wiki", "markdown", or "view"
        """
        url = f"{self.confluence_url}/rest/api/content"
        
        payload = {
            "type": "page",
            "title": title,
            "space": {"key": space_key},
            "body": {
                content_format: {
                    "value": content,
                    "representation": content_format
                }
            }
        }
        
        if parent_id:
            payload["ancestors"] = [{"id": parent_id}]
        
        response = requests.post(url, json=payload, headers=self.headers, auth=self.auth)
        response.raise_for_status()
        return response.json()
    
    def update_page(self, page_id: str, title: Optional[str] = None,
                   content: Optional[str] = None, version: int = None,
                   content_format: str = "storage") -> Dict:
        """Update an existing Confluence page"""
        # First get the current page to get the version
        url = f"{self.confluence_url}/rest/api/content/{page_id}"
        get_response = requests.get(url, headers=self.headers, auth=self.auth, params={"expand": "version"})
        get_response.raise_for_status()
        current_page = get_response.json()
        
        current_version = current_page.get("version", {}).get("number", 1)
        if version is None:
            version = current_version + 1
        
        payload = {
            "version": {"number": version}
        }
        
        if title:
            payload["title"] = title
        
        if content:
            payload["body"] = {
                content_format: {
                    "value": content,
                    "representation": content_format
                }
            }
        else:
            # Keep existing body if not updating content
            payload["body"] = current_page.get("body", {})
        
        response = requests.put(url, json=payload, headers=self.headers, auth=self.auth)
        response.raise_for_status()
        return response.json()
    
    def publish_product_plan(self, space_key: str, plan_title: str, plan_content: str,
                           parent_page_id: Optional[str] = None) -> Dict:
        """Publish a complete product management plan to Confluence"""
        # Convert markdown to Confluence storage format (simplified)
        confluence_content = self._markdown_to_confluence(plan_content)
        
        return self.create_page(
            space_key=space_key,
            title=plan_title,
            content=confluence_content,
            parent_id=parent_page_id,
            content_format="storage"
        )
    
    def publish_report(self, space_key: str, report_title: str, report_content: str,
                      report_type: str = "Report", parent_page_id: Optional[str] = None) -> Dict:
        """Publish a report (sprint planning, retro, etc.) to Confluence"""
        # Add report metadata
        formatted_content = f"""
<h2>{report_type}</h2>
<p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
<hr/>
{self._markdown_to_confluence(report_content)}
"""
        
        return self.create_page(
            space_key=space_key,
            title=report_title,
            content=formatted_content,
            parent_id=parent_page_id,
            content_format="storage"
        )
    
    def create_report_index(self, space_key: str, index_title: str,
                          reports: List[Dict[str, str]]) -> Dict:
        """Create an index page linking to all reports"""
        content = "<h2>Product Management Reports Index</h2><ul>"
        
        for report in reports:
            content += f'<li><a href="/wiki{report.get("url", "")}">{report.get("title", "Untitled")}</a> - {report.get("type", "Report")}</li>'
        
        content += "</ul>"
        
        return self.create_page(
            space_key=space_key,
            title=index_title,
            content=content,
            content_format="storage"
        )
    
    def _markdown_to_confluence(self, markdown: str) -> str:
        """
        Convert markdown to Confluence storage format (simplified).
        For production, consider using a library like markdown2 or pandoc.
        """
        # Basic markdown to HTML conversion
        html = markdown
        
        # Headers
        html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        
        # Bold
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
        
        # Italic
        html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
        
        # Lists
        html = re.sub(r'^- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
        html = re.sub(r'(<li>.*</li>)', r'<ul>\1</ul>', html, flags=re.DOTALL)
        
        # Code blocks
        html = re.sub(r'```(.+?)```', r'<pre><code>\1</code></pre>', html, flags=re.DOTALL)
        
        # Line breaks
        html = html.replace('\n\n', '</p><p>')
        html = f'<p>{html}</p>'
        
        return html
    
    def search_pages(self, space_key: str, query: str, limit: int = 25) -> List[Dict]:
        """Search for pages in a space"""
        url = f"{self.confluence_url}/rest/api/content/search"
        params = {
            "cql": f"space = {space_key} AND text ~ \"{query}\"",
            "limit": limit
        }
        response = requests.get(url, headers=self.headers, auth=self.auth, params=params)
        response.raise_for_status()
        return response.json().get("results", [])
    
    def get_page_comments(self, page_id: str) -> List[Dict]:
        """Get comments on a Confluence page"""
        url = f"{self.confluence_url}/rest/api/content/{page_id}/child/comment"
        response = requests.get(url, headers=self.headers, auth=self.auth, params={"expand": "body.storage"})
        response.raise_for_status()
        return response.json().get("results", [])
    
    def get_all_comments_in_space(self, space_key: str, since: Optional[datetime] = None) -> List[Dict]:
        """Get all comments in a space, optionally filtered by date"""
        # Get all pages in space
        pages = self.search_pages(space_key, "", limit=100)
        all_comments = []
        
        for page in pages:
            page_id = page.get("id")
            if page_id:
                comments = self.get_page_comments(page_id)
                for comment in comments:
                    if since:
                        created = datetime.fromisoformat(comment.get("version", {}).get("when", "").replace("Z", "+00:00"))
                        if created >= since:
                            comment["page_id"] = page_id
                            comment["page_title"] = page.get("title")
                            all_comments.append(comment)
                    else:
                        comment["page_id"] = page_id
                        comment["page_title"] = page.get("title")
                        all_comments.append(comment)
        
        return all_comments
    
    def get_page_url(self, page_id: str) -> str:
        """Get URL to a Confluence page"""
        return f"{self.confluence_url}/pages/viewpage.action?pageId={page_id}"


def create_confluence_tools_from_env() -> Optional[ConfluenceTools]:
    """Create ConfluenceTools from environment variables"""
    confluence_url = os.getenv("CONFLUENCE_URL")
    confluence_email = os.getenv("CONFLUENCE_EMAIL")
    confluence_token = os.getenv("CONFLUENCE_API_TOKEN")
    
    if all([confluence_url, confluence_email, confluence_token]):
        return ConfluenceTools(confluence_url, confluence_email, confluence_token)
    return None

