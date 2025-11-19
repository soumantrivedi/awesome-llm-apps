"""
Token Management System for FuturisticPM
Secure storage and management of API tokens and credentials
"""

import os
import json
import logging
import base64
from typing import Dict, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)

# Try to import cryptography
try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    Fernet = None
    logger.warning("cryptography not available. Tokens will be stored in plain text (not recommended for production)")


class TokenManager:
    """Manages secure storage of API tokens and credentials"""
    
    def __init__(self, storage_dir: str = "tokens", master_key: Optional[str] = None):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True, mode=0o700)  # Secure directory permissions
        
        self.tokens_file = self.storage_dir / "tokens.json"
        self.key_file = self.storage_dir / ".key"
        
        # Initialize encryption
        if CRYPTO_AVAILABLE:
            self.cipher = self._get_or_create_cipher(master_key)
        else:
            self.cipher = None
            logger.warning("Encryption not available - storing tokens in plain text")
    
    def _get_or_create_cipher(self, master_key: Optional[str] = None) -> Optional[Fernet]:
        """Get or create encryption cipher"""
        if not CRYPTO_AVAILABLE:
            return None
        
        if self.key_file.exists():
            # Load existing key
            with open(self.key_file, 'rb') as f:
                key = f.read()
        else:
            # Generate new key
            if master_key:
                # Derive key from master password
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=b'futuristic_pm_salt',
                    iterations=100000,
                )
                key = base64.urlsafe_b64encode(kdf.derive(master_key.encode()))
            else:
                # Generate random key
                key = Fernet.generate_key()
            
            # Save key
            with open(self.key_file, 'wb') as f:
                f.write(key)
            self.key_file.chmod(0o600)  # Secure file permissions
        
        return Fernet(key)
    
    def _encrypt(self, value: str) -> str:
        """Encrypt a value"""
        if self.cipher:
            return self.cipher.encrypt(value.encode()).decode()
        return value  # No encryption available
    
    def _decrypt(self, value: str) -> str:
        """Decrypt a value"""
        if self.cipher:
            try:
                return self.cipher.decrypt(value.encode()).decode()
            except Exception as e:
                logger.error(f"Decryption error: {e}")
                return value
        return value  # No encryption available
    
    def save_token(self, service: str, token_name: str, token_value: str):
        """Save a token for a service"""
        tokens = self.load_all_tokens()
        
        if service not in tokens:
            tokens[service] = {}
        
        tokens[service][token_name] = self._encrypt(token_value)
        self._save_tokens(tokens)
        logger.info(f"Saved token: {service}.{token_name}")
    
    def get_token(self, service: str, token_name: str) -> Optional[str]:
        """Get a token"""
        tokens = self.load_all_tokens()
        if service in tokens and token_name in tokens[service]:
            return self._decrypt(tokens[service][token_name])
        return None
    
    def delete_token(self, service: str, token_name: str):
        """Delete a token"""
        tokens = self.load_all_tokens()
        if service in tokens and token_name in tokens[service]:
            del tokens[service][token_name]
            if not tokens[service]:
                del tokens[service]
            self._save_tokens(tokens)
            logger.info(f"Deleted token: {service}.{token_name}")
    
    def load_all_tokens(self) -> Dict:
        """Load all tokens"""
        if not self.tokens_file.exists():
            return {}
        
        try:
            with open(self.tokens_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading tokens: {e}")
            return {}
    
    def _save_tokens(self, tokens: Dict):
        """Save tokens to file"""
        try:
            with open(self.tokens_file, 'w') as f:
                json.dump(tokens, f, indent=2)
            self.tokens_file.chmod(0o600)  # Secure file permissions
        except Exception as e:
            logger.error(f"Error saving tokens: {e}")
    
    def get_service_tokens(self, service: str) -> Dict[str, str]:
        """Get all tokens for a service"""
        tokens = self.load_all_tokens()
        if service not in tokens:
            return {}
        
        return {k: self._decrypt(v) for k, v in tokens[service].items()}
    
    def list_services(self) -> List[str]:
        """List all services with stored tokens"""
        tokens = self.load_all_tokens()
        return list(tokens.keys())


# Predefined token configurations
TOKEN_CONFIGS = {
    "OpenAI": {
        "api_key": {
            "label": "OpenAI API Key",
            "type": "password",
            "required": True,
            "help": "Get your API key from https://platform.openai.com/api-keys"
        }
    },
    "Jira": {
        "url": {
            "label": "Jira URL",
            "type": "text",
            "required": True,
            "help": "e.g., https://yourcompany.atlassian.net"
        },
        "email": {
            "label": "Jira Email",
            "type": "text",
            "required": True,
            "help": "Your Atlassian account email"
        },
        "api_token": {
            "label": "Jira API Token",
            "type": "password",
            "required": True,
            "help": "Get from https://id.atlassian.com/manage-profile/security/api-tokens"
        },
        "project_key": {
            "label": "Project Key",
            "type": "text",
            "required": False,
            "help": "e.g., PROJ"
        },
        "board_id": {
            "label": "Board ID",
            "type": "text",
            "required": False,
            "help": "Numeric board ID"
        }
    },
    "Confluence": {
        "url": {
            "label": "Confluence URL",
            "type": "text",
            "required": True,
            "help": "e.g., https://yourcompany.atlassian.net/wiki"
        },
        "email": {
            "label": "Confluence Email",
            "type": "text",
            "required": True,
            "help": "Your Atlassian account email"
        },
        "api_token": {
            "label": "Confluence API Token",
            "type": "password",
            "required": True,
            "help": "Get from https://id.atlassian.com/manage-profile/security/api-tokens"
        },
        "space": {
            "label": "Space Key",
            "type": "text",
            "required": False,
            "help": "e.g., PM"
        }
    },
    "GitHub": {
        "token": {
            "label": "GitHub Personal Access Token",
            "type": "password",
            "required": True,
            "help": "Get from https://github.com/settings/tokens"
        },
        "owner": {
            "label": "Owner/Organization",
            "type": "text",
            "required": False,
            "help": "GitHub username or org name"
        },
        "repo": {
            "label": "Repository",
            "type": "text",
            "required": False,
            "help": "Repository name"
        }
    },
    "Slack": {
        "bot_token": {
            "label": "Slack Bot Token",
            "type": "password",
            "required": False,
            "help": "Bot token for MCP integration (xoxb-...)"
        },
        "team_id": {
            "label": "Team ID",
            "type": "text",
            "required": False,
            "help": "Slack workspace team ID"
        },
        "email": {
            "label": "Slack Email",
            "type": "text",
            "required": False,
            "help": "Email for notifications"
        },
        "channel": {
            "label": "Channel Name",
            "type": "text",
            "required": False,
            "help": "e.g., #product-team"
        }
    },
    "Email": {
        "smtp_server": {
            "label": "SMTP Server",
            "type": "text",
            "required": False,
            "help": "e.g., smtp.gmail.com"
        },
        "smtp_port": {
            "label": "SMTP Port",
            "type": "number",
            "required": False,
            "help": "e.g., 587"
        },
        "email_address": {
            "label": "Email Address",
            "type": "text",
            "required": False,
            "help": "Sender email"
        },
        "email_password": {
            "label": "Email Password",
            "type": "password",
            "required": False,
            "help": "Email password or app password"
        }
    },
    "Amazon Q": {
        "app_id": {
            "label": "Amazon Q App ID",
            "type": "text",
            "required": False,
            "help": "Amazon Q application ID"
        },
        "region": {
            "label": "AWS Region",
            "type": "text",
            "required": False,
            "help": "e.g., us-east-1"
        },
        "access_key_id": {
            "label": "AWS Access Key ID",
            "type": "password",
            "required": False,
            "help": "AWS access key"
        },
        "secret_access_key": {
            "label": "AWS Secret Access Key",
            "type": "password",
            "required": False,
            "help": "AWS secret key"
        }
    }
}

