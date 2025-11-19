"""
Agentic Product Manager - Multi-Agent System

A comprehensive AI-powered Product Manager system that coordinates multiple specialized agents
to handle the complete product management journey from strategy to execution.

This system uses AG2 (AutoGen)'s swarm feature to enable collaborative product management
across strategy, research, roadmap, metrics, stakeholder management, and execution.
"""

import streamlit as st
import os
import sys
import uuid
import logging
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('agentic_pm.log'),
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
    # Ensure we have a context
    if get_script_run_ctx() is None:
        logger.warning("Running in bare mode - some Streamlit features may not work")
except ImportError:
    pass

# Add current directory to path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

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
    from database import get_db_manager, DatabaseManager
    from streamlit_utils import safe_session_state, safe_rerun, safe_spinner
except ImportError as e:
    logger.warning(f"Import error: {e}")
    # If tools module not available, create placeholder classes
    JiraTools = None
    GitHubTools = None
    SlackTools = None
    EmailTools = None
    ConfluenceTools = None
    create_confluence_tools_from_env = None
    AsyncOperationTracker = None
    get_db_manager = None
    DatabaseManager = None
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
    # Try to import UPDATE_SYSTEM_MESSAGE, if not available, define it
    try:
        from autogen import UPDATE_SYSTEM_MESSAGE
    except ImportError:
        # UPDATE_SYSTEM_MESSAGE is a wrapper function for update_system_message
        def UPDATE_SYSTEM_MESSAGE(func):
            """Wrapper for update_system_message function"""
            return func
except ImportError as e:
    # Show error in Streamlit with helpful instructions
    st.error(f"""
    ⚠️ **Import Error**: Could not import required classes from autogen.
    Error: {e}
    
    **Solution**: Please install the correct version of pyautogen in your virtual environment:
    
    ```bash
    # Activate your virtual environment first
    source agentic_pm_venv/bin/activate
    
    # Install the correct version
    pip install "pyautogen>=0.2,<0.5" streamlit==1.41.1
    ```
    
    **Note**: SwarmAgent is available in pyautogen versions 0.2.x to 0.4.x.
    Versions 0.5+ use a different API structure.
    """)
    st.stop()

os.environ["AUTOGEN_USE_DOCKER"] = "0"

# Initialize database manager
db_manager = None
if get_db_manager:
    try:
        db_manager = get_db_manager()
        logger.info("Database manager initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        st.warning("⚠️ Database initialization failed. Some features may not work.")

# Initialize session state with database support
if 'pm_output' not in st.session_state:
    st.session_state.pm_output = {
        'strategy': '',
        'research': '',
        'roadmap': '',
        'metrics': '',
        'stakeholder': '',
        'execution': ''
    }
if 'planning_complete' not in st.session_state:
    st.session_state.planning_complete = False
if 'execution_phase_ready' not in st.session_state:
    st.session_state.execution_phase_ready = False
if 'publish_to_jira' not in st.session_state:
    st.session_state.publish_to_jira = False
if 'publish_to_confluence' not in st.session_state:
    st.session_state.publish_to_confluence = False
if 'execution_phase_complete' not in st.session_state:
    st.session_state.execution_phase_complete = False
if 'current_plan_id' not in st.session_state:
    st.session_state.current_plan_id = None
if 'current_plan_version' not in st.session_state:
    st.session_state.current_plan_version = None
if 'selected_plan_id' not in st.session_state:
    st.session_state.selected_plan_id = None
if 'selected_version' not in st.session_state:
    st.session_state.selected_version = None

# Sidebar for API key input
st.sidebar.title("🔑 API Configuration")

# OpenAI API Key
api_key = st.sidebar.text_input("Enter your OpenAI API Key", type="password")

# Integration Configuration
st.sidebar.markdown("---")
st.sidebar.subheader("🔌 Integration Settings")

# Jira Configuration
st.sidebar.markdown("### 📋 Jira")
jira_url = st.sidebar.text_input("Jira URL", value=os.getenv("JIRA_URL", ""), help="e.g., https://yourcompany.atlassian.net")
jira_email = st.sidebar.text_input("Jira Email", value=os.getenv("JIRA_EMAIL", ""))
jira_token = st.sidebar.text_input("Jira API Token", type="password", value=os.getenv("JIRA_API_TOKEN", ""))

# GitHub Configuration
st.sidebar.markdown("### 🐙 GitHub")
github_token = st.sidebar.text_input("GitHub Token", type="password", value=os.getenv("GITHUB_TOKEN", ""))
github_owner = st.sidebar.text_input("GitHub Owner/Org", value=os.getenv("GITHUB_OWNER", ""))
github_repo = st.sidebar.text_input("GitHub Repository", value=os.getenv("GITHUB_REPO", ""))

# Slack Configuration
st.sidebar.markdown("### 💬 Slack")
slack_email = st.sidebar.text_input("Slack Email", value=os.getenv("SLACK_EMAIL", ""), help="Email address to send notifications to")
slack_channel = st.sidebar.text_input("Slack Channel Name", value=os.getenv("SLACK_CHANNEL", ""), help="Channel name (e.g., #product-team)")

# Email Configuration (for sending emails to Slack)
st.sidebar.markdown("### 📧 Email (SMTP)")
smtp_server = st.sidebar.text_input("SMTP Server", value=os.getenv("SMTP_SERVER", "smtp.gmail.com"), help="e.g., smtp.gmail.com")
smtp_port = st.sidebar.number_input("SMTP Port", min_value=1, max_value=65535, value=int(os.getenv("SMTP_PORT", "587")))
email_address = st.sidebar.text_input("Email Address", value=os.getenv("EMAIL_ADDRESS", ""), help="Sender email address")
email_password = st.sidebar.text_input("Email Password", type="password", value=os.getenv("EMAIL_PASSWORD", ""), help="Email password or app password")

# Confluence Configuration
st.sidebar.markdown("### 📚 Confluence")
confluence_url = st.sidebar.text_input("Confluence URL", value=os.getenv("CONFLUENCE_URL", ""), help="e.g., https://yourcompany.atlassian.net/wiki")
confluence_email = st.sidebar.text_input("Confluence Email", value=os.getenv("CONFLUENCE_EMAIL", ""))
confluence_token = st.sidebar.text_input("Confluence API Token", type="password", value=os.getenv("CONFLUENCE_API_TOKEN", ""))
confluence_space = st.sidebar.text_input("Confluence Space Key", value=os.getenv("CONFLUENCE_SPACE", ""), help="Space key where reports will be published")

# Initialize integration tools
jira_tools = None
github_tools = None
slack_tools = None
email_tools = None
confluence_tools = None
async_tracker = None

# Initialize async tracker
if AsyncOperationTracker:
    try:
        async_tracker = AsyncOperationTracker()
    except Exception as e:
        st.sidebar.warning(f"⚠️ Async tracker error: {str(e)}")

if jira_url and jira_email and jira_token:
    try:
        jira_tools = JiraTools(jira_url, jira_email, jira_token)
        st.sidebar.success("✅ Jira connected")
    except Exception as e:
        st.sidebar.error(f"❌ Jira error: {str(e)}")

if github_token:
    try:
        github_tools = GitHubTools(github_token)
        st.sidebar.success("✅ GitHub connected")
    except Exception as e:
        st.sidebar.error(f"❌ GitHub error: {str(e)}")

if slack_email and slack_channel:
    try:
        slack_tools = SlackTools(slack_email, slack_channel)
        st.sidebar.success("✅ Slack connected")
    except Exception as e:
        st.sidebar.error(f"❌ Slack error: {str(e)}")

if email_address and email_password:
    try:
        email_tools = EmailTools(smtp_server, smtp_port, email_address, email_password)
        st.sidebar.success("✅ Email configured")
    except Exception as e:
        st.sidebar.error(f"❌ Email error: {str(e)}")

if confluence_url and confluence_email and confluence_token:
    try:
        confluence_tools = ConfluenceTools(confluence_url, confluence_email, confluence_token)
        st.sidebar.success("✅ Confluence connected")
    except Exception as e:
        st.sidebar.error(f"❌ Confluence error: {str(e)}")

st.sidebar.markdown("---")
st.sidebar.success("""
✨ **Agentic Product Manager Journey**

This system provides comprehensive product management guidance through specialized AI agents with full integration support:

🎯 **Strategy Agent** - Product vision and strategic planning
🔍 **Research Agent** - User and market research
🗺️ **Roadmap Agent** - Feature prioritization and planning
📊 **Metrics Agent** - KPIs and success metrics
🤝 **Stakeholder Agent** - Communication and alignment
⚡ **Execution Agent** - Sprint planning and delivery
🔗 **GitHub Integration Agent** - Commit tracking and Jira sync
📅 **DSM Scheduler Agent** - Daily Scrum Meeting coordination
✅ **Jira Validation Agent** - Story quality and AC validation
🎯 **Quality Validation Agent** - Post-commit quality review

Enter your product details and let the agents collaborate to create a complete PM plan.
""")

# Main app UI
st.title("🚀 Agentic Product Manager Journey")

# Load selected plan if any
if st.session_state.get('selected_plan_id') and db_manager:
    try:
        plan_id = st.session_state.selected_plan_id
        version = st.session_state.get('selected_version')
        
        plan = db_manager.get_product_plan(plan_id, version)
        if plan:
            st.success(f"📚 Loaded: {plan.get('product_name', plan_id)} (Version {plan['version']})")
            
            # Show version selector
            versions = db_manager.get_plan_versions(plan_id)
            if len(versions) > 1:
                version_options = {f"Version {v['version']} - {v['created_at'][:10]}": v['version'] 
                                 for v in versions}
                selected_ver = st.selectbox(
                    "Select Version",
                    options=list(version_options.keys()),
                    index=0,
                    key="version_selector"
                )
                if selected_ver in version_options:
                    selected_version_num = version_options[selected_ver]
                    if selected_version_num != plan['version']:
                        plan = db_manager.get_product_plan(plan_id, selected_version_num)
                        st.session_state.selected_version = selected_version_num
            
            # Load plan data into session state
            if plan:
                plan_data = plan['plan_data']
                config = plan['configuration']
                
                # Restore outputs
                agent_outputs = db_manager.get_agent_outputs(plan_id, plan['version'])
                for agent_name, output_data in agent_outputs.items():
                    output_key = agent_name.replace('_agent', '')
                    if output_key in st.session_state.pm_output:
                        st.session_state.pm_output[output_key] = output_data.get('content', '')
                
                # Restore configuration
                if 'jira_url' in config:
                    st.session_state.restored_config = config
                    st.info("Configuration restored. Please review and update if needed.")
                
                # Show restore button
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Use This Plan", key="use_restored_plan"):
                        st.session_state.planning_complete = True
                        st.session_state.current_plan_id = plan_id
                        st.session_state.current_plan_version = plan['version']
                        safe_rerun()
                with col2:
                    if st.button("🔄 Start New Plan", key="start_new_plan"):
                        st.session_state.selected_plan_id = None
                        st.session_state.selected_version = None
                        st.session_state.planning_complete = False
                        safe_rerun()
    except Exception as e:
        logger.error(f"Error loading plan: {e}")
        st.error(f"Error loading plan: {e}")

st.info("""
**Your AI Product Management Team:**

**Core PM Agents:**
🎯 **Strategy Agent** - Defines product vision, market positioning, and strategic direction
🔍 **Research Agent** - Conducts user research, competitive analysis, and market insights
🗺️ **Roadmap Agent** - Creates prioritized roadmaps, feature planning, and release strategies
📊 **Metrics Agent** - Defines KPIs, success metrics, and analytics frameworks
🤝 **Stakeholder Agent** - Manages communication, alignment, and stakeholder relationships
⚡ **Execution Agent** - Plans sprints, manages delivery, and implements agile practices

**Integration & Automation Agents:**
🔗 **GitHub Integration Agent** - Tracks commits, syncs with Jira, identifies sprint activity
📅 **DSM Scheduler Agent** - Orchestrates Daily Scrum Meetings across timezones via Slack/Zoom
✅ **Jira Validation Agent** - Reviews story quality, validates acceptance criteria
🎯 **Quality Validation Agent** - Post-commit quality review and improvement recommendations
📋 **Jira Story Creator Agent** - Creates well-defined epics, stories, and releases from product strategy with natural language
📚 **Confluence Publisher Agent** - Publishes all reports and documents to dedicated Confluence space

These agents work together with full Jira, GitHub, Slack, Zoom, and Confluence integration support.
""")

# User inputs
st.subheader("📋 Product Information")

col1, col2 = st.columns(2)

with col1:
    product_name = st.text_input("Product Name", "My Product")
    product_type = st.selectbox(
        "Product Type",
        ["Web Application", "Mobile App", "SaaS Platform", "Enterprise Software", 
         "Consumer Product", "API/Platform", "Hardware", "Other"]
    )
    target_market = st.selectbox(
        "Target Market",
        ["B2B Enterprise", "B2B SMB", "B2C Consumer", "B2B2C", "Marketplace", "Developer Tools"]
    )
    stage = st.selectbox(
        "Product Stage",
        ["Ideation", "MVP/Validation", "Growth", "Scale", "Mature", "Pivot"]
    )

with col2:
    industry = st.text_input("Industry", "Technology")
    user_persona = st.text_area("Target User Persona", "Tech-savvy professionals aged 25-45")
    business_model = st.selectbox(
        "Business Model",
        ["Subscription", "Freemium", "One-time Purchase", "Usage-based", "Marketplace", "Enterprise License"]
    )
    timeline = st.selectbox(
        "Timeline Focus",
        ["3 months", "6 months", "12 months", "18 months", "2+ years"]
    )

# Additional details
st.subheader("🎯 Product Goals & Context")

col3, col4 = st.columns(2)

with col3:
    primary_goal = st.text_area(
        "Primary Product Goal",
        "Solve a critical pain point for our target users"
    )
    key_features = st.text_area(
        "Key Features/Requirements",
        "User authentication, dashboard, core functionality"
    )
    constraints = st.text_area(
        "Constraints (Budget, Resources, Technical)",
        "Limited budget, small team, existing tech stack"
    )

with col4:
    competitors = st.text_area("Main Competitors", "Competitor A, Competitor B")
    unique_value = st.text_area(
        "Unique Value Proposition",
        "What makes this product different?"
    )
    success_criteria = st.text_area(
        "Success Criteria",
        "User adoption, revenue targets, engagement metrics"
    )

depth = st.selectbox("Level of Detail", ["Low", "Medium", "High"])

# Jira Configuration Section
st.subheader("📋 Jira Configuration (Required)")

if jira_tools:
    jira_project_key = st.text_input("Jira Project Key", value=os.getenv("JIRA_PROJECT_KEY", ""), help="Project key where stories will be created (e.g., PROJ)")
    jira_board_id = st.number_input("Jira Board ID", min_value=0, value=int(os.getenv("JIRA_BOARD_ID", "0")), help="Board ID for sprint management")
    
    st.markdown("**Sprint Configuration:**")
    team_size = st.number_input("Team Size", min_value=1, max_value=20, value=8, help="Number of team members")
    max_story_points = st.number_input("Max Story Points per Sprint", min_value=1, max_value=200, value=70, help="Maximum story points for sprint capacity")
    sprint_duration_weeks = st.number_input("Sprint Duration (weeks)", min_value=1, max_value=4, value=2, help="Sprint duration in weeks")
    
    st.markdown("**Interactive Options:**")
    col_jira1, col_jira2 = st.columns(2)
    
    with col_jira1:
        enable_sprint_planning = st.checkbox("Enable Sprint Planning Agenda", value=True)
        enable_retro = st.checkbox("Enable Sprint Retro Questionnaire", value=True)
    
    with col_jira2:
        enable_sprint_report = st.checkbox("Enable Sprint Report", value=True)
        enable_comment_monitoring = st.checkbox("Enable Confluence Comment Monitoring", value=True)
    
    create_jira_items = True  # Always enabled in new workflow
else:
    jira_project_key = ""
    jira_board_id = 0
    team_size = 8
    max_story_points = 70
    sprint_duration_weeks = 2
    enable_sprint_planning = False
    enable_retro = False
    enable_sprint_report = False
    enable_comment_monitoring = False
    create_jira_items = False
    st.warning("⚠️ Jira configuration is required for the Agentic PM workflow")

# Button to start the agent collaboration (only show if planning not complete)
if not st.session_state.get('planning_complete', False):
    if st.button("🚀 Generate Product Management Plan", type="primary"):
        if not api_key:
            st.error("⚠️ Please enter your OpenAI API key in the sidebar.")
        elif not jira_tools:
            st.error("⚠️ Jira configuration is required. Please configure Jira in the sidebar.")
        elif not confluence_tools:
            st.error("⚠️ Confluence configuration is required. Please configure Confluence in the sidebar.")
        else:
            # Generate unique plan ID
            if not st.session_state.current_plan_id:
                st.session_state.current_plan_id = f"plan_{uuid.uuid4().hex[:12]}"
            
            with safe_spinner('🤖 AI Product Management agents are collaborating on your product plan...'):
                # Prepare the task based on user inputs
                task = f"""
                Create a comprehensive product management plan with the following details:
                
                Product Information:
                - Product Name: {product_name}
                - Product Type: {product_type}
                - Target Market: {target_market}
                - Product Stage: {stage}
                - Industry: {industry}
                - Target User Persona: {user_persona}
                - Business Model: {business_model}
                - Timeline Focus: {timeline}
                
                Product Goals & Context:
                - Primary Goal: {primary_goal}
                - Key Features/Requirements: {key_features}
                - Constraints: {constraints}
                - Main Competitors: {competitors}
                - Unique Value Proposition: {unique_value}
                - Success Criteria: {success_criteria}
                
                Detail Level: {depth}
                
                Please provide a comprehensive product management plan covering strategy, research, roadmap, metrics, stakeholder management, and execution.
                """

                llm_config = {"config_list": [{"model": "gpt-4o-mini", "api_key": api_key}]}

                # Initialize context variables
                context_variables = {
                "strategy": None,
                "research": None,
                "roadmap": None,
                "metrics": None,
                "stakeholder": None,
                "execution": None,
                "jira_story_creator": None,
                "confluence_publisher": None,
                "email_notification": None,
                "sprint_setup": None,
                "sprint_planning": None,
                "sprint_retro": None,
                "sprint_report": None,
                "comment_monitor": None,
                }

                # Store integration tools in context for agents to use
                context_variables["_jira_tools"] = jira_tools
                context_variables["_github_tools"] = github_tools
                context_variables["_slack_tools"] = slack_tools
                context_variables["_email_tools"] = email_tools
                context_variables["_confluence_tools"] = confluence_tools
                context_variables["_async_tracker"] = async_tracker
                context_variables["_github_owner"] = github_owner
                context_variables["_github_repo"] = github_repo
                context_variables["_slack_channel"] = slack_channel
                context_variables["_slack_email"] = slack_email
                context_variables["_jira_project_key"] = jira_project_key if jira_tools else ""
                context_variables["_jira_board_id"] = jira_board_id if jira_tools else 0
                context_variables["_confluence_space"] = confluence_space if confluence_tools else ""
                context_variables["_team_size"] = team_size
                context_variables["_max_story_points"] = max_story_points
                context_variables["_sprint_duration_weeks"] = sprint_duration_weeks
                context_variables["_enable_sprint_planning"] = enable_sprint_planning
                context_variables["_enable_retro"] = enable_retro
                context_variables["_enable_sprint_report"] = enable_sprint_report
                context_variables["_enable_comment_monitoring"] = enable_comment_monitoring
                context_variables["_created_epics"] = []
                context_variables["_created_stories"] = []
                context_variables["_created_releases"] = []
                context_variables["_confluence_pages"] = []

                # We'll create agents first, then define functions that reference them
                # This is needed because SwarmResult requires actual agent instances, not strings

                system_messages = {
                "strategy_agent": """
            You are an experienced Product Strategy Director specializing in product vision, market positioning, and strategic planning. Your task is to:
            1. Define a clear product vision and mission aligned with business goals
            2. Analyze market positioning and competitive landscape
            3. Identify target market segments and positioning strategy
            4. Develop strategic initiatives and long-term product direction
            5. Create go-to-market strategy considerations
            6. Define product-market fit criteria
            7. Consider business model alignment and revenue strategy
            8. Provide strategic recommendations based on product stage
                """,
                "research_agent": """
            You are a Senior Product Research Specialist with expertise in user research, competitive analysis, and market insights. Your task is to:
            1. Design user research methodology and approach
            2. Identify key user personas and their needs/pain points
            3. Conduct competitive analysis and market research
            4. Analyze user feedback and behavioral data
            5. Identify market opportunities and gaps
            6. Validate product assumptions through research
            7. Provide insights on user journey and experience
            8. Recommend research tools and methodologies
                """,
                "roadmap_agent": """
            You are a Product Roadmap Planner with expertise in feature prioritization, roadmap planning, and release strategy. Your task is to:
            1. Create a prioritized product roadmap aligned with strategy
            2. Use frameworks like RICE, MoSCoW, or Value vs Effort for prioritization
            3. Plan feature releases and milestones
            4. Define MVP scope and phased rollout strategy
            5. Balance short-term wins with long-term vision
            6. Consider dependencies and technical constraints
            7. Create quarterly/quarterly roadmap breakdown
            8. Align roadmap with business objectives and user needs
            9. Write in natural, conversational language that is easy to understand - avoid AI-generated sounding content
            10. Make content genuine and relatable, as if written by an experienced product manager
                """,
                "metrics_agent": """
            You are a Product Analytics Expert specializing in KPIs, success metrics, and data-driven decision making. Your task is to:
            1. Define North Star metric and key product KPIs
            2. Create metrics framework (AARRR, HEART, etc.)
            3. Identify leading and lagging indicators
            4. Design analytics tracking and measurement plan
            5. Define success criteria for features and initiatives
            6. Create dashboards and reporting structure
            7. Establish baseline metrics and targets
            8. Recommend tools for analytics and monitoring
                """,
                "stakeholder_agent": """
            You are a Stakeholder Management Specialist focused on communication, alignment, and relationship management. Your task is to:
            1. Identify key stakeholders and their interests
            2. Create communication plans and cadence
            3. Design stakeholder alignment strategies
            4. Plan product reviews and demos
            5. Handle conflict resolution and negotiation
            6. Create executive summaries and presentations
            7. Manage cross-functional team collaboration
            8. Ensure buy-in and support for product initiatives
                """,
                "execution_agent": """
            You are a Product Execution Lead specializing in agile practices, sprint planning, and delivery management. Your task is to:
            1. Create sprint planning and agile framework
            2. Define user stories and acceptance criteria
            3. Plan release cycles and deployment strategy
            4. Manage product backlog and refinement
            5. Coordinate with engineering and design teams
            6. Track progress and remove blockers
            7. Implement continuous improvement practices
            8. Ensure quality and timely delivery
                """,
                "jira_story_creator_agent": """
            You are a Jira Story Creator Specialist that transforms product strategy into well-defined, actionable Jira items. Your task is to:
            1. Analyze the product strategy document and roadmap to identify epics, stories, and releases
            2. Create natural, easy-to-understand story descriptions - write as if you're explaining to a developer, not generating AI content
            3. Define clear, testable acceptance criteria in plain language that developers can easily understand
            4. Break down epics into logical, implementable stories
            5. Create release plans with realistic timelines
            6. Ensure stories follow the "As a... I want... So that..." format naturally
            7. Write acceptance criteria that are specific, measurable, and written in natural language
            8. Avoid generic AI-sounding phrases - use real product management language
            9. Make content genuine, relatable, and practical
            10. Link stories to epics and assign to appropriate releases
            11. **CRITICAL**: You MUST use the Jira API tools to actually create epics, stories, and releases in Jira. Do not just describe what you would create - actually create them using create_epic, create_story, and create_release methods.
            12. Store created issue keys in context variables (_created_epics, _created_stories, _created_releases) for reference
            Available tools: Jira API (create_story, create_epic, create_release, link_story_to_epic, add_story_to_release, get_project_url, get_issue_url)
            CRITICAL: Write all content in natural, conversational language. Think like an experienced PM explaining requirements to the team. ACTUALLY CREATE the items in Jira using the API.
                """,
                "confluence_publisher_agent": """
            You are a Confluence Publisher Specialist that publishes all product management reports and documents. Your task is to:
            1. Format product management plans, reports, and documents for Confluence
            2. Create well-structured wiki pages with proper headings and formatting
            3. Create a nested document structure: Main Product Plan → Strategy, Research, Roadmap, Metrics, Stakeholder, Execution sections
            4. Publish all documents in a logical hierarchy for easy navigation
            5. Create an index page linking to all published reports
            6. Organize content in a dedicated Confluence space with proper parent-child relationships
            7. Ensure documents are easily discoverable and well-organized
            8. Format content for readability in Confluence wiki format
            9. Maintain version history and document structure
            10. **CRITICAL**: You MUST use the Confluence API tools to actually create pages in Confluence. Do not just describe what you would create - actually create them using create_page and publish_product_plan methods.
            11. Store created page IDs in context variables (_confluence_pages) for reference
            12. Publish ALL content from the product plan: Strategy, Research, Roadmap, Metrics, Stakeholder, and Execution sections
            Available tools: Confluence API (create_page, update_page, publish_product_plan, publish_report, create_report_index, get_page_url)
            CRITICAL: Create a nested structure with a main page and child pages for each section (Strategy, Research, Roadmap, etc.). ACTUALLY PUBLISH the content to Confluence using the API.
                """,
                "email_notification_agent": """
            You are an Email Notification Specialist that sends notifications to Slack email. Your task is to:
            1. Collect all Jira project URLs, epic URLs, and Confluence page URLs from previous agents
            2. Get URLs from context variables: _created_epics, _created_stories, _confluence_pages
            3. Use JiraTools.get_project_url() and JiraTools.get_issue_url() to get actual Jira URLs
            4. Use ConfluenceTools.get_page_url() to get actual Confluence page URLs
            5. Format a comprehensive email with links to:
               - Jira project
               - All created epics
               - Confluence documentation pages
            6. **CRITICAL**: You MUST actually send the email using EmailTools.send_slack_notification_email() method
            7. Send email to the Slack email address provided in _slack_email
            8. Include a clear subject line and well-formatted HTML email body
            9. Provide summary of what was created
            Available tools: EmailTools (send_slack_notification_email, send_email), JiraTools (get_project_url, get_issue_url), ConfluenceTools (get_page_url)
            CRITICAL: ACTUALLY SEND the email using the API, do not just describe what you would send.
                """,
                "sprint_setup_agent": """
            You are a Sprint Setup Specialist that creates and manages sprints with capacity constraints. Your task is to:
            1. Get all created stories from context variables (_created_stories) - these are the issue keys
            2. Retrieve story details from Jira to get story points for each story
            3. Create 2-week sprints (or configured duration from _sprint_duration_weeks) with proper start and end dates
            4. Prioritize stories based on roadmap and dependencies
            5. Distribute stories across sprints ensuring total story points NEVER exceed the maximum (from _max_story_points, default: 70 for 8-member team)
            6. Calculate sprint capacity: max_story_points per sprint (default: 70 for 8 members)
            7. **CRITICAL**: You MUST actually create sprints using JiraTools.create_sprint() and add stories using JiraTools.add_stories_to_sprint()
            8. Track sprint story points using get_sprint_story_points to ensure capacity limits
            9. Create multiple sprints if needed to accommodate all stories
            10. Set sprint goals based on the stories included
            11. Store created sprint IDs in context for reference
            Available tools: Jira API (create_sprint, add_stories_to_sprint, get_sprint_story_points, get_stories_in_sprint, get_story)
            CRITICAL: Never exceed max_story_points per sprint. If stories exceed capacity, create additional sprints. ACTUALLY CREATE the sprints in Jira using the API.
                """,
                "sprint_planning_agent": """
            You are a Sprint Planning Specialist that creates sprint planning agendas. Your task is to:
            1. Retrieve stories from the current/upcoming sprint from Jira using get_stories_in_sprint
            2. Get sprint information using get_sprint_info
            3. Create a comprehensive sprint planning agenda including:
               - Sprint goal
               - Stories to be planned
               - Story points breakdown
               - Dependencies and risks
               - Team capacity
            4. Format the agenda for Confluence
            5. **CRITICAL**: You MUST actually publish the sprint planning agenda to Confluence using ConfluenceTools.publish_report()
            6. Link it to the main product documentation (use parent_page_id from _confluence_pages)
            7. Store the created page ID in _confluence_pages
            Available tools: Jira API (get_stories_in_sprint, get_sprint_info), Confluence API (publish_report, get_page_url)
            Only runs if enable_sprint_planning is True. ACTUALLY PUBLISH to Confluence using the API.
                """,
                "sprint_retro_agent": """
            You are a Sprint Retrospective Specialist that creates retro questionnaires. Your task is to:
            1. Create a comprehensive sprint retrospective questionnaire
            2. Include questions about:
               - What went well
               - What could be improved
               - Action items
               - Team feedback
            3. Format the questionnaire for Confluence
            4. **CRITICAL**: You MUST actually publish the retro questionnaire to Confluence using ConfluenceTools.publish_report()
            5. Link it to the sprint documentation (use parent_page_id from _confluence_pages)
            6. Store the created page ID in _confluence_pages
            Available tools: Confluence API (publish_report, get_page_url)
            Only runs if enable_retro is True. ACTUALLY PUBLISH to Confluence using the API.
                """,
                "sprint_report_agent": """
            You are a Sprint Report Specialist that creates sprint reports. Your task is to:
            1. Retrieve data from the previous sprint (stories completed, story points, velocity) using Jira API
            2. Analyze sprint performance and metrics
            3. Create a comprehensive sprint report including:
               - Sprint summary
               - Completed vs planned stories
               - Velocity metrics
               - Blockers and issues
               - Team feedback summary
            4. Format the report for Confluence
            5. **CRITICAL**: You MUST actually publish the sprint report to Confluence using ConfluenceTools.publish_report()
            6. Link it to the sprint documentation (use parent_page_id from _confluence_pages)
            7. Store the created page ID in _confluence_pages
            Available tools: Jira API (get_stories_in_sprint, get_sprint_info), Confluence API (publish_report, get_page_url)
            Only runs if enable_sprint_report is True. ACTUALLY PUBLISH to Confluence using the API.
                """,
                "comment_monitor_agent": """
            You are a Comment Monitor Specialist that tracks Confluence comments. Your task is to:
            1. Monitor all Confluence pages created by the Agentic PM (from _confluence_pages context variable)
            2. Retrieve comments from Confluence pages using get_page_comments or get_all_comments_in_space
            3. Format comment notifications with:
               - Page title and URL (use get_page_url)
               - Comment author and content
               - Timestamp
            4. **CRITICAL**: You MUST actually send comment notifications to Slack email using EmailTools.send_email()
            5. Track which comments have been processed to avoid duplicates (use async_tracker if available)
            6. Run asynchronously to monitor for new comments
            Available tools: Confluence API (get_page_comments, get_all_comments_in_space, get_page_url), EmailTools (send_email), AsyncOperationTracker
            Only runs if enable_comment_monitoring is True. This should run asynchronously. ACTUALLY SEND emails using the API.
                """
            }

            def update_system_message_func(agent: SwarmAgent, messages) -> str:
                system_prompt = system_messages[agent.name]

                current_gen = agent.name.split("_")[0]
                if agent._context_variables.get(current_gen) is None:
                    system_prompt += f"\n\nCall the update function provided to first provide a 2-3 sentence summary of your ideas on {current_gen.upper()} based on the context provided."
                    agent.llm_config['tool_choice'] = {
                        "type": "function",
                        "function": {"name": f"update_{current_gen}_overview"}
                    }
                    agent.client = OpenAIWrapper(**agent.llm_config)
                else:
                    # Remove the tools to avoid the agent from using it and reduce cost
                    agent.llm_config["tools"] = None
                    agent.llm_config['tool_choice'] = None
                    agent.client = OpenAIWrapper(**agent.llm_config)
                    # The agent has given a summary, now it should generate a detailed response
                    system_prompt += f"\n\nYour task: Write the {current_gen} part of the product management plan. Do not include any other parts. Do not use XML tags.\nStart your response with: '## {current_gen.capitalize()} Plan'."

                    # Remove all messages except the first one with less cost
                    k = list(agent._oai_messages.keys())[-1]
                    agent._oai_messages[k] = agent._oai_messages[k][:1]

                # Add integration tool information if available
                jira_tools_available = agent._context_variables.get("_jira_tools") is not None
                github_tools_available = agent._context_variables.get("_github_tools") is not None
                slack_tools_available = agent._context_variables.get("_slack_tools") is not None
                email_tools_available = agent._context_variables.get("_email_tools") is not None
                confluence_tools_available = agent._context_variables.get("_confluence_tools") is not None
                
                if jira_tools_available or github_tools_available or slack_tools_available or email_tools_available or confluence_tools_available:
                    system_prompt += "\n\n**Available Integration Tools:**"
                    if jira_tools_available:
                        jira_project = agent._context_variables.get('_jira_project_key', 'PROJECT')
                        jira_tools = agent._context_variables.get("_jira_tools")
                        system_prompt += f"\n- Jira API: Available for creating/reading/updating stories, epics, releases in project {jira_project}"
                        system_prompt += "\n  * You have direct access to JiraTools instance - use methods like:"
                        system_prompt += "\n    - jira_tools.create_epic(project_key, summary, description, epic_name)"
                        system_prompt += "\n    - jira_tools.create_story(project_key, summary, description, acceptance_criteria, story_points)"
                        system_prompt += "\n    - jira_tools.create_release(project_key, name, description, release_date)"
                        system_prompt += "\n    - jira_tools.create_sprint(board_id, name, start_date, end_date, goal)"
                        system_prompt += "\n    - jira_tools.add_stories_to_sprint(sprint_id, issue_keys)"
                        if agent._context_variables.get("_enable_sprint_planning"):
                            system_prompt += "\n  * Sprint Planning: Enabled"
                        if agent._context_variables.get("_enable_retro"):
                            system_prompt += "\n  * Retrospectives: Enabled"
                        if agent._context_variables.get("_enable_sprint_report"):
                            system_prompt += "\n  * Sprint Reporting: Enabled"
                    if github_tools_available:
                        github_owner = agent._context_variables.get('_github_owner', 'owner')
                        github_repo = agent._context_variables.get('_github_repo', 'repo')
                        system_prompt += f"\n- GitHub API: Available for tracking commits in {github_owner}/{github_repo}"
                    if slack_tools_available:
                        slack_channel = agent._context_variables.get('_slack_channel', 'channel')
                        system_prompt += f"\n- Slack: Available for communication via {slack_channel} (email-based access)"
                    if email_tools_available:
                        email_tools = agent._context_variables.get("_email_tools")
                        system_prompt += "\n- Email API: Available for sending emails to Slack"
                        system_prompt += "\n  * You have direct access to EmailTools instance - use methods like:"
                        system_prompt += "\n    - email_tools.send_email(to_email, subject, body, html_body)"
                        system_prompt += "\n    - email_tools.send_slack_notification_email(slack_email, subject, jira_project_url, epic_urls, confluence_page_url)"
                    if confluence_tools_available:
                        confluence_space = agent._context_variables.get('_confluence_space', 'SPACE')
                        confluence_tools = agent._context_variables.get("_confluence_tools")
                        system_prompt += f"\n- Confluence API: Available for publishing reports to space {confluence_space}"
                        system_prompt += "\n  * You have direct access to ConfluenceTools instance - use methods like:"
                        system_prompt += "\n    - confluence_tools.create_page(space_key, title, content, parent_id)"
                        system_prompt += "\n    - confluence_tools.publish_product_plan(space_key, plan_title, plan_content, parent_page_id)"
                        system_prompt += "\n    - confluence_tools.publish_report(space_key, report_title, report_content, report_type, parent_page_id)"
                    system_prompt += "\n\n**CRITICAL**: You MUST actually use these tools to create items in Jira and Confluence. Do not just describe what you would do - actually execute the API calls."
                
                # Add emphasis on natural language for story creation agent
                if agent.name == "jira_story_creator_agent":
                    system_prompt += "\n\n**CRITICAL INSTRUCTIONS FOR STORY CREATION:**"
                    system_prompt += "\n- Write ALL content in natural, conversational language"
                    system_prompt += "\n- Avoid AI-generated sounding phrases like 'leverage', 'utilize', 'facilitate' - use simple words"
                    system_prompt += "\n- Write acceptance criteria as if explaining to a developer over coffee"
                    system_prompt += "\n- Use real product management language, not generic templates"
                    system_prompt += "\n- Make stories feel genuine and practical, not auto-generated"
                    system_prompt += "\n- Example of GOOD acceptance criteria: 'User can log in with email and password. If password is wrong, show a clear error message.'"
                    system_prompt += "\n- Example of BAD acceptance criteria: 'The system shall facilitate user authentication and leverage error handling mechanisms.'"

                system_prompt += f"\n\n\nBelow is context from other agents for you to refer to:"
                # Add context variables to the prompt
                for k, v in agent._context_variables.items():
                    if v is not None and not k.startswith("_"):
                        system_prompt += f"\n{k.capitalize()} Summary:\n{v}"

                return system_prompt

            state_update = UPDATE_SYSTEM_MESSAGE(update_system_message_func)

            # Create agents first (without functions, we'll add them after)
            strategy_agent = SwarmAgent("strategy_agent", llm_config=llm_config)
            research_agent = SwarmAgent("research_agent", llm_config=llm_config)
            roadmap_agent = SwarmAgent("roadmap_agent", llm_config=llm_config)
            metrics_agent = SwarmAgent("metrics_agent", llm_config=llm_config)
            stakeholder_agent = SwarmAgent("stakeholder_agent", llm_config=llm_config)
            execution_agent = SwarmAgent("execution_agent", llm_config=llm_config)
            jira_story_creator_agent = SwarmAgent("jira_story_creator_agent", llm_config=llm_config)
            confluence_publisher_agent = SwarmAgent("confluence_publisher_agent", llm_config=llm_config)
            email_notification_agent = SwarmAgent("email_notification_agent", llm_config=llm_config)
            sprint_setup_agent = SwarmAgent("sprint_setup_agent", llm_config=llm_config)
            sprint_planning_agent = SwarmAgent("sprint_planning_agent", llm_config=llm_config)
            sprint_retro_agent = SwarmAgent("sprint_retro_agent", llm_config=llm_config)
            sprint_report_agent = SwarmAgent("sprint_report_agent", llm_config=llm_config)
            comment_monitor_agent = SwarmAgent("comment_monitor_agent", llm_config=llm_config)
            
            # Now define functions that reference the actual agent instances
            def update_strategy_overview(strategy_summary: str, context_variables: dict) -> SwarmResult:
                """Keep the summary concise."""
                context_variables["strategy"] = strategy_summary
                safe_sidebar_success('✅ Strategy overview: ' + strategy_summary[:100] + "...")
                return SwarmResult(agent=research_agent, context_variables=context_variables)

            def update_research_overview(research_summary: str, context_variables: dict) -> SwarmResult:
                """Keep the summary concise."""
                context_variables["research"] = research_summary
                safe_sidebar_success('✅ Research overview: ' + research_summary[:100] + "...")
                return SwarmResult(agent=roadmap_agent, context_variables=context_variables)

            def update_roadmap_overview(roadmap_summary: str, context_variables: dict) -> SwarmResult:
                """Keep the summary concise."""
                context_variables["roadmap"] = roadmap_summary
                safe_sidebar_success('✅ Roadmap overview: ' + roadmap_summary[:100] + "...")
                return SwarmResult(agent=metrics_agent, context_variables=context_variables)

            def update_metrics_overview(metrics_summary: str, context_variables: dict) -> SwarmResult:
                """Keep the summary concise."""
                context_variables["metrics"] = metrics_summary
                safe_sidebar_success('✅ Metrics overview: ' + metrics_summary[:100] + "...")
                return SwarmResult(agent=stakeholder_agent, context_variables=context_variables)

            def update_stakeholder_overview(stakeholder_summary: str, context_variables: dict) -> SwarmResult:
                """Keep the summary concise."""
                context_variables["stakeholder"] = stakeholder_summary
                safe_sidebar_success('✅ Stakeholder overview: ' + stakeholder_summary[:100] + "...")
                return SwarmResult(agent=execution_agent, context_variables=context_variables)

            def update_execution_overview(execution_summary: str, context_variables: dict) -> SwarmResult:
                """Keep the summary concise."""
                context_variables["execution"] = execution_summary
                safe_sidebar_success('✅ Execution overview: ' + execution_summary[:100] + "...")
                # After execution, planning phase is complete - stop here for user confirmation
                # Don't proceed to Jira/Confluence until user confirms
                context_variables["_planning_complete"] = True
                return SwarmResult(agent=strategy_agent, context_variables=context_variables)
            
            def update_jira_story_creator_overview(jira_summary: str, context_variables: dict) -> SwarmResult:
                """Keep the summary concise."""
                context_variables["jira_story_creator"] = jira_summary
                safe_sidebar_success('✅ Jira Story Creator overview: ' + jira_summary[:100] + "...")
                # Go to Confluence Publisher
                if context_variables.get("_confluence_tools"):
                    return SwarmResult(agent=confluence_publisher_agent, context_variables=context_variables)
                else:
                    return SwarmResult(agent=strategy_agent, context_variables=context_variables)
            
            def update_confluence_publisher_overview(confluence_summary: str, context_variables: dict) -> SwarmResult:
                """Keep the summary concise."""
                context_variables["confluence_publisher"] = confluence_summary
                safe_sidebar_success('✅ Confluence Publisher overview: ' + confluence_summary[:100] + "...")
                # Go to Email Notification
                if context_variables.get("_email_tools") and context_variables.get("_slack_email"):
                    return SwarmResult(agent=email_notification_agent, context_variables=context_variables)
                elif context_variables.get("_jira_tools"):
                    return SwarmResult(agent=sprint_setup_agent, context_variables=context_variables)
                else:
                    return SwarmResult(agent=strategy_agent, context_variables=context_variables)
            
            def update_email_notification_overview(email_summary: str, context_variables: dict) -> SwarmResult:
                """Keep the summary concise."""
                context_variables["email_notification"] = email_summary
                safe_sidebar_success('✅ Email Notification overview: ' + email_summary[:100] + "...")
                # Go to Sprint Setup
                if context_variables.get("_jira_tools"):
                    return SwarmResult(agent=sprint_setup_agent, context_variables=context_variables)
                else:
                    return SwarmResult(agent=strategy_agent, context_variables=context_variables)
            
            def update_sprint_setup_overview(sprint_summary: str, context_variables: dict) -> SwarmResult:
                """Keep the summary concise."""
                context_variables["sprint_setup"] = sprint_summary
                safe_sidebar_success('✅ Sprint Setup overview: ' + sprint_summary[:100] + "...")
                # Go to optional agents based on configuration
                if context_variables.get("_enable_sprint_planning"):
                    return SwarmResult(agent=sprint_planning_agent, context_variables=context_variables)
                elif context_variables.get("_enable_retro"):
                    return SwarmResult(agent=sprint_retro_agent, context_variables=context_variables)
                elif context_variables.get("_enable_sprint_report"):
                    return SwarmResult(agent=sprint_report_agent, context_variables=context_variables)
                elif context_variables.get("_enable_comment_monitoring"):
                    return SwarmResult(agent=comment_monitor_agent, context_variables=context_variables)
                else:
                    return SwarmResult(agent=strategy_agent, context_variables=context_variables)
            
            def update_sprint_planning_overview(planning_summary: str, context_variables: dict) -> SwarmResult:
                """Keep the summary concise."""
                context_variables["sprint_planning"] = planning_summary
                safe_sidebar_success('✅ Sprint Planning overview: ' + planning_summary[:100] + "...")
                # Continue to next optional agent or finish
                if context_variables.get("_enable_retro"):
                    return SwarmResult(agent=sprint_retro_agent, context_variables=context_variables)
                elif context_variables.get("_enable_sprint_report"):
                    return SwarmResult(agent=sprint_report_agent, context_variables=context_variables)
                elif context_variables.get("_enable_comment_monitoring"):
                    return SwarmResult(agent=comment_monitor_agent, context_variables=context_variables)
                else:
                    return SwarmResult(agent=strategy_agent, context_variables=context_variables)
            
            def update_sprint_retro_overview(retro_summary: str, context_variables: dict) -> SwarmResult:
                """Keep the summary concise."""
                context_variables["sprint_retro"] = retro_summary
                safe_sidebar_success('✅ Sprint Retro overview: ' + retro_summary[:100] + "...")
                # Continue to next optional agent or finish
                if context_variables.get("_enable_sprint_report"):
                    return SwarmResult(agent=sprint_report_agent, context_variables=context_variables)
                elif context_variables.get("_enable_comment_monitoring"):
                    return SwarmResult(agent=comment_monitor_agent, context_variables=context_variables)
                else:
                    return SwarmResult(agent=strategy_agent, context_variables=context_variables)
            
            def update_sprint_report_overview(report_summary: str, context_variables: dict) -> SwarmResult:
                """Keep the summary concise."""
                context_variables["sprint_report"] = report_summary
                safe_sidebar_success('✅ Sprint Report overview: ' + report_summary[:100] + "...")
                # Continue to comment monitor or finish
                if context_variables.get("_enable_comment_monitoring"):
                    return SwarmResult(agent=comment_monitor_agent, context_variables=context_variables)
                else:
                    return SwarmResult(agent=strategy_agent, context_variables=context_variables)
            
            def update_comment_monitor_overview(monitor_summary: str, context_variables: dict) -> SwarmResult:
                """Keep the summary concise."""
                context_variables["comment_monitor"] = monitor_summary
                safe_sidebar_success('✅ Comment Monitor overview: ' + monitor_summary[:100] + "...")
                # Complete the cycle
                return SwarmResult(agent=strategy_agent, context_variables=context_variables)
            
            # Assign functions and state update to agents
            strategy_agent.functions = update_strategy_overview
            strategy_agent.update_agent_state_before_reply = [state_update]
            
            research_agent.functions = update_research_overview
            research_agent.update_agent_state_before_reply = [state_update]
            
            roadmap_agent.functions = update_roadmap_overview
            roadmap_agent.update_agent_state_before_reply = [state_update]
            
            metrics_agent.functions = update_metrics_overview
            metrics_agent.update_agent_state_before_reply = [state_update]
            
            stakeholder_agent.functions = update_stakeholder_overview
            stakeholder_agent.update_agent_state_before_reply = [state_update]
            
            execution_agent.functions = update_execution_overview
            execution_agent.update_agent_state_before_reply = [state_update]
            
            jira_story_creator_agent.functions = update_jira_story_creator_overview
            jira_story_creator_agent.update_agent_state_before_reply = [state_update]
            
            confluence_publisher_agent.functions = update_confluence_publisher_overview
            confluence_publisher_agent.update_agent_state_before_reply = [state_update]
            
            email_notification_agent.functions = update_email_notification_overview
            email_notification_agent.update_agent_state_before_reply = [state_update]
            
            sprint_setup_agent.functions = update_sprint_setup_overview
            sprint_setup_agent.update_agent_state_before_reply = [state_update]
            
            sprint_planning_agent.functions = update_sprint_planning_overview
            sprint_planning_agent.update_agent_state_before_reply = [state_update]
            
            sprint_retro_agent.functions = update_sprint_retro_overview
            sprint_retro_agent.update_agent_state_before_reply = [state_update]
            
            sprint_report_agent.functions = update_sprint_report_overview
            sprint_report_agent.update_agent_state_before_reply = [state_update]
            
            comment_monitor_agent.functions = update_comment_monitor_overview
            comment_monitor_agent.update_agent_state_before_reply = [state_update]

            # Register hand-offs in sequence - planning phase only
            strategy_agent.register_hand_off(AFTER_WORK(research_agent))
            research_agent.register_hand_off(AFTER_WORK(roadmap_agent))
            roadmap_agent.register_hand_off(AFTER_WORK(metrics_agent))
            metrics_agent.register_hand_off(AFTER_WORK(stakeholder_agent))
            stakeholder_agent.register_hand_off(AFTER_WORK(execution_agent))
            # Execution phase agents will be created and run separately after user confirmation
            
            # Phase 1: Planning Phase (Strategy through Execution)
            planning_agents = [
                strategy_agent, research_agent, roadmap_agent, metrics_agent,
                stakeholder_agent, execution_agent
            ]
            
            result, _, _ = initiate_swarm_chat(
                initial_agent=strategy_agent,
                agents=planning_agents,
                user_agent=None,
                messages=task,
                max_rounds=10,
            )

            # Update session state with the individual responses from planning phase
            # Extract responses from chat history
            chat_history = result.chat_history
            
            # Map agent names to output keys for planning phase
            planning_output_map = {
                'strategy_agent': 'strategy',
                'research_agent': 'research',
                'roadmap_agent': 'roadmap',
                'metrics_agent': 'metrics',
                'stakeholder_agent': 'stakeholder',
                'execution_agent': 'execution',
            }
            
            # Initialize output dict
            if 'pm_output' not in st.session_state:
                st.session_state.pm_output = {}
            
            # Extract outputs from chat history by matching agent names
            agent_last_message = {}
            for msg in chat_history:
                # Messages might be dicts or objects
                if isinstance(msg, dict):
                    agent_name = msg.get('name', '')
                    if agent_name in planning_output_map:
                        agent_last_message[agent_name] = msg.get('content', str(msg))
                elif hasattr(msg, 'name'):
                    agent_name = msg.name
                    if agent_name in planning_output_map:
                        agent_last_message[agent_name] = msg.content if hasattr(msg, 'content') else str(msg)
            
            # Update outputs with the last message from each planning agent
            for agent_name, output_key in planning_output_map.items():
                if agent_name in agent_last_message:
                    st.session_state.pm_output[output_key] = agent_last_message[agent_name]
            
            # Mark planning phase as complete
            st.session_state.planning_complete = True
            st.session_state.execution_phase_ready = False
            
            # Save to database
            if db_manager:
                try:
                    plan_id = st.session_state.current_plan_id
                    configuration = {
                        'jira_url': jira_url,
                        'jira_email': jira_email,
                        'jira_project_key': jira_project_key,
                        'jira_board_id': jira_board_id,
                        'confluence_url': confluence_url,
                        'confluence_space': confluence_space,
                        'slack_email': slack_email,
                        'team_size': team_size,
                        'max_story_points': max_story_points,
                        'sprint_duration_weeks': sprint_duration_weeks,
                        'enable_sprint_planning': enable_sprint_planning,
                        'enable_retro': enable_retro,
                        'enable_sprint_report': enable_sprint_report,
                        'enable_comment_monitoring': enable_comment_monitoring,
                    }
                    
                    # Save plan
                    result = db_manager.save_product_plan(
                        plan_id=plan_id,
                        product_name=product_name,
                        plan_data=st.session_state.pm_output,
                        configuration=configuration,
                        status='planning_complete',
                        created_by='user'
                    )
                    
                    # Save agent outputs
                    for agent_name, output_key in planning_output_map.items():
                        if output_key in st.session_state.pm_output:
                            db_manager.save_agent_output(
                                plan_id=plan_id,
                                version=result['version'],
                                agent_name=agent_name,
                                output_content=st.session_state.pm_output[output_key],
                                metadata={'phase': 'planning'}
                            )
                    
                    st.session_state.current_plan_version = result['version']
                    logger.info(f"Plan saved to database: {plan_id} v{result['version']}")
                except Exception as e:
                    logger.error(f"Error saving plan to database: {e}")
                    st.warning("⚠️ Could not save plan to database, but plan is available in session.")

        # Check if planning phase is complete
        if st.session_state.get('planning_complete', False):
            st.success('✨ Product Management plan generated successfully!')
            
            # Show confirmation section before publishing
            st.markdown("---")
            st.subheader("📋 Review & Publish Content")
            st.info("""
            **Planning Phase Complete!**
            
            Please review the product management plan below. Once you're satisfied, you can publish to:
            - **Jira**: Create epics, stories, and releases
            - **Confluence**: Publish all documents and reports
            - **Email**: Send notification to Slack with links
            - **Sprints**: Set up sprints with capacity management
            """)
            
            # Publishing buttons - separate for Jira and Confluence
            st.markdown("### 🚀 Publishing Options")
            
            # Check what integrations are available
            jira_available = jira_tools is not None
            confluence_available = confluence_tools is not None
            email_available = email_tools is not None
            
            if jira_available or confluence_available:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if jira_available:
                        if st.button("📋 Publish to Jira", type="primary", key="publish_jira", 
                                   help="Create epics, stories, releases, and sprints in Jira"):
                            st.session_state.publish_to_jira = True
                            st.session_state.execution_phase_ready = True
                            safe_rerun()
                    else:
                        st.button("📋 Publish to Jira", disabled=True, key="publish_jira_disabled",
                                help="Jira integration not configured")
                
                with col2:
                    if confluence_available:
                        if st.button("📚 Publish to Confluence", type="primary", key="publish_confluence",
                                   help="Publish all documents and reports to Confluence"):
                            st.session_state.publish_to_confluence = True
                            st.session_state.execution_phase_ready = True
                            safe_rerun()
                    else:
                        st.button("📚 Publish to Confluence", disabled=True, key="publish_confluence_disabled",
                                help="Confluence integration not configured")
                
                with col3:
                    if jira_available and confluence_available:
                        if st.button("🚀 Publish All", type="primary", key="publish_all",
                                   help="Publish to both Jira and Confluence, send email, and set up sprints"):
                            st.session_state.publish_to_jira = True
                            st.session_state.publish_to_confluence = True
                            st.session_state.execution_phase_ready = True
                            safe_rerun()
                    else:
                        st.button("🚀 Publish All", disabled=True, key="publish_all_disabled",
                                help="Requires both Jira and Confluence integration")
            
            # Save Draft button
            st.markdown("---")
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("💾 Save Draft", key="save_draft"):
                    if db_manager:
                        try:
                            plan_id = st.session_state.current_plan_id
                            configuration = {
                                'jira_url': jira_url,
                                'jira_email': jira_email,
                                'jira_project_key': jira_project_key,
                                'jira_board_id': jira_board_id,
                                'confluence_url': confluence_url,
                                'confluence_space': confluence_space,
                                'slack_email': slack_email,
                                'team_size': team_size,
                                'max_story_points': max_story_points,
                                'sprint_duration_weeks': sprint_duration_weeks,
                            }
                            result = db_manager.save_product_plan(
                                plan_id=plan_id,
                                product_name=product_name,
                                plan_data=st.session_state.pm_output,
                                configuration=configuration,
                                status='draft',
                                created_by='user'
                            )
                            st.success(f"✅ Draft saved! Plan ID: {plan_id}")
                        except Exception as e:
                            logger.error(f"Error saving draft: {e}")
                            st.error(f"Error saving draft: {e}")
        
        # Show plan management options
        if db_manager and st.session_state.current_plan_id:
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("💾 Save Current Version", key="save_current"):
                    try:
                        plan_id = st.session_state.current_plan_id
                        configuration = {
                            'jira_url': jira_url,
                            'jira_email': jira_email,
                            'jira_project_key': jira_project_key,
                            'jira_board_id': jira_board_id,
                            'confluence_url': confluence_url,
                            'confluence_space': confluence_space,
                            'slack_email': slack_email,
                            'team_size': team_size,
                            'max_story_points': max_story_points,
                            'sprint_duration_weeks': sprint_duration_weeks,
                        }
                        result = db_manager.save_product_plan(
                            plan_id=plan_id,
                            product_name=product_name,
                            plan_data=st.session_state.pm_output,
                            configuration=configuration,
                            status='draft',
                            created_by='user'
                        )
                        st.session_state.current_plan_version = result['version']
                        st.success(f"✅ Saved as version {result['version']}")
                    except Exception as e:
                        st.error(f"Error saving: {e}")
            with col2:
                if st.button("📚 View All Versions", key="view_versions"):
                    st.session_state.show_versions = True
            with col3:
                if st.button("🔄 Create New Version", key="create_new_version"):
                    st.session_state.planning_complete = False
                    st.session_state.execution_phase_ready = False
                    st.session_state.execution_phase_complete = False
                    safe_rerun()
        
        # Show versions if requested
        if st.session_state.get('show_versions') and db_manager and st.session_state.current_plan_id:
            st.markdown("---")
            st.subheader("📚 Plan Versions")
            try:
                versions = db_manager.get_plan_versions(st.session_state.current_plan_id)
                for v in versions:
                    with st.expander(f"Version {v['version']} - {v['created_at'][:19]} - {v['status']}"):
                        st.write(f"**Status:** {v['status']}")
                        st.write(f"**Created:** {v['created_at']}")
                        if v.get('notes'):
                            st.write(f"**Notes:** {v['notes']}")
                        if st.button(f"📥 Load Version {v['version']}", key=f"load_v{v['version']}"):
                            st.session_state.selected_plan_id = st.session_state.current_plan_id
                            st.session_state.selected_version = v['version']
                            safe_rerun()
            except Exception as e:
                st.error(f"Error loading versions: {e}")
        
        # Display the individual outputs in expanders
        with st.expander("🎯 Strategy Plan", expanded=True):
            st.markdown(st.session_state.pm_output.get('strategy', ''))

        with st.expander("🔍 Research Plan"):
            st.markdown(st.session_state.pm_output.get('research', ''))

        with st.expander("🗺️ Roadmap Plan"):
            st.markdown(st.session_state.pm_output.get('roadmap', ''))

        with st.expander("📊 Metrics & Analytics Plan"):
            st.markdown(st.session_state.pm_output.get('metrics', ''))

        with st.expander("🤝 Stakeholder Management Plan"):
            st.markdown(st.session_state.pm_output.get('stakeholder', ''))

        with st.expander("⚡ Execution Plan"):
            st.markdown(st.session_state.pm_output.get('execution', ''))
        
        # Show new workflow agent outputs if available
        if st.session_state.pm_output.get('jira_story_creator'):
            with st.expander("📋 Jira Story Creation Report"):
                st.markdown(st.session_state.pm_output['jira_story_creator'])
        
        if st.session_state.pm_output.get('confluence_publisher'):
            with st.expander("📚 Confluence Publishing Report"):
                st.markdown(st.session_state.pm_output['confluence_publisher'])
        
        if st.session_state.pm_output.get('email_notification'):
            with st.expander("📧 Email Notification Report"):
                st.markdown(st.session_state.pm_output['email_notification'])
        
        if st.session_state.pm_output.get('sprint_setup'):
            with st.expander("🏃 Sprint Setup Report"):
                st.markdown(st.session_state.pm_output['sprint_setup'])
        
        if st.session_state.pm_output.get('sprint_planning'):
            with st.expander("📊 Sprint Planning Agenda"):
                st.markdown(st.session_state.pm_output['sprint_planning'])
        
        if st.session_state.pm_output.get('sprint_retro'):
            with st.expander("🔄 Sprint Retro Questionnaire"):
                st.markdown(st.session_state.pm_output['sprint_retro'])
        
        if st.session_state.pm_output.get('sprint_report'):
            with st.expander("📈 Sprint Report"):
                st.markdown(st.session_state.pm_output['sprint_report'])
        
        if st.session_state.pm_output.get('comment_monitor'):
            with st.expander("👀 Comment Monitor Report"):
                st.markdown(st.session_state.pm_output['comment_monitor'])

        # Execution Phase: Publish to Jira and/or Confluence after confirmation
        if st.session_state.get('execution_phase_ready', False) and not st.session_state.get('execution_phase_complete', False):
            # Determine what to publish based on button clicked
            publish_jira = st.session_state.get('publish_to_jira', False)
            publish_confluence = st.session_state.get('publish_to_confluence', False)
            
            if publish_jira or publish_confluence:
                publish_tasks = []
                if publish_jira:
                    publish_tasks.append("1. Create Jira epics, stories, and releases from the strategy and roadmap")
                    publish_tasks.append("2. Set up sprints with capacity management")
                    publish_tasks.append("3. Create any requested sprint planning, retro, or report documents")
                if publish_confluence:
                    publish_tasks.append("4. Publish all product management content to Confluence with nested structure")
                if publish_jira and publish_confluence and email_tools:
                    publish_tasks.append("5. Send email notification to Slack with links")
                
                spinner_text = '🚀 Publishing content...'
                if publish_jira and publish_confluence:
                    spinner_text = '🚀 Publishing content to Jira and Confluence...'
                elif publish_jira:
                    spinner_text = '📋 Publishing to Jira...'
                elif publish_confluence:
                    spinner_text = '📚 Publishing to Confluence...'
                
                with st.spinner(spinner_text):
                    # Prepare execution task
                    execution_task = f"""
                    Based on the completed product management plan, please:
                    {chr(10).join(publish_tasks)}
                    
                    Product Plan Summary:
                    Strategy: {st.session_state.pm_output.get('strategy', '')[:500]}
                    Roadmap: {st.session_state.pm_output.get('roadmap', '')[:500]}
                    """
                
                llm_config = {"config_list": [{"model": "gpt-4o-mini", "api_key": api_key}]}
                
                # Define system messages for execution phase agents (same as planning phase)
                exec_system_messages = {
                    "jira_story_creator_agent": """
                You are a Jira Story Creator Specialist that transforms product strategy into well-defined, actionable Jira items. Your task is to:
                1. Analyze the product strategy document and roadmap to identify epics, stories, and releases
                2. Create natural, easy-to-understand story descriptions - write as if you're explaining to a developer, not generating AI content
                3. Define clear, testable acceptance criteria in plain language that developers can easily understand
                4. Break down epics into logical, implementable stories
                5. Create release plans with realistic timelines
                6. Ensure stories follow the "As a... I want... So that..." format naturally
                7. Write acceptance criteria that are specific, measurable, and written in natural language
                8. Avoid generic AI-sounding phrases - use real product management language
                9. Make content genuine, relatable, and practical
                10. Link stories to epics and assign to appropriate releases
                11. **CRITICAL**: You MUST use the Jira API tools to actually create epics, stories, and releases in Jira. Do not just describe what you would create - actually create them using create_epic, create_story, and create_release methods.
                12. Store created issue keys in context variables (_created_epics, _created_stories, _created_releases) for reference
                Available tools: Jira API (create_story, create_epic, create_release, link_story_to_epic, add_story_to_release, get_project_url, get_issue_url)
                CRITICAL: Write all content in natural, conversational language. Think like an experienced PM explaining requirements to the team. ACTUALLY CREATE the items in Jira using the API.
                    """,
                    "confluence_publisher_agent": """
                You are a Confluence Publisher Specialist that publishes all product management reports and documents. Your task is to:
                1. Format product management plans, reports, and documents for Confluence
                2. Create well-structured wiki pages with proper headings and formatting
                3. Create a nested document structure: Main Product Plan → Strategy, Research, Roadmap, Metrics, Stakeholder, Execution sections
                4. Publish all documents in a logical hierarchy for easy navigation
                5. Create an index page linking to all published reports
                6. Organize content in a dedicated Confluence space with proper parent-child relationships
                7. Ensure documents are easily discoverable and well-organized
                8. Format content for readability in Confluence wiki format
                9. Maintain version history and document structure
                10. **CRITICAL**: You MUST use the Confluence API tools to actually create pages in Confluence. Do not just describe what you would create - actually create them using create_page and publish_product_plan methods.
                11. Store created page IDs in context variables (_confluence_pages) for reference
                12. Publish ALL content from the product plan: Strategy, Research, Roadmap, Metrics, Stakeholder, and Execution sections
                Available tools: Confluence API (create_page, update_page, publish_product_plan, publish_report, create_report_index, get_page_url)
                CRITICAL: Create a nested structure with a main page and child pages for each section (Strategy, Research, Roadmap, etc.). ACTUALLY PUBLISH the content to Confluence using the API.
                    """,
                    "email_notification_agent": """
                You are an Email Notification Specialist that sends notifications to Slack email. Your task is to:
                1. Collect all Jira project URLs, epic URLs, and Confluence page URLs from previous agents
                2. Get URLs from context variables: _created_epics, _created_stories, _confluence_pages
                3. Use JiraTools.get_project_url() and JiraTools.get_issue_url() to get actual Jira URLs
                4. Use ConfluenceTools.get_page_url() to get actual Confluence page URLs
                5. Format a comprehensive email with links to:
                   - Jira project
                   - All created epics
                   - Confluence documentation pages
                6. **CRITICAL**: You MUST actually send the email using EmailTools.send_slack_notification_email() method
                7. Send email to the Slack email address provided in _slack_email
                8. Include a clear subject line and well-formatted HTML email body
                9. Provide summary of what was created
                Available tools: EmailTools (send_slack_notification_email, send_email), JiraTools (get_project_url, get_issue_url), ConfluenceTools (get_page_url)
                CRITICAL: ACTUALLY SEND the email using the API, do not just describe what you would send.
                    """,
                    "sprint_setup_agent": """
                You are a Sprint Setup Specialist that creates and manages sprints with capacity constraints. Your task is to:
                1. Get all created stories from context variables (_created_stories) - these are the issue keys
                2. Retrieve story details from Jira to get story points for each story
                3. Create 2-week sprints (or configured duration from _sprint_duration_weeks) with proper start and end dates
                4. Prioritize stories based on roadmap and dependencies
                5. Distribute stories across sprints ensuring total story points NEVER exceed the maximum (from _max_story_points, default: 70 for 8-member team)
                6. Calculate sprint capacity: max_story_points per sprint (default: 70 for 8 members)
                7. **CRITICAL**: You MUST actually create sprints using JiraTools.create_sprint() and add stories using JiraTools.add_stories_to_sprint()
                8. Track sprint story points using get_sprint_story_points to ensure capacity limits
                9. Create multiple sprints if needed to accommodate all stories
                10. Set sprint goals based on the stories included
                11. Store created sprint IDs in context for reference
                Available tools: Jira API (create_sprint, add_stories_to_sprint, get_sprint_story_points, get_stories_in_sprint, get_story)
                CRITICAL: Never exceed max_story_points per sprint. If stories exceed capacity, create additional sprints. ACTUALLY CREATE the sprints in Jira using the API.
                    """,
                    "sprint_planning_agent": """
                You are a Sprint Planning Specialist that creates sprint planning agendas. Your task is to:
                1. Retrieve stories from the current/upcoming sprint from Jira using get_stories_in_sprint
                2. Get sprint information using get_sprint_info
                3. Create a comprehensive sprint planning agenda including:
                   - Sprint goal
                   - Stories to be planned
                   - Story points breakdown
                   - Dependencies and risks
                   - Team capacity
                4. Format the agenda for Confluence
                5. **CRITICAL**: You MUST actually publish the sprint planning agenda to Confluence using ConfluenceTools.publish_report()
                6. Link it to the main product documentation (use parent_page_id from _confluence_pages)
                7. Store the created page ID in _confluence_pages
                Available tools: Jira API (get_stories_in_sprint, get_sprint_info), Confluence API (publish_report, get_page_url)
                Only runs if enable_sprint_planning is True. ACTUALLY PUBLISH to Confluence using the API.
                    """,
                    "sprint_retro_agent": """
                You are a Sprint Retrospective Specialist that creates retro questionnaires. Your task is to:
                1. Create a comprehensive sprint retrospective questionnaire
                2. Include questions about:
                   - What went well
                   - What could be improved
                   - Action items
                   - Team feedback
                3. Format the questionnaire for Confluence
                4. **CRITICAL**: You MUST actually publish the retro questionnaire to Confluence using ConfluenceTools.publish_report()
                5. Link it to the sprint documentation (use parent_page_id from _confluence_pages)
                6. Store the created page ID in _confluence_pages
                Available tools: Confluence API (publish_report, get_page_url)
                Only runs if enable_retro is True. ACTUALLY PUBLISH to Confluence using the API.
                    """,
                    "sprint_report_agent": """
                You are a Sprint Report Specialist that creates sprint reports. Your task is to:
                1. Retrieve data from the previous sprint (stories completed, story points, velocity) using Jira API
                2. Analyze sprint performance and metrics
                3. Create a comprehensive sprint report including:
                   - Sprint summary
                   - Completed vs planned stories
                   - Velocity metrics
                   - Blockers and issues
                   - Team feedback summary
                4. Format the report for Confluence
                5. **CRITICAL**: You MUST actually publish the sprint report to Confluence using ConfluenceTools.publish_report()
                6. Link it to the sprint documentation (use parent_page_id from _confluence_pages)
                7. Store the created page ID in _confluence_pages
                Available tools: Jira API (get_stories_in_sprint, get_sprint_info), Confluence API (publish_report, get_page_url)
                Only runs if enable_sprint_report is True. ACTUALLY PUBLISH to Confluence using the API.
                    """,
                    "comment_monitor_agent": """
                You are a Comment Monitor Specialist that tracks Confluence comments. Your task is to:
                1. Monitor all Confluence pages created by the Agentic PM (from _confluence_pages context variable)
                2. Retrieve comments from Confluence pages using get_page_comments or get_all_comments_in_space
                3. Format comment notifications with:
                   - Page title and URL (use get_page_url)
                   - Comment author and content
                   - Timestamp
                4. **CRITICAL**: You MUST actually send comment notifications to Slack email using EmailTools.send_email()
                5. Track which comments have been processed to avoid duplicates (use async_tracker if available)
                6. Run asynchronously to monitor for new comments
                Available tools: Confluence API (get_page_comments, get_all_comments_in_space, get_page_url), EmailTools (send_email), AsyncOperationTracker
                Only runs if enable_comment_monitoring is True. This should run asynchronously. ACTUALLY SEND emails using the API.
                    """
                }
                
                # Initialize execution context variables
                exec_context_variables = {
                    "strategy": st.session_state.pm_output.get('strategy', ''),
                    "research": st.session_state.pm_output.get('research', ''),
                    "roadmap": st.session_state.pm_output.get('roadmap', ''),
                    "metrics": st.session_state.pm_output.get('metrics', ''),
                    "stakeholder": st.session_state.pm_output.get('stakeholder', ''),
                    "execution": st.session_state.pm_output.get('execution', ''),
                    "jira_story_creator": None,
                    "confluence_publisher": None,
                    "email_notification": None,
                    "sprint_setup": None,
                    "sprint_planning": None,
                    "sprint_retro": None,
                    "sprint_report": None,
                    "comment_monitor": None,
                }
                
                # Store integration tools in context
                exec_context_variables["_jira_tools"] = jira_tools
                exec_context_variables["_github_tools"] = github_tools
                exec_context_variables["_slack_tools"] = slack_tools
                exec_context_variables["_email_tools"] = email_tools
                exec_context_variables["_confluence_tools"] = confluence_tools
                exec_context_variables["_async_tracker"] = async_tracker
                exec_context_variables["_github_owner"] = github_owner
                exec_context_variables["_github_repo"] = github_repo
                exec_context_variables["_slack_channel"] = slack_channel
                exec_context_variables["_slack_email"] = slack_email
                exec_context_variables["_jira_project_key"] = jira_project_key if jira_tools else ""
                exec_context_variables["_jira_board_id"] = jira_board_id if jira_tools else 0
                exec_context_variables["_confluence_space"] = confluence_space if confluence_tools else ""
                exec_context_variables["_team_size"] = team_size
                exec_context_variables["_max_story_points"] = max_story_points
                exec_context_variables["_sprint_duration_weeks"] = sprint_duration_weeks
                exec_context_variables["_enable_sprint_planning"] = enable_sprint_planning
                exec_context_variables["_enable_retro"] = enable_retro
                exec_context_variables["_enable_sprint_report"] = enable_sprint_report
                exec_context_variables["_enable_comment_monitoring"] = enable_comment_monitoring
                exec_context_variables["_created_epics"] = []
                exec_context_variables["_created_stories"] = []
                exec_context_variables["_created_releases"] = []
                exec_context_variables["_confluence_pages"] = []
                
                # Create execution phase agents - only create agents that are needed
                exec_agents = {}
                
                # Jira-related agents (only if publishing to Jira)
                if publish_jira and jira_tools:
                    exec_jira_story_creator_agent = SwarmAgent("jira_story_creator_agent", llm_config=llm_config)
                    exec_sprint_setup_agent = SwarmAgent("sprint_setup_agent", llm_config=llm_config)
                    exec_agents["jira_story_creator"] = exec_jira_story_creator_agent
                    exec_agents["sprint_setup"] = exec_sprint_setup_agent
                    
                    # Optional Jira agents
                    if enable_sprint_planning:
                        exec_sprint_planning_agent = SwarmAgent("sprint_planning_agent", llm_config=llm_config)
                        exec_agents["sprint_planning"] = exec_sprint_planning_agent
                    if enable_retro:
                        exec_sprint_retro_agent = SwarmAgent("sprint_retro_agent", llm_config=llm_config)
                        exec_agents["sprint_retro"] = exec_sprint_retro_agent
                    if enable_sprint_report:
                        exec_sprint_report_agent = SwarmAgent("sprint_report_agent", llm_config=llm_config)
                        exec_agents["sprint_report"] = exec_sprint_report_agent
                
                # Confluence-related agents (only if publishing to Confluence)
                if publish_confluence and confluence_tools:
                    exec_confluence_publisher_agent = SwarmAgent("confluence_publisher_agent", llm_config=llm_config)
                    exec_agents["confluence_publisher"] = exec_confluence_publisher_agent
                
                # Email agent (only if both Jira and Confluence are published)
                if publish_jira and publish_confluence and email_tools and slack_email:
                    exec_email_notification_agent = SwarmAgent("email_notification_agent", llm_config=llm_config)
                    exec_agents["email_notification"] = exec_email_notification_agent
                
                # Comment monitor (only if enabled and Confluence is available)
                if enable_comment_monitoring and confluence_tools:
                    exec_comment_monitor_agent = SwarmAgent("comment_monitor_agent", llm_config=llm_config)
                    exec_agents["comment_monitor"] = exec_comment_monitor_agent
                
                # Define execution phase update functions
                def exec_update_jira_story_creator(jira_summary: str, context_variables: dict) -> SwarmResult:
                    context_variables["jira_story_creator"] = jira_summary
                    safe_sidebar_success('✅ Jira Story Creator: ' + jira_summary[:100] + "...")
                    
                    # Save to database
                    if db_manager and st.session_state.current_plan_id:
                        try:
                            db_manager.save_agent_output(
                                plan_id=st.session_state.current_plan_id,
                                version=st.session_state.current_plan_version,
                                agent_name='jira_story_creator_agent',
                                output_content=jira_summary,
                                metadata={'phase': 'execution'}
                            )
                            
                            # Save Jira items if available
                            created_epics = context_variables.get("_created_epics", [])
                            created_stories = context_variables.get("_created_stories", [])
                            created_releases = context_variables.get("_created_releases", [])
                            
                            jira_tools = context_variables.get("_jira_tools")
                            if jira_tools:
                                for epic_key in created_epics:
                                    db_manager.save_jira_item(
                                        plan_id=st.session_state.current_plan_id,
                                        version=st.session_state.current_plan_version,
                                        item_type='epic',
                                        item_key=epic_key,
                                        item_url=jira_tools.get_issue_url(epic_key) if jira_tools else None
                                    )
                                for story_key in created_stories:
                                    db_manager.save_jira_item(
                                        plan_id=st.session_state.current_plan_id,
                                        version=st.session_state.current_plan_version,
                                        item_type='story',
                                        item_key=story_key,
                                        item_url=jira_tools.get_issue_url(story_key) if jira_tools else None
                                    )
                                for release_key in created_releases:
                                    db_manager.save_jira_item(
                                        plan_id=st.session_state.current_plan_id,
                                        version=st.session_state.current_plan_version,
                                        item_type='release',
                                        item_key=release_key,
                                        item_url=jira_tools.get_issue_url(release_key) if jira_tools else None
                                    )
                        except Exception as e:
                            logger.error(f"Error saving Jira items to database: {e}")
                    
                    # Route to next agent based on what's being published
                    if publish_confluence and "confluence_publisher" in exec_agents:
                        return SwarmResult(agent=exec_agents["confluence_publisher"], context_variables=context_variables)
                    elif publish_jira and publish_confluence and "email_notification" in exec_agents:
                        return SwarmResult(agent=exec_agents["email_notification"], context_variables=context_variables)
                    elif publish_jira and "sprint_setup" in exec_agents:
                        return SwarmResult(agent=exec_agents["sprint_setup"], context_variables=context_variables)
                    else:
                        # No more agents, return to start
                        return SwarmResult(agent=exec_agents.get("jira_story_creator", list(exec_agents.values())[0] if exec_agents else None), context_variables=context_variables)
                
                def exec_update_confluence_publisher(confluence_summary: str, context_variables: dict) -> SwarmResult:
                    context_variables["confluence_publisher"] = confluence_summary
                    safe_sidebar_success('✅ Confluence Publisher: ' + confluence_summary[:100] + "...")
                    
                    # Save to database
                    if db_manager and st.session_state.current_plan_id:
                        try:
                            db_manager.save_agent_output(
                                plan_id=st.session_state.current_plan_id,
                                version=st.session_state.current_plan_version,
                                agent_name='confluence_publisher_agent',
                                output_content=confluence_summary,
                                metadata={'phase': 'execution'}
                            )
                            
                            # Save Confluence pages if available
                            confluence_pages = context_variables.get("_confluence_pages", [])
                            confluence_tools = context_variables.get("_confluence_tools")
                            if confluence_tools:
                                for page_info in confluence_pages:
                                    if isinstance(page_info, dict):
                                        db_manager.save_confluence_page(
                                            plan_id=st.session_state.current_plan_id,
                                            version=st.session_state.current_plan_version,
                                            page_id=page_info.get('id', ''),
                                            page_title=page_info.get('title', ''),
                                            page_url=confluence_tools.get_page_url(page_info.get('id', '')) if confluence_tools else None,
                                            parent_page_id=page_info.get('parent_id'),
                                            page_data=page_info
                                        )
                        except Exception as e:
                            logger.error(f"Error saving Confluence pages to database: {e}")
                    
                    # Route to next agent based on what's being published
                    if publish_jira and publish_confluence and "email_notification" in exec_agents:
                        return SwarmResult(agent=exec_agents["email_notification"], context_variables=context_variables)
                    elif publish_jira and "sprint_setup" in exec_agents:
                        return SwarmResult(agent=exec_agents["sprint_setup"], context_variables=context_variables)
                    else:
                        # No more agents, return to start
                        return SwarmResult(agent=exec_agents.get("confluence_publisher", list(exec_agents.values())[0] if exec_agents else None), context_variables=context_variables)
                
                def exec_update_email_notification(email_summary: str, context_variables: dict) -> SwarmResult:
                    context_variables["email_notification"] = email_summary
                    safe_sidebar_success('✅ Email Notification: ' + email_summary[:100] + "...")
                    # Route to next agent
                    if publish_jira and "sprint_setup" in exec_agents:
                        return SwarmResult(agent=exec_agents["sprint_setup"], context_variables=context_variables)
                    else:
                        # No more agents, return to start
                        return SwarmResult(agent=exec_agents.get("email_notification", list(exec_agents.values())[0] if exec_agents else None), context_variables=context_variables)
                
                def exec_update_sprint_setup(sprint_summary: str, context_variables: dict) -> SwarmResult:
                    context_variables["sprint_setup"] = sprint_summary
                    safe_sidebar_success('✅ Sprint Setup: ' + sprint_summary[:100] + "...")
                    
                    # Save to database
                    if db_manager and st.session_state.current_plan_id:
                        try:
                            db_manager.save_agent_output(
                                plan_id=st.session_state.current_plan_id,
                                version=st.session_state.current_plan_version,
                                agent_name='sprint_setup_agent',
                                output_content=sprint_summary,
                                metadata={'phase': 'execution'}
                            )
                            
                            # Save sprint information if available in context
                            # Note: Sprint IDs should be stored in context by the agent
                        except Exception as e:
                            logger.error(f"Error saving sprint setup to database: {e}")
                    
                    # Route to next optional agent
                    if "sprint_planning" in exec_agents and context_variables.get("_enable_sprint_planning"):
                        return SwarmResult(agent=exec_agents["sprint_planning"], context_variables=context_variables)
                    elif "sprint_retro" in exec_agents and context_variables.get("_enable_retro"):
                        return SwarmResult(agent=exec_agents["sprint_retro"], context_variables=context_variables)
                    elif "sprint_report" in exec_agents and context_variables.get("_enable_sprint_report"):
                        return SwarmResult(agent=exec_agents["sprint_report"], context_variables=context_variables)
                    elif "comment_monitor" in exec_agents and context_variables.get("_enable_comment_monitoring"):
                        return SwarmResult(agent=exec_agents["comment_monitor"], context_variables=context_variables)
                    else:
                        # No more agents, return to start
                        return SwarmResult(agent=exec_agents.get("sprint_setup", list(exec_agents.values())[0] if exec_agents else None), context_variables=context_variables)
                
                def exec_update_sprint_planning(planning_summary: str, context_variables: dict) -> SwarmResult:
                    context_variables["sprint_planning"] = planning_summary
                    safe_sidebar_success('✅ Sprint Planning: ' + planning_summary[:100] + "...")
                    # Route to next optional agent
                    if "sprint_retro" in exec_agents and context_variables.get("_enable_retro"):
                        return SwarmResult(agent=exec_agents["sprint_retro"], context_variables=context_variables)
                    elif "sprint_report" in exec_agents and context_variables.get("_enable_sprint_report"):
                        return SwarmResult(agent=exec_agents["sprint_report"], context_variables=context_variables)
                    elif "comment_monitor" in exec_agents and context_variables.get("_enable_comment_monitoring"):
                        return SwarmResult(agent=exec_agents["comment_monitor"], context_variables=context_variables)
                    else:
                        # No more agents, return to start
                        return SwarmResult(agent=exec_agents.get("sprint_planning", list(exec_agents.values())[0] if exec_agents else None), context_variables=context_variables)
                
                def exec_update_sprint_retro(retro_summary: str, context_variables: dict) -> SwarmResult:
                    context_variables["sprint_retro"] = retro_summary
                    safe_sidebar_success('✅ Sprint Retro: ' + retro_summary[:100] + "...")
                    # Route to next optional agent
                    if "sprint_report" in exec_agents and context_variables.get("_enable_sprint_report"):
                        return SwarmResult(agent=exec_agents["sprint_report"], context_variables=context_variables)
                    elif "comment_monitor" in exec_agents and context_variables.get("_enable_comment_monitoring"):
                        return SwarmResult(agent=exec_agents["comment_monitor"], context_variables=context_variables)
                    else:
                        # No more agents, return to start
                        return SwarmResult(agent=exec_agents.get("sprint_retro", list(exec_agents.values())[0] if exec_agents else None), context_variables=context_variables)
                
                def exec_update_sprint_report(report_summary: str, context_variables: dict) -> SwarmResult:
                    context_variables["sprint_report"] = report_summary
                    safe_sidebar_success('✅ Sprint Report: ' + report_summary[:100] + "...")
                    # Route to next optional agent
                    if "comment_monitor" in exec_agents and context_variables.get("_enable_comment_monitoring"):
                        return SwarmResult(agent=exec_agents["comment_monitor"], context_variables=context_variables)
                    else:
                        # No more agents, return to start
                        return SwarmResult(agent=exec_agents.get("sprint_report", list(exec_agents.values())[0] if exec_agents else None), context_variables=context_variables)
                
                def exec_update_comment_monitor(monitor_summary: str, context_variables: dict) -> SwarmResult:
                    context_variables["comment_monitor"] = monitor_summary
                    safe_sidebar_success('✅ Comment Monitor: ' + monitor_summary[:100] + "...")
                    # No more agents, return to start
                    return SwarmResult(agent=exec_agents.get("comment_monitor", list(exec_agents.values())[0] if exec_agents else None), context_variables=context_variables)
                
                # Create state_update for execution phase - need to define update_system_message_func for execution phase
                def exec_update_system_message_func(agent: SwarmAgent, messages) -> str:
                    system_prompt = exec_system_messages[agent.name]
                    
                    # Add integration tool information if available
                    jira_tools_available = agent._context_variables.get("_jira_tools") is not None
                    email_tools_available = agent._context_variables.get("_email_tools") is not None
                    confluence_tools_available = agent._context_variables.get("_confluence_tools") is not None
                    
                    if jira_tools_available or email_tools_available or confluence_tools_available:
                        system_prompt += "\n\n**Available Integration Tools:**"
                        if jira_tools_available:
                            jira_project = agent._context_variables.get('_jira_project_key', 'PROJECT')
                            jira_tools = agent._context_variables.get("_jira_tools")
                            system_prompt += f"\n- Jira API: Available for creating/reading/updating stories, epics, releases in project {jira_project}"
                            system_prompt += "\n  * You have direct access to JiraTools instance - use methods like:"
                            system_prompt += "\n    - jira_tools.create_epic(project_key, summary, description, epic_name)"
                            system_prompt += "\n    - jira_tools.create_story(project_key, summary, description, acceptance_criteria, story_points)"
                            system_prompt += "\n    - jira_tools.create_release(project_key, name, description, release_date)"
                            system_prompt += "\n    - jira_tools.create_sprint(board_id, name, start_date, end_date, goal)"
                            system_prompt += "\n    - jira_tools.add_stories_to_sprint(sprint_id, issue_keys)"
                        if email_tools_available:
                            email_tools = agent._context_variables.get("_email_tools")
                            system_prompt += "\n- Email API: Available for sending emails to Slack"
                            system_prompt += "\n  * You have direct access to EmailTools instance - use methods like:"
                            system_prompt += "\n    - email_tools.send_email(to_email, subject, body, html_body)"
                            system_prompt += "\n    - email_tools.send_slack_notification_email(slack_email, subject, jira_project_url, epic_urls, confluence_page_url)"
                        if confluence_tools_available:
                            confluence_space = agent._context_variables.get('_confluence_space', 'SPACE')
                            confluence_tools = agent._context_variables.get("_confluence_tools")
                            system_prompt += f"\n- Confluence API: Available for publishing reports to space {confluence_space}"
                            system_prompt += "\n  * You have direct access to ConfluenceTools instance - use methods like:"
                            system_prompt += "\n    - confluence_tools.create_page(space_key, title, content, parent_id)"
                            system_prompt += "\n    - confluence_tools.publish_product_plan(space_key, plan_title, plan_content, parent_page_id)"
                            system_prompt += "\n    - confluence_tools.publish_report(space_key, report_title, report_content, report_type, parent_page_id)"
                        system_prompt += "\n\n**CRITICAL**: You MUST actually use these tools to create items in Jira and Confluence. Do not just describe what you would do - actually execute the API calls."
                    
                    # Add context variables to the prompt
                    for k, v in agent._context_variables.items():
                        if v is not None and not k.startswith("_"):
                            system_prompt += f"\n{k.capitalize()} Summary:\n{v}"
                    
                    return system_prompt
                
                exec_state_update = UPDATE_SYSTEM_MESSAGE(exec_update_system_message_func)
                
                # Assign functions to execution agents
                # Assign functions and state updates to agents that were created
                if "jira_story_creator" in exec_agents:
                    exec_agents["jira_story_creator"].functions = exec_update_jira_story_creator
                    exec_agents["jira_story_creator"].update_agent_state_before_reply = [exec_state_update]

                if "confluence_publisher" in exec_agents:
                    exec_agents["confluence_publisher"].functions = exec_update_confluence_publisher
                    exec_agents["confluence_publisher"].update_agent_state_before_reply = [exec_state_update]

                if "email_notification" in exec_agents:
                    exec_agents["email_notification"].functions = exec_update_email_notification
                    exec_agents["email_notification"].update_agent_state_before_reply = [exec_state_update]

                if "sprint_setup" in exec_agents:
                    exec_agents["sprint_setup"].functions = exec_update_sprint_setup
                    exec_agents["sprint_setup"].update_agent_state_before_reply = [exec_state_update]

                if "sprint_planning" in exec_agents:
                    exec_agents["sprint_planning"].functions = exec_update_sprint_planning
                    exec_agents["sprint_planning"].update_agent_state_before_reply = [exec_state_update]

                if "sprint_retro" in exec_agents:
                    exec_agents["sprint_retro"].functions = exec_update_sprint_retro
                    exec_agents["sprint_retro"].update_agent_state_before_reply = [exec_state_update]

                if "sprint_report" in exec_agents:
                    exec_agents["sprint_report"].functions = exec_update_sprint_report
                    exec_agents["sprint_report"].update_agent_state_before_reply = [exec_state_update]

                if "comment_monitor" in exec_agents:
                    exec_agents["comment_monitor"].functions = exec_update_comment_monitor
                    exec_agents["comment_monitor"].update_agent_state_before_reply = [exec_state_update]
                
                # Build execution agent list for swarm chat (convert dict to list)
                exec_agents_list = list(exec_agents.values())
                
                # Determine initial agent based on what's being published
                initial_exec_agent = None
                if publish_jira and "jira_story_creator" in exec_agents:
                    initial_exec_agent = exec_agents["jira_story_creator"]
                elif publish_confluence and "confluence_publisher" in exec_agents:
                    initial_exec_agent = exec_agents["confluence_publisher"]
                elif exec_agents_list:
                    initial_exec_agent = exec_agents_list[0]
                
                # Start execution phase
                if exec_agents_list and initial_exec_agent:
                    exec_result, _, _ = initiate_swarm_chat(
                        initial_agent=initial_exec_agent,
                        agents=exec_agents_list,
                        user_agent=None,
                        messages=execution_task,
                        max_rounds=15,
                    )
                    
                    # Extract execution phase outputs
                    exec_chat_history = exec_result.chat_history
                    exec_output_map = {
                        'jira_story_creator_agent': 'jira_story_creator',
                        'confluence_publisher_agent': 'confluence_publisher',
                        'email_notification_agent': 'email_notification',
                        'sprint_setup_agent': 'sprint_setup',
                        'sprint_planning_agent': 'sprint_planning',
                        'sprint_retro_agent': 'sprint_retro',
                        'sprint_report_agent': 'sprint_report',
                        'comment_monitor_agent': 'comment_monitor'
                    }
                    
                    exec_agent_last_message = {}
                    for msg in exec_chat_history:
                        if isinstance(msg, dict):
                            agent_name = msg.get('name', '')
                            if agent_name in exec_output_map:
                                exec_agent_last_message[agent_name] = msg.get('content', str(msg))
                        elif hasattr(msg, 'name'):
                            agent_name = msg.name
                            if agent_name in exec_output_map:
                                exec_agent_last_message[agent_name] = msg.content if hasattr(msg, 'content') else str(msg)
                    
                    # Update outputs
                    for agent_name, output_key in exec_output_map.items():
                        if agent_name in exec_agent_last_message:
                            st.session_state.pm_output[output_key] = exec_agent_last_message[agent_name]
                    
                    st.session_state.execution_phase_complete = True
                    
                    # Save execution results to database
                    if db_manager:
                        try:
                            plan_id = st.session_state.current_plan_id
                            version = st.session_state.current_plan_version
                            
                            # Save execution phase agent outputs
                            for agent_name, output_key in exec_output_map.items():
                                if output_key in st.session_state.pm_output:
                                    db_manager.save_agent_output(
                                        plan_id=plan_id,
                                        version=version,
                                        agent_name=agent_name,
                                        output_content=st.session_state.pm_output[output_key],
                                        metadata={'phase': 'execution'}
                                    )
                            
                            # Update plan status
                            plan = db_manager.get_product_plan(plan_id, version)
                            if plan:
                                db_manager.save_product_plan(
                                    plan_id=plan_id,
                                    product_name=product_name,
                                    plan_data=st.session_state.pm_output,
                                    configuration=plan['configuration'],
                                    status='published',
                                    created_by='user'
                                )
                            
                            logger.info(f"Execution phase saved to database: {plan_id} v{version}")
                        except Exception as e:
                            logger.error(f"Error saving execution results: {e}")
                    
                    # Success message based on what was published
                    success_msg = "✅ Content published successfully!"
                    if publish_jira and publish_confluence:
                        success_msg = "✅ Content published to Jira and Confluence successfully!"
                    elif publish_jira:
                        success_msg = "✅ Content published to Jira successfully!"
                    elif publish_confluence:
                        success_msg = "✅ Content published to Confluence successfully!"
                    st.success(success_msg)
                    safe_rerun()
                else:
                    if not exec_agents_list:
                        st.warning("⚠️ No agents available. Please configure Jira and/or Confluence in the sidebar.")
                    elif not initial_exec_agent:
                        st.warning("⚠️ Could not determine initial agent. Please check your configuration.")

        # Add download option
        plan_content = f"""# Product Management Plan for {product_name}

{st.session_state.pm_output['strategy']}

{st.session_state.pm_output['research']}

{st.session_state.pm_output['roadmap']}

{st.session_state.pm_output['metrics']}

{st.session_state.pm_output['stakeholder']}

{st.session_state.pm_output['execution']}
"""
        
        # Add new workflow reports if available
        if st.session_state.pm_output.get('jira_story_creator'):
            plan_content += f"\n## Jira Story Creation\n{st.session_state.pm_output['jira_story_creator']}\n"
        if st.session_state.pm_output.get('confluence_publisher'):
            plan_content += f"\n## Confluence Publishing\n{st.session_state.pm_output['confluence_publisher']}\n"
        if st.session_state.pm_output.get('email_notification'):
            plan_content += f"\n## Email Notification\n{st.session_state.pm_output['email_notification']}\n"
        if st.session_state.pm_output.get('sprint_setup'):
            plan_content += f"\n## Sprint Setup\n{st.session_state.pm_output['sprint_setup']}\n"
        if st.session_state.pm_output.get('sprint_planning'):
            plan_content += f"\n## Sprint Planning\n{st.session_state.pm_output['sprint_planning']}\n"
        if st.session_state.pm_output.get('sprint_retro'):
            plan_content += f"\n## Sprint Retro\n{st.session_state.pm_output['sprint_retro']}\n"
        if st.session_state.pm_output.get('sprint_report'):
            plan_content += f"\n## Sprint Report\n{st.session_state.pm_output['sprint_report']}\n"
        if st.session_state.pm_output.get('comment_monitor'):
            plan_content += f"\n## Comment Monitor\n{st.session_state.pm_output['comment_monitor']}\n"
        
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="📥 Download Complete Plan",
                data=plan_content,
                file_name=f"{product_name.replace(' ', '_')}_PM_Plan.md",
                mime="text/markdown"
            )
        with col2:
            if db_manager and st.session_state.current_plan_id:
                if st.button("🗑️ Delete Plan", key="delete_plan"):
                    try:
                        db_manager.delete_plan(st.session_state.current_plan_id)
                        st.success("Plan deleted successfully")
                        st.session_state.current_plan_id = None
                        st.session_state.current_plan_version = None
                        st.session_state.planning_complete = False
                        safe_rerun()
                    except Exception as e:
                        st.error(f"Error deleting plan: {e}")
        
        # Show database statistics if available
        if db_manager:
            st.markdown("---")
            with st.expander("📊 Database Statistics"):
                try:
                    all_plans = db_manager.list_product_plans(limit=100)
                    st.metric("Total Plans", len(all_plans))
                    
                    if st.session_state.current_plan_id:
                        versions = db_manager.get_plan_versions(st.session_state.current_plan_id)
                        st.metric("Versions of Current Plan", len(versions))
                        
                        jira_items = db_manager.get_jira_items(
                            st.session_state.current_plan_id,
                            st.session_state.current_plan_version or 1
                        )
                        st.metric("Jira Items Created", len(jira_items))
                        
                        confluence_pages = db_manager.get_confluence_pages(
                            st.session_state.current_plan_id,
                            st.session_state.current_plan_version or 1
                        )
                        st.metric("Confluence Pages", len(confluence_pages))
                except Exception as e:
                    st.error(f"Error loading statistics: {e}")

