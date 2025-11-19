"""
FuturisticPM - Next-Generation AI Product Management System
A comprehensive, enterprise-ready product management platform with full database persistence,
rich multi-step UI, and complete integration support.

Built from the ground up with:
- Full database persistence with versioning
- Rich multi-step workflow UI
- Complete agent orchestration
- All integrations (Jira, GitHub, Slack, Confluence, Email)
- Enterprise-ready features
"""

import streamlit as st
import os
import sys
import uuid
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('futuristic_pm.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Fix Streamlit ScriptRunContext warning
def safe_sidebar_success(message: str):
    """Safely show sidebar success message"""
    try:
        st.sidebar.success(message)
    except Exception as e:
        logger.info(message)

try:
    from streamlit.runtime.scriptrunner import get_script_run_ctx
    if get_script_run_ctx() is None:
        logger.warning("Running in bare mode - some Streamlit features may not work")
except ImportError:
    pass

# Add current directory to path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Import tools and utilities
try:
    from tools import (
        create_jira_tools_from_env,
        create_github_tools_from_env,
        create_slack_tools_from_env,
        create_email_tools_from_env,
        JiraTools,
        GitHubTools,
        SlackTools,
        EmailTools
    )
    from confluence_tools import (
        ConfluenceTools,
        create_confluence_tools_from_env
    )
    from async_tracker import AsyncOperationTracker
    from database import get_db_manager, FuturisticPMDatabase
    from streamlit_utils import safe_session_state, safe_rerun, safe_spinner
    from mcp_integration import MCPToolsWrapper, get_atlassian_oauth_info
    from atlassian_oauth import AtlassianOAuthHelper, initiate_oauth_flow
    from unified_agent_system import UnifiedAgentSystem
    from ui_components import (
        apply_custom_css, render_agent_card, render_step_indicator,
        render_editable_output, render_agent_interaction_flow,
        render_status_dashboard, render_info_box
    )
except ImportError as e:
    logger.warning(f"Import error: {e}")
    JiraTools = None
    GitHubTools = None
    SlackTools = None
    EmailTools = None
    ConfluenceTools = None
    create_confluence_tools_from_env = None
    AsyncOperationTracker = None
    get_db_manager = None
    FuturisticPMDatabase = None
    MCPToolsWrapper = None
    UnifiedAgentSystem = None
    apply_custom_css = lambda: None
    render_agent_card = lambda *args, **kwargs: None
    render_step_indicator = lambda *args, **kwargs: None
    render_editable_output = lambda *args, **kwargs: ""
    render_agent_interaction_flow = lambda *args, **kwargs: None
    render_status_dashboard = lambda *args, **kwargs: None
    render_info_box = lambda *args, **kwargs: None
    safe_session_state = lambda k, d=None: d
    safe_rerun = lambda: None
    safe_spinner = lambda m: __import__('contextlib').nullcontext()

# Import SwarmAgent and related classes from autogen
try:
    from autogen import (
        SwarmAgent,
        SwarmResult,
        initiate_swarm_chat,
        OpenAIWrapper,
        AFTER_WORK,
    )
    try:
        from autogen import UPDATE_SYSTEM_MESSAGE
    except ImportError:
        def UPDATE_SYSTEM_MESSAGE(func):
            return func
except ImportError as e:
    st.error(f"""
    ⚠️ **Import Error**: Could not import required classes from autogen.
    Error: {e}
    
    **Solution**: Please install the correct version:
    ```bash
    pip install "pyautogen>=0.2,<0.5" streamlit==1.41.1
    ```
    """)
    st.stop()

os.environ["AUTOGEN_USE_DOCKER"] = "0"

# Page configuration - only set if not already set (prevents error when script is imported)
try:
    st.set_page_config(
        page_title="FuturisticPM - Next-Gen Product Management",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded"
    )
except Exception:
    # Page config already set, ignore
    pass

# Initialize database manager (only once, silently)
db_manager = None
if get_db_manager:
    try:
        db_manager = get_db_manager()
        # Don't log every time - it's initialized on every page load
        # logger.info("FuturisticPM database initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        # Only show warning once
        if 'db_warning_shown' not in st.session_state:
            st.warning("⚠️ Database initialization failed. Some features may not work.")
            st.session_state.db_warning_shown = True

# Initialize session state
if 'current_step' not in st.session_state:
    st.session_state.current_step = 0
if 'workflow_steps' not in st.session_state:
    st.session_state.workflow_steps = [
        {'name': 'Configuration', 'status': 'pending', 'icon': '⚙️'},
        {'name': 'Product Info', 'status': 'pending', 'icon': '📝'},
        {'name': 'Strategy', 'status': 'pending', 'icon': '🎯'},
        {'name': 'Research', 'status': 'pending', 'icon': '🔍'},
        {'name': 'Roadmap', 'status': 'pending', 'icon': '🗺️'},
        {'name': 'Metrics', 'status': 'pending', 'icon': '📊'},
        {'name': 'Stakeholder', 'status': 'pending', 'icon': '🤝'},
        {'name': 'Execution', 'status': 'pending', 'icon': '⚡'},
        {'name': 'Publish', 'status': 'pending', 'icon': '🚀'},
    ]
# Initialize plan_loaded flag first
if 'plan_loaded' not in st.session_state:
    st.session_state.plan_loaded = False

# Only initialize pm_output if it doesn't exist AND we don't have a plan to load
if 'pm_output' not in st.session_state:
    st.session_state.pm_output = {}
elif st.session_state.get('plan_loaded', False) and not st.session_state.pm_output:
    # If plan is marked as loaded but pm_output is empty, something went wrong
    # Try to reload from database
    if db_manager and st.session_state.current_plan_id:
        try:
            plan = db_manager.get_product_plan(st.session_state.current_plan_id, st.session_state.current_plan_version)
            if plan:
                plan_data = plan.get('plan_data', {})
                if isinstance(plan_data, str):
                    import json
                    try:
                        plan_data = json.loads(plan_data) if plan_data else {}
                    except (json.JSONDecodeError, TypeError):
                        plan_data = {}
                if plan_data:
                    st.session_state.pm_output = plan_data
        except Exception as e:
            logger.error(f"Error recovering pm_output: {e}")
if 'current_plan_id' not in st.session_state:
    st.session_state.current_plan_id = None
if 'current_plan_version' not in st.session_state:
    st.session_state.current_plan_version = None
if 'product_info' not in st.session_state:
    st.session_state.product_info = {}
elif st.session_state.get('plan_loaded', False) and not st.session_state.product_info:
    # If plan is marked as loaded but product_info is empty, try to recover
    if st.session_state.pm_output and isinstance(st.session_state.pm_output, dict):
        product_info = st.session_state.pm_output.get('product_info', {})
        if product_info:
            st.session_state.product_info = product_info

if 'config' not in st.session_state:
    st.session_state.config = {}
elif st.session_state.get('plan_loaded', False) and not st.session_state.config:
    # If plan is marked as loaded but config is empty, try to recover from database
    if db_manager and st.session_state.current_plan_id:
        try:
            plan = db_manager.get_product_plan(st.session_state.current_plan_id, st.session_state.current_plan_version)
            if plan:
                config = plan.get('configuration', {})
                if isinstance(config, str):
                    import json
                    try:
                        config = json.loads(config) if config else {}
                    except (json.JSONDecodeError, TypeError):
                        config = {}
                if config:
                    st.session_state.config = config
        except Exception as e:
            logger.error(f"Error recovering config: {e}")

# Auto-load current plan if it exists and hasn't been loaded yet
if db_manager and st.session_state.current_plan_id and not st.session_state.plan_loaded:
    try:
        plan = db_manager.get_product_plan(st.session_state.current_plan_id, st.session_state.current_plan_version)
        if plan:
            # Load plan data
            plan_data = plan.get('plan_data', {})
            if isinstance(plan_data, str):
                import json
                try:
                    plan_data = json.loads(plan_data) if plan_data else {}
                except (json.JSONDecodeError, TypeError):
                    plan_data = {}
            
            if plan_data:
                st.session_state.pm_output = plan_data
            
            # Load configuration
            config = plan.get('configuration', {})
            if isinstance(config, str):
                import json
                try:
                    config = json.loads(config) if config else {}
                except (json.JSONDecodeError, TypeError):
                    config = {}
            elif config is None:
                config = {}
            
            if config:
                st.session_state.config = config
            
            # Load product info
            if plan_data and isinstance(plan_data, dict):
                product_info = plan_data.get('product_info', {})
                if product_info:
                    st.session_state.product_info = product_info
            
            # Load agent outputs
            try:
                agent_outputs = db_manager.get_agent_outputs(st.session_state.current_plan_id, plan['version'])
                for agent_name, output_data in agent_outputs.items():
                    output_key = agent_name.replace('_agent', '')
                    agent_to_key = {
                        'strategy_agent': 'strategy',
                        'research_agent': 'research',
                        'roadmap_agent': 'roadmap',
                        'metrics_agent': 'metrics',
                        'stakeholder_agent': 'stakeholder',
                        'execution_agent': 'execution',
                    }
                    output_key = agent_to_key.get(agent_name, output_key)
                    if output_data and isinstance(output_data, dict):
                        content = output_data.get('content', '')
                        if content:
                            st.session_state.pm_output[output_key] = content
            except Exception as e:
                logger.error(f"Error loading agent outputs on auto-load: {e}")
            
            # Load chat history
            try:
                chat_history = db_manager.get_chat_history(st.session_state.current_plan_id, plan['version'])
                if chat_history:
                    st.session_state.chat_history = chat_history
            except Exception as e:
                logger.error(f"Error loading chat history on auto-load: {e}")
            
            # Update workflow steps
            if st.session_state.pm_output.get('strategy'):
                st.session_state.workflow_steps[2]['status'] = 'completed'
            if st.session_state.pm_output.get('research'):
                st.session_state.workflow_steps[3]['status'] = 'completed'
            if st.session_state.pm_output.get('roadmap'):
                st.session_state.workflow_steps[4]['status'] = 'completed'
            if st.session_state.pm_output.get('metrics'):
                st.session_state.workflow_steps[5]['status'] = 'completed'
            if st.session_state.pm_output.get('stakeholder'):
                st.session_state.workflow_steps[6]['status'] = 'completed'
            if st.session_state.pm_output.get('execution'):
                st.session_state.workflow_steps[7]['status'] = 'completed'
            
            # Re-initialize tools from loaded configuration
            if config:
                # Import tools directly (not from futuristic_pm package to avoid re-executing st.set_page_config)
                from tools import JiraTools, ConfluenceTools, GitHubTools, SlackTools, EmailTools
                
                # Initialize Jira tools if config exists
                jira_url = config.get('jira_url')
                jira_email = config.get('jira_email')
                jira_token = config.get('jira_token')
                if jira_url and jira_email and jira_token and JiraTools:
                    try:
                        st.session_state.jira_tools = JiraTools(jira_url, jira_email, jira_token)
                        logger.info("✅ Jira tools re-initialized from auto-loaded config")
                    except Exception as e:
                        logger.warning(f"Could not re-initialize Jira tools: {e}")
                
                # Initialize Confluence tools if config exists
                confluence_url = config.get('confluence_url')
                confluence_email = config.get('confluence_email')
                confluence_token = config.get('confluence_token')
                if confluence_url and confluence_email and confluence_token and ConfluenceTools:
                    try:
                        st.session_state.confluence_tools = ConfluenceTools(confluence_url, confluence_email, confluence_token)
                        logger.info("✅ Confluence tools re-initialized from auto-loaded config")
                    except Exception as e:
                        logger.warning(f"Could not re-initialize Confluence tools: {e}")
                
                # Initialize GitHub tools if config exists
                github_token = config.get('github_token')
                if github_token and GitHubTools:
                    try:
                        st.session_state.github_tools = GitHubTools(github_token)
                        logger.info("✅ GitHub tools re-initialized from auto-loaded config")
                    except Exception as e:
                        logger.warning(f"Could not re-initialize GitHub tools: {e}")
                
                # Initialize Slack tools if config exists
                slack_email = config.get('slack_email')
                slack_channel = config.get('slack_channel')
                if slack_email and slack_channel and SlackTools:
                    try:
                        st.session_state.slack_tools = SlackTools(slack_email, slack_channel)
                        logger.info("✅ Slack tools re-initialized from auto-loaded config")
                    except Exception as e:
                        logger.warning(f"Could not re-initialize Slack tools: {e}")
                
                # Initialize Email tools if config exists
                email_address = config.get('email_address')
                email_password = config.get('email_password')
                smtp_server = config.get('smtp_server', 'smtp.gmail.com')
                smtp_port = config.get('smtp_port', 587)
                if email_address and email_password and EmailTools:
                    try:
                        st.session_state.email_tools = EmailTools(smtp_server, smtp_port, email_address, email_password)
                        logger.info("✅ Email tools re-initialized from auto-loaded config")
                    except Exception as e:
                        logger.warning(f"Could not re-initialize Email tools: {e}")
            
            st.session_state.plan_loaded = True
            logger.info(f"Auto-loaded plan {st.session_state.current_plan_id} version {plan['version']}")
    except Exception as e:
        logger.error(f"Error auto-loading plan: {e}", exc_info=True)
        st.session_state.plan_loaded = False

# ============================================================================
# Multi-Step Workflow UI Components
# ============================================================================

def render_progress_indicator():
    """Render a beautiful progress indicator for the workflow"""
    steps = st.session_state.workflow_steps
    current = st.session_state.current_step
    
    # Ensure CSS is applied (it should be, but double-check)
    # Always use the rich UI component if available
    try:
        if render_step_indicator and callable(render_step_indicator):
            # Make sure CSS is loaded
            if apply_custom_css and callable(apply_custom_css):
                try:
                    apply_custom_css()
                except:
                    pass  # CSS might already be applied
            render_step_indicator(steps, current)
            return
    except Exception as e:
        logger.warning(f"Error rendering step indicator with rich UI: {e}")
        # Fall through to fallback
    
    # Fallback to simple indicator using Streamlit columns
    cols = st.columns(len(steps))
    for i, (col, step) in enumerate(zip(cols, steps)):
        with col:
            if i < current:
                status = "✅"
                color = "green"
            elif i == current:
                status = "🔄"
                color = "blue"
            else:
                status = "⏳"
                color = "gray"
            
            st.markdown(
                f'<div style="text-align: center; padding: 10px;">'
                f'<div style="font-size: 24px; margin-bottom: 5px;">{status}</div>'
                f'<div style="font-weight: bold; color: {color};">{step["icon"]} {step["name"]}</div>'
                f'</div>',
                unsafe_allow_html=True
            )
    
    # Progress bar
    progress = (current + 1) / len(steps) if steps else 0
    st.progress(progress)
    st.caption(f"Step {current + 1} of {len(steps)} ({int(progress * 100)}%)")

def render_step_content():
    """Render content for the current step"""
    current = st.session_state.current_step
    steps = st.session_state.workflow_steps
    
    if current < len(steps):
        step_name = steps[current]['name']
        
        if step_name == 'Configuration':
            return render_configuration_step()
        elif step_name == 'Product Info':
            return render_product_info_step()
        elif step_name == 'Strategy':
            return render_strategy_step()
        elif step_name == 'Research':
            return render_research_step()
        elif step_name == 'Roadmap':
            return render_roadmap_step()
        elif step_name == 'Metrics':
            return render_metrics_step()
        elif step_name == 'Stakeholder':
            return render_stakeholder_step()
        elif step_name == 'Execution':
            return render_execution_step()
        elif step_name == 'Publish':
            return render_publish_step()
    
    return None

def render_configuration_step():
    """Step 0: Configuration"""
    st.header("⚙️ Step 1: Configuration")
    st.info("Configure your API keys and integrations. You can skip optional integrations.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔑 API Keys")
        api_key = st.text_input("OpenAI API Key", type="password", key="config_openai_key",
                               help="Required for AI agents")
        
        st.subheader("📋 Jira Integration")
        jira_auth_method = st.radio(
            "Authentication Method",
            ["OAuth 2.0 (Recommended - Official MCP)", "API Token (Fallback)"],
            key="jira_auth_method",
            help="OAuth 2.0 uses official Atlassian Remote MCP Server. API Token uses direct API."
        )
        
        if jira_auth_method == "OAuth 2.0 (Recommended - Official MCP)":
            st.info("🌐 Using Official Atlassian Remote MCP Server (https://mcp.atlassian.com/v1/sse)")
            st.info("✅ Full MCP integration available with OAuth 2.0")
            jira_oauth_client_id = st.text_input("OAuth Client ID", value=os.getenv("ATLASSIAN_CLIENT_ID", ""), key="config_jira_oauth_client_id", help="Get from Atlassian Developer Console")
            jira_oauth_client_secret = st.text_input("OAuth Client Secret", type="password", value=os.getenv("ATLASSIAN_CLIENT_SECRET", ""), key="config_jira_oauth_client_secret")
            jira_oauth_access_token = st.text_input("OAuth Access Token", type="password", value=os.getenv("ATLASSIAN_ACCESS_TOKEN", ""), key="config_jira_oauth_token", help="Obtained from OAuth flow")
            jira_url = st.text_input("Atlassian Site URL", value=os.getenv("JIRA_URL", ""), key="config_jira_url", help="e.g., https://yourcompany.atlassian.net")
            jira_email = None
            jira_token = None
        else:
            st.warning("⚠️ API Token method uses direct API calls (not MCP). For MCP integration, use OAuth 2.0.")
            st.info("💡 Direct API tools will be initialized and work, but won't use MCP protocol.")
            jira_url = st.text_input("Jira URL", value=os.getenv("JIRA_URL", ""), key="config_jira_url", help="e.g., https://yourcompany.atlassian.net")
            jira_email = st.text_input("Jira Email", value=os.getenv("JIRA_EMAIL", ""), key="config_jira_email", help="Your Atlassian account email")
            jira_token = st.text_input("Jira API Token", type="password", value=os.getenv("JIRA_API_TOKEN", ""), key="config_jira_token", help="Get from https://id.atlassian.com/manage-profile/security/api-tokens")
            jira_oauth_client_id = None
            jira_oauth_client_secret = None
            jira_oauth_access_token = None
            jira_auth_method = "API Token (Direct API)"
        
        jira_project_key = st.text_input("Jira Project Key", value=os.getenv("JIRA_PROJECT_KEY", ""), key="config_jira_project")
        jira_board_id = st.number_input("Jira Board ID", min_value=0, value=int(os.getenv("JIRA_BOARD_ID", "0")), key="config_jira_board")
        
        st.subheader("📚 Confluence Integration")
        confluence_auth_method = st.radio(
            "Authentication Method",
            ["OAuth 2.0 (Recommended - Official MCP)", "API Token (Fallback)"],
            key="confluence_auth_method",
            help="OAuth 2.0 uses official Atlassian Remote MCP Server (https://mcp.atlassian.com/v1/sse). API Token uses direct API."
        )
        
        if confluence_auth_method == "OAuth 2.0 (Recommended - Official MCP)":
            st.info("✅ Full MCP integration available with OAuth 2.0")
            # Reuse Jira OAuth credentials if same Atlassian site
            reuse_jira_oauth = st.checkbox("Use same OAuth credentials as Jira", key="reuse_jira_oauth", value=True, help="If Jira and Confluence are on the same Atlassian site")
            
            if reuse_jira_oauth and jira_auth_method == "OAuth 2.0 (Recommended - Official MCP)":
                confluence_oauth_client_id = jira_oauth_client_id
                confluence_oauth_client_secret = jira_oauth_client_secret
                confluence_oauth_access_token = jira_oauth_access_token
                st.info("✅ Using Jira OAuth credentials")
            else:
                confluence_oauth_client_id = st.text_input("OAuth Client ID", value=os.getenv("ATLASSIAN_CLIENT_ID", ""), key="config_confluence_oauth_client_id")
                confluence_oauth_client_secret = st.text_input("OAuth Client Secret", type="password", value=os.getenv("ATLASSIAN_CLIENT_SECRET", ""), key="config_confluence_oauth_client_secret")
                
                if confluence_oauth_client_id and confluence_oauth_client_secret:
                    if st.button("🔐 Initiate OAuth Flow", key="confluence_oauth_flow"):
                        try:
                            oauth_result = initiate_oauth_flow(confluence_oauth_client_id, confluence_oauth_client_secret)
                            st.markdown(f"**Authorization URL:** {oauth_result['authorization_url']}")
                            st.markdown(oauth_result['instructions'])
                            st.link_button("Open Authorization URL", oauth_result['authorization_url'])
                        except Exception as e:
                            st.error(f"Error initiating OAuth flow: {e}")
                
                confluence_oauth_access_token = st.text_input("OAuth Access Token", type="password", value=os.getenv("ATLASSIAN_ACCESS_TOKEN", ""), key="config_confluence_oauth_token")
            
            confluence_url = st.text_input("Atlassian Site URL", value=os.getenv("CONFLUENCE_URL", ""), key="config_confluence_url", help="e.g., https://yourcompany.atlassian.net/wiki")
            confluence_email = None
            confluence_token = None
        else:
            st.warning("⚠️ API Token method uses direct API calls (not MCP). For MCP integration, use OAuth 2.0.")
            st.info("💡 Direct API tools will be initialized and work, but won't use MCP protocol.")
            confluence_url = st.text_input("Confluence URL", value=os.getenv("CONFLUENCE_URL", ""), key="config_confluence_url", help="e.g., https://yourcompany.atlassian.net/wiki")
            confluence_email = st.text_input("Confluence Email", value=os.getenv("CONFLUENCE_EMAIL", ""), key="config_confluence_email", help="Your Atlassian account email")
            confluence_token = st.text_input("Confluence API Token", type="password", value=os.getenv("CONFLUENCE_API_TOKEN", ""), key="config_confluence_token", help="Get from https://id.atlassian.com/manage-profile/security/api-tokens")
            confluence_oauth_client_id = None
            confluence_oauth_client_secret = None
            confluence_oauth_access_token = None
            confluence_auth_method = "API Token (Direct API)"
        
        confluence_space = st.text_input("Confluence Space Key", value=os.getenv("CONFLUENCE_SPACE", ""), key="config_confluence_space", help="e.g., PM")
    
    with col2:
        st.subheader("🐙 GitHub Integration")
        github_token = st.text_input("GitHub Token", type="password", value=os.getenv("GITHUB_TOKEN", ""), key="config_github_token")
        github_owner = st.text_input("GitHub Owner/Org", value=os.getenv("GITHUB_OWNER", ""), key="config_github_owner")
        github_repo = st.text_input("GitHub Repository", value=os.getenv("GITHUB_REPO", ""), key="config_github_repo")
        
        st.subheader("💬 Slack Integration")
        slack_email = st.text_input("Slack Email", value=os.getenv("SLACK_EMAIL", ""), key="config_slack_email")
        slack_channel = st.text_input("Slack Channel", value=os.getenv("SLACK_CHANNEL", ""), key="config_slack_channel")
        slack_bot_token = st.text_input("Slack Bot Token (for MCP)", type="password", value=os.getenv("SLACK_BOT_TOKEN", ""), key="config_slack_bot_token", help="Required for Slack MCP integration")
        slack_team_id = st.text_input("Slack Team ID (optional)", value=os.getenv("SLACK_TEAM_ID", ""), key="config_slack_team_id")
        
        st.subheader("🤖 Amazon Q Developer (Optional)")
        amazon_q_app_id = st.text_input("Amazon Q App ID", value=os.getenv("AMAZON_Q_APP_ID", ""), key="config_amazon_q_app_id")
        amazon_q_region = st.text_input("AWS Region", value=os.getenv("AWS_REGION", "us-east-1"), key="config_amazon_q_region")
        amazon_q_access_key = st.text_input("AWS Access Key ID", type="password", value=os.getenv("AWS_ACCESS_KEY_ID", ""), key="config_amazon_q_access_key")
        amazon_q_secret_key = st.text_input("AWS Secret Access Key", type="password", value=os.getenv("AWS_SECRET_ACCESS_KEY", ""), key="config_amazon_q_secret_key")
        
        st.subheader("📧 Email (SMTP)")
        smtp_server = st.text_input("SMTP Server", value=os.getenv("SMTP_SERVER", "smtp.gmail.com"), key="config_smtp_server")
        smtp_port = st.number_input("SMTP Port", min_value=1, max_value=65535, value=int(os.getenv("SMTP_PORT", "587")), key="config_smtp_port")
        email_address = st.text_input("Email Address", value=os.getenv("EMAIL_ADDRESS", ""), key="config_email_address")
        email_password = st.text_input("Email Password", type="password", value=os.getenv("EMAIL_PASSWORD", ""), key="config_email_password")
        
        st.subheader("🏃 Sprint Configuration")
        team_size = st.number_input("Team Size", min_value=1, max_value=20, value=8, key="config_team_size")
        max_story_points = st.number_input("Max Story Points per Sprint", min_value=1, max_value=200, value=70, key="config_max_points")
        sprint_duration_weeks = st.number_input("Sprint Duration (weeks)", min_value=1, max_value=4, value=2, key="config_sprint_duration")
    
    # Store configuration
    if st.button("✅ Save Configuration & Continue", type="primary", key="save_config"):
        if not api_key:
            st.error("⚠️ OpenAI API Key is required!")
        else:
            # Store in session state - include auth methods
            st.session_state.config = {
                'api_key': api_key,
                'jira_url': jira_url,
                'jira_email': jira_email,
                'jira_token': jira_token,
                'jira_oauth_client_id': jira_oauth_client_id,
                'jira_oauth_client_secret': jira_oauth_client_secret,
                'jira_oauth_access_token': jira_oauth_access_token,
                'jira_auth_method': jira_auth_method,
                'jira_project_key': jira_project_key,
                'jira_board_id': jira_board_id,
                'confluence_url': confluence_url,
                'confluence_email': confluence_email,
                'confluence_token': confluence_token,
                'confluence_oauth_client_id': confluence_oauth_client_id,
                'confluence_oauth_client_secret': confluence_oauth_client_secret,
                'confluence_oauth_access_token': confluence_oauth_access_token,
                'confluence_auth_method': confluence_auth_method,
                'confluence_space': confluence_space,
                'github_token': github_token,
                'github_owner': github_owner,
                'github_repo': github_repo,
                'slack_email': slack_email,
                'slack_channel': slack_channel,
                'slack_bot_token': slack_bot_token,
                'slack_team_id': slack_team_id,
                'amazon_q_app_id': amazon_q_app_id,
                'amazon_q_region': amazon_q_region,
                'amazon_q_access_key': amazon_q_access_key,
                'amazon_q_secret_key': amazon_q_secret_key,
                'smtp_server': smtp_server,
                'smtp_port': smtp_port,
                'email_address': email_address,
                'email_password': email_password,
                'team_size': team_size,
                'max_story_points': max_story_points,
                'sprint_duration_weeks': sprint_duration_weeks,
            }
            
            # Initialize MCP tools (preferred) or fallback to direct API
            st.session_state.mcp_tools = None
            st.session_state.jira_tools = None
            st.session_state.confluence_tools = None
            st.session_state.github_tools = None
            st.session_state.slack_tools = None
            st.session_state.email_tools = None
            
            # Try to initialize MCP tools first
            if MCPToolsWrapper:
                try:
                    mcp_wrapper = MCPToolsWrapper()
                    jira_config = None
                    confluence_config = None
                    github_config = None
                    slack_config = None
                    
                    # Jira configuration (OAuth or API token)
                    if jira_auth_method == "OAuth 2.0 (Recommended - Official MCP)":
                        if jira_oauth_access_token and jira_oauth_client_id:
                            jira_config = {
                                'url': jira_url,
                                'oauth_access_token': jira_oauth_access_token,
                                'oauth_client_id': jira_oauth_client_id,
                                'oauth_client_secret': jira_oauth_client_secret,
                                'project_key': jira_project_key,
                                'board_id': jira_board_id,
                                'auth_method': 'oauth'
                            }
                        else:
                            jira_config = None
                            st.warning("⚠️ Jira OAuth credentials incomplete")
                    else:
                        # API Token method - initialize tools immediately if credentials provided
                        if jira_url and jira_email and jira_token:
                            jira_config = {
                                'url': jira_url,
                                'email': jira_email,
                                'token': jira_token,
                                'project_key': jira_project_key,
                                'board_id': jira_board_id,
                                'auth_method': 'api_token'
                            }
                            # Try to initialize Jira tools immediately
                            if JiraTools:
                                try:
                                    st.session_state.jira_tools = JiraTools(jira_url, jira_email, jira_token)
                                    safe_sidebar_success("✅ Jira connected (direct API)")
                                except Exception as e2:
                                    st.warning(f"⚠️ Jira connection failed: {e2}. Will retry on publish.")
                                    logger.warning(f"Jira connection error: {e2}")
                            else:
                                logger.warning("JiraTools not available - install required dependencies")
                        else:
                            jira_config = None
                    
                    # Confluence configuration (OAuth or API token)
                    if confluence_auth_method == "OAuth 2.0 (Recommended - Official MCP)":
                        if confluence_oauth_access_token and confluence_oauth_client_id:
                            confluence_config = {
                                'url': confluence_url,
                                'oauth_access_token': confluence_oauth_access_token,
                                'oauth_client_id': confluence_oauth_client_id,
                                'oauth_client_secret': confluence_oauth_client_secret,
                                'space': confluence_space,
                                'auth_method': 'oauth'
                            }
                        else:
                            confluence_config = None
                            st.warning("⚠️ Confluence OAuth credentials incomplete")
                    else:
                        # API Token method - initialize tools immediately if credentials provided
                        if confluence_url and confluence_email and confluence_token:
                            confluence_config = {
                                'url': confluence_url,
                                'email': confluence_email,
                                'token': confluence_token,
                                'space': confluence_space,
                                'auth_method': 'api_token'
                            }
                            # Try to initialize Confluence tools immediately
                            if ConfluenceTools:
                                try:
                                    st.session_state.confluence_tools = ConfluenceTools(confluence_url, confluence_email, confluence_token)
                                    safe_sidebar_success("✅ Confluence connected (direct API)")
                                except Exception as e2:
                                    st.warning(f"⚠️ Confluence connection failed: {e2}. Will retry on publish.")
                                    logger.warning(f"Confluence connection error: {e2}")
                            else:
                                logger.warning("ConfluenceTools not available - install required dependencies")
                        else:
                            confluence_config = None
                    
                    if github_token:
                        github_config = {
                            'token': github_token,
                            'owner': github_owner,
                            'repo': github_repo,
                            'toolsets': 'repos,issues,pull_requests'
                        }
                    
                    if slack_bot_token or (slack_email and slack_channel):
                        slack_config = {
                            'email': slack_email,
                            'channel': slack_channel,
                            'bot_token': slack_bot_token,
                            'team_id': slack_team_id
                        }
                    
                    amazon_q_config = None
                    if amazon_q_app_id and amazon_q_access_key and amazon_q_secret_key:
                        amazon_q_config = {
                            'app_id': amazon_q_app_id,
                            'region': amazon_q_region,
                            'access_key_id': amazon_q_access_key,
                            'secret_access_key': amazon_q_secret_key
                        }
                    
                    if jira_config or confluence_config or github_config or slack_config or amazon_q_config:
                        mcp_wrapper.initialize(
                            jira_config=jira_config,
                            confluence_config=confluence_config,
                            github_config=github_config,
                            slack_config=slack_config,
                            amazon_q_config=amazon_q_config
                        )
                        st.session_state.mcp_tools = mcp_wrapper
                        active_servers = mcp_wrapper.get_active_servers()
                        if active_servers:
                            safe_sidebar_success(f"✅ MCP integrations connected: {', '.join(active_servers.keys())}")
                        else:
                            safe_sidebar_success("✅ MCP configured (using direct API fallback)")
                except Exception as e:
                    logger.warning(f"MCP initialization failed, falling back to direct API: {e}")
                    # Fallback to direct API implementations
                    if jira_url and jira_email and jira_token and JiraTools:
                        try:
                            st.session_state.jira_tools = JiraTools(jira_url, jira_email, jira_token)
                            safe_sidebar_success("✅ Jira connected (direct API)")
                        except Exception as e2:
                            st.error(f"Jira connection error: {e2}")
                    elif jira_url and jira_email and jira_token:
                        logger.warning("JiraTools not available - install required dependencies")
                    
                    if confluence_url and confluence_email and confluence_token and ConfluenceTools:
                        try:
                            st.session_state.confluence_tools = ConfluenceTools(confluence_url, confluence_email, confluence_token)
                            safe_sidebar_success("✅ Confluence connected (direct API)")
                        except Exception as e2:
                            st.error(f"Confluence connection error: {e2}")
                    elif confluence_url and confluence_email and confluence_token:
                        logger.warning("ConfluenceTools not available - install required dependencies")
                    
                    if github_token and GitHubTools:
                        try:
                            st.session_state.github_tools = GitHubTools(github_token)
                            safe_sidebar_success("✅ GitHub connected (direct API)")
                        except Exception as e2:
                            st.error(f"GitHub connection error: {e2}")
                    elif github_token:
                        logger.warning("GitHubTools not available - install required dependencies")
            else:
                # Fallback to direct API if MCP not available
                if jira_url and jira_email and jira_token and JiraTools:
                    try:
                        st.session_state.jira_tools = JiraTools(jira_url, jira_email, jira_token)
                        safe_sidebar_success("✅ Jira connected")
                    except Exception as e:
                        st.error(f"Jira connection error: {e}")
                elif jira_url and jira_email and jira_token:
                    logger.warning("JiraTools not available - install required dependencies")
                
                if confluence_url and confluence_email and confluence_token and ConfluenceTools:
                    try:
                        st.session_state.confluence_tools = ConfluenceTools(confluence_url, confluence_email, confluence_token)
                        safe_sidebar_success("✅ Confluence connected")
                    except Exception as e:
                        st.error(f"Confluence connection error: {e}")
                elif confluence_url and confluence_email and confluence_token:
                    logger.warning("ConfluenceTools not available - install required dependencies")
                
                if github_token and GitHubTools:
                    try:
                        st.session_state.github_tools = GitHubTools(github_token)
                        safe_sidebar_success("✅ GitHub connected")
                    except Exception as e:
                        st.error(f"GitHub connection error: {e}")
                elif github_token:
                    logger.warning("GitHubTools not available - install required dependencies")
            
            if slack_email and slack_channel and SlackTools:
                try:
                    st.session_state.slack_tools = SlackTools(slack_email, slack_channel)
                    safe_sidebar_success("✅ Slack configured")
                except Exception as e:
                    st.error(f"Slack configuration error: {e}")
            elif slack_email and slack_channel:
                logger.warning("SlackTools not available - install required dependencies")
            
            if email_address and email_password and EmailTools:
                try:
                    st.session_state.email_tools = EmailTools(smtp_server, smtp_port, email_address, email_password)
                    safe_sidebar_success("✅ Email configured")
                except Exception as e:
                    st.error(f"Email configuration error: {e}")
            elif email_address and email_password:
                logger.warning("EmailTools not available - install required dependencies")
            
            # Update workflow step
            st.session_state.workflow_steps[0]['status'] = 'completed'
            st.session_state.current_step = 1
            safe_rerun()
    
    return None

def render_product_info_step():
    """Step 1: Product Information"""
    st.header("📝 Step 2: Product Information")
    st.info("Provide details about your product to get started.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        product_name = st.text_input("Product Name", key="product_name", placeholder="e.g., AI-Powered Analytics Platform")
        product_type = st.selectbox("Product Type", 
            ["SaaS", "Mobile App", "Web Application", "Enterprise Software", "Hardware", "Other"],
            key="product_type")
        target_market = st.text_input("Target Market", key="target_market", placeholder="e.g., Enterprise B2B")
        product_stage = st.selectbox("Product Stage",
            ["Ideation", "MVP/Validation", "Growth", "Maturity", "Pivot"],
            key="product_stage")
    
    with col2:
        industry = st.text_input("Industry", key="industry", placeholder="e.g., FinTech")
        user_persona = st.text_area("User Persona", key="user_persona", 
                                   placeholder="Describe your target user...", height=100)
        business_model = st.selectbox("Business Model",
            ["Subscription", "Freemium", "One-time Purchase", "Marketplace", "Enterprise License", "Other"],
            key="business_model")
        timeline = st.selectbox("Timeline Focus",
            ["Short-term (0-3 months)", "Medium-term (3-6 months)", "Long-term (6-12 months)", "Strategic (12+ months)"],
            key="timeline")
    
    st.subheader("Product Goals & Context")
    primary_goals = st.text_area("Primary Goals", key="primary_goals",
                                placeholder="What are your main objectives?", height=80)
    key_features = st.text_area("Key Features", key="key_features",
                               placeholder="List key features or capabilities...", height=80)
    
    col3, col4 = st.columns(2)
    with col3:
        constraints = st.text_area("Constraints", key="constraints",
                                  placeholder="Budget, timeline, technical constraints...", height=80)
        competitors = st.text_area("Competitors", key="competitors",
                                  placeholder="Main competitors or alternatives...", height=80)
    with col4:
        value_prop = st.text_area("Unique Value Proposition", key="value_prop",
                                 placeholder="What makes your product unique?", height=80)
        success_criteria = st.text_area("Success Criteria", key="success_criteria",
                                       placeholder="How will you measure success?", height=80)
    
    detail_level = st.selectbox("Level of Detail", ["Low", "Medium", "High"], key="detail_level")
    
    if st.button("✅ Save Product Info & Continue", type="primary", key="save_product_info"):
        if not product_name:
            st.error("⚠️ Product Name is required!")
        else:
            # Store product info
            product_info = {
                'product_name': product_name,
                'product_type': product_type,
                'target_market': target_market,
                'product_stage': product_stage,
                'industry': industry,
                'user_persona': user_persona,
                'business_model': business_model,
                'timeline': timeline,
                'primary_goals': primary_goals,
                'key_features': key_features,
                'constraints': constraints,
                'competitors': competitors,
                'value_prop': value_prop,
                'success_criteria': success_criteria,
                'detail_level': detail_level,
            }
            st.session_state.product_info = product_info
            
            # Generate plan ID if not exists
            if not st.session_state.current_plan_id:
                st.session_state.current_plan_id = f"plan_{uuid.uuid4().hex[:8]}"
                st.session_state.current_plan_version = 1
                st.session_state.plan_loaded = False  # Reset flag when creating new plan
            
            # Save product info to database immediately
            if db_manager:
                try:
                    # Ensure pm_output has product_info
                    if 'pm_output' not in st.session_state:
                        st.session_state.pm_output = {}
                    st.session_state.pm_output['product_info'] = product_info
                    
                    # Save to database
                    config = st.session_state.get('config', {})
                    db_manager.save_product_plan(
                        plan_id=st.session_state.current_plan_id,
                        product_name=product_name,
                        plan_data=st.session_state.pm_output,
                        configuration=config,
                        status='in_progress',
                        created_by='user',
                        notes='Product information captured'
                    )
                    logger.info(f"Saved product info for plan {st.session_state.current_plan_id}")
                except Exception as e:
                    logger.error(f"Error saving product info to database: {e}")
            
            # Update workflow step
            st.session_state.workflow_steps[1]['status'] = 'completed'
            st.session_state.current_step = 2
            safe_rerun()
    
    return None

def render_strategy_step():
    """Step 2: Strategy Generation"""
    st.header("🎯 Step 3: Strategy Generation")
    
    if 'product_info' not in st.session_state:
        st.warning("⚠️ Please complete Product Information step first!")
        if st.button("← Go to Product Info", key="back_to_product"):
            st.session_state.current_step = 1
            safe_rerun()
        return None
    
    if st.session_state.workflow_steps[2]['status'] == 'completed':
        st.success("✅ Strategy generated successfully!")
        
        # Show editable output
        strategy_content = st.session_state.pm_output.get('strategy', 'Not available')
        
        if render_editable_output:
            edited_strategy = render_editable_output(
                "📄 Strategy Output",
                strategy_content,
                "strategy",
                "Review and edit the strategy before proceeding. Your edits will be saved."
            )
            if edited_strategy != strategy_content:
                st.session_state.pm_output['strategy'] = edited_strategy
                # Save edited version to database
                if db_manager:
                    try:
                        db_manager.save_agent_output(
                            plan_id=st.session_state.current_plan_id,
                            version=st.session_state.current_plan_version or 1,
                            agent_name='strategy_agent',
                            output_content=edited_strategy,
                            metadata={'step': 'strategy', 'edited': True}
                        )
                    except Exception as e:
                        logger.error(f"Error saving edited strategy: {e}")
        else:
            with st.expander("📄 View Strategy", expanded=True):
                st.markdown(strategy_content)
        
        if st.button("🔄 Regenerate Strategy", key="regenerate_strategy"):
            st.session_state.workflow_steps[2]['status'] = 'pending'
            st.session_state.pm_output['strategy'] = ''
            safe_rerun()
    else:
        st.info("Click the button below to generate your product strategy using AI agents.")
        
        if st.button("🚀 Generate Strategy", type="primary", key="generate_strategy"):
            api_key = st.session_state.config.get('api_key')
            if not api_key:
                st.error("⚠️ OpenAI API Key not configured!")
                return None
            
            # Try to use unified agent system if available
            use_unified_system = UnifiedAgentSystem and 'unified_agent_system' not in st.session_state
            
            if use_unified_system:
                try:
                    # Initialize unified system
                    unified_system = UnifiedAgentSystem(api_key)
                    config = st.session_state.config.copy()
                    config['api_key'] = api_key
                    
                    with st.spinner("🎯 Initializing agent system..."):
                        import asyncio
                        asyncio.run(unified_system.initialize(config))
                    
                    st.session_state.unified_agent_system = unified_system
                    
                    # Show agent status
                    if render_status_dashboard:
                        agent_status = unified_system.get_agent_status()
                        render_status_dashboard(agent_status)
                    
                except Exception as e:
                    logger.warning(f"Unified agent system not available, using fallback: {e}")
                    use_unified_system = False
            
            with st.spinner("🎯 Generating strategy..."):
                product_info = st.session_state.product_info
                task = f"""
                Create a comprehensive product strategy for:
                
                Product: {product_info['product_name']}
                Type: {product_info['product_type']}
                Stage: {product_info['product_stage']}
                Target Market: {product_info['target_market']}
                Industry: {product_info['industry']}
                
                Goals: {product_info['primary_goals']}
                Value Proposition: {product_info['value_prop']}
                Competitors: {product_info['competitors']}
                
                Please provide:
                1. Product vision and mission
                2. Market positioning
                3. Competitive strategy
                4. Go-to-market approach
                5. Strategic initiatives
                6. Business model alignment
                
                Detail Level: {product_info['detail_level']}
                """
                
                if use_unified_system and st.session_state.unified_agent_system:
                    # Use unified agent system
                    try:
                        import asyncio
                        result = asyncio.run(
                            st.session_state.unified_agent_system.run_workflow_step(
                                'Strategy', task, {'product_info': product_info}
                            )
                        )
                        strategy_output = result.get('results', {}).get('strategy', {}).get('result', '')
                        
                        # Show interaction history
                        if render_agent_interaction_flow:
                            interactions = result.get('interaction_history', [])
                            render_agent_interaction_flow(interactions)
                    except Exception as e:
                        logger.error(f"Error using unified system: {e}")
                        # Fallback to simple agent
                        llm_config = {"config_list": [{"model": "gpt-4o-mini", "api_key": api_key}]}
                        strategy_agent = SwarmAgent("strategy_agent", llm_config=llm_config)
                        result, _, _ = initiate_swarm_chat(
                            initial_agent=strategy_agent,
                            agents=[strategy_agent],
                            user_agent=None,
                            messages=task,
                            max_rounds=3,
                        )
                        strategy_output = result.chat_history[-1].get('content', '') if result.chat_history else ''
                else:
                    # Fallback to simple agent
                    llm_config = {"config_list": [{"model": "gpt-4o-mini", "api_key": api_key}]}
                    strategy_agent = SwarmAgent("strategy_agent", llm_config=llm_config)
                    result, _, _ = initiate_swarm_chat(
                        initial_agent=strategy_agent,
                        agents=[strategy_agent],
                        user_agent=None,
                        messages=task,
                        max_rounds=3,
                    )
                    strategy_output = result.chat_history[-1].get('content', '') if result.chat_history else ''
                
                st.session_state.pm_output['strategy'] = strategy_output
                
                # Ensure product_info is in pm_output for saving
                if 'product_info' not in st.session_state.pm_output and st.session_state.get('product_info'):
                    st.session_state.pm_output['product_info'] = st.session_state.product_info
                
                # Save to database
                if db_manager:
                    try:
                        plan_version = st.session_state.current_plan_version or 1
                        db_manager.save_agent_output(
                            plan_id=st.session_state.current_plan_id,
                            version=plan_version,
                            agent_name='strategy_agent',
                            output_content=strategy_output,
                            metadata={'step': 'strategy'}
                        )
                        
                        # Also update the main plan with latest data
                        config = st.session_state.get('config', {})
                        db_manager.save_product_plan(
                            plan_id=st.session_state.current_plan_id,
                            product_name=st.session_state.product_info.get('product_name', 'Unknown'),
                            plan_data=st.session_state.pm_output,
                            configuration=config,
                            status='in_progress',
                            created_by='user'
                        )
                        
                        # Save chat history
                        for msg in result.chat_history:
                            if isinstance(msg, dict):
                                role = msg.get('role', 'assistant')
                                content = msg.get('content', '')
                                if content:
                                    db_manager.save_chat_history(
                                        plan_id=st.session_state.current_plan_id,
                                        version=plan_version,
                                        agent_name='strategy_agent',
                                        message_role=role,
                                        message_content=content,
                                        metadata={'step': 'strategy'}
                                    )
                    except Exception as e:
                        logger.error(f"Error saving strategy: {e}")
                
                st.session_state.workflow_steps[2]['status'] = 'completed'
                safe_rerun()
    
    # Navigation buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Previous Step", key="prev_from_strategy"):
            st.session_state.current_step = 1
            safe_rerun()
    with col2:
        if st.session_state.workflow_steps[2]['status'] == 'completed':
            if st.button("Next Step →", type="primary", key="next_from_strategy"):
                st.session_state.current_step = 3
                safe_rerun()
    
    return None

def render_research_step():
    """Step 3: Research Generation"""
    st.header("🔍 Step 4: Research & Analysis")
    
    if st.session_state.workflow_steps[2]['status'] != 'completed':
        st.warning("⚠️ Please complete Strategy step first!")
        if st.button("← Go to Strategy", key="back_to_strategy"):
            st.session_state.current_step = 2
            safe_rerun()
        return None
    
    if st.session_state.workflow_steps[3]['status'] == 'completed':
        st.success("✅ Research completed successfully!")
        with st.expander("📄 View Research", expanded=True):
            st.markdown(st.session_state.pm_output.get('research', 'Not available'))
        
        if st.button("🔄 Regenerate Research", key="regenerate_research"):
            st.session_state.workflow_steps[3]['status'] = 'pending'
            st.session_state.pm_output['research'] = ''
            safe_rerun()
    else:
        st.info("Generate comprehensive user research, competitive analysis, and market insights.")
        
        if st.button("🚀 Generate Research", type="primary", key="generate_research"):
            with st.spinner("🔍 Conducting research..."):
                api_key = st.session_state.config.get('api_key')
                llm_config = {"config_list": [{"model": "gpt-4o-mini", "api_key": api_key}]}
                
                product_info = st.session_state.product_info
                strategy = st.session_state.pm_output.get('strategy', '')
                
                task = f"""
                Based on the product strategy, conduct comprehensive research:
                
                Product: {product_info['product_name']}
                User Persona: {product_info['user_persona']}
                Competitors: {product_info['competitors']}
                
                Strategy Context:
                {strategy[:1000]}
                
                Please provide:
                1. User research methodology
                2. Persona development and user needs
                3. Competitive analysis
                4. Market opportunities
                5. Validation strategies
                
                Detail Level: {product_info['detail_level']}
                """
                
                research_agent = SwarmAgent("research_agent", llm_config=llm_config)
                
                result, _, _ = initiate_swarm_chat(
                    initial_agent=research_agent,
                    agents=[research_agent],
                    user_agent=None,
                    messages=task,
                    max_rounds=3,
                )
                
                research_output = result.chat_history[-1].get('content', '') if result.chat_history else ''
                st.session_state.pm_output['research'] = research_output
                
                if db_manager:
                    try:
                        plan_id = st.session_state.current_plan_id
                        version = st.session_state.current_plan_version or 1
                        
                        db_manager.save_agent_output(
                            plan_id=plan_id,
                            version=version,
                            agent_name='research_agent',
                            output_content=research_output,
                            metadata={'step': 'research'}
                        )
                        
                        # Save chat history
                        if result.chat_history:
                            for idx, msg in enumerate(result.chat_history):
                                if isinstance(msg, dict):
                                    role = msg.get('role', 'assistant')
                                    content = msg.get('content', '')
                                    agent_name = msg.get('name', 'research_agent')
                                    if content:
                                        try:
                                            db_manager.save_chat_history(
                                                plan_id=plan_id,
                                                version=version,
                                                agent_name=agent_name,
                                                message_role=role,
                                                message_content=content,
                                                metadata={'round': idx, 'step': 'research'}
                                            )
                                        except Exception as e2:
                                            logger.error(f"Error saving chat history: {e2}")
                    except Exception as e:
                        logger.error(f"Error saving research: {e}")
                
                st.session_state.workflow_steps[3]['status'] = 'completed'
                safe_rerun()
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Previous Step", key="prev_from_research"):
            st.session_state.current_step = 2
            safe_rerun()
    with col2:
        if st.session_state.workflow_steps[3]['status'] == 'completed':
            if st.button("Next Step →", type="primary", key="next_from_research"):
                st.session_state.current_step = 4
                safe_rerun()
    
    return None

def render_roadmap_step():
    """Step 4: Roadmap Generation"""
    st.header("🗺️ Step 5: Product Roadmap")
    
    if st.session_state.workflow_steps[3]['status'] != 'completed':
        st.warning("⚠️ Please complete Research step first!")
        if st.button("← Go to Research", key="back_to_research"):
            st.session_state.current_step = 3
            safe_rerun()
        return None
    
    if st.session_state.workflow_steps[4]['status'] == 'completed':
        st.success("✅ Roadmap created successfully!")
        with st.expander("📄 View Roadmap", expanded=True):
            st.markdown(st.session_state.pm_output.get('roadmap', 'Not available'))
        
        if st.button("🔄 Regenerate Roadmap", key="regenerate_roadmap"):
            st.session_state.workflow_steps[4]['status'] = 'pending'
            st.session_state.pm_output['roadmap'] = ''
            safe_rerun()
    else:
        st.info("Create a prioritized product roadmap with features, releases, and milestones.")
        
        if st.button("🚀 Generate Roadmap", type="primary", key="generate_roadmap"):
            with st.spinner("🗺️ Creating roadmap..."):
                api_key = st.session_state.config.get('api_key')
                llm_config = {"config_list": [{"model": "gpt-4o-mini", "api_key": api_key}]}
                
                product_info = st.session_state.product_info
                strategy = st.session_state.pm_output.get('strategy', '')
                research = st.session_state.pm_output.get('research', '')
                
                task = f"""
                Create a comprehensive product roadmap:
                
                Product: {product_info['product_name']}
                Timeline: {product_info['timeline']}
                Key Features: {product_info['key_features']}
                
                Strategy Context:
                {strategy[:800]}
                
                Research Context:
                {research[:800]}
                
                Please provide:
                1. Feature prioritization (RICE, MoSCoW, or Value vs Effort)
                2. Release planning and milestones
                3. MVP scoping
                4. Phased rollouts
                5. Dependency management
                
                Detail Level: {product_info['detail_level']}
                """
                
                roadmap_agent = SwarmAgent("roadmap_agent", llm_config=llm_config)
                
                result, _, _ = initiate_swarm_chat(
                    initial_agent=roadmap_agent,
                    agents=[roadmap_agent],
                    user_agent=None,
                    messages=task,
                    max_rounds=3,
                )
                
                roadmap_output = result.chat_history[-1].get('content', '') if result.chat_history else ''
                st.session_state.pm_output['roadmap'] = roadmap_output
                
                if db_manager:
                    try:
                        plan_id = st.session_state.current_plan_id
                        version = st.session_state.current_plan_version or 1
                        
                        db_manager.save_agent_output(
                            plan_id=plan_id,
                            version=version,
                            agent_name='roadmap_agent',
                            output_content=roadmap_output,
                            metadata={'step': 'roadmap'}
                        )
                        
                        # Save chat history
                        if result.chat_history:
                            for idx, msg in enumerate(result.chat_history):
                                if isinstance(msg, dict):
                                    role = msg.get('role', 'assistant')
                                    content = msg.get('content', '')
                                    agent_name = msg.get('name', 'roadmap_agent')
                                    if content:
                                        try:
                                            db_manager.save_chat_history(
                                                plan_id=plan_id,
                                                version=version,
                                                agent_name=agent_name,
                                                message_role=role,
                                                message_content=content,
                                                metadata={'round': idx, 'step': 'roadmap'}
                                            )
                                        except Exception as e2:
                                            logger.error(f"Error saving chat history: {e2}")
                    except Exception as e:
                        logger.error(f"Error saving roadmap: {e}")
                
                st.session_state.workflow_steps[4]['status'] = 'completed'
                safe_rerun()
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Previous Step", key="prev_from_roadmap"):
            st.session_state.current_step = 3
            safe_rerun()
    with col2:
        if st.session_state.workflow_steps[4]['status'] == 'completed':
            if st.button("Next Step →", type="primary", key="next_from_roadmap"):
                st.session_state.current_step = 5
                safe_rerun()
    
    return None

def render_metrics_step():
    """Step 5: Metrics Framework"""
    st.header("📊 Step 6: Metrics & Analytics")
    
    if st.session_state.workflow_steps[4]['status'] != 'completed':
        st.warning("⚠️ Please complete Roadmap step first!")
        if st.button("← Go to Roadmap", key="back_to_roadmap"):
            st.session_state.current_step = 4
            safe_rerun()
        return None
    
    if st.session_state.workflow_steps[5]['status'] == 'completed':
        st.success("✅ Metrics framework created successfully!")
        with st.expander("📄 View Metrics", expanded=True):
            st.markdown(st.session_state.pm_output.get('metrics', 'Not available'))
        
        if st.button("🔄 Regenerate Metrics", key="regenerate_metrics"):
            st.session_state.workflow_steps[5]['status'] = 'pending'
            st.session_state.pm_output['metrics'] = ''
            safe_rerun()
    else:
        st.info("Define KPIs, success metrics, and analytics frameworks.")
        
        if st.button("🚀 Generate Metrics Framework", type="primary", key="generate_metrics"):
            with st.spinner("📊 Creating metrics framework..."):
                api_key = st.session_state.config.get('api_key')
                llm_config = {"config_list": [{"model": "gpt-4o-mini", "api_key": api_key}]}
                
                product_info = st.session_state.product_info
                success_criteria = product_info.get('success_criteria', '')
                
                task = f"""
                Create a comprehensive metrics framework:
                
                Product: {product_info['product_name']}
                Business Model: {product_info['business_model']}
                Success Criteria: {success_criteria}
                
                Please provide:
                1. North Star metric definition
                2. KPI framework (AARRR, HEART, etc.)
                3. Analytics tracking plan
                4. Success measurement criteria
                5. Dashboard structure
                
                Detail Level: {product_info['detail_level']}
                """
                
                metrics_agent = SwarmAgent("metrics_agent", llm_config=llm_config)
                
                result, _, _ = initiate_swarm_chat(
                    initial_agent=metrics_agent,
                    agents=[metrics_agent],
                    user_agent=None,
                    messages=task,
                    max_rounds=3,
                )
                
                metrics_output = result.chat_history[-1].get('content', '') if result.chat_history else ''
                st.session_state.pm_output['metrics'] = metrics_output
                
                if db_manager:
                    try:
                        plan_id = st.session_state.current_plan_id
                        version = st.session_state.current_plan_version or 1
                        
                        db_manager.save_agent_output(
                            plan_id=plan_id,
                            version=version,
                            agent_name='metrics_agent',
                            output_content=metrics_output,
                            metadata={'step': 'metrics'}
                        )
                        
                        # Save chat history
                        if result.chat_history:
                            for idx, msg in enumerate(result.chat_history):
                                if isinstance(msg, dict):
                                    role = msg.get('role', 'assistant')
                                    content = msg.get('content', '')
                                    agent_name = msg.get('name', 'metrics_agent')
                                    if content:
                                        try:
                                            db_manager.save_chat_history(
                                                plan_id=plan_id,
                                                version=version,
                                                agent_name=agent_name,
                                                message_role=role,
                                                message_content=content,
                                                metadata={'round': idx, 'step': 'metrics'}
                                            )
                                        except Exception as e2:
                                            logger.error(f"Error saving chat history: {e2}")
                    except Exception as e:
                        logger.error(f"Error saving metrics: {e}")
                
                st.session_state.workflow_steps[5]['status'] = 'completed'
                safe_rerun()
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Previous Step", key="prev_from_metrics"):
            st.session_state.current_step = 4
            safe_rerun()
    with col2:
        if st.session_state.workflow_steps[5]['status'] == 'completed':
            if st.button("Next Step →", type="primary", key="next_from_metrics"):
                st.session_state.current_step = 6
                safe_rerun()
    
    return None

def render_stakeholder_step():
    """Step 6: Stakeholder Management"""
    st.header("🤝 Step 7: Stakeholder Management")
    
    if st.session_state.workflow_steps[5]['status'] != 'completed':
        st.warning("⚠️ Please complete Metrics step first!")
        if st.button("← Go to Metrics", key="back_to_metrics"):
            st.session_state.current_step = 5
            safe_rerun()
        return None
    
    if st.session_state.workflow_steps[6]['status'] == 'completed':
        st.success("✅ Stakeholder plan created successfully!")
        with st.expander("📄 View Stakeholder Plan", expanded=True):
            st.markdown(st.session_state.pm_output.get('stakeholder', 'Not available'))
        
        if st.button("🔄 Regenerate Stakeholder Plan", key="regenerate_stakeholder"):
            st.session_state.workflow_steps[6]['status'] = 'pending'
            st.session_state.pm_output['stakeholder'] = ''
            safe_rerun()
    else:
        st.info("Create stakeholder management, communication plans, and alignment strategies.")
        
        if st.button("🚀 Generate Stakeholder Plan", type="primary", key="generate_stakeholder"):
            with st.spinner("🤝 Creating stakeholder plan..."):
                api_key = st.session_state.config.get('api_key')
                llm_config = {"config_list": [{"model": "gpt-4o-mini", "api_key": api_key}]}
                
                product_info = st.session_state.product_info
                
                task = f"""
                Create a comprehensive stakeholder management plan:
                
                Product: {product_info['product_name']}
                Target Market: {product_info['target_market']}
                Industry: {product_info['industry']}
                
                Please provide:
                1. Stakeholder identification and mapping
                2. Communication plans and cadence
                3. Alignment strategies
                4. Product reviews and demos
                5. Cross-functional collaboration
                
                Detail Level: {product_info['detail_level']}
                """
                
                stakeholder_agent = SwarmAgent("stakeholder_agent", llm_config=llm_config)
                
                result, _, _ = initiate_swarm_chat(
                    initial_agent=stakeholder_agent,
                    agents=[stakeholder_agent],
                    user_agent=None,
                    messages=task,
                    max_rounds=3,
                )
                
                stakeholder_output = result.chat_history[-1].get('content', '') if result.chat_history else ''
                st.session_state.pm_output['stakeholder'] = stakeholder_output
                
                if db_manager:
                    try:
                        plan_id = st.session_state.current_plan_id
                        version = st.session_state.current_plan_version or 1
                        
                        db_manager.save_agent_output(
                            plan_id=plan_id,
                            version=version,
                            agent_name='stakeholder_agent',
                            output_content=stakeholder_output,
                            metadata={'step': 'stakeholder'}
                        )
                        
                        # Save chat history
                        if result.chat_history:
                            for idx, msg in enumerate(result.chat_history):
                                if isinstance(msg, dict):
                                    role = msg.get('role', 'assistant')
                                    content = msg.get('content', '')
                                    agent_name = msg.get('name', 'stakeholder_agent')
                                    if content:
                                        try:
                                            db_manager.save_chat_history(
                                                plan_id=plan_id,
                                                version=version,
                                                agent_name=agent_name,
                                                message_role=role,
                                                message_content=content,
                                                metadata={'round': idx, 'step': 'stakeholder'}
                                            )
                                        except Exception as e2:
                                            logger.error(f"Error saving chat history: {e2}")
                    except Exception as e:
                        logger.error(f"Error saving stakeholder plan: {e}")
                
                st.session_state.workflow_steps[6]['status'] = 'completed'
                safe_rerun()
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Previous Step", key="prev_from_stakeholder"):
            st.session_state.current_step = 5
            safe_rerun()
    with col2:
        if st.session_state.workflow_steps[6]['status'] == 'completed':
            if st.button("Next Step →", type="primary", key="next_from_stakeholder"):
                st.session_state.current_step = 7
                safe_rerun()
    
    return None

def render_execution_step():
    """Step 7: Execution Plan"""
    st.header("⚡ Step 8: Execution Plan")
    
    if st.session_state.workflow_steps[6]['status'] != 'completed':
        st.warning("⚠️ Please complete Stakeholder step first!")
        if st.button("← Go to Stakeholder", key="back_to_stakeholder"):
            st.session_state.current_step = 6
            safe_rerun()
        return None
    
    if st.session_state.workflow_steps[7]['status'] == 'completed':
        st.success("✅ Execution plan created successfully!")
        with st.expander("📄 View Execution Plan", expanded=True):
            st.markdown(st.session_state.pm_output.get('execution', 'Not available'))
        
        if st.button("🔄 Regenerate Execution Plan", key="regenerate_execution"):
            st.session_state.workflow_steps[7]['status'] = 'pending'
            st.session_state.pm_output['execution'] = ''
            safe_rerun()
    else:
        st.info("Create sprint planning, agile frameworks, and delivery coordination plans.")
        
        if st.button("🚀 Generate Execution Plan", type="primary", key="generate_execution"):
            with st.spinner("⚡ Creating execution plan..."):
                api_key = st.session_state.config.get('api_key')
                llm_config = {"config_list": [{"model": "gpt-4o-mini", "api_key": api_key}]}
                
                product_info = st.session_state.product_info
                config = st.session_state.config
                
                task = f"""
                Create a comprehensive execution plan:
                
                Product: {product_info['product_name']}
                Team Size: {config.get('team_size', 8)}
                Sprint Duration: {config.get('sprint_duration_weeks', 2)} weeks
                Max Story Points: {config.get('max_story_points', 70)}
                
                Please provide:
                1. Sprint planning framework
                2. Agile practices and ceremonies
                3. User stories and acceptance criteria guidelines
                4. Release cycles and deployment
                5. Backlog management
                6. Quality assurance and delivery
                
                Detail Level: {product_info['detail_level']}
                """
                
                execution_agent = SwarmAgent("execution_agent", llm_config=llm_config)
                
                result, _, _ = initiate_swarm_chat(
                    initial_agent=execution_agent,
                    agents=[execution_agent],
                    user_agent=None,
                    messages=task,
                    max_rounds=3,
                )
                
                execution_output = result.chat_history[-1].get('content', '') if result.chat_history else ''
                st.session_state.pm_output['execution'] = execution_output
                
                if db_manager:
                    try:
                        plan_id = st.session_state.current_plan_id
                        version = st.session_state.current_plan_version or 1
                        
                        db_manager.save_agent_output(
                            plan_id=plan_id,
                            version=version,
                            agent_name='execution_agent',
                            output_content=execution_output,
                            metadata={'step': 'execution'}
                        )
                        
                        # Save chat history
                        if result.chat_history:
                            for idx, msg in enumerate(result.chat_history):
                                if isinstance(msg, dict):
                                    role = msg.get('role', 'assistant')
                                    content = msg.get('content', '')
                                    agent_name = msg.get('name', 'execution_agent')
                                    if content:
                                        try:
                                            db_manager.save_chat_history(
                                                plan_id=plan_id,
                                                version=version,
                                                agent_name=agent_name,
                                                message_role=role,
                                                message_content=content,
                                                metadata={'round': idx, 'step': 'execution'}
                                            )
                                        except Exception as e2:
                                            logger.error(f"Error saving chat history: {e2}")
                    except Exception as e:
                        logger.error(f"Error saving execution plan: {e}")
                
                st.session_state.workflow_steps[7]['status'] = 'completed'
                safe_rerun()
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Previous Step", key="prev_from_execution"):
            st.session_state.current_step = 6
            safe_rerun()
    with col2:
        if st.session_state.workflow_steps[7]['status'] == 'completed':
            if st.button("Next Step →", type="primary", key="next_from_execution"):
                st.session_state.current_step = 8
                safe_rerun()
    
    return None

def render_publish_step():
    """Step 8: Publish to Jira & Confluence"""
    st.header("🚀 Step 9: Publish & Execute")
    
    if st.session_state.workflow_steps[7]['status'] != 'completed':
        st.warning("⚠️ Please complete Execution step first!")
        if st.button("← Go to Execution", key="back_to_execution"):
            st.session_state.current_step = 7
            safe_rerun()
        return None
    
    st.success("✨ All planning steps completed! Ready to publish.")
    
    # Show summary
    with st.expander("📋 Review Complete Plan", expanded=False):
        st.markdown("### Strategy")
        st.markdown(st.session_state.pm_output.get('strategy', 'N/A')[:500] + "...")
        st.markdown("### Research")
        st.markdown(st.session_state.pm_output.get('research', 'N/A')[:500] + "...")
        st.markdown("### Roadmap")
        st.markdown(st.session_state.pm_output.get('roadmap', 'N/A')[:500] + "...")
    
    # Publishing options
    st.subheader("📤 Publishing Options")
    
    # Check configuration from session state
    config = st.session_state.get('config', {})
    
    # Check for MCP tools first, then fallback to direct API
    mcp_tools_obj = st.session_state.get('mcp_tools')
    mcp_available = False
    if mcp_tools_obj:
        try:
            mcp_available = mcp_tools_obj.is_initialized() if hasattr(mcp_tools_obj, 'is_initialized') else False
        except:
            mcp_available = False
    
    # Check if we have direct API tools
    jira_tools_obj = st.session_state.get('jira_tools')
    confluence_tools_obj = st.session_state.get('confluence_tools')
    
    # Also check if we have config that can be used to initialize tools
    has_jira_config = bool(config.get('jira_url') and config.get('jira_email') and config.get('jira_token'))
    has_confluence_config = bool(config.get('confluence_url') and config.get('confluence_email') and config.get('confluence_token'))
    
    # Determine availability - tools exist OR we can initialize from config
    jira_available = mcp_available or (jira_tools_obj is not None) or (has_jira_config and JiraTools)
    confluence_available = mcp_available or (confluence_tools_obj is not None) or (has_confluence_config and ConfluenceTools)
    email_available = st.session_state.get('email_tools') is not None
    
    # Debug information
    with st.expander("🔍 Integration Status", expanded=False):
        st.write("**MCP Tools:**", "✅ Available" if mcp_available else "❌ Not available")
        st.write("**Jira Tools Object:**", "✅ Present" if jira_tools_obj else "❌ Not present")
        st.write("**Jira Config:**", "✅ Present" if has_jira_config else "❌ Not present")
        st.write("**JiraTools Class:**", "✅ Available" if JiraTools else "❌ Not available")
        st.write("**Confluence Tools Object:**", "✅ Present" if confluence_tools_obj else "❌ Not present")
        st.write("**Confluence Config:**", "✅ Present" if has_confluence_config else "❌ Not present")
        st.write("**ConfluenceTools Class:**", "✅ Available" if ConfluenceTools else "❌ Not available")
        st.write("**Jira Available:**", "✅ Yes" if jira_available else "❌ No")
        st.write("**Confluence Available:**", "✅ Yes" if confluence_available else "❌ No")
    
    if mcp_available:
        # Check if custom MCP server is being used
        active_servers = mcp_tools_obj.get_active_servers() if hasattr(mcp_tools_obj, 'get_active_servers') else {}
        if "atlassian_custom" in active_servers:
            st.success("✅ Custom Atlassian MCP server configured (API token authentication)")
            st.info("📡 MCP integrations available - will use custom MCP server for publishing")
        else:
            st.info("📡 MCP integrations available - will use MCP servers for publishing")
    elif has_jira_config or has_confluence_config:
        # Check if using API tokens
        using_api_tokens = (
            (config.get('jira_auth_method', '').endswith('API Token')) or
            (config.get('confluence_auth_method', '').endswith('API Token'))
        )
        
        if using_api_tokens:
            # Check if custom MCP server is available
            import pathlib
            custom_mcp_path = pathlib.Path(__file__).parent / "custom_mcp_atlassian.py"
            if custom_mcp_path.exists():
                st.success("✅ Custom Atlassian MCP server available (API token authentication)")
                st.info("📡 Custom MCP wrapper will be used for publishing - full MCP protocol support")
            else:
                st.warning("⚠️ API Token authentication detected for Jira/Confluence")
                st.info("💡 Custom MCP server not found. Direct API tools will be used (not MCP protocol).")
        else:
            st.info("✅ MCP integration ready - tools will be initialized on publish")
    
    # Add button to re-initialize tools if config exists but tools aren't available
    if (has_jira_config or has_confluence_config) and not jira_available and not confluence_available:
        if st.button("🔄 Initialize Tools from Configuration", type="secondary", key="reinit_tools"):
            with st.spinner("Initializing tools..."):
                # Initialize Jira if config exists
                if has_jira_config and JiraTools:
                    try:
                        jira_url = config.get('jira_url')
                        jira_email = config.get('jira_email')
                        jira_token = config.get('jira_token')
                        if jira_url and jira_email and jira_token:
                            st.session_state.jira_tools = JiraTools(jira_url, jira_email, jira_token)
                            st.success("✅ Jira tools initialized successfully!")
                            safe_rerun()
                    except Exception as e:
                        st.error(f"❌ Failed to initialize Jira tools: {e}")
                        logger.error(f"Jira initialization error: {e}")
                
                # Initialize Confluence if config exists
                if has_confluence_config and ConfluenceTools:
                    try:
                        confluence_url = config.get('confluence_url')
                        confluence_email = config.get('confluence_email')
                        confluence_token = config.get('confluence_token')
                        if confluence_url and confluence_email and confluence_token:
                            st.session_state.confluence_tools = ConfluenceTools(confluence_url, confluence_email, confluence_token)
                            st.success("✅ Confluence tools initialized successfully!")
                            safe_rerun()
                    except Exception as e:
                        st.error(f"❌ Failed to initialize Confluence tools: {e}")
                        logger.error(f"Confluence initialization error: {e}")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if jira_available:
            if st.button("📋 Publish to Jira", type="primary", key="publish_jira_btn",
                         help="Create epics, stories, releases, and sprints in Jira"):
                st.session_state.publish_to_jira = True
                st.session_state.publish_to_confluence = False
                execute_publishing()
        else:
            st.button("📋 Publish to Jira", disabled=True, key="publish_jira_disabled",
                    help="Jira integration not configured")
    
    with col2:
        if confluence_available:
            if st.button("📚 Publish to Confluence", type="primary", key="publish_confluence_btn",
                        help="Publish all documents and reports to Confluence"):
                st.session_state.publish_to_jira = False
                st.session_state.publish_to_confluence = True
                execute_publishing()
        else:
            st.button("📚 Publish to Confluence", disabled=True, key="publish_confluence_disabled",
                    help="Confluence integration not configured")
    
    with col3:
        if jira_available and confluence_available:
            if st.button("🚀 Publish All", type="primary", key="publish_all_btn",
                        help="Publish to both Jira and Confluence, send email, and set up sprints"):
                st.session_state.publish_to_jira = True
                st.session_state.publish_to_confluence = True
                execute_publishing()
        else:
            st.button("🚀 Publish All", disabled=True, key="publish_all_disabled",
                    help="Requires both Jira and Confluence integration")
    
    # Save to database
    if st.button("💾 Save Plan to Database", key="save_plan_db"):
        if db_manager:
            try:
                product_info = st.session_state.product_info
                config = st.session_state.config
                
                result = db_manager.save_product_plan(
                    plan_id=st.session_state.current_plan_id,
                    product_name=product_info['product_name'],
                    plan_data=st.session_state.pm_output,
                    configuration=config,
                    status='planning_complete',
                    created_by='user'
                )
                
                st.session_state.current_plan_version = result['version']
                st.success(f"✅ Plan saved! ID: {st.session_state.current_plan_id}, Version: {result['version']}")
            except Exception as e:
                st.error(f"Error saving plan: {e}")
                logger.error(f"Error saving plan: {e}")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Previous Step", key="prev_from_publish"):
            st.session_state.current_step = 7
            safe_rerun()
    
    return None

def execute_publishing():
    """Execute the publishing workflow with full agent orchestration"""
    publish_jira = st.session_state.get('publish_to_jira', False)
    publish_confluence = st.session_state.get('publish_to_confluence', False)
    
    if not publish_jira and not publish_confluence:
        st.warning("⚠️ Please select at least one publishing option!")
        return
    
    with st.spinner("🚀 Publishing content..."):
        api_key = st.session_state.config.get('api_key')
        if not api_key:
            st.error("⚠️ OpenAI API Key not configured!")
            return
        
        # Initialize tools if not already initialized
        config = st.session_state.config
        
        # Initialize Jira tools if needed
        if publish_jira and not st.session_state.get('jira_tools') and not st.session_state.get('mcp_tools'):
            jira_url = config.get('jira_url')
            jira_email = config.get('jira_email')
            jira_token = config.get('jira_token')
            
            if jira_url and jira_email and jira_token and JiraTools:
                try:
                    st.session_state.jira_tools = JiraTools(jira_url, jira_email, jira_token)
                    st.info("✅ Jira tools initialized")
                except Exception as e:
                    st.error(f"❌ Failed to initialize Jira tools: {e}")
                    logger.error(f"Jira initialization error: {e}")
                    return
        
        # Initialize Confluence tools if needed
        if publish_confluence and not st.session_state.get('confluence_tools') and not st.session_state.get('mcp_tools'):
            confluence_url = config.get('confluence_url')
            confluence_email = config.get('confluence_email')
            confluence_token = config.get('confluence_token')
            
            if confluence_url and confluence_email and confluence_token and ConfluenceTools:
                try:
                    st.session_state.confluence_tools = ConfluenceTools(confluence_url, confluence_email, confluence_token)
                    st.info("✅ Confluence tools initialized")
                except Exception as e:
                    st.error(f"❌ Failed to initialize Confluence tools: {e}")
                    logger.error(f"Confluence initialization error: {e}")
                    return
        
        llm_config = {"config_list": [{"model": "gpt-4o-mini", "api_key": api_key}]}
        
        # Prepare execution task
        product_info = st.session_state.product_info
        
        execution_tasks = []
        if publish_jira:
            execution_tasks.append("1. Create Jira epics, stories, and releases from the strategy and roadmap")
            execution_tasks.append("2. Set up sprints with capacity management")
        if publish_confluence:
            execution_tasks.append("3. Publish all product management content to Confluence with nested structure")
        if publish_jira and publish_confluence and st.session_state.get('email_tools'):
            execution_tasks.append("4. Send email notification to Slack with links")
        
        execution_task = f"""
        As the Product Management Execution Team, your mission is to create a COMPLETE, PRODUCTION-READY product management structure that cuts down time for creating PRDs, Strategy documents, and all other product management artifacts.
        
        Based on the completed product management plan, please:
        {chr(10).join(execution_tasks)}
        
        **CRITICAL REQUIREMENTS**:
        - For Jira: Create MULTIPLE items (3-5+ epics, 15-30+ stories, 2-3+ releases) - NOT just single items
        - For Confluence: Create COMPLETE nested structure (8-12+ pages) - NOT just a single page
        - All content must be production-ready and enable the entire team to use it effectively
        - This is about building a complete knowledge base and project structure, not creating test items
        
        Product Plan Summary:
        Strategy: {st.session_state.pm_output.get('strategy', '')[:500]}
        Roadmap: {st.session_state.pm_output.get('roadmap', '')[:500]}
        Execution: {st.session_state.pm_output.get('execution', '')[:500]}
        """
        
        # Create execution agents
        exec_agents = {}
        exec_context_variables = {
            "strategy": st.session_state.pm_output.get('strategy', ''),
            "research": st.session_state.pm_output.get('research', ''),
            "roadmap": st.session_state.pm_output.get('roadmap', ''),
            "metrics": st.session_state.pm_output.get('metrics', ''),
            "stakeholder": st.session_state.pm_output.get('stakeholder', ''),
            "execution": st.session_state.pm_output.get('execution', ''),
        }
        
        # Use MCP tools if available, otherwise fallback to direct API
        mcp_tools_obj = st.session_state.get('mcp_tools')
        mcp_tools_available = False
        if mcp_tools_obj:
            try:
                mcp_tools_available = mcp_tools_obj.is_initialized() if hasattr(mcp_tools_obj, 'is_initialized') else False
            except:
                mcp_tools_available = False
        
        # Prepare MCP tools configuration (for future use or re-initialization)
        jira_config = None
        confluence_config = None
        github_config = None
        
        if publish_jira:
            # Check for OAuth or API token method
            jira_auth_method = config.get('jira_auth_method', 'api_token')
            if jira_auth_method == 'oauth':
                jira_config = {
                    'url': config.get('jira_url', ''),
                    'oauth_access_token': config.get('jira_oauth_access_token', ''),
                    'oauth_client_id': config.get('jira_oauth_client_id', ''),
                    'oauth_client_secret': config.get('jira_oauth_client_secret', ''),
                    'project_key': config.get('jira_project_key', ''),
                    'board_id': config.get('jira_board_id', 0),
                    'auth_method': 'oauth'
                }
            else:
                jira_config = {
                    'url': config.get('jira_url', ''),
                    'email': config.get('jira_email', ''),
                    'token': config.get('jira_token', ''),
                    'project_key': config.get('jira_project_key', ''),
                    'board_id': config.get('jira_board_id', 0),
                    'auth_method': 'api_token'
                }
        
        if publish_confluence:
            # Check for OAuth or API token method
            confluence_auth_method = config.get('confluence_auth_method', 'api_token')
            if confluence_auth_method == 'oauth':
                confluence_config = {
                    'url': config.get('confluence_url', ''),
                    'oauth_access_token': config.get('confluence_oauth_access_token', ''),
                    'oauth_client_id': config.get('confluence_oauth_client_id', ''),
                    'oauth_client_secret': config.get('confluence_oauth_client_secret', ''),
                    'space': config.get('confluence_space', ''),
                    'auth_method': 'oauth'
                }
            else:
                confluence_config = {
                    'url': config.get('confluence_url', ''),
                    'email': config.get('confluence_email', ''),
                    'token': config.get('confluence_token', ''),
                    'space': config.get('confluence_space', ''),
                    'auth_method': 'api_token'
                }
        
        if config.get('github_token'):
            github_config = {
                'token': config.get('github_token', ''),
                'owner': config.get('github_owner', ''),
                'repo': config.get('github_repo', ''),
                'toolsets': 'repos,issues,pull_requests'
            }
        
        slack_config = None
        if config.get('slack_bot_token') or (config.get('slack_email') and config.get('slack_channel')):
            slack_config = {
                'email': config.get('slack_email', ''),
                'channel': config.get('slack_channel', ''),
                'bot_token': config.get('slack_bot_token', ''),
                'team_id': config.get('slack_team_id', '')
            }
        
        amazon_q_config = None
        if config.get('amazon_q_app_id'):
            amazon_q_config = {
                'app_id': config.get('amazon_q_app_id', ''),
                'region': config.get('amazon_q_region', 'us-east-1'),
                'access_key_id': config.get('amazon_q_access_key', ''),
                'secret_access_key': config.get('amazon_q_secret_key', '')
            }
        
        # Store tools in context (MCP or direct API)
        if mcp_tools_available:
            exec_context_variables["_mcp_tools"] = st.session_state.mcp_tools.get_tools()
            exec_context_variables["_use_mcp"] = True
            logger.info("Using MCP tools for publishing")
        else:
            exec_context_variables["_jira_tools"] = st.session_state.get('jira_tools')
            exec_context_variables["_confluence_tools"] = st.session_state.get('confluence_tools')
            exec_context_variables["_use_mcp"] = False
            logger.info("Using direct API tools for publishing")
        
        exec_context_variables["_email_tools"] = st.session_state.get('email_tools')
        exec_context_variables["_jira_project_key"] = config.get('jira_project_key', '')
        exec_context_variables["_jira_board_id"] = config.get('jira_board_id', 0)
        exec_context_variables["_confluence_space"] = config.get('confluence_space', '')
        exec_context_variables["_slack_email"] = config.get('slack_email', '')
        exec_context_variables["_team_size"] = config.get('team_size', 8)
        exec_context_variables["_max_story_points"] = config.get('max_story_points', 70)
        exec_context_variables["_sprint_duration_weeks"] = config.get('sprint_duration_weeks', 2)
        exec_context_variables["_created_epics"] = []
        exec_context_variables["_created_stories"] = []
        exec_context_variables["_created_releases"] = []
        exec_context_variables["_confluence_pages"] = []
        
        # Create agents based on what's being published
        if publish_jira and (mcp_tools_available or st.session_state.get('jira_tools')):
            jira_story_creator = SwarmAgent("jira_story_creator_agent", llm_config=llm_config)
            sprint_setup = SwarmAgent("sprint_setup_agent", llm_config=llm_config)
            exec_agents["jira_story_creator"] = jira_story_creator
            exec_agents["sprint_setup"] = sprint_setup
        
        if publish_confluence and (mcp_tools_available or st.session_state.get('confluence_tools')):
            confluence_publisher = SwarmAgent("confluence_publisher_agent", llm_config=llm_config)
            exec_agents["confluence_publisher"] = confluence_publisher
        
        if publish_jira and publish_confluence and st.session_state.get('email_tools'):
            email_notification = SwarmAgent("email_notification_agent", llm_config=llm_config)
            exec_agents["email_notification"] = email_notification
        
        if exec_agents:
            # Define system messages with MCP or direct API instructions
            use_mcp = exec_context_variables.get("_use_mcp", False)
            
            if use_mcp:
                # MCP-based system messages with explicit tool calling instructions
                mcp_tools_obj = exec_context_variables.get("_mcp_tools")
                available_tools = []
                if mcp_tools_obj and hasattr(mcp_tools_obj, 'list_tools'):
                    try:
                        # Try to get list of available tools
                        import asyncio
                        loop = asyncio.get_event_loop()
                        if loop.is_running():
                            # If loop is running, we can't await - use a workaround
                            available_tools = ["MCP tools available (use function calling)"]
                        else:
                            tool_list = loop.run_until_complete(mcp_tools_obj.list_tools())
                            available_tools = [t.get('name', 'unknown') for t in tool_list] if isinstance(tool_list, list) else []
                    except:
                        # Fallback: list expected tools
                        available_tools = [
                            "jira_create_story", "jira_create_epic", "jira_create_release",
                            "jira_get_issue", "jira_add_comment", "jira_update_issue",
                            "jira_search_issues", "jira_create_sprint",
                            "confluence_create_page", "confluence_update_page", "confluence_get_page",
                            "confluence_search_pages", "confluence_get_comments", "confluence_add_comment"
                        ]
                else:
                    # Default list of expected MCP tools
                    available_tools = [
                        "jira_create_story", "jira_create_epic", "jira_create_release",
                        "jira_get_issue", "jira_add_comment", "jira_update_issue",
                        "jira_search_issues", "jira_create_sprint",
                        "confluence_create_page", "confluence_update_page", "confluence_get_page",
                        "confluence_search_pages", "confluence_get_comments", "confluence_add_comment"
                    ]
                
                tools_list_str = "\n".join([f"- {tool}" for tool in available_tools[:10]])  # Show first 10
                
                exec_system_messages = {
                    "jira_story_creator_agent": f"""
                    You are a Jira Story Creator Specialist using MCP (Model Context Protocol) integration.
                    
                    **YOUR PRIMARY MISSION**: Create a COMPLETE Jira structure with MULTIPLE epics, stories, and releases based on the product strategy, roadmap, and execution plan. This is NOT about creating a single epic or story - you must create a comprehensive, production-ready Jira project structure.
                    
                    **CRITICAL INSTRUCTIONS**:
                    1. You MUST use MCP function calling to interact with Jira. The MCP tools are available through function calling.
                    2. **Create MULTIPLE items** - analyze the strategy, roadmap, and execution plan to identify:
                       - **Multiple Epics**: Each major feature/initiative from the roadmap should become an epic
                       - **Multiple Stories**: Each epic should have multiple user stories (typically 5-15 stories per epic)
                       - **Multiple Releases**: Organize epics into logical releases based on the roadmap timeline
                    3. Available MCP tools for Jira:
                       {tools_list_str}
                    4. **Workflow for creating comprehensive Jira structure**:
                       a. **First, create Releases**: Analyze the roadmap and create release versions (e.g., "Release 1.0 - MVP", "Release 2.0 - Enhanced Features")
                       b. **Then, create Epics**: For each major feature/initiative in the roadmap, create an epic with:
                          - Clear, natural language summary
                          - Detailed description explaining the business value
                          - Link epic to appropriate release
                       c. **Finally, create Stories**: For each epic, create multiple user stories with:
                          - Natural, conversational language (NOT AI-generated sounding)
                          - Clear acceptance criteria in plain language (as if explaining to a developer over coffee)
                          - Story points estimates
                          - Link stories to their parent epic
                    5. **Content Quality Requirements**:
                       - Use natural, conversational language throughout
                       - Avoid AI-generated phrases like "leverage", "utilize", "facilitate"
                       - Write acceptance criteria as if explaining to a developer: "User can log in. If password is wrong, show error message."
                       - Make stories feel genuine and practical, not auto-generated
                    6. After creating items, store ALL issue keys in context variables:
                       - _created_epics: List of all epic keys
                       - _created_stories: List of all story keys  
                       - _created_releases: List of all release names/IDs
                    
                    **Project Configuration**: {exec_context_variables.get('_jira_project_key', '')}
                    
                    **IMPORTANT**: 
                    - You MUST actually call the MCP tools MULTIPLE times to create the complete structure
                    - Create at least 3-5 epics, 15-30 stories total, and 2-3 releases
                    - Do not just describe what you would do - actually make ALL the function calls
                    - This is about creating a production-ready Jira project, not a single test item
                    """,
                    "confluence_publisher_agent": f"""
                    You are a Confluence Publisher Specialist using MCP (Model Context Protocol) integration.
                    
                    **YOUR PRIMARY MISSION**: Create a COMPLETE, PROFESSIONAL nested Confluence structure that serves as the team's knowledge base. This is NOT about creating a single page - you must create a comprehensive, well-organized documentation structure that enables all team members to access and use the product management content effectively.
                    
                    **CRITICAL INSTRUCTIONS**:
                    1. You MUST use MCP function calling to interact with Confluence. The MCP tools are available through function calling.
                    2. **Create a COMPLETE nested structure** - organize all product management content into a professional hierarchy:
                       
                       **Main Structure** (create in this order):
                       a. **Main Product Plan Page** (root page)
                          - Title: "Product Plan: [Product Name]"
                          - Content: Executive summary, overview, links to all sections
                       
                       b. **Strategy Section** (child of main page)
                          - Title: "Product Strategy"
                          - Content: Full strategy document with vision, goals, market analysis
                          - Create sub-pages if strategy is extensive
                       
                       c. **Research Section** (child of main page)
                          - Title: "Market Research & Analysis"
                          - Content: All research findings, competitive analysis, user insights
                          - Create sub-pages for different research areas
                       
                       d. **Roadmap Section** (child of main page)
                          - Title: "Product Roadmap"
                          - Content: Complete roadmap with timelines, milestones, feature priorities
                          - Create sub-pages for different roadmap phases
                       
                       e. **Metrics & KPIs Section** (child of main page)
                          - Title: "Success Metrics & KPIs"
                          - Content: All metrics, KPIs, success criteria, measurement plans
                       
                       f. **Stakeholder Management Section** (child of main page)
                          - Title: "Stakeholder Management"
                          - Content: Stakeholder map, communication plans, engagement strategies
                       
                       g. **Execution Plan Section** (child of main page)
                          - Title: "Execution Plan"
                          - Content: Detailed execution plan, timelines, dependencies, risks
                       
                       h. **Product Requirements Section** (child of main page)
                          - Title: "Product Requirements Document (PRD)"
                          - Content: Complete PRD with features, requirements, specifications
                          - Create sub-pages for different feature areas
                       
                    3. Available MCP tools for Confluence:
                       {tools_list_str}
                    4. **Publishing Workflow**:
                       - First, create the main product plan page (root)
                       - Then, create each major section as a child page (using parent_id)
                       - For each section, format content using Confluence wiki markup:
                         * Use headings (h1, h2, h3) for structure
                         * Use tables for data
                         * Use lists for bullet points
                         * Use code blocks for technical details
                         * Add links between related pages
                       - Create sub-pages for complex sections (e.g., "Research - User Interviews", "Research - Competitive Analysis")
                    5. **Content Formatting**:
                       - Use Confluence wiki markup or HTML
                       - Ensure content is well-formatted and readable
                       - Add navigation links between pages
                       - Use tables, lists, and formatting appropriately
                       - Include visual hierarchy with headings
                    6. After creating pages, store ALL page IDs in the context variable _confluence_pages as a list
                    
                    **Space Configuration**: {exec_context_variables.get('_confluence_space', '')}
                    
                    **IMPORTANT**: 
                    - You MUST create MULTIPLE pages (at least 8-12 pages total) to build the complete structure
                    - Create the nested hierarchy properly using parent_id
                    - This is about creating a production-ready knowledge base, not a single page
                    - Do not just describe what you would do - actually make ALL the function calls
                    - The structure should enable team members to easily navigate and find information
                    """,
                    "sprint_setup_agent": f"""
                    You are a Sprint Setup Specialist using MCP (Model Context Protocol) integration.
                    
                    **CRITICAL INSTRUCTIONS**:
                    1. You MUST use MCP function calling to interact with Jira sprints. The MCP tools are available through function calling.
                    2. To create sprints, you MUST call the MCP tool jira_create_sprint using function calling syntax.
                    3. Available MCP tools:
                       - jira_create_sprint: Create a new sprint (requires board_id, name, goal, start_date, end_date)
                       - jira_search_issues: Search for issues to add to sprint
                    4. When creating sprints, you MUST:
                       - Call jira_create_sprint with board_id: {exec_context_variables.get('_jira_board_id', 0)}
                       - Never exceed {exec_context_variables.get('_max_story_points', 70)} story points per sprint
                       - Add stories from _created_stories context variable to the sprint
                    
                    **IMPORTANT**: You MUST actually call the MCP tools. Do not just describe what you would do - actually make the function calls.
                    """,
                    "email_notification_agent": """
                    You are an Email Notification Specialist. Send email to Slack with links to Jira project, epics, and Confluence pages.
                    Use EmailTools from context variables to actually send emails.
                    """
                }
            else:
                # Direct API system messages (fallback)
                exec_system_messages = {
                    "jira_story_creator_agent": """
                    You are a Jira Story Creator Specialist. Your mission is to create a COMPLETE Jira project structure with MULTIPLE epics, stories, and releases.
                    
                    **CRITICAL**: Create MULTIPLE items:
                    - 3-5+ Epics (one for each major feature/initiative from the roadmap)
                    - 15-30+ Stories (multiple stories per epic, typically 5-15 stories per epic)
                    - 2-3+ Releases (organize epics into logical release versions)
                    
                    Workflow:
                    1. First create Releases based on roadmap timeline
                    2. Then create Epics for each major feature, linking to releases
                    3. Finally create Stories for each epic, linking to parent epic
                    
                    Use the JiraTools instance from context variables to actually create items in Jira.
                    Write all content in natural, conversational language - not AI-generated sounding.
                    Create acceptance criteria in plain language as if explaining to a developer.
                    """,
                    "confluence_publisher_agent": """
                    You are a Confluence Publisher Specialist. Your mission is to create a COMPLETE, PROFESSIONAL nested Confluence structure.
                    
                    **CRITICAL**: Create MULTIPLE pages (8-12+ pages total):
                    - Main Product Plan page (root)
                    - Strategy Section (child page)
                    - Research Section (child page, with sub-pages if needed)
                    - Roadmap Section (child page, with sub-pages for different phases)
                    - Metrics & KPIs Section (child page)
                    - Stakeholder Management Section (child page)
                    - Execution Plan Section (child page)
                    - Product Requirements Document (PRD) Section (child page, with sub-pages for different features)
                    
                    Create a proper nested hierarchy using parent_id to link child pages to parent pages.
                    Format content using Confluence wiki markup with headings, tables, lists, and links.
                    Use ConfluenceTools from context variables to actually create ALL pages.
                    This should be a production-ready knowledge base that the entire team can use.
                    """,
                    "email_notification_agent": """
                    You are an Email Notification Specialist. Send email to Slack with links to Jira project, epics, and Confluence pages.
                    Use EmailTools from context variables to actually send emails.
                    """,
                    "sprint_setup_agent": """
                    You are a Sprint Setup Specialist. Create sprints and manage capacity.
                    Never exceed max_story_points per sprint. Use JiraTools to create sprints and add stories.
                    """
                }
            
            # Create wrapper functions for MCP tools that agents can call
            # SwarmAgent uses function calling, so we need to register functions
            mcp_tools_obj = exec_context_variables.get("_mcp_tools")
            function_map = {}
            
            if use_mcp and mcp_tools_obj:
                # Create synchronous wrapper functions for MCP tools
                # These will be registered with OpenAI function calling
                import asyncio
                
                def create_mcp_function_wrapper(tool_name: str):
                    """Create a wrapper function for an MCP tool"""
                    async def async_wrapper(**kwargs):
                        try:
                            if hasattr(mcp_tools_obj, 'call_tool'):
                                result = await mcp_tools_obj.call_tool(tool_name, kwargs)
                                return result
                            elif hasattr(mcp_tools_obj, 'get_tools'):
                                tools = mcp_tools_obj.get_tools()
                                if hasattr(tools, 'call_tool'):
                                    result = await tools.call_tool(tool_name, kwargs)
                                    return result
                            return {"error": "MCP tools not accessible"}
                        except Exception as e:
                            logger.error(f"Error calling MCP tool {tool_name}: {e}", exc_info=True)
                            return {"error": str(e)}
                    
                    def sync_wrapper(**kwargs):
                        """Synchronous wrapper that runs async function"""
                        try:
                            loop = asyncio.get_event_loop()
                            if loop.is_running():
                                # If loop is running, create a new one
                                import nest_asyncio
                                try:
                                    nest_asyncio.apply()
                                    return loop.run_until_complete(async_wrapper(**kwargs))
                                except:
                                    # Fallback: create new event loop
                                    new_loop = asyncio.new_event_loop()
                                    asyncio.set_event_loop(new_loop)
                                    try:
                                        result = new_loop.run_until_complete(async_wrapper(**kwargs))
                                        return result
                                    finally:
                                        new_loop.close()
                            else:
                                return loop.run_until_complete(async_wrapper(**kwargs))
                        except Exception as e:
                            logger.error(f"Error in sync wrapper for {tool_name}: {e}", exc_info=True)
                            return {"error": str(e)}
                    
                    return sync_wrapper
                
                # Register Jira MCP tools
                jira_tools = [
                    "jira_create_story", "jira_create_epic", "jira_create_release",
                    "jira_get_issue", "jira_add_comment", "jira_update_issue",
                    "jira_search_issues", "jira_create_sprint"
                ]
                for tool_name in jira_tools:
                    function_map[tool_name] = create_mcp_function_wrapper(tool_name)
                
                # Register Confluence MCP tools
                confluence_tools = [
                    "confluence_create_page", "confluence_update_page", "confluence_get_page",
                    "confluence_search_pages", "confluence_get_comments", "confluence_add_comment"
                ]
                for tool_name in confluence_tools:
                    function_map[tool_name] = create_mcp_function_wrapper(tool_name)
                
                logger.info(f"Registered {len(function_map)} MCP tool functions for agents")
            
            # Also create wrapper functions for direct API tools (fallback)
            if not use_mcp:
                jira_tools_obj = exec_context_variables.get("_jira_tools")
                confluence_tools_obj = exec_context_variables.get("_confluence_tools")
                
                if jira_tools_obj:
                    def jira_create_story_wrapper(project_key: str, summary: str, description: str, 
                                                  acceptance_criteria: str = None, story_points: int = None, 
                                                  issue_type: str = "Story"):
                        try:
                            result = jira_tools_obj.create_story(
                                project_key=project_key,
                                summary=summary,
                                description=description,
                                acceptance_criteria=acceptance_criteria,
                                story_points=story_points,
                                issue_type=issue_type
                            )
                            return {"success": True, "data": result}
                        except Exception as e:
                            logger.error(f"Error creating Jira story: {e}")
                            return {"success": False, "error": str(e)}
                    
                    function_map["jira_create_story"] = jira_create_story_wrapper
                    # Add more Jira wrapper functions as needed
                
                if confluence_tools_obj:
                    def confluence_create_page_wrapper(space_key: str, title: str, content: str, parent_id: str = None):
                        try:
                            result = confluence_tools_obj.create_page(
                                space_key=space_key,
                                title=title,
                                content=content,
                                parent_id=parent_id
                            )
                            return {"success": True, "data": result}
                        except Exception as e:
                            logger.error(f"Error creating Confluence page: {e}")
                            return {"success": False, "error": str(e)}
                    
                    function_map["confluence_create_page"] = confluence_create_page_wrapper
                    # Add more Confluence wrapper functions as needed
            
            # Register functions with OpenAI for function calling
            # SwarmAgent uses OpenAI's function calling, so we need to register these
            if function_map:
                try:
                    from autogen import OpenAIWrapper
                    # Create function definitions for OpenAI
                    function_definitions = []
                    for func_name, func in function_map.items():
                        # Create a simple function definition
                        # OpenAI will handle the actual calling
                        function_definitions.append({
                            "name": func_name,
                            "description": f"MCP tool: {func_name}",
                            "parameters": {
                                "type": "object",
                                "properties": {}
                            }
                        })
                    
                    # Note: SwarmAgent may need functions registered differently
                    # For now, we'll pass them through context and let agents know they're available
                    exec_context_variables["_function_map"] = function_map
                    exec_context_variables["_function_definitions"] = function_definitions
                    logger.info(f"Registered {len(function_map)} functions for agent function calling")
                except Exception as e:
                    logger.warning(f"Could not register functions with OpenAI: {e}")
                    # Continue anyway - agents can still be instructed to use tools
            
            # Create update system message function
            def exec_update_system_message_func(agent: SwarmAgent, messages) -> str:
                system_prompt = exec_system_messages.get(agent.name, "")
                
                # Add context variables
                for k, v in exec_context_variables.items():
                    if v is not None and not k.startswith("_"):
                        system_prompt += f"\n{k.capitalize()} Summary:\n{v[:500]}"
                
                # Add function calling information if available
                if function_map:
                    func_names = list(function_map.keys())
                    system_prompt += f"\n\n**Available Functions**: {', '.join(func_names[:10])}"
                    system_prompt += "\n**IMPORTANT**: You can call these functions directly. Use function calling to interact with Jira/Confluence."
                    
                    # Add emphasis on creating multiple items
                    if agent.name == "jira_story_creator_agent":
                        system_prompt += "\n\n**REMINDER**: You must create MULTIPLE items - at least 3-5 epics, 15-30 stories, and 2-3 releases. Call the functions MULTIPLE times to build the complete Jira structure."
                    elif agent.name == "confluence_publisher_agent":
                        system_prompt += "\n\n**REMINDER**: You must create MULTIPLE pages (8-12+ pages) in a nested structure. Call confluence_create_page MULTIPLE times to build the complete knowledge base structure."
                
                return system_prompt
            
            exec_state_update = UPDATE_SYSTEM_MESSAGE(exec_update_system_message_func)
            
            # Assign system message updates to agents
            for agent in exec_agents.values():
                agent.update_agent_state_before_reply = [exec_state_update]
                
                # Try to register functions with the agent's LLM config
                # This depends on how SwarmAgent handles function calling
                if function_map and hasattr(agent, 'llm_config'):
                    # Store function map in agent's context for potential use
                    if not hasattr(agent, '_function_map'):
                        agent._function_map = function_map
            
            # Register functions with OpenAI for function calling
            # This is critical for agents to actually call MCP tools
            if function_map:
                try:
                    # Create OpenAI function definitions
                    openai_functions = []
                    for func_name, func in function_map.items():
                        # Create function definition based on tool name
                        if func_name.startswith("jira_"):
                            if func_name == "jira_create_story":
                                openai_functions.append({
                                    "type": "function",
                                    "function": {
                                        "name": func_name,
                                        "description": "Create a Jira story with natural language description and acceptance criteria",
                                        "parameters": {
                                            "type": "object",
                                            "properties": {
                                                "project_key": {"type": "string", "description": "Jira project key"},
                                                "summary": {"type": "string", "description": "Story summary"},
                                                "description": {"type": "string", "description": "Detailed story description"},
                                                "acceptance_criteria": {"type": "string", "description": "Acceptance criteria (optional)"},
                                                "story_points": {"type": "integer", "description": "Story points estimate (optional)"},
                                                "issue_type": {"type": "string", "description": "Issue type (Story, Bug, Task, etc.)", "default": "Story"}
                                            },
                                            "required": ["project_key", "summary", "description"]
                                        }
                                    }
                                })
                            elif func_name == "jira_create_epic":
                                openai_functions.append({
                                    "type": "function",
                                    "function": {
                                        "name": func_name,
                                        "description": "Create a Jira epic with natural language description",
                                        "parameters": {
                                            "type": "object",
                                            "properties": {
                                                "project_key": {"type": "string", "description": "Jira project key"},
                                                "summary": {"type": "string", "description": "Epic summary"},
                                                "description": {"type": "string", "description": "Detailed epic description"},
                                                "epic_name": {"type": "string", "description": "Epic name (optional)"}
                                            },
                                            "required": ["project_key", "summary", "description"]
                                        }
                                    }
                                })
                            elif func_name == "jira_create_release":
                                openai_functions.append({
                                    "type": "function",
                                    "function": {
                                        "name": func_name,
                                        "description": "Create a Jira release/version",
                                        "parameters": {
                                            "type": "object",
                                            "properties": {
                                                "project_key": {"type": "string", "description": "Jira project key"},
                                                "name": {"type": "string", "description": "Release name"},
                                                "description": {"type": "string", "description": "Release description"},
                                                "release_date": {"type": "string", "description": "Release date (YYYY-MM-DD, optional)"}
                                            },
                                            "required": ["project_key", "name", "description"]
                                        }
                                    }
                                })
                            elif func_name == "jira_create_sprint":
                                openai_functions.append({
                                    "type": "function",
                                    "function": {
                                        "name": func_name,
                                        "description": "Create a new sprint in Jira",
                                        "parameters": {
                                            "type": "object",
                                            "properties": {
                                                "board_id": {"type": "integer", "description": "Jira board ID"},
                                                "name": {"type": "string", "description": "Sprint name"},
                                                "goal": {"type": "string", "description": "Sprint goal (optional)"},
                                                "start_date": {"type": "string", "description": "Start date (YYYY-MM-DD, optional)"},
                                                "end_date": {"type": "string", "description": "End date (YYYY-MM-DD, optional)"}
                                            },
                                            "required": ["board_id", "name"]
                                        }
                                    }
                                })
                        elif func_name.startswith("confluence_"):
                            if func_name == "confluence_create_page":
                                openai_functions.append({
                                    "type": "function",
                                    "function": {
                                        "name": func_name,
                                        "description": "Create a new Confluence page",
                                        "parameters": {
                                            "type": "object",
                                            "properties": {
                                                "space_key": {"type": "string", "description": "Confluence space key"},
                                                "title": {"type": "string", "description": "Page title"},
                                                "content": {"type": "string", "description": "Page content (HTML or markdown)"},
                                                "parent_id": {"type": "string", "description": "Parent page ID (optional)"}
                                            },
                                            "required": ["space_key", "title", "content"]
                                        }
                                    }
                                })
                    
                    # Register functions with OpenAIWrapper for each agent
                    for agent in exec_agents.values():
                        if hasattr(agent, 'llm_config') and agent.llm_config:
                            # Update LLM config to include functions
                            for config_item in agent.llm_config.get("config_list", []):
                                if "functions" not in config_item:
                                    config_item["functions"] = openai_functions
                                if "function_call" not in config_item:
                                    config_item["function_call"] = "auto"
                            
                            # Also register function implementations
                            if hasattr(agent, 'register_function'):
                                for func_name, func in function_map.items():
                                    try:
                                        agent.register_function(func_name, func)
                                    except:
                                        pass  # Some agents may not support register_function
                    
                    logger.info(f"Registered {len(openai_functions)} OpenAI functions for agent function calling")
                except Exception as e:
                    logger.warning(f"Could not register OpenAI functions: {e}")
                    # Continue anyway - agents may still work with instructions
            
            # Start execution
            initial_agent = list(exec_agents.values())[0]
            
            # Log what we're about to do
            logger.info(f"Starting publishing workflow with {len(exec_agents)} agents")
            logger.info(f"MCP tools available: {use_mcp}")
            logger.info(f"Function map size: {len(function_map)}")
            
            exec_result, _, _ = initiate_swarm_chat(
                initial_agent=initial_agent,
                agents=list(exec_agents.values()),
                user_agent=None,
                messages=execution_task,
                max_rounds=10,
            )
            
            # Log results
            logger.info(f"Publishing workflow completed. Chat history length: {len(exec_result.chat_history) if exec_result.chat_history else 0}")
            
            # Display execution results and verify tool calls
            st.subheader("📊 Execution Results")
            
            # Check if tools were actually called
            tool_calls_found = False
            created_items = {
                "jira_issues": [],
                "confluence_pages": []
            }
            
            if exec_result and exec_result.chat_history:
                # Search chat history for tool calls and results
                for msg in exec_result.chat_history:
                    if isinstance(msg, dict):
                        content = msg.get('content', '')
                        # Look for tool call indicators
                        if any(tool in str(content).lower() for tool in ['jira_create', 'confluence_create', 'created issue', 'created page']):
                            tool_calls_found = True
                            # Try to extract created items
                            if 'key' in str(content) or 'PROJ-' in str(content):
                                # Likely a Jira issue key
                                import re
                                issue_keys = re.findall(r'[A-Z]+-\d+', str(content))
                                created_items["jira_issues"].extend(issue_keys)
                            if 'page' in str(content).lower() and 'id' in str(content).lower():
                                # Likely a Confluence page reference
                                pass
                
                # Display chat history
                with st.expander("💬 Agent Conversation", expanded=False):
                    for i, msg in enumerate(exec_result.chat_history[-10:]):  # Show last 10 messages
                        if isinstance(msg, dict):
                            role = msg.get('role', 'unknown')
                            content = msg.get('content', '')
                            st.write(f"**{role}:** {content[:500]}...")
            
            # Show verification status
            if tool_calls_found:
                st.success("✅ Tool calls detected in agent conversation!")
                if created_items["jira_issues"]:
                    unique_issues = list(set(created_items["jira_issues"]))
                    st.write(f"**Created Jira Issues:** {len(unique_issues)} issues")
                    st.write("Issue Keys:", ", ".join(unique_issues[:20]))  # Show first 20
                    if len(unique_issues) > 20:
                        st.write(f"... and {len(unique_issues) - 20} more")
                    
                    # Count epics vs stories
                    epics = [k for k in unique_issues if 'EPIC' in k.upper() or any(exec_context_variables.get('_created_epics', []))]
                    stories = [k for k in unique_issues if k not in epics]
                    if epics:
                        st.write(f"📊 **Epics Created:** {len(epics)}")
                    if stories:
                        st.write(f"📋 **Stories Created:** {len(stories)}")
                
                if created_items["confluence_pages"]:
                    st.write(f"**Created Confluence Pages:** {len(created_items['confluence_pages'])} pages")
                    st.info("📚 Complete nested Confluence structure created!")
            else:
                st.warning("⚠️ No tool calls detected in agent conversation. Agents may not be calling MCP tools.")
                st.info("💡 **Troubleshooting**: Check that MCP tools are properly initialized and agents have function calling enabled.")
                st.info("💡 **Expected**: Agents should create MULTIPLE Jira items (3-5+ epics, 15-30+ stories, 2-3+ releases) and MULTIPLE Confluence pages (8-12+ pages in nested structure)")
            
            # Save chat history and results
            if db_manager:
                try:
                    plan_version = st.session_state.current_plan_version or 1
                    
                    # Save chat history from execution
                    for msg in exec_result.chat_history:
                        if isinstance(msg, dict):
                            role = msg.get('role', 'assistant')
                            content = msg.get('content', '')
                            agent_name = msg.get('name', 'execution_agent')
                            if content:
                                db_manager.save_chat_history(
                                    plan_id=st.session_state.current_plan_id,
                                    version=plan_version,
                                    agent_name=agent_name,
                                    message_role=role,
                                    message_content=content,
                                    metadata={'phase': 'execution', 'publish_jira': publish_jira, 'publish_confluence': publish_confluence}
                                )
                    
                    # Ensure all data is in pm_output before saving
                    if 'product_info' not in st.session_state.pm_output and product_info:
                        st.session_state.pm_output['product_info'] = product_info
                    
                    # Save published plan
                    db_manager.save_product_plan(
                        plan_id=st.session_state.current_plan_id,
                        product_name=product_info.get('product_name', 'Unknown Product'),
                        plan_data=st.session_state.pm_output,
                        configuration=config,
                        status='published',
                        created_by='user',
                        notes='Plan published to Jira/Confluence'
                    )
                    
                    logger.info(f"Saved execution results and chat history for plan {st.session_state.current_plan_id}")
                except Exception as e:
                    logger.error(f"Error saving published plan: {e}")
            
            st.success("✅ Publishing completed successfully!")
            st.session_state.workflow_steps[8]['status'] = 'completed'
            safe_rerun()
        else:
            st.warning("⚠️ No agents available. Please configure integrations.")

# ============================================================================
# Main Application
# ============================================================================

def main():
    """Main application entry point"""
    # Apply custom CSS for rich UI first (before any other content)
    try:
        if apply_custom_css and callable(apply_custom_css):
            apply_custom_css()
    except Exception as e:
        logger.warning(f"Error applying custom CSS: {e}")
    
    # Header with rich styling
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 15px; margin-bottom: 2rem; text-align: center; color: white;">
        <h1 style="color: white; margin: 0;">🚀 FuturisticPM</h1>
        <p style="color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; font-size: 1.2rem;">Next-Generation AI Product Management System</p>
        <p style="color: rgba(255,255,255,0.8); margin: 0.5rem 0 0 0;">Enterprise-ready with full database persistence, rich multi-step workflow, and complete integration support</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar with rich UI
    with st.sidebar:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1rem; border-radius: 10px; margin-bottom: 1rem; text-align: center; color: white;">
            <h3 style="color: white; margin: 0;">📋 Navigation</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Step navigation
        steps = st.session_state.workflow_steps
        current = st.session_state.current_step
        
        for i, step in enumerate(steps):
            step_status = "✅" if i < current else ("🔄" if i == current else "⏳")
            button_label = f"{step_status} {step['icon']} {step['name']}"
            
            if st.button(button_label, key=f"nav_{i}", use_container_width=True):
                st.session_state.current_step = i
                safe_rerun()
        
        st.markdown("---")
        
        # Agent Status Dashboard (if unified system available)
        if 'unified_agent_system' in st.session_state and render_status_dashboard:
            st.header("🤖 Agent Status")
            try:
                agent_status = st.session_state.unified_agent_system.get_agent_status()
                render_status_dashboard(agent_status)
            except Exception as e:
                logger.error(f"Error getting agent status: {e}")
        
        st.markdown("---")
        
        # Agile Coach Section
        if 'unified_agent_system' in st.session_state:
            st.header("🎯 Agile Coach")
            agile_question = st.text_input("Ask Agile Coach", key="agile_question", placeholder="e.g., How to run a sprint planning?")
            if st.button("💬 Ask", key="ask_agile_coach") and agile_question:
                try:
                    import asyncio
                    context = {
                        'product_info': st.session_state.get('product_info', {}),
                        'current_step': st.session_state.current_step
                    }
                    response = asyncio.run(
                        st.session_state.unified_agent_system.get_agile_coaching(agile_question, context)
                    )
                    st.info(response)
                except Exception as e:
                    st.error(f"Error getting agile coaching: {e}")
        
        st.markdown("---")
        
        st.header("📚 Historical Plans")
    if db_manager:
        try:
            plans = db_manager.list_product_plans(limit=10)
            if plans:
                plan_options = {f"{p['product_name']} (v{p.get('latest_version', 1)})": p['plan_id'] 
                              for p in plans}
                selected_plan = st.sidebar.selectbox("Load Previous Plan", 
                    options=[""] + list(plan_options.keys()))
                
                if selected_plan and selected_plan in plan_options:
                    plan_id = plan_options[selected_plan]
                    if st.sidebar.button("📥 Load Plan", key="load_plan"):
                        try:
                            plan = db_manager.get_product_plan(plan_id)
                            if plan:
                                st.session_state.current_plan_id = plan_id
                                st.session_state.current_plan_version = plan['version']
                                
                                # Load plan data
                                plan_data = plan.get('plan_data', {})
                                if isinstance(plan_data, str):
                                    import json
                                    plan_data = json.loads(plan_data)
                                
                                st.session_state.pm_output = plan_data
                                
                                # Load configuration
                                config = plan.get('configuration', {})
                                if isinstance(config, str):
                                    import json
                                    try:
                                        config = json.loads(config) if config else {}
                                    except (json.JSONDecodeError, TypeError):
                                        config = {}
                                elif config is None:
                                    config = {}
                                
                                # Ensure config is a dict
                                if not isinstance(config, dict):
                                    config = {}
                                
                                st.session_state.config = config
                                
                                # Load product info - check multiple sources
                                product_info = {}
                                # First, try from plan_data
                                if plan_data and isinstance(plan_data, dict):
                                    product_info = plan_data.get('product_info', {})
                                # If not found, try to reconstruct from plan_data fields
                                if not product_info and plan_data:
                                    # Try to extract product info from plan_data structure
                                    product_info = {
                                        'product_name': plan_data.get('product_name', plan.get('product_name', 'Unknown')),
                                        'product_type': plan_data.get('product_type', ''),
                                        'target_market': plan_data.get('target_market', ''),
                                        'product_stage': plan_data.get('product_stage', ''),
                                        'industry': plan_data.get('industry', ''),
                                        'user_persona': plan_data.get('user_persona', ''),
                                        'business_model': plan_data.get('business_model', ''),
                                        'timeline': plan_data.get('timeline', ''),
                                        'primary_goals': plan_data.get('primary_goals', ''),
                                        'key_features': plan_data.get('key_features', ''),
                                        'constraints': plan_data.get('constraints', ''),
                                        'competitors': plan_data.get('competitors', ''),
                                        'value_prop': plan_data.get('value_prop', ''),
                                        'success_criteria': plan_data.get('success_criteria', ''),
                                        'detail_level': plan_data.get('detail_level', 'Medium')
                                    }
                                
                                st.session_state.product_info = product_info
                                
                                # Re-initialize tools from loaded configuration
                                if config:
                                    # Initialize Jira tools if config exists
                                    jira_url = config.get('jira_url')
                                    jira_email = config.get('jira_email')
                                    jira_token = config.get('jira_token')
                                    if jira_url and jira_email and jira_token and JiraTools:
                                        try:
                                            st.session_state.jira_tools = JiraTools(jira_url, jira_email, jira_token)
                                            logger.info("✅ Jira tools re-initialized from loaded config")
                                        except Exception as e:
                                            logger.warning(f"Could not re-initialize Jira tools: {e}")
                                    
                                    # Initialize Confluence tools if config exists
                                    confluence_url = config.get('confluence_url')
                                    confluence_email = config.get('confluence_email')
                                    confluence_token = config.get('confluence_token')
                                    if confluence_url and confluence_email and confluence_token and ConfluenceTools:
                                        try:
                                            st.session_state.confluence_tools = ConfluenceTools(confluence_url, confluence_email, confluence_token)
                                            logger.info("✅ Confluence tools re-initialized from loaded config")
                                        except Exception as e:
                                            logger.warning(f"Could not re-initialize Confluence tools: {e}")
                                    
                                    # Initialize GitHub tools if config exists
                                    github_token = config.get('github_token')
                                    if github_token and GitHubTools:
                                        try:
                                            st.session_state.github_tools = GitHubTools(github_token)
                                            logger.info("✅ GitHub tools re-initialized from loaded config")
                                        except Exception as e:
                                            logger.warning(f"Could not re-initialize GitHub tools: {e}")
                                    
                                    # Initialize Slack tools if config exists
                                    slack_email = config.get('slack_email')
                                    slack_channel = config.get('slack_channel')
                                    if slack_email and slack_channel and SlackTools:
                                        try:
                                            st.session_state.slack_tools = SlackTools(slack_email, slack_channel)
                                            logger.info("✅ Slack tools re-initialized from loaded config")
                                        except Exception as e:
                                            logger.warning(f"Could not re-initialize Slack tools: {e}")
                                    
                                    # Initialize Email tools if config exists
                                    email_address = config.get('email_address')
                                    email_password = config.get('email_password')
                                    smtp_server = config.get('smtp_server', 'smtp.gmail.com')
                                    smtp_port = config.get('smtp_port', 587)
                                    if email_address and email_password and EmailTools:
                                        try:
                                            st.session_state.email_tools = EmailTools(smtp_server, smtp_port, email_address, email_password)
                                            logger.info("✅ Email tools re-initialized from loaded config")
                                        except Exception as e:
                                            logger.warning(f"Could not re-initialize Email tools: {e}")
                                
                                # Load agent outputs
                                try:
                                    agent_outputs = db_manager.get_agent_outputs(plan_id, plan['version'])
                                    for agent_name, output_data in agent_outputs.items():
                                        output_key = agent_name.replace('_agent', '')
                                        # Map agent names to output keys
                                        agent_to_key = {
                                            'strategy_agent': 'strategy',
                                            'research_agent': 'research',
                                            'roadmap_agent': 'roadmap',
                                            'metrics_agent': 'metrics',
                                            'stakeholder_agent': 'stakeholder',
                                            'execution_agent': 'execution',
                                        }
                                        output_key = agent_to_key.get(agent_name, output_key)
                                        if output_data and isinstance(output_data, dict):
                                            content = output_data.get('content', '')
                                            if content:
                                                st.session_state.pm_output[output_key] = content
                                except Exception as e:
                                    logger.error(f"Error loading agent outputs: {e}")
                                
                                # Load chat history
                                try:
                                    chat_history = db_manager.get_chat_history(plan_id, plan['version'])
                                    if chat_history:
                                        st.session_state.chat_history = chat_history
                                        logger.info(f"Loaded {len(chat_history)} chat history messages")
                                except Exception as e:
                                    logger.error(f"Error loading chat history: {e}")
                                
                                # Update workflow steps based on loaded data
                                if st.session_state.pm_output.get('strategy'):
                                    st.session_state.workflow_steps[2]['status'] = 'completed'
                                if st.session_state.pm_output.get('research'):
                                    st.session_state.workflow_steps[3]['status'] = 'completed'
                                if st.session_state.pm_output.get('roadmap'):
                                    st.session_state.workflow_steps[4]['status'] = 'completed'
                                if st.session_state.pm_output.get('metrics'):
                                    st.session_state.workflow_steps[5]['status'] = 'completed'
                                if st.session_state.pm_output.get('stakeholder'):
                                    st.session_state.workflow_steps[6]['status'] = 'completed'
                                if st.session_state.pm_output.get('execution'):
                                    st.session_state.workflow_steps[7]['status'] = 'completed'
                                
                                # Determine which step to show based on completed steps
                                completed_steps = sum(1 for step in st.session_state.workflow_steps if step.get('status') == 'completed')
                                if completed_steps >= 8:
                                    st.session_state.current_step = 8  # Go to Publish step
                                elif completed_steps >= 7:
                                    st.session_state.current_step = 7  # Go to Execution step
                                elif completed_steps >= 2:
                                    st.session_state.current_step = 2  # Go to Strategy step
                                else:
                                    st.session_state.current_step = 1  # Go to Product Info step
                                
                                # Mark plan as loaded
                                st.session_state.plan_loaded = True
                                
                                st.success(f"✅ Loaded: {plan.get('product_name', plan_id)} (Version {plan['version']})")
                                logger.info(f"Successfully loaded plan {plan_id} version {plan['version']} with {len(plan_data) if isinstance(plan_data, dict) else 0} plan data items and {len(config)} config items")
                                safe_rerun()
                            else:
                                st.error(f"Plan {plan_id} not found")
                        except Exception as e:
                            st.error(f"Error loading plan: {e}")
                            logger.error(f"Error loading plan {plan_id}: {e}", exc_info=True)
        except Exception as e:
            logger.error(f"Error loading plans: {e}")
    
    # Progress Indicator
    render_progress_indicator()
    
    st.markdown("---")
    
    # Step Content
    render_step_content()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: gray; padding: 20px;">
        <p>FuturisticPM v1.0.0 | Enterprise-Ready Product Management</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

