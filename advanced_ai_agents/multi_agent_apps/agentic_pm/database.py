"""
Database Module for Agentic PM
Provides persistent storage for product plans, configurations, and historical context
"""

import sqlite3
import json
import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from contextlib import contextmanager
import logging
from functools import wraps

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Retry decorator for database operations
def retry_db_operation(max_retries=3, delay=1):
    """Decorator to retry database operations on failure"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except sqlite3.OperationalError as e:
                    last_exception = e
                    if "locked" in str(e).lower() or "database is locked" in str(e).lower():
                        logger.warning(f"Database locked, retrying ({attempt + 1}/{max_retries})...")
                        time.sleep(delay * (attempt + 1))
                    else:
                        raise
                except Exception as e:
                    last_exception = e
                    logger.error(f"Database operation failed: {e}, retrying ({attempt + 1}/{max_retries})...")
                    time.sleep(delay * (attempt + 1))
            raise last_exception
        return wrapper
    return decorator

# Database path
DB_DIR = Path(__file__).parent / "databases"
DB_DIR.mkdir(exist_ok=True)
DB_PATH = DB_DIR / "agentic_pm.db"


@contextmanager
def get_db_connection():
    """Get a database connection with proper error handling and retry logic"""
    max_retries = 3
    retry_delay = 0.5
    
    for attempt in range(max_retries):
        try:
            conn = sqlite3.connect(
                str(DB_PATH), 
                check_same_thread=False,
                timeout=30.0  # 30 second timeout
            )
            conn.row_factory = sqlite3.Row
            # Enable WAL mode for better concurrency
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA foreign_keys=ON")
            conn.execute("PRAGMA synchronous=NORMAL")
            try:
                yield conn
                conn.commit()
            except Exception as e:
                conn.rollback()
                logger.error(f"Database error: {e}")
                raise
            finally:
                conn.close()
            break
        except sqlite3.OperationalError as e:
            if "locked" in str(e).lower() and attempt < max_retries - 1:
                logger.warning(f"Database locked, retrying ({attempt + 1}/{max_retries})...")
                time.sleep(retry_delay * (attempt + 1))
            else:
                raise


class DatabaseManager:
    """Enterprise-ready database manager for Agentic PM"""
    
    def __init__(self):
        self.db_path = DB_PATH
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database schema"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Product Plans table - stores complete product management plans
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS product_plans (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        plan_id TEXT UNIQUE NOT NULL,
                        product_name TEXT NOT NULL,
                        plan_data TEXT NOT NULL,
                        configuration TEXT NOT NULL,
                        status TEXT DEFAULT 'draft',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        created_by TEXT,
                        version INTEGER DEFAULT 1
                    )
                """)
                
                # Plan Versions table - tracks all versions of a plan
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS plan_versions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        plan_id TEXT NOT NULL,
                        version INTEGER NOT NULL,
                        plan_data TEXT NOT NULL,
                        configuration TEXT NOT NULL,
                        status TEXT DEFAULT 'draft',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        created_by TEXT,
                        notes TEXT,
                        FOREIGN KEY (plan_id) REFERENCES product_plans(plan_id),
                        UNIQUE(plan_id, version)
                    )
                """)
                
                # Agent Outputs table - stores individual agent outputs
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS agent_outputs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        plan_id TEXT NOT NULL,
                        version INTEGER NOT NULL,
                        agent_name TEXT NOT NULL,
                        output_content TEXT NOT NULL,
                        metadata TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (plan_id, version) REFERENCES plan_versions(plan_id, version)
                    )
                """)
                
                # Configurations table - stores integration configurations
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS configurations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        config_id TEXT UNIQUE NOT NULL,
                        config_name TEXT NOT NULL,
                        config_type TEXT NOT NULL,
                        config_data TEXT NOT NULL,
                        is_active BOOLEAN DEFAULT 1,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        created_by TEXT
                    )
                """)
                
                # Jira Items table - tracks created Jira items
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS jira_items (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        plan_id TEXT NOT NULL,
                        version INTEGER NOT NULL,
                        item_type TEXT NOT NULL,
                        item_key TEXT NOT NULL,
                        item_url TEXT,
                        item_data TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (plan_id, version) REFERENCES plan_versions(plan_id, version)
                    )
                """)
                
                # Confluence Pages table - tracks created Confluence pages
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS confluence_pages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        plan_id TEXT NOT NULL,
                        version INTEGER NOT NULL,
                        page_id TEXT NOT NULL,
                        page_title TEXT NOT NULL,
                        page_url TEXT,
                        parent_page_id TEXT,
                        page_data TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (plan_id, version) REFERENCES plan_versions(plan_id, version)
                    )
                """)
                
                # Sprints table - tracks created sprints
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS sprints (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        plan_id TEXT NOT NULL,
                        version INTEGER NOT NULL,
                        sprint_id TEXT NOT NULL,
                        sprint_name TEXT NOT NULL,
                        start_date TEXT,
                        end_date TEXT,
                        story_points INTEGER,
                        sprint_data TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (plan_id, version) REFERENCES plan_versions(plan_id, version)
                    )
                """)
                
                # Async Operations table - tracks async operations
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS async_operations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        operation_id TEXT UNIQUE NOT NULL,
                        operation_type TEXT NOT NULL,
                        status TEXT NOT NULL,
                        description TEXT,
                        metadata TEXT,
                        result TEXT,
                        error TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Execution History table - tracks execution phase history
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS execution_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        plan_id TEXT NOT NULL,
                        version INTEGER NOT NULL,
                        phase TEXT NOT NULL,
                        agent_name TEXT,
                        execution_data TEXT,
                        status TEXT DEFAULT 'pending',
                        error_message TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        completed_at TIMESTAMP,
                        FOREIGN KEY (plan_id, version) REFERENCES plan_versions(plan_id, version)
                    )
                """)
                
                # Create indexes for better performance
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_plan_id ON product_plans(plan_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_plan_versions ON plan_versions(plan_id, version)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_agent_outputs ON agent_outputs(plan_id, version)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_jira_items ON jira_items(plan_id, version)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_confluence_pages ON confluence_pages(plan_id, version)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_sprints ON sprints(plan_id, version)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_async_operations ON async_operations(operation_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_execution_history ON execution_history(plan_id, version)")
                
                conn.commit()
                logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    @retry_db_operation(max_retries=3, delay=1)
    def save_product_plan(self, plan_id: str, product_name: str, plan_data: Dict,
                         configuration: Dict, status: str = 'draft', created_by: Optional[str] = None) -> Dict:
        """Save a new product plan or update existing one"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Check if plan exists
                cursor.execute("SELECT id, version FROM product_plans WHERE plan_id = ?", (plan_id,))
                existing = cursor.fetchone()
                
                if existing:
                    # Update existing plan and create new version
                    new_version = existing['version'] + 1
                    cursor.execute("""
                        UPDATE product_plans 
                        SET plan_data = ?, configuration = ?, status = ?, 
                            updated_at = CURRENT_TIMESTAMP, version = ?
                        WHERE plan_id = ?
                    """, (json.dumps(plan_data), json.dumps(configuration), status, new_version, plan_id))
                    
                    # Create version record
                    cursor.execute("""
                        INSERT INTO plan_versions (plan_id, version, plan_data, configuration, status, created_by)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (plan_id, new_version, json.dumps(plan_data), json.dumps(configuration), status, created_by))
                    
                    version = new_version
                else:
                    # Create new plan
                    cursor.execute("""
                        INSERT INTO product_plans (plan_id, product_name, plan_data, configuration, status, created_by)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (plan_id, product_name, json.dumps(plan_data), json.dumps(configuration), status, created_by))
                    
                    # Create initial version
                    cursor.execute("""
                        INSERT INTO plan_versions (plan_id, version, plan_data, configuration, status, created_by)
                        VALUES (?, 1, ?, ?, ?, ?)
                    """, (plan_id, json.dumps(plan_data), json.dumps(configuration), status, created_by))
                    
                    version = 1
                
                conn.commit()
                return {"plan_id": plan_id, "version": version, "status": "saved"}
        except Exception as e:
            logger.error(f"Error saving product plan: {e}")
            raise
    
    @retry_db_operation(max_retries=3, delay=0.5)
    def get_product_plan(self, plan_id: str, version: Optional[int] = None) -> Optional[Dict]:
        """Get a product plan by ID and optional version"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                if version:
                    cursor.execute("""
                        SELECT * FROM plan_versions 
                        WHERE plan_id = ? AND version = ?
                    """, (plan_id, version))
                else:
                    cursor.execute("""
                        SELECT pv.*, pp.product_name 
                        FROM plan_versions pv
                        JOIN product_plans pp ON pv.plan_id = pp.plan_id
                        WHERE pv.plan_id = ? 
                        ORDER BY pv.version DESC 
                        LIMIT 1
                    """, (plan_id,))
                
                row = cursor.fetchone()
                if row:
                    plan = dict(row)
                    plan['plan_data'] = json.loads(plan['plan_data'])
                    plan['configuration'] = json.loads(plan['configuration'])
                    return plan
                return None
        except Exception as e:
            logger.error(f"Error getting product plan: {e}")
            raise
    
    def list_product_plans(self, limit: int = 50, offset: int = 0) -> List[Dict]:
        """List all product plans"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT pp.*, 
                           (SELECT MAX(version) FROM plan_versions WHERE plan_id = pp.plan_id) as latest_version
                    FROM product_plans pp
                    ORDER BY pp.updated_at DESC
                    LIMIT ? OFFSET ?
                """, (limit, offset))
                
                plans = []
                for row in cursor.fetchall():
                    plan = dict(row)
                    plan['plan_data'] = json.loads(plan['plan_data'])
                    plan['configuration'] = json.loads(plan['configuration'])
                    plans.append(plan)
                return plans
        except Exception as e:
            logger.error(f"Error listing product plans: {e}")
            raise
    
    def get_plan_versions(self, plan_id: str) -> List[Dict]:
        """Get all versions of a product plan"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM plan_versions 
                    WHERE plan_id = ? 
                    ORDER BY version DESC
                """, (plan_id,))
                
                versions = []
                for row in cursor.fetchall():
                    version = dict(row)
                    version['plan_data'] = json.loads(version['plan_data'])
                    version['configuration'] = json.loads(version['configuration'])
                    versions.append(version)
                return versions
        except Exception as e:
            logger.error(f"Error getting plan versions: {e}")
            raise
    
    @retry_db_operation(max_retries=3, delay=0.5)
    def save_agent_output(self, plan_id: str, version: int, agent_name: str,
                          output_content: str, metadata: Optional[Dict] = None):
        """Save agent output"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO agent_outputs (plan_id, version, agent_name, output_content, metadata)
                    VALUES (?, ?, ?, ?, ?)
                """, (plan_id, version, agent_name, output_content, 
                      json.dumps(metadata) if metadata else None))
                conn.commit()
        except Exception as e:
            logger.error(f"Error saving agent output: {e}")
            raise
    
    def get_agent_outputs(self, plan_id: str, version: int) -> Dict[str, str]:
        """Get all agent outputs for a plan version"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT agent_name, output_content, metadata 
                    FROM agent_outputs 
                    WHERE plan_id = ? AND version = ?
                """, (plan_id, version))
                
                outputs = {}
                for row in cursor.fetchall():
                    outputs[row['agent_name']] = {
                        'content': row['output_content'],
                        'metadata': json.loads(row['metadata']) if row['metadata'] else {}
                    }
                return outputs
        except Exception as e:
            logger.error(f"Error getting agent outputs: {e}")
            raise
    
    @retry_db_operation(max_retries=3, delay=0.5)
    def save_jira_item(self, plan_id: str, version: int, item_type: str,
                      item_key: str, item_url: Optional[str] = None, item_data: Optional[Dict] = None):
        """Save Jira item reference"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO jira_items (plan_id, version, item_type, item_key, item_url, item_data)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (plan_id, version, item_type, item_key, item_url,
                      json.dumps(item_data) if item_data else None))
                conn.commit()
        except Exception as e:
            logger.error(f"Error saving Jira item: {e}")
            raise
    
    def get_jira_items(self, plan_id: str, version: int) -> List[Dict]:
        """Get all Jira items for a plan version"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM jira_items 
                    WHERE plan_id = ? AND version = ?
                """, (plan_id, version))
                
                items = []
                for row in cursor.fetchall():
                    item = dict(row)
                    item['item_data'] = json.loads(item['item_data']) if item['item_data'] else {}
                    items.append(item)
                return items
        except Exception as e:
            logger.error(f"Error getting Jira items: {e}")
            raise
    
    @retry_db_operation(max_retries=3, delay=0.5)
    def save_confluence_page(self, plan_id: str, version: int, page_id: str,
                            page_title: str, page_url: Optional[str] = None,
                            parent_page_id: Optional[str] = None, page_data: Optional[Dict] = None):
        """Save Confluence page reference"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO confluence_pages (plan_id, version, page_id, page_title, page_url, parent_page_id, page_data)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (plan_id, version, page_id, page_title, page_url, parent_page_id,
                      json.dumps(page_data) if page_data else None))
                conn.commit()
        except Exception as e:
            logger.error(f"Error saving Confluence page: {e}")
            raise
    
    def get_confluence_pages(self, plan_id: str, version: int) -> List[Dict]:
        """Get all Confluence pages for a plan version"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM confluence_pages 
                    WHERE plan_id = ? AND version = ?
                """, (plan_id, version))
                
                pages = []
                for row in cursor.fetchall():
                    page = dict(row)
                    page['page_data'] = json.loads(page['page_data']) if page['page_data'] else {}
                    pages.append(page)
                return pages
        except Exception as e:
            logger.error(f"Error getting Confluence pages: {e}")
            raise
    
    def save_sprint(self, plan_id: str, version: int, sprint_id: str, sprint_name: str,
                   start_date: Optional[str] = None, end_date: Optional[str] = None,
                   story_points: Optional[int] = None, sprint_data: Optional[Dict] = None):
        """Save sprint information"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO sprints (plan_id, version, sprint_id, sprint_name, start_date, end_date, story_points, sprint_data)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (plan_id, version, sprint_id, sprint_name, start_date, end_date, story_points,
                      json.dumps(sprint_data) if sprint_data else None))
                conn.commit()
        except Exception as e:
            logger.error(f"Error saving sprint: {e}")
            raise
    
    def get_sprints(self, plan_id: str, version: int) -> List[Dict]:
        """Get all sprints for a plan version"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM sprints 
                    WHERE plan_id = ? AND version = ?
                    ORDER BY created_at
                """, (plan_id, version))
                
                sprints = []
                for row in cursor.fetchall():
                    sprint = dict(row)
                    sprint['sprint_data'] = json.loads(sprint['sprint_data']) if sprint['sprint_data'] else {}
                    sprints.append(sprint)
                return sprints
        except Exception as e:
            logger.error(f"Error getting sprints: {e}")
            raise
    
    def save_configuration(self, config_id: str, config_name: str, config_type: str,
                          config_data: Dict, created_by: Optional[str] = None) -> Dict:
        """Save a configuration"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Check if exists
                cursor.execute("SELECT id FROM configurations WHERE config_id = ?", (config_id,))
                if cursor.fetchone():
                    cursor.execute("""
                        UPDATE configurations 
                        SET config_name = ?, config_data = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE config_id = ?
                    """, (config_name, json.dumps(config_data), config_id))
                else:
                    cursor.execute("""
                        INSERT INTO configurations (config_id, config_name, config_type, config_data, created_by)
                        VALUES (?, ?, ?, ?, ?)
                    """, (config_id, config_name, config_type, json.dumps(config_data), created_by))
                
                conn.commit()
                return {"config_id": config_id, "status": "saved"}
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            raise
    
    def get_configuration(self, config_id: str) -> Optional[Dict]:
        """Get a configuration"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM configurations WHERE config_id = ?", (config_id,))
                row = cursor.fetchone()
                if row:
                    config = dict(row)
                    config['config_data'] = json.loads(config['config_data'])
                    return config
                return None
        except Exception as e:
            logger.error(f"Error getting configuration: {e}")
            raise
    
    def list_configurations(self, config_type: Optional[str] = None) -> List[Dict]:
        """List configurations"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                if config_type:
                    cursor.execute("""
                        SELECT * FROM configurations 
                        WHERE config_type = ? AND is_active = 1
                        ORDER BY updated_at DESC
                    """, (config_type,))
                else:
                    cursor.execute("""
                        SELECT * FROM configurations 
                        WHERE is_active = 1
                        ORDER BY updated_at DESC
                    """)
                
                configs = []
                for row in cursor.fetchall():
                    config = dict(row)
                    config['config_data'] = json.loads(config['config_data'])
                    configs.append(config)
                return configs
        except Exception as e:
            logger.error(f"Error listing configurations: {e}")
            raise
    
    def save_async_operation(self, operation_id: str, operation_type: str, status: str,
                             description: Optional[str] = None, metadata: Optional[Dict] = None,
                             result: Optional[Dict] = None, error: Optional[str] = None):
        """Save or update async operation"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO async_operations 
                    (operation_id, operation_type, status, description, metadata, result, error, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (operation_id, operation_type, status, description,
                      json.dumps(metadata) if metadata else None,
                      json.dumps(result) if result else None, error))
                conn.commit()
        except Exception as e:
            logger.error(f"Error saving async operation: {e}")
            raise
    
    def get_async_operations(self, status: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Get async operations"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                if status:
                    cursor.execute("""
                        SELECT * FROM async_operations 
                        WHERE status = ?
                        ORDER BY updated_at DESC
                        LIMIT ?
                    """, (status, limit))
                else:
                    cursor.execute("""
                        SELECT * FROM async_operations 
                        ORDER BY updated_at DESC
                        LIMIT ?
                    """, (limit,))
                
                operations = []
                for row in cursor.fetchall():
                    op = dict(row)
                    op['metadata'] = json.loads(op['metadata']) if op['metadata'] else {}
                    op['result'] = json.loads(op['result']) if op['result'] else {}
                    operations.append(op)
                return operations
        except Exception as e:
            logger.error(f"Error getting async operations: {e}")
            raise
    
    def save_execution_history(self, plan_id: str, version: int, phase: str,
                              agent_name: Optional[str] = None, execution_data: Optional[Dict] = None,
                              status: str = 'pending', error_message: Optional[str] = None):
        """Save execution history"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                completed_at = datetime.now().isoformat() if status == 'completed' else None
                cursor.execute("""
                    INSERT INTO execution_history 
                    (plan_id, version, phase, agent_name, execution_data, status, error_message, completed_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (plan_id, version, phase, agent_name,
                      json.dumps(execution_data) if execution_data else None,
                      status, error_message, completed_at))
                conn.commit()
        except Exception as e:
            logger.error(f"Error saving execution history: {e}")
            raise
    
    def get_execution_history(self, plan_id: str, version: int) -> List[Dict]:
        """Get execution history for a plan version"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM execution_history 
                    WHERE plan_id = ? AND version = ?
                    ORDER BY created_at
                """, (plan_id, version))
                
                history = []
                for row in cursor.fetchall():
                    hist = dict(row)
                    hist['execution_data'] = json.loads(hist['execution_data']) if hist['execution_data'] else {}
                    history.append(hist)
                return history
        except Exception as e:
            logger.error(f"Error getting execution history: {e}")
            raise
    
    @retry_db_operation(max_retries=3, delay=1)
    def delete_plan(self, plan_id: str) -> bool:
        """Delete a product plan and all related data"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM product_plans WHERE plan_id = ?", (plan_id,))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error deleting plan: {e}")
            raise


# Global database manager instance
_db_manager = None

def get_db_manager() -> DatabaseManager:
    """Get or create database manager instance"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager

