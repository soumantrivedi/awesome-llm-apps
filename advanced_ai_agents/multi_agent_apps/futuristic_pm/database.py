"""
FuturisticPM Database Module
Enterprise-ready database persistence with full versioning, history tracking, and robust error handling
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
DB_PATH = DB_DIR / "futuristic_pm.db"


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
                timeout=30.0
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


class FuturisticPMDatabase:
    """Enterprise-ready database manager for FuturisticPM"""
    
    def __init__(self):
        self.db_path = DB_PATH
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database schema with all required tables"""
        # Only log once per session, not on every initialization
        if not hasattr(self, '_init_logged'):
            logger.info("Initializing FuturisticPM database schema...")
            self._init_logged = True
        
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Product Plans table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS product_plans (
                        plan_id TEXT PRIMARY KEY,
                        version INTEGER DEFAULT 1,
                        product_name TEXT NOT NULL,
                        plan_data TEXT NOT NULL,
                        configuration TEXT NOT NULL,
                        status TEXT DEFAULT 'draft',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        created_by TEXT,
                        notes TEXT
                    )
                """)
                
                # Plan Versions table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS plan_versions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        plan_id TEXT NOT NULL,
                        version INTEGER NOT NULL,
                        plan_data TEXT NOT NULL,
                        configuration TEXT NOT NULL,
                        status TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        notes TEXT,
                        FOREIGN KEY (plan_id) REFERENCES product_plans(plan_id),
                        UNIQUE(plan_id, version)
                    )
                """)
                
                # Agent Outputs table
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
                
                # Jira Items table
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
                
                # Confluence Pages table
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
                
                # Sprints table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS sprints (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        plan_id TEXT NOT NULL,
                        version INTEGER NOT NULL,
                        sprint_id TEXT NOT NULL,
                        sprint_name TEXT NOT NULL,
                        sprint_data TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (plan_id, version) REFERENCES plan_versions(plan_id, version)
                    )
                """)
                
                # Workflow Steps table (for tracking multi-step workflows)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS workflow_steps (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        plan_id TEXT NOT NULL,
                        version INTEGER NOT NULL,
                        step_name TEXT NOT NULL,
                        step_status TEXT DEFAULT 'pending',
                        step_data TEXT,
                        completed_at TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (plan_id, version) REFERENCES plan_versions(plan_id, version)
                    )
                """)
                
                # Async Operations table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS async_operations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        operation_id TEXT UNIQUE NOT NULL,
                        operation_type TEXT NOT NULL,
                        status TEXT DEFAULT 'pending',
                        operation_data TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Chat History table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS chat_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        plan_id TEXT NOT NULL,
                        version INTEGER NOT NULL,
                        agent_name TEXT NOT NULL,
                        message_role TEXT NOT NULL,
                        message_content TEXT NOT NULL,
                        metadata TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (plan_id, version) REFERENCES plan_versions(plan_id, version)
                    )
                """)
                
                # Create indexes
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_plan_versions_plan_id ON plan_versions(plan_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_agent_outputs_plan ON agent_outputs(plan_id, version)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_jira_items_plan ON jira_items(plan_id, version)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_workflow_steps_plan ON workflow_steps(plan_id, version)")
                
                conn.commit()
                # Only log success once per session
                if not hasattr(self, '_init_success_logged'):
                    logger.info("FuturisticPM database initialized successfully")
                    self._init_success_logged = True
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    @retry_db_operation(max_retries=3, delay=1)
    def save_product_plan(self, plan_id: str, product_name: str, plan_data: Dict,
                         configuration: Dict, status: str = 'draft', created_by: Optional[str] = None,
                         notes: Optional[str] = None) -> Dict:
        """Save a new product plan or update existing one"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Ensure plan_data and configuration are dicts
                if not isinstance(plan_data, dict):
                    plan_data = {}
                if not isinstance(configuration, dict):
                    configuration = {}
                
                # Ensure product_info is in plan_data if we have it
                if 'product_info' not in plan_data and isinstance(plan_data, dict):
                    # Try to preserve any existing product_info
                    pass
                
                # Serialize to JSON
                plan_data_json = json.dumps(plan_data, default=str) if plan_data else '{}'
                configuration_json = json.dumps(configuration, default=str) if configuration else '{}'
                
                # Check if plan exists
                cursor.execute("SELECT plan_id, version FROM product_plans WHERE plan_id = ?", (plan_id,))
                existing = cursor.fetchone()
                
                if existing:
                    # Get next version
                    cursor.execute("SELECT MAX(version) FROM plan_versions WHERE plan_id = ?", (plan_id,))
                    max_version_result = cursor.fetchone()
                    max_version = max_version_result[0] if max_version_result and max_version_result[0] else 0
                    version = max_version + 1
                    
                    # Update main plan
                    cursor.execute("""
                        UPDATE product_plans 
                        SET product_name = ?, plan_data = ?, configuration = ?, 
                            status = ?, updated_at = CURRENT_TIMESTAMP, notes = ?
                        WHERE plan_id = ?
                    """, (product_name, plan_data_json, configuration_json, 
                          status, notes, plan_id))
                else:
                    version = 1
                    # Insert new plan
                    cursor.execute("""
                        INSERT INTO product_plans (plan_id, version, product_name, plan_data, configuration, status, created_by, notes)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (plan_id, version, product_name, plan_data_json, 
                          configuration_json, status, created_by, notes))
                
                # Save to versions table
                cursor.execute("""
                    INSERT INTO plan_versions (plan_id, version, plan_data, configuration, status, notes)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (plan_id, version, plan_data_json, configuration_json, status, notes))
                
                logger.info(f"Saved plan {plan_id} version {version} with status {status}")
                return {"plan_id": plan_id, "version": version, "status": "saved"}
        except Exception as e:
            logger.error(f"Error saving product plan: {e}", exc_info=True)
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
                        SELECT * FROM plan_versions 
                        WHERE plan_id = ? 
                        ORDER BY version DESC LIMIT 1
                    """, (plan_id,))
                
                row = cursor.fetchone()
                if row:
                    plan = dict(row)
                    # Safely parse JSON
                    try:
                        plan['plan_data'] = json.loads(plan['plan_data']) if plan['plan_data'] else {}
                    except (json.JSONDecodeError, TypeError):
                        plan['plan_data'] = {}
                    
                    try:
                        plan['configuration'] = json.loads(plan['configuration']) if plan['configuration'] else {}
                    except (json.JSONDecodeError, TypeError):
                        plan['configuration'] = {}
                    
                    return plan
                return None
        except Exception as e:
            logger.error(f"Error getting product plan: {e}")
            raise
    
    @retry_db_operation(max_retries=3, delay=0.5)
    def list_product_plans(self, limit: int = 50, offset: int = 0) -> List[Dict]:
        """List all product plans"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT pp.plan_id, pp.product_name, pp.status, pp.created_at, pp.updated_at,
                           (SELECT MAX(version) FROM plan_versions WHERE plan_id = pp.plan_id) as latest_version
                    FROM product_plans pp
                    ORDER BY pp.updated_at DESC
                    LIMIT ? OFFSET ?
                """, (limit, offset))
                
                plans = []
                for row in cursor.fetchall():
                    plan = dict(row)
                    plans.append(plan)
                return plans
        except Exception as e:
            logger.error(f"Error listing product plans: {e}")
            raise
    
    @retry_db_operation(max_retries=3, delay=0.5)
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
                    # Safely parse JSON
                    try:
                        version['plan_data'] = json.loads(version['plan_data']) if version['plan_data'] else {}
                    except (json.JSONDecodeError, TypeError):
                        version['plan_data'] = {}
                    
                    try:
                        version['configuration'] = json.loads(version['configuration']) if version['configuration'] else {}
                    except (json.JSONDecodeError, TypeError):
                        version['configuration'] = {}
                    
                    versions.append(version)
                return versions
        except Exception as e:
            logger.error(f"Error getting plan versions: {e}")
            raise
    
    @retry_db_operation(max_retries=3, delay=0.5)
    def save_agent_output(self, plan_id: str, version: int, agent_name: str,
                          output_content: str, metadata: Optional[Dict] = None):
        """Save agent output - ensures plan version exists first"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Ensure the plan version exists (required for foreign key constraint)
                cursor.execute("""
                    SELECT plan_id, version FROM plan_versions 
                    WHERE plan_id = ? AND version = ?
                """, (plan_id, version))
                version_exists = cursor.fetchone()
                
                if not version_exists:
                    # Get plan data from product_plans if available
                    cursor.execute("""
                        SELECT product_name, plan_data, configuration, status, notes
                        FROM product_plans 
                        WHERE plan_id = ?
                    """, (plan_id,))
                    plan_row = cursor.fetchone()
                    
                    if plan_row:
                        # Use existing plan data
                        product_name, plan_data, configuration, status, notes = plan_row
                    else:
                        # Create minimal plan version entry
                        product_name = f"Plan {plan_id}"
                        plan_data = '{}'
                        configuration = '{}'
                        status = 'in_progress'
                        notes = 'Auto-created for agent output'
                    
                    # Insert plan version
                    cursor.execute("""
                        INSERT OR IGNORE INTO plan_versions (plan_id, version, plan_data, configuration, status, notes)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (plan_id, version, plan_data, configuration, status, notes))
                    logger.info(f"Created plan version {plan_id} v{version} for agent output")
                
                # Now save agent output
                cursor.execute("""
                    INSERT INTO agent_outputs (plan_id, version, agent_name, output_content, metadata)
                    VALUES (?, ?, ?, ?, ?)
                """, (plan_id, version, agent_name, output_content, 
                      json.dumps(metadata) if metadata else None))
        except Exception as e:
            logger.error(f"Error saving agent output: {e}")
            raise
    
    @retry_db_operation(max_retries=3, delay=0.5)
    def save_chat_history(self, plan_id: str, version: int, agent_name: str,
                         message_role: str, message_content: str, metadata: Optional[Dict] = None):
        """Save chat history message - ensures plan version exists first"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Ensure the plan version exists (required for foreign key constraint)
                cursor.execute("""
                    SELECT plan_id, version FROM plan_versions 
                    WHERE plan_id = ? AND version = ?
                """, (plan_id, version))
                version_exists = cursor.fetchone()
                
                if not version_exists:
                    # Get plan data from product_plans if available
                    cursor.execute("""
                        SELECT product_name, plan_data, configuration, status, notes
                        FROM product_plans 
                        WHERE plan_id = ?
                    """, (plan_id,))
                    plan_row = cursor.fetchone()
                    
                    if plan_row:
                        # Use existing plan data
                        product_name, plan_data, configuration, status, notes = plan_row
                    else:
                        # Create minimal plan version entry
                        product_name = f"Plan {plan_id}"
                        plan_data = '{}'
                        configuration = '{}'
                        status = 'in_progress'
                        notes = 'Auto-created for chat history'
                    
                    # Insert plan version
                    cursor.execute("""
                        INSERT OR IGNORE INTO plan_versions (plan_id, version, plan_data, configuration, status, notes)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (plan_id, version, plan_data, configuration, status, notes))
                    logger.info(f"Created plan version {plan_id} v{version} for chat history")
                
                # Now save chat history
                cursor.execute("""
                    INSERT INTO chat_history (plan_id, version, agent_name, message_role, message_content, metadata)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (plan_id, version, agent_name, message_role, message_content,
                      json.dumps(metadata) if metadata else None))
        except Exception as e:
            logger.error(f"Error saving chat history: {e}")
            raise
    
    @retry_db_operation(max_retries=3, delay=0.5)
    def get_chat_history(self, plan_id: str, version: int, agent_name: Optional[str] = None) -> List[Dict]:
        """Get chat history for a plan version"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                if agent_name:
                    cursor.execute("""
                        SELECT * FROM chat_history 
                        WHERE plan_id = ? AND version = ? AND agent_name = ?
                        ORDER BY created_at ASC
                    """, (plan_id, version, agent_name))
                else:
                    cursor.execute("""
                        SELECT * FROM chat_history 
                        WHERE plan_id = ? AND version = ?
                        ORDER BY created_at ASC
                    """, (plan_id, version))
                
                history = []
                for row in cursor.fetchall():
                    msg = dict(row)
                    try:
                        msg['metadata'] = json.loads(msg['metadata']) if msg['metadata'] else {}
                    except (json.JSONDecodeError, TypeError):
                        msg['metadata'] = {}
                    history.append(msg)
                return history
        except Exception as e:
            logger.error(f"Error getting chat history: {e}")
            raise
    
    @retry_db_operation(max_retries=3, delay=0.5)
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
    def save_workflow_step(self, plan_id: str, version: int, step_name: str,
                          step_status: str = 'pending', step_data: Optional[Dict] = None):
        """Save workflow step status - ensures plan version exists first"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Ensure the plan version exists (required for foreign key constraint)
                cursor.execute("""
                    SELECT plan_id, version FROM plan_versions 
                    WHERE plan_id = ? AND version = ?
                """, (plan_id, version))
                version_exists = cursor.fetchone()
                
                if not version_exists:
                    # Get plan data from product_plans if available
                    cursor.execute("""
                        SELECT product_name, plan_data, configuration, status, notes
                        FROM product_plans 
                        WHERE plan_id = ?
                    """, (plan_id,))
                    plan_row = cursor.fetchone()
                    
                    if plan_row:
                        # Use existing plan data
                        product_name, plan_data, configuration, status, notes = plan_row
                    else:
                        # Create minimal plan version entry
                        product_name = f"Plan {plan_id}"
                        plan_data = '{}'
                        configuration = '{}'
                        status = 'in_progress'
                        notes = 'Auto-created for workflow step'
                    
                    # Insert plan version
                    cursor.execute("""
                        INSERT OR IGNORE INTO plan_versions (plan_id, version, plan_data, configuration, status, notes)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (plan_id, version, plan_data, configuration, status, notes))
                    logger.info(f"Created plan version {plan_id} v{version} for workflow step")
                
                # Now save workflow step
                cursor.execute("""
                    INSERT OR REPLACE INTO workflow_steps 
                    (plan_id, version, step_name, step_status, step_data, completed_at)
                    VALUES (?, ?, ?, ?, ?, 
                        CASE WHEN ? = 'completed' THEN CURRENT_TIMESTAMP ELSE NULL END)
                """, (plan_id, version, step_name, step_status, 
                      json.dumps(step_data) if step_data else None, step_status))
        except Exception as e:
            logger.error(f"Error saving workflow step: {e}")
            raise
    
    @retry_db_operation(max_retries=3, delay=0.5)
    def get_workflow_steps(self, plan_id: str, version: int) -> List[Dict]:
        """Get all workflow steps for a plan"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM workflow_steps 
                    WHERE plan_id = ? AND version = ?
                    ORDER BY created_at ASC
                """, (plan_id, version))
                
                steps = []
                for row in cursor.fetchall():
                    step = dict(row)
                    step['step_data'] = json.loads(step['step_data']) if step['step_data'] else {}
                    steps.append(step)
                return steps
        except Exception as e:
            logger.error(f"Error getting workflow steps: {e}")
            raise
    
    @retry_db_operation(max_retries=3, delay=1)
    def delete_plan(self, plan_id: str) -> bool:
        """Delete a product plan and all related data"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM product_plans WHERE plan_id = ?", (plan_id,))
                return True
        except Exception as e:
            logger.error(f"Error deleting plan: {e}")
            raise
    
    @retry_db_operation(max_retries=3, delay=0.5)
    def save_chat_history(self, plan_id: str, version: int, agent_name: str,
                         message_role: str, message_content: str, metadata: Optional[Dict] = None):
        """Save chat history message"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO chat_history (plan_id, version, agent_name, message_role, message_content, metadata)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (plan_id, version, agent_name, message_role, message_content,
                      json.dumps(metadata) if metadata else None))
        except Exception as e:
            logger.error(f"Error saving chat history: {e}")
            raise
    
    @retry_db_operation(max_retries=3, delay=0.5)
    def get_chat_history(self, plan_id: str, version: int, agent_name: Optional[str] = None) -> List[Dict]:
        """Get chat history for a plan version"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                if agent_name:
                    cursor.execute("""
                        SELECT * FROM chat_history 
                        WHERE plan_id = ? AND version = ? AND agent_name = ?
                        ORDER BY created_at ASC
                    """, (plan_id, version, agent_name))
                else:
                    cursor.execute("""
                        SELECT * FROM chat_history 
                        WHERE plan_id = ? AND version = ?
                        ORDER BY created_at ASC
                    """, (plan_id, version))
                
                history = []
                for row in cursor.fetchall():
                    msg = dict(row)
                    msg['metadata'] = json.loads(msg['metadata']) if msg['metadata'] else {}
                    history.append(msg)
                return history
        except Exception as e:
            logger.error(f"Error getting chat history: {e}")
            raise


def get_db_manager() -> FuturisticPMDatabase:
    """Get or create database manager instance"""
    return FuturisticPMDatabase()

