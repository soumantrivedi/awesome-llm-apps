"""
Integration Tools for Agentic PM
Provides tools for Jira, GitHub, Slack, and Zoom integrations
"""

import os
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
import re


# ============================================================================
# Jira Integration Tools
# ============================================================================

class JiraTools:
    """Tools for interacting with Jira API"""
    
    def __init__(self, jira_url: str, email: str, api_token: str):
        if not all([jira_url, email, api_token]):
            raise ValueError("Jira URL, email, and API token are required")
        self.jira_url = jira_url.rstrip('/')
        self.email = email
        self.api_token = api_token
        self.auth = (email, api_token)
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    
    def create_story(self, project_key: str, summary: str, description: str, 
                    issue_type: str = "Story", acceptance_criteria: Optional[str] = None,
                    story_points: Optional[int] = None, **kwargs) -> Dict:
        """Create a new Jira story/epic/release with natural, well-defined content"""
        url = f"{self.jira_url}/rest/api/3/issue"
        
        # Build description with acceptance criteria if provided
        description_content = [{"type": "paragraph", "content": [{"type": "text", "text": description}]}]
        
        if acceptance_criteria:
            description_content.append({
                "type": "heading",
                "attrs": {"level": 3},
                "content": [{"type": "text", "text": "Acceptance Criteria"}]
            })
            # Split acceptance criteria into list items for better readability
            criteria_items = [item.strip() for item in acceptance_criteria.split('\n') if item.strip()]
            for criteria in criteria_items:
                description_content.append({
                    "type": "bulletList",
                    "content": [{
                        "type": "listItem",
                        "content": [{
                            "type": "paragraph",
                            "content": [{"type": "text", "text": criteria}]
                        }]
                    }]
                })
        
        payload = {
            "fields": {
                "project": {"key": project_key},
                "summary": summary,
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": description_content
                },
                "issuetype": {"name": issue_type}
            }
        }
        
        # Add story points if provided
        if story_points is not None:
            payload["fields"]["customfield_10016"] = story_points  # Common story points field ID
        
        # Add additional fields
        for key, value in kwargs.items():
            payload["fields"][key] = value
        
        response = requests.post(url, json=payload, headers=self.headers, auth=self.auth)
        response.raise_for_status()
        return response.json()
    
    def create_epic(self, project_key: str, summary: str, description: str,
                   epic_name: Optional[str] = None, **kwargs) -> Dict:
        """Create a Jira epic with natural language description"""
        url = f"{self.jira_url}/rest/api/3/issue"
        
        payload = {
            "fields": {
                "project": {"key": project_key},
                "summary": summary,
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [{"type": "paragraph", "content": [{"type": "text", "text": description}]}]
                },
                "issuetype": {"name": "Epic"}
            }
        }
        
        # Add epic name if provided (custom field for epic name)
        if epic_name:
            payload["fields"]["customfield_10011"] = epic_name  # Common epic name field ID
        
        # Add additional fields
        for key, value in kwargs.items():
            payload["fields"][key] = value
        
        response = requests.post(url, json=payload, headers=self.headers, auth=self.auth)
        response.raise_for_status()
        return response.json()
    
    def create_release(self, project_key: str, name: str, description: str,
                      release_date: Optional[str] = None, **kwargs) -> Dict:
        """Create a Jira release/version"""
        url = f"{self.jira_url}/rest/api/3/version"
        
        payload = {
            "name": name,
            "description": description,
            "project": project_key,
            "released": False,
            "archived": False
        }
        
        if release_date:
            payload["releaseDate"] = release_date
        
        # Add additional fields
        payload.update(kwargs)
        
        response = requests.post(url, json=payload, headers=self.headers, auth=self.auth)
        response.raise_for_status()
        return response.json()
    
    def link_story_to_epic(self, story_key: str, epic_key: str) -> Dict:
        """Link a story to an epic"""
        url = f"{self.jira_url}/rest/api/3/issue/{story_key}"
        
        # Get epic custom field ID (common field ID for epic link)
        payload = {
            "fields": {
                "customfield_10014": epic_key  # Epic Link field
            }
        }
        
        response = requests.put(url, json=payload, headers=self.headers, auth=self.auth)
        response.raise_for_status()
        return response.json()
    
    def add_story_to_release(self, story_key: str, release_id: str) -> Dict:
        """Add a story to a release/version"""
        url = f"{self.jira_url}/rest/api/3/issue/{story_key}"
        
        payload = {
            "fields": {
                "fixVersions": [{"id": release_id}]
            }
        }
        
        response = requests.put(url, json=payload, headers=self.headers, auth=self.auth)
        response.raise_for_status()
        return response.json()
    
    def get_sprint_info(self, board_id: int, sprint_id: int) -> Dict:
        """Get sprint information"""
        url = f"{self.jira_url}/rest/agile/1.0/sprint/{sprint_id}"
        response = requests.get(url, headers=self.headers, auth=self.auth)
        response.raise_for_status()
        return response.json()
    
    def create_sprint(self, board_id: int, name: str, start_date: Optional[str] = None,
                     end_date: Optional[str] = None, goal: Optional[str] = None) -> Dict:
        """Create a new sprint"""
        url = f"{self.jira_url}/rest/agile/1.0/sprint"
        
        payload = {
            "name": name,
            "originBoardId": board_id
        }
        
        if start_date:
            payload["startDate"] = start_date
        if end_date:
            payload["endDate"] = end_date
        if goal:
            payload["goal"] = goal
        
        response = requests.post(url, json=payload, headers=self.headers, auth=self.auth)
        response.raise_for_status()
        return response.json()
    
    def add_stories_to_sprint(self, sprint_id: int, issue_keys: List[str]) -> Dict:
        """Add stories to a sprint"""
        url = f"{self.jira_url}/rest/agile/1.0/sprint/{sprint_id}/issue"
        
        payload = {
            "issues": issue_keys
        }
        
        response = requests.post(url, json=payload, headers=self.headers, auth=self.auth)
        response.raise_for_status()
        return response.json()
    
    def get_sprint_story_points(self, board_id: int, sprint_id: int) -> int:
        """Get total story points in a sprint"""
        issues = self.get_stories_in_sprint(board_id, sprint_id)
        total_points = 0
        
        for issue in issues:
            # Try common story points field IDs
            fields = issue.get("fields", {})
            points = fields.get("customfield_10016") or fields.get("storyPoints") or 0
            if isinstance(points, (int, float)):
                total_points += points
        
        return int(total_points)
    
    def get_project_url(self, project_key: str) -> str:
        """Get URL to Jira project"""
        return f"{self.jira_url}/browse/{project_key}"
    
    def get_issue_url(self, issue_key: str) -> str:
        """Get URL to Jira issue"""
        return f"{self.jira_url}/browse/{issue_key}"
    
    def get_story(self, issue_key: str) -> Dict:
        """Get details of a Jira story/epic/release"""
        url = f"{self.jira_url}/rest/api/3/issue/{issue_key}"
        response = requests.get(url, headers=self.headers, auth=self.auth)
        response.raise_for_status()
        return response.json()
    
    def update_story(self, issue_key: str, summary: Optional[str] = None,
                    description: Optional[str] = None, **kwargs) -> Dict:
        """Update a Jira story (scope, description, etc.)"""
        url = f"{self.jira_url}/rest/api/3/issue/{issue_key}"
        
        fields = {}
        if summary:
            fields["summary"] = summary
        if description:
            fields["description"] = {
                "type": "doc",
                "version": 1,
                "content": [{"type": "paragraph", "content": [{"type": "text", "text": description}]}]
            }
        
        fields.update(kwargs)
        
        payload = {"fields": fields}
        response = requests.put(url, json=payload, headers=self.headers, auth=self.auth)
        response.raise_for_status()
        return response.json()
    
    def add_comment(self, issue_key: str, comment: str) -> Dict:
        """Add a comment to a Jira story"""
        url = f"{self.jira_url}/rest/api/3/issue/{issue_key}/comment"
        
        payload = {
            "body": {
                "type": "doc",
                "version": 1,
                "content": [{"type": "paragraph", "content": [{"type": "text", "text": comment}]}]
            }
        }
        
        response = requests.post(url, json=payload, headers=self.headers, auth=self.auth)
        response.raise_for_status()
        return response.json()
    
    def get_stories_in_sprint(self, board_id: int, sprint_id: int) -> List[Dict]:
        """Get all stories in an active sprint"""
        url = f"{self.jira_url}/rest/agile/1.0/board/{board_id}/sprint/{sprint_id}/issue"
        response = requests.get(url, headers=self.headers, auth=self.auth)
        response.raise_for_status()
        return response.json().get("issues", [])
    
    def search_stories(self, jql: str) -> List[Dict]:
        """Search Jira stories using JQL"""
        url = f"{self.jira_url}/rest/api/3/search"
        params = {"jql": jql}
        response = requests.get(url, headers=self.headers, auth=self.auth, params=params)
        response.raise_for_status()
        return response.json().get("issues", [])


# ============================================================================
# GitHub Integration Tools
# ============================================================================

class GitHubTools:
    """Tools for interacting with GitHub API"""
    
    def __init__(self, token: str):
        if not token:
            raise ValueError("GitHub token is required")
        self.token = token
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        self.base_url = "https://api.github.com"
    
    def get_commits(self, owner: str, repo: str, since: Optional[datetime] = None,
                   author: Optional[str] = None, branch: str = "main") -> List[Dict]:
        """Get commits from a repository"""
        url = f"{self.base_url}/repos/{owner}/{repo}/commits"
        params = {"sha": branch}
        
        if since:
            params["since"] = since.isoformat()
        if author:
            params["author"] = author
        
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_commit_details(self, owner: str, repo: str, sha: str) -> Dict:
        """Get detailed information about a specific commit"""
        url = f"{self.base_url}/repos/{owner}/{repo}/commits/{sha}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def extract_jira_references(self, commit_message: str) -> List[str]:
        """Extract Jira issue keys from commit message (e.g., PROJ-123)"""
        import re
        pattern = r'[A-Z]+-\d+'
        return re.findall(pattern, commit_message)
    
    def get_user_commits(self, owner: str, repo: str, username: str,
                        since: Optional[datetime] = None) -> List[Dict]:
        """Get commits by a specific user"""
        return self.get_commits(owner, repo, since=since, author=username)


# ============================================================================
# Slack Integration Tools
# ============================================================================

class SlackTools:
    """Tools for interacting with Slack using email-based channel access"""
    
    def __init__(self, email: str, channel_name: str):
        """
        Initialize Slack tools using email and channel name.
        Note: This uses email-based access. For full API access, bot token is recommended.
        """
        if not email:
            raise ValueError("Slack email is required")
        if not channel_name:
            raise ValueError("Slack channel name is required")
        self.email = email
        self.channel_name = channel_name
        # Store channel info for reference
        self.channel_info = {
            "email": email,
            "channel": channel_name
        }
    
    def send_message(self, text: str, thread_ts: Optional[str] = None) -> Dict:
        """
        Prepare message for Slack channel.
        Returns message details that can be sent via email or webhook.
        """
        return {
            "status": "prepared",
            "channel": self.channel_name,
            "email": self.email,
            "text": text,
            "thread_ts": thread_ts,
            "note": "Message prepared for Slack channel. Use email notification or webhook to send."
        }
    
    def send_dm(self, user_email: str, text: str) -> Dict:
        """Prepare DM for Slack user via email"""
        return {
            "status": "prepared",
            "recipient_email": user_email,
            "sender_email": self.email,
            "text": text,
            "note": "DM prepared. Send via email notification."
        }
    
    def create_interactive_message(self, text: str, buttons: List[Dict]) -> Dict:
        """Prepare interactive message for Slack"""
        return {
            "status": "prepared",
            "channel": self.channel_name,
            "email": self.email,
            "text": text,
            "buttons": buttons,
            "note": "Interactive message prepared. Use webhook or email to send."
        }
    
    def get_channel_info(self) -> Dict:
        """Get channel information"""
        return {
            "channel_name": self.channel_name,
            "contact_email": self.email,
            "note": "Channel accessed via email contact"
        }


# ============================================================================
# Email Integration Tools
# ============================================================================

class EmailTools:
    """Tools for sending emails (e.g., to Slack email addresses)"""
    
    def __init__(self, smtp_server: str, smtp_port: int, email: str, password: str):
        """
        Initialize email tools with SMTP configuration.
        
        Args:
            smtp_server: SMTP server (e.g., 'smtp.gmail.com')
            smtp_port: SMTP port (e.g., 587 for TLS)
            email: Sender email address
            password: Email password or app password
        """
        if not all([smtp_server, email, password]):
            raise ValueError("SMTP server, email, and password are required")
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.email = email
        self.password = password
    
    def send_email(self, to_email: str, subject: str, body: str, 
                   html_body: Optional[str] = None) -> Dict:
        """
        Send an email to the specified address.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Plain text email body
            html_body: Optional HTML email body
        
        Returns:
            Dict with status information
        """
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            msg = MIMEMultipart('alternative')
            msg['From'] = self.email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add plain text part
            text_part = MIMEText(body, 'plain')
            msg.attach(text_part)
            
            # Add HTML part if provided
            if html_body:
                html_part = MIMEText(html_body, 'html')
                msg.attach(html_part)
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email, self.password)
            server.send_message(msg)
            server.quit()
            
            return {
                "status": "success",
                "to": to_email,
                "subject": subject,
                "message": "Email sent successfully"
            }
        except Exception as e:
            return {
                "status": "error",
                "to": to_email,
                "subject": subject,
                "error": str(e)
            }
    
    def send_slack_notification_email(self, slack_email: str, subject: str, 
                                     jira_project_url: str, epic_urls: List[str],
                                     confluence_page_url: str) -> Dict:
        """
        Send a formatted email to Slack email with links to Jira and Confluence.
        
        Args:
            slack_email: Slack email address to send to
            subject: Email subject
            jira_project_url: URL to Jira project
            epic_urls: List of URLs to Jira epics
            confluence_page_url: URL to Confluence page
        """
        body = f"""
Product Management Plan Created

Your product management plan has been created and published. Here are the links:

Jira Project:
{jira_project_url}

Epics:
""" + "\n".join([f"- {url}" for url in epic_urls]) + f"""

Confluence Documentation:
{confluence_page_url}

Please review the documents and provide feedback.
"""
        
        html_body = f"""
<html>
<body>
<h2>Product Management Plan Created</h2>
<p>Your product management plan has been created and published. Here are the links:</p>

<h3>Jira Project:</h3>
<p><a href="{jira_project_url}">{jira_project_url}</a></p>

<h3>Epics:</h3>
<ul>
""" + "\n".join([f"<li><a href='{url}'>{url}</a></li>" for url in epic_urls]) + f"""
</ul>

<h3>Confluence Documentation:</h3>
<p><a href="{confluence_page_url}">{confluence_page_url}</a></p>

<p>Please review the documents and provide feedback.</p>
</body>
</html>
"""
        
        return self.send_email(slack_email, subject, body, html_body)


# ============================================================================
# Helper Functions for Agent Tools
# ============================================================================

def create_jira_tools_from_env() -> Optional[JiraTools]:
    """Create JiraTools from environment variables"""
    jira_url = os.getenv("JIRA_URL")
    jira_email = os.getenv("JIRA_EMAIL")
    jira_token = os.getenv("JIRA_API_TOKEN")
    
    if all([jira_url, jira_email, jira_token]):
        return JiraTools(jira_url, jira_email, jira_token)
    return None


def create_github_tools_from_env() -> Optional[GitHubTools]:
    """Create GitHubTools from environment variables"""
    github_token = os.getenv("GITHUB_TOKEN")
    if github_token:
        return GitHubTools(github_token)
    return None


def create_slack_tools_from_env() -> Optional[SlackTools]:
    """Create SlackTools from environment variables"""
    slack_email = os.getenv("SLACK_EMAIL")
    slack_channel = os.getenv("SLACK_CHANNEL")
    if slack_email and slack_channel:
        return SlackTools(slack_email, slack_channel)
    return None


def create_email_tools_from_env() -> Optional[EmailTools]:
    """Create EmailTools from environment variables"""
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    email = os.getenv("EMAIL_ADDRESS")
    password = os.getenv("EMAIL_PASSWORD")
    
    if all([email, password]):
        return EmailTools(smtp_server, smtp_port, email, password)
    return None

