# 🚀 Agentic Product Manager Journey

The Agentic Product Manager Journey is a comprehensive AI-powered product management system built with [AG2](https://github.com/ag2ai/ag2?tab=readme-ov-file) (formerly AutoGen)'s AI Agent framework. This system provides end-to-end product management guidance through the coordination of specialized AI agents with full integration support for Jira, GitHub, Slack, Zoom, and Confluence.

## ✨ Key Features

- **Natural Language Content**: All Jira stories, epics, and acceptance criteria are written in natural, conversational language - not AI-generated sounding content
- **Jira Story Creation**: Automatically create epics, stories, and releases from product strategy with well-defined acceptance criteria
- **Sprint Configuration**: Configure Jira for sprint planning, grooming, retrospectives, releases, and reporting
- **Confluence Integration**: Publish all reports and documents to a dedicated Confluence wiki space
- **Email-based Slack Access**: Use Slack channel email instead of bot tokens for easier setup
- **Multi-Agent Collaboration**: Specialized agents work together to create comprehensive PM plans
- **Enterprise-Ready**: Full database persistence, historical context tracking, and robust error handling

## 🏢 Enterprise Features

### Database Persistence
- **SQLite Database**: All product plans, configurations, and agent outputs are stored in a persistent SQLite database
- **Version Control**: Complete version history for all product plans
- **Historical Context**: View and restore any previous plan generation
- **Data Integrity**: ACID-compliant transactions with foreign key constraints
- **Concurrent Access**: WAL (Write-Ahead Logging) mode for better multi-user support
- **Automatic Retries**: Built-in retry logic for database operations on lock errors

### Historical Plan Management
- **Load Previous Plans**: Browse and load any previously generated plan from the sidebar
- **Version Selection**: View all versions of a plan and select specific versions
- **Plan Restoration**: Restore complete plan data including configurations and agent outputs
- **Plan Comparison**: Compare different versions of the same plan
- **Save Drafts**: Save work-in-progress plans before completion
- **Create New Versions**: Create new versions based on existing plans

### Enterprise-Ready Features
- **Comprehensive Logging**: File (`agentic_pm.log`) and console logging for all operations
- **Error Handling**: Robust error handling with automatic retry logic for database operations
- **Connection Pooling**: Efficient database connection management with 30-second timeout
- **Transaction Safety**: Automatic rollback on errors to maintain data integrity
- **ScriptRunContext Fix**: Proper handling of Streamlit context warnings
- **Graceful Degradation**: System continues to work even if database fails

### Database Schema

The database includes the following tables:
- `product_plans` - Main product plan records with versioning
- `plan_versions` - Version history for plans
- `agent_outputs` - Individual agent outputs linked to plans
- `jira_items` - Jira item references (epics, stories, releases)
- `confluence_pages` - Confluence page references
- `sprints` - Sprint information and configurations
- `configurations` - Saved integration configurations
- `async_operations` - Async operation tracking
- `execution_history` - Execution phase history

### Database Location

The database is automatically created at:
```
advanced_ai_agents/multi_agent_apps/agentic_pm/databases/agentic_pm.db
```

**Note**: Back up this file regularly as it contains all your product management data.

## 🔌 Integration Capabilities

This system includes comprehensive integrations for:

- **📋 Jira**: Create, read, update, and comment on stories, epics, and releases. Automatically sync GitHub commits with Jira stories. Create well-defined stories from product strategy with natural language.
- **🐙 GitHub**: Track commits, extract Jira references, monitor developer activity, and sync with Jira.
- **💬 Slack**: Send messages, DMs, interactive notifications, and coordinate team communication via email-based channel access.
- **📹 Zoom**: Schedule and manage Daily Scrum Meetings (DSM) across timezones with automatic invites.
- **📚 Confluence**: Publish all product management reports, plans, and documents to dedicated Confluence wiki spaces.

## 🎯 Multi-Agent Automation Framework

Based on the Multi-Agent Automation Framework for Sprint and Update Management, this system automates:
- Developer status tracking and commit synchronization
- Jira story updates based on real-time GitHub activity
- DSM preparation and coordination across distributed teams
- Story quality validation and acceptance criteria review

## Features

### Specialized Product Management Agent Team

**Core PM Agents:**
- 🎯 **Strategy Agent**: Defines product vision, market positioning, strategic direction, and go-to-market strategy
- 🔍 **Research Agent**: Conducts user research, competitive analysis, market insights, and validates product assumptions
- 🗺️ **Roadmap Agent**: Creates prioritized roadmaps, feature planning, release strategies, and MVP scoping
- 📊 **Metrics Agent**: Defines KPIs, success metrics, analytics frameworks, and measurement plans
- 🤝 **Stakeholder Agent**: Manages communication, alignment, stakeholder relationships, and cross-functional collaboration
- ⚡ **Execution Agent**: Plans sprints, manages delivery, implements agile practices, and ensures quality delivery

**Integration & Automation Agents:**
- 🔗 **GitHub Integration Agent**: Automates commit tracking, identifies users with open stories, extracts Jira references from commits, and syncs GitHub activity with Jira stories
- 📅 **DSM Scheduler Agent**: Orchestrates Daily Scrum Meetings across timezones using Slack user profiles and Zoom API for optimal scheduling
- ✅ **Jira Validation Agent**: Reviews all open Jira stories for proper definition, validates acceptance criteria, flags incomplete stories, and suggests improvements
- 🎯 **Quality Validation Agent**: Reviews updated Jira stories post-commit, evaluates acceptance criteria completion, and provides quality recommendations via Slack
- 📋 **Jira Story Creator Agent**: Creates well-defined epics, stories, and releases from product strategy with natural, easy-to-understand language (not AI-generated sounding)
- 📚 **Confluence Publisher Agent**: Publishes all product management reports, plans, and documents to dedicated Confluence wiki spaces

### Comprehensive Product Management Outputs

- **Strategic Planning**: Product vision, market positioning, competitive strategy, and business alignment
- **Research Insights**: User personas, competitive analysis, market opportunities, and validation strategies
- **Product Roadmap**: Prioritized features, release planning, milestone tracking, and phased rollouts
- **Metrics Framework**: North Star metrics, KPIs, analytics tracking, and success measurement
- **Stakeholder Management**: Communication plans, alignment strategies, and relationship management
- **Execution Plan**: Sprint planning, agile frameworks, backlog management, and delivery coordination

### Customizable Input Parameters

- Product type and target market
- Product stage and business model
- User personas and industry context
- Product goals and constraints
- Competitive landscape and unique value proposition
- Success criteria and timeline focus

### Interactive Results

- Real-time collaboration updates from each agent
- Detailed plans presented in expandable sections
- Downloadable comprehensive product management plan
- Sidebar progress tracking for each agent's contribution

## How to Run

Follow these steps to set up and run the application:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Shubhamsaboo/awesome-llm-apps.git
   cd advanced_ai_agents/multi_agent_apps/agentic_pm
   ```

2. **Create and Activate Virtual Environment** (Recommended):
   ```bash
   # Create virtual environment
   python3 -m venv agentic_pm
   
   # Activate virtual environment
   # On macOS/Linux:
   source agentic_pm/bin/activate
   # On Windows:
   # agentic_pm\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   
   **Important**: The application requires `pyautogen` version 0.2.x to 0.4.x (SwarmAgent is available in these versions).
   
   If you encounter import errors:
   
   ```bash
   # Make sure you're in your virtual environment, then:
   pip install "pyautogen>=0.2,<0.5" streamlit==1.41.1 requests python-dateutil
   
   # Verify installation
   pip show pyautogen
   ```
   
   **Troubleshooting Import Errors**:
   
   If you get `ImportError: cannot import name 'SwarmAgent'`:
   
   1. Check your pyautogen version (must be 0.2.x - 0.4.x):
      ```bash
      pip show pyautogen
      ```
   
   2. Install the correct version:
      ```bash
      pip install "pyautogen>=0.2,<0.5"
      ```
   
   3. Note: Versions 0.5+ of pyautogen use a different API and don't include SwarmAgent.

4. **Database Setup** (Automatic):
   
   The database is automatically created and initialized on first run. No manual setup is required.
   
   **What happens automatically**:
   - The `databases/` directory is created in the project folder
   - SQLite database file `agentic_pm.db` is created automatically
   - All required tables are initialized with proper schema
   - Database uses WAL (Write-Ahead Logging) mode for better concurrency
   
   **Database Location**:
   ```
   advanced_ai_agents/multi_agent_apps/agentic_pm/databases/agentic_pm.db
   ```
   
   **Manual Database Reset** (if needed):
   If you need to reset the database, simply delete the database file:
   ```bash
   # From the agentic_pm directory
   rm databases/agentic_pm.db
   # The database will be recreated automatically on next run
   ```
   
   **Database Backup** (Recommended):
   It's recommended to back up your database regularly:
   ```bash
   # Create a backup
   cp databases/agentic_pm.db databases/agentic_pm_backup_$(date +%Y%m%d).db
   ```

5. **Configure Integration Credentials** (Optional but Recommended):
   
   You can configure integrations either via:
   
   **Option A: Environment Variables** (Recommended for production):
   ```bash
   # Jira
   export JIRA_URL="https://yourcompany.atlassian.net"
   export JIRA_EMAIL="your-email@company.com"
   export JIRA_API_TOKEN="your-jira-api-token"
   export JIRA_PROJECT_KEY="PROJ"  # Project key where stories will be created
   export JIRA_BOARD_ID="123"  # Board ID for sprint management
   
   # GitHub
   export GITHUB_TOKEN="your-github-token"
   export GITHUB_OWNER="your-org-or-username"
   export GITHUB_REPO="your-repo-name"
   
   # Slack (Email-based access)
   export SLACK_EMAIL="your-email@company.com"  # Email for Slack channel
   export SLACK_CHANNEL="product-team"  # Channel name (e.g., #product-team)
   
   # Zoom
   export ZOOM_ACCOUNT_ID="your-zoom-account-id"
   export ZOOM_CLIENT_ID="your-zoom-client-id"
   export ZOOM_CLIENT_SECRET="your-zoom-client-secret"
   
   # Confluence
   export CONFLUENCE_URL="https://yourcompany.atlassian.net/wiki"
   export CONFLUENCE_EMAIL="your-email@company.com"
   export CONFLUENCE_API_TOKEN="your-confluence-api-token"
   export CONFLUENCE_SPACE="PM"  # Space key where reports will be published
   ```
   
   **Option B: UI Configuration**:
   - Enter credentials directly in the Streamlit sidebar when running the app
   - Credentials are stored in session state (not persisted)
   
   **Getting API Tokens**:
   - **Jira**: [Atlassian Account Settings > Security > API Tokens](https://id.atlassian.com/manage-profile/security/api-tokens)
   - **GitHub**: [GitHub Settings > Developer Settings > Personal Access Tokens](https://github.com/settings/tokens)
   - **Slack**: Use your Slack workspace email address and channel name (no bot token required for email-based access)
   - **Zoom**: [Zoom Marketplace > Create App > OAuth](https://marketplace.zoom.us/develop/create)
   - **Confluence**: [Atlassian Account Settings > Security > API Tokens](https://id.atlassian.com/manage-profile/security/api-tokens) (same as Jira)

6. **Set Up OpenAI API Key**:
   - Obtain an OpenAI API key from [OpenAI's platform](https://platform.openai.com)
   - You'll input this key in the app's sidebar when running

7. **Run the Streamlit App**:
   ```bash
   streamlit run agentic_pm_agent.py
   ```
   
   **First Run**:
   - The database will be automatically created and initialized
   - You'll see a log message: `Database initialized successfully`
   - The `databases/` directory will be created if it doesn't exist
   - All tables will be set up with proper schema and indexes
   
   **Subsequent Runs**:
   - The database will be reused (all your plans and history are preserved)
   - You can load previous plans from the sidebar
   - All agent outputs and configurations are stored persistently

## Usage

1. **Enter your OpenAI API key** in the sidebar
2. **Database is ready** - The database is automatically initialized on first run. You can:
   - View all previous plans in the sidebar under "Historical Plans"
   - Load any previous plan to continue working on it
   - Create new versions of existing plans
   - Delete plans you no longer need
3. **Configure integrations** (optional but recommended):
   - Enter Jira credentials (URL, email, API token, project key, board ID)
   - Configure Jira sprint activities (planning, grooming, retro, releases, reporting)
   - Enable "Create Jira Items from Strategy" to automatically create epics, stories, and releases
   - Enter GitHub token, owner, and repository
   - Enter Slack email and channel name (email-based access, no bot token required)
   - Enter Zoom credentials (Account ID, Client ID, Client Secret)
   - Enter Confluence credentials (URL, email, API token, space key)
4. **Fill in the product information**:
   - Product name, type, target market, and stage
   - Industry, user persona, business model, and timeline
5. **Provide product goals and context**:
   - Primary goals and key features
   - Constraints and competitors
   - Unique value proposition and success criteria
6. **Select detail level** (Low, Medium, or High)
7. **Click "Generate Product Management Plan"** to receive comprehensive guidance from all agents
   - The plan is automatically saved to the database after the planning phase
   - You can save drafts at any time using the "Save Draft" button
8. **Review the outputs** in expandable sections:
   - Core PM plans (Strategy, Research, Roadmap, Metrics, Stakeholder, Execution)
   - Integration reports (GitHub Integration, DSM Scheduler, Jira Validation, Quality Validation, Jira Story Creator, Confluence Publisher) - shown if integrations are configured
9. **Confirm and publish** (if integrations are configured):
   - Review the generated plan
   - Click "Confirm & Publish to Jira & Confluence" to execute the publishing phase
   - All Jira items, Confluence pages, and execution history are saved to the database
10. **Manage your plans**:
    - View all versions of a plan using "View All Versions"
    - Create new versions based on existing plans
    - Load previous plans from the sidebar
    - Download the complete plan as a markdown file

## Integration Features

### Jira Integration
- **Create Stories/Epics/Releases**: Automatically create Jira issues from roadmap planning with natural, easy-to-understand descriptions
- **Natural Language Content**: All stories and acceptance criteria written in conversational language (not AI-generated sounding)
- **Read Story Contents**: Retrieve and analyze existing stories, epics, and releases
- **Update Story Scope**: Modify story descriptions, summaries, and fields
- **Add Comments**: Post updates and feedback directly to Jira stories
- **Sprint Management**: Get stories in active sprints, create sprints, and track progress
- **JQL Search**: Search stories using Jira Query Language
- **Sprint Configuration**: Configure sprint planning, grooming, retrospectives, release planning, and reporting
- **Link Stories to Epics**: Automatically link stories to epics and assign to releases

### GitHub Integration
- **Commit Tracking**: Monitor recent commits from your repository
- **Jira Reference Extraction**: Automatically extract Jira issue keys (e.g., PROJ-123) from commit messages
- **Developer Activity**: Track commits by specific users
- **Commit Details**: Get detailed information about commits including changes, authors, timestamps
- **Auto-Sync with Jira**: Update Jira stories with commit details and links

### Slack Integration
- **Email-based Access**: Use Slack channel email instead of bot tokens for easier setup
- **Channel Messages**: Send messages to Slack channels via email
- **Direct Messages**: Send DMs to team members via email
- **Interactive Messages**: Create messages with buttons for DSM participation
- **Channel Information**: Get channel details and contact information
- **Note**: Uses email-based access for channel communication. For full API functionality, consider using Slack webhooks or bot tokens

### Zoom Integration
- **Meeting Creation**: Automatically create Zoom meetings for DSM
- **Timezone Coordination**: Schedule meetings at optimal times for distributed teams
- **Meeting Invites**: Send invites to participants via email
- **Meeting Updates**: Modify meeting details (time, duration, agenda)

### Confluence Integration
- **Publish Reports**: Publish product management plans, sprint reports, retrospectives, and release plans to Confluence
- **Wiki Pages**: Create well-structured wiki pages with proper formatting
- **Index Pages**: Create index pages linking to all published reports
- **Space Organization**: Organize content in dedicated Confluence spaces
- **Content Formatting**: Format content for readability in Confluence wiki format
- **Version Management**: Maintain version history and document structure

## Agent Responsibilities

### GitHub Integration Agent
- Connects to GitHub API to retrieve recent commits
- Identifies users with open stories in active sprint (via Jira)
- Extracts Jira reference IDs from commit messages
- Automatically updates corresponding Jira stories with commit details
- Generates structured update messages for DSM Scheduler

### DSM Scheduler Agent
- Consumes data from GitHub Integration Agent
- Uses Slack user profiles and timezone metadata
- Schedules DSM meetings via Zoom API at optimal times
- Manages meeting timing, reminders, and coordination
- Sends meeting invites via Slack and Zoom

### Jira Validation Agent
- Reviews all open Jira stories for proper definition
- Validates acceptance criteria (AC) completeness
- Flags stories that are poorly defined or incomplete
- Suggests improvements via Slack
- Ensures backlog readiness

### Quality Validation Agent
- Reviews updated Jira stories post-commit or post-DSM
- Evaluates acceptance criteria completion
- Assesses if commits align with story requirements
- Provides quality recommendations via Slack
- Generates quality reports

### Jira Story Creator Agent
- Analyzes product strategy document and roadmap to identify epics, stories, and releases
- Creates natural, easy-to-understand story descriptions (not AI-generated sounding)
- Defines clear, testable acceptance criteria in plain language
- Breaks down epics into logical, implementable stories
- Creates release plans with realistic timelines
- Links stories to epics and assigns to appropriate releases
- **Critical**: Writes all content in natural, conversational language as if explaining to a developer

### Confluence Publisher Agent
- Formats product management plans, reports, and documents for Confluence
- Creates well-structured wiki pages with proper headings and formatting
- Publishes sprint planning reports, retrospectives, and release plans
- Creates index pages linking to all published reports
- Organizes content in dedicated Confluence spaces
- Ensures documents are easily discoverable and well-organized

## Example Use Cases

### Scenario 1: New Product Launch
```
Product: SaaS Platform for Project Management
Stage: MVP/Validation
Goal: Validate product-market fit with early adopters
```
→ Agents collaborate to create strategy, research plan, MVP roadmap, metrics, stakeholder alignment, and execution plan

### Scenario 2: Product Growth Phase
```
Product: Mobile App
Stage: Growth
Goal: Scale user base and increase engagement
```
→ Agents provide growth strategy, user research insights, feature prioritization, growth metrics, stakeholder communication, and scaling execution

### Scenario 3: Product Pivot
```
Product: Enterprise Software
Stage: Pivot
Goal: Reposition product for new market segment
```
→ Agents help with strategic repositioning, market research, new roadmap, pivot metrics, stakeholder buy-in, and transition execution

## Agent Collaboration Flow

The system uses AG2's swarm feature to enable sequential collaboration:

```
Strategy Agent → Research Agent → Roadmap Agent → 
Metrics Agent → Stakeholder Agent → Execution Agent → Strategy Agent (refinement)
```

Each agent:
1. First provides a brief summary of their approach
2. Reviews context from previous agents
3. Generates detailed plan for their domain
4. Passes context to the next agent

This ensures cohesive, integrated product management guidance across all domains.

## Multi-Agent Pattern

This system demonstrates **Sequential Swarm Collaboration**:

```
Initial Agent (Strategy)
    ↓
Research Agent (uses Strategy context)
    ↓
Roadmap Agent (uses Strategy + Research context)
    ↓
Metrics Agent (uses all previous context)
    ↓
Stakeholder Agent (uses all previous context)
    ↓
Execution Agent (uses all previous context)
    ↓
Strategy Agent (refinement with full context)
```

**Why this pattern?**
- **Comprehensive**: Covers entire product management journey
- **Contextual**: Each agent builds on previous insights
- **Collaborative**: Agents work together for cohesive output
- **Scalable**: Easy to add new specialized agents
- **Production-ready**: Real-world product management workflow

## Key Capabilities

### Strategy Agent
- Product vision and mission definition
- Market positioning and competitive analysis
- Strategic initiatives and long-term direction
- Go-to-market strategy
- Business model alignment

### Research Agent
- User research methodology
- Persona development and user needs analysis
- Competitive analysis and market research
- User feedback analysis
- Market opportunity identification

### Roadmap Agent
- Feature prioritization (RICE, MoSCoW, Value vs Effort)
- Release planning and milestones
- MVP scoping and phased rollouts
- Dependency management
- Quarterly/quarterly roadmap breakdown

### Metrics Agent
- North Star metric definition
- KPI framework (AARRR, HEART, etc.)
- Analytics tracking and measurement
- Success criteria definition
- Dashboard and reporting structure

### Stakeholder Agent
- Stakeholder identification and mapping
- Communication plans and cadence
- Alignment strategies
- Product reviews and demos
- Cross-functional collaboration

### Execution Agent
- Sprint planning and agile frameworks
- User stories and acceptance criteria
- Release cycles and deployment
- Backlog management
- Quality assurance and delivery

## Technical Details

- **Framework**: AG2 (AutoGen) Swarm
- **UI**: Streamlit
- **LLM**: OpenAI GPT-4o-mini (configurable)
- **Pattern**: Sequential Swarm Collaboration
- **Output Format**: Markdown (downloadable)
- **Database**: SQLite with WAL mode for concurrency
- **Persistence**: Full database persistence with versioning

## 🔧 Enterprise Configuration

### Logging

The system logs all operations to:
- **Console**: Real-time logging during execution
- **File**: `agentic_pm.log` in the project directory

Log levels can be configured in `agentic_pm_agent.py`:
```python
logging.basicConfig(
    level=logging.INFO,  # Change to DEBUG for more details
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('agentic_pm.log'),
        logging.StreamHandler()
    ]
)
```

### Database Configuration

The database is automatically initialized on first run. To customize:

1. **Database Location**: Modify `DB_PATH` in `database.py`
2. **Connection Timeout**: Adjust `timeout` in `get_db_connection()` (default: 30 seconds)
3. **Retry Logic**: Configure `max_retries` and `delay` in `@retry_db_operation` decorator

### Error Handling

The system includes:
- **Automatic Retries**: Database operations retry up to 3 times on lock errors
- **Transaction Safety**: Automatic rollback on errors
- **Graceful Degradation**: System continues to work even if database fails
- **Error Logging**: All errors are logged for debugging

## ⚠️ Common Issues

### ScriptRunContext Warning

If you see the warning: `missing ScriptRunContext! This warning can be ignored when running in bare mode.`

**Solution**: This warning has been fixed in the code. The system now safely handles Streamlit context issues. If you still see it:
1. Ensure you're using the latest version of the code
2. The warning is harmless and can be ignored
3. All functionality works correctly despite the warning

### Database Lock Errors

If you encounter database lock errors:
1. The system automatically retries operations up to 3 times
2. Ensure only one instance of the app is running
3. Check file permissions on the database directory
4. The database uses WAL mode for better concurrency

### Import Errors

If you see import errors for `autogen`:
1. Ensure you're using the correct version: `pip install "pyautogen>=0.2,<0.5"`
2. Activate your virtual environment before running
3. Check that all dependencies are installed: `pip install -r requirements.txt`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is part of the awesome-llm-apps repository.

## Acknowledgments

Built using [AG2](https://github.com/ag2ai/ag2) (formerly AutoGen) framework for multi-agent collaboration.

