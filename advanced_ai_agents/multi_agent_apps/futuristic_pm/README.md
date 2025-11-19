# 🚀 FuturisticPM - Next-Generation AI Product Management System

**FuturisticPM** is a comprehensive, enterprise-ready AI-powered product management platform built from the ground up with full database persistence, rich multi-step workflow UI, and complete integration support for Jira, GitHub, Slack, and Confluence.

## ✨ Key Features

### 🎯 Multi-Step Workflow UI
- **9-Step Guided Workflow**: Configuration → Product Info → Strategy → Research → Roadmap → Metrics → Stakeholder → Execution → Publish
- **Visual Progress Indicator**: Beautiful step-by-step progress tracking with status indicators
- **Step-by-Step Navigation**: Navigate forward and backward through the workflow
- **Individual Step Completion**: Complete each step independently with regeneration options
- **Rich UI Components**: Modern, intuitive interface with expandable sections and clear feedback

### 🏢 Enterprise Features
- **Full Database Persistence**: SQLite database with complete versioning and history tracking
- **Workflow Step Tracking**: Track completion status of each workflow step
- **Historical Plan Management**: Load, view, and restore previous plans
- **Version Control**: Complete version history for all product plans
- **Data Integrity**: ACID-compliant transactions with foreign key constraints
- **Concurrent Access**: WAL (Write-Ahead Logging) mode for better multi-user support
- **Automatic Retries**: Built-in retry logic for database operations

### 🤖 Complete Agent System
**Core PM Agents:**
- 🎯 **Strategy Agent**: Product vision, market positioning, strategic direction
- 🔍 **Research Agent**: User research, competitive analysis, market insights
- 🗺️ **Roadmap Agent**: Feature prioritization, release planning, MVP scoping
- 📊 **Metrics Agent**: KPIs, success metrics, analytics frameworks
- 🤝 **Stakeholder Agent**: Communication plans, alignment strategies
- ⚡ **Execution Agent**: Sprint planning, agile frameworks, delivery coordination

**Integration Agents:**
- 📋 **Jira Story Creator Agent**: Creates epics, stories, releases with natural language
- 📚 **Confluence Publisher Agent**: Publishes all documents with nested structure
- 📧 **Email Notification Agent**: Sends notifications to Slack with links
- 🏃 **Sprint Setup Agent**: Creates sprints with capacity management

### 🔌 Complete Integration Support

**MCP (Model Context Protocol) Integrations** (Preferred):
- **📋 Jira/Confluence**: Via Atlassian MCP server (with direct API fallback)
- **🐙 GitHub**: Official GitHub MCP server (`@modelcontextprotocol/server-github`)
- **💬 Slack**: Slack MCP server (`@modelcontextprotocol/server-slack`)
- **🤖 Amazon Q Developer**: Amazon Q MCP server for AI-powered assistance
- **🔧 Extensible**: Support for custom MCP servers (Notion, Perplexity, Calendar, etc.)

**Direct API Integrations** (Fallback):
- **📋 Jira**: Create, read, update stories, epics, releases, sprints
- **📚 Confluence**: Publish reports, documents, create nested structures
- **🐙 GitHub**: Track commits, extract Jira references, sync with Jira
- **💬 Slack**: Email-based channel access for notifications
- **📧 Email (SMTP)**: Send emails to Slack channels and team members

**Note**: The system automatically uses MCP integrations when available, falling back to direct API implementations for compatibility.

## 🚀 Quick Start

### 1. Clone and Navigate
```bash
git clone https://github.com/Shubhamsaboo/awesome-llm-apps.git
cd advanced_ai_agents/multi_agent_apps/futuristic_pm
```

### 2. Create Virtual Environment
```bash
python3 -m venv futuristic_pm_venv
source futuristic_pm_venv/bin/activate  # On Windows: futuristic_pm_venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

**Important**: Requires `pyautogen` version 0.2.x to 0.4.x:
```bash
pip install "pyautogen>=0.2,<0.5"
```

**Node.js Required for MCP Servers**:
MCP (Model Context Protocol) servers run via Node.js. Ensure Node.js is installed:
```bash
# Check if Node.js is installed
node --version
npm --version

# If not installed, download from https://nodejs.org/
# MCP servers will be automatically installed via npx when first used
```

### 4. Database Setup (Automatic)
The database is automatically created on first run at:
```
futuristic_pm/databases/futuristic_pm.db
```

### 5. Run the Application
```bash
streamlit run futuristic_pm.py
```

## 📖 Usage Guide

### Step-by-Step Workflow

1. **⚙️ Configuration (Step 1)**
   - Enter OpenAI API Key (required)
   - Configure Jira integration (optional) - Uses MCP if available
   - Configure Confluence integration (optional) - Uses MCP if available
   - Configure GitHub integration (optional) - Uses MCP server
   - Configure Slack integration (optional) - Supports MCP with bot token
   - Configure Amazon Q Developer (optional) - MCP integration
   - Configure Email (SMTP) (optional)
   - Set sprint configuration (team size, story points, duration)
   - Click "Save Configuration & Continue"
   
   **MCP Integration Note**: When MCP servers are configured, the system will automatically use them. If MCP is unavailable, it falls back to direct API implementations.

2. **📝 Product Info (Step 2)**
   - Enter product name, type, target market, stage
   - Provide industry, user persona, business model
   - Define goals, features, constraints, competitors
   - Set value proposition and success criteria
   - Select detail level (Low, Medium, High)
   - Click "Save Product Info & Continue"

3. **🎯 Strategy (Step 3)**
   - Click "Generate Strategy" to create product strategy
   - Review the generated strategy
   - Option to regenerate if needed
   - Click "Next Step" when satisfied

4. **🔍 Research (Step 4)**
   - Click "Generate Research" for comprehensive research
   - Includes user research, competitive analysis, market insights
   - Review and proceed to next step

5. **🗺️ Roadmap (Step 5)**
   - Click "Generate Roadmap" for prioritized roadmap
   - Includes feature prioritization, release planning, MVP scoping
   - Review and proceed

6. **📊 Metrics (Step 6)**
   - Click "Generate Metrics Framework"
   - Defines KPIs, success metrics, analytics tracking
   - Review and proceed

7. **🤝 Stakeholder (Step 7)**
   - Click "Generate Stakeholder Plan"
   - Creates communication plans and alignment strategies
   - Review and proceed

8. **⚡ Execution (Step 8)**
   - Click "Generate Execution Plan"
   - Creates sprint planning and agile frameworks
   - Review and proceed

9. **🚀 Publish (Step 9)**
   - Review complete plan summary
   - Choose publishing options:
     - **📋 Publish to Jira**: Create epics, stories, releases, sprints
     - **📚 Publish to Confluence**: Publish all documents
     - **🚀 Publish All**: Both Jira and Confluence + email notification
   - Save plan to database
   - Complete the workflow

### Navigation
- Use "← Previous Step" and "Next Step →" buttons to navigate
- Each step can be completed independently
- Completed steps show ✅ status
- Current step shows 🔄 status
- Pending steps show ⏳ status

## 🗄️ Database Features

### Automatic Persistence
- All plans are automatically saved to the database
- Each agent output is stored with metadata
- Workflow step status is tracked
- Complete version history maintained

### Plan Management
- **Load Previous Plans**: Use sidebar to load any previous plan
- **Version History**: View all versions of a plan
- **Restore Plans**: Restore complete plan data and configuration
- **Save Drafts**: Save work-in-progress at any step

### Database Schema
- `product_plans`: Main plan records
- `plan_versions`: Version history
- `agent_outputs`: Individual agent outputs
- `jira_items`: Jira item references
- `confluence_pages`: Confluence page references
- `sprints`: Sprint information
- `workflow_steps`: Workflow step tracking
- `async_operations`: Async operation tracking

## 🔧 Configuration

### Environment Variables (Optional)
```bash
# OpenAI
export OPENAI_API_KEY="your-key"

# Jira
export JIRA_URL="https://yourcompany.atlassian.net"
export JIRA_EMAIL="your-email@company.com"
export JIRA_API_TOKEN="your-token"
export JIRA_PROJECT_KEY="PROJ"
export JIRA_BOARD_ID="123"

# Confluence
export CONFLUENCE_URL="https://yourcompany.atlassian.net/wiki"
export CONFLUENCE_EMAIL="your-email@company.com"
export CONFLUENCE_API_TOKEN="your-token"
export CONFLUENCE_SPACE="PM"

# GitHub
export GITHUB_TOKEN="your-token"
export GITHUB_OWNER="your-org"
export GITHUB_REPO="your-repo"

# Slack
export SLACK_EMAIL="your-email@company.com"
export SLACK_CHANNEL="product-team"
export SLACK_BOT_TOKEN="your-slack-bot-token"  # For MCP integration
export SLACK_TEAM_ID="your-team-id"  # Optional for MCP

# Amazon Q Developer (Optional)
export AMAZON_Q_APP_ID="your-app-id"
export AWS_REGION="us-east-1"
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"

# Email (SMTP)
export SMTP_SERVER="smtp.gmail.com"
export SMTP_PORT="587"
export EMAIL_ADDRESS="your-email@company.com"
export EMAIL_PASSWORD="your-password"
```

## 🎨 UI Features

### Progress Indicator
- Visual step-by-step progress bar
- Color-coded status indicators (✅ Completed, 🔄 In Progress, ⏳ Pending)
- Real-time step tracking

### Step Content
- Each step has dedicated UI with clear instructions
- Expandable sections for viewing generated content
- Regeneration options for each step
- Navigation buttons for forward/backward movement

### Sidebar
- Historical plans browser
- Quick plan loading
- Configuration status indicators

## 🔄 Workflow States

Each workflow step can be in one of these states:
- **pending**: Not yet started
- **in_progress**: Currently being processed
- **completed**: Successfully completed

## 📊 Agent Outputs

All agent outputs are:
- Stored in session state for immediate access
- Saved to database with metadata
- Linked to plan ID and version
- Available for review and regeneration

## 🛠️ Technical Details

- **Framework**: AG2 (AutoGen) Swarm
- **UI**: Streamlit with multi-step workflow
- **Database**: SQLite with WAL mode
- **LLM**: OpenAI GPT-4o-mini (configurable)
- **Pattern**: Sequential Step-by-Step Workflow
- **Persistence**: Full database persistence with versioning
- **MCP Integration**: Model Context Protocol for service integrations
- **MCP Libraries**: `agno` and `mcp` Python packages
- **MCP Servers**: Node.js-based servers installed via `npx` on first use

## 🔌 MCP Integration Details

### Supported MCP Servers

1. **Atlassian (Jira & Confluence) MCP**
   - **Official Remote MCP Server** (OAuth 2.0): `https://mcp.atlassian.com/v1/sse`
     - Requires OAuth 2.0 app creation
     - Full MCP protocol support via SSE (Server-Sent Events)
   - **Custom MCP Wrapper** (API Token): `custom_mcp_atlassian.py`
     - ✅ **For Enterprise Environments**: Works with API tokens when OAuth app creation is not allowed
     - Full MCP protocol implementation following official standards
     - Supports all Jira operations (stories, epics, releases, sprints, comments)
     - Supports all Confluence operations (pages, comments, search)
     - Automatically initialized when API tokens are configured
     - Uses stdio-based MCP protocol (compatible with MultiMCPTools)

2. **GitHub MCP** (`@modelcontextprotocol/server-github`)
   - Repository management
   - Issues and pull requests
   - Commit tracking
   - Automatic installation via npx

3. **Slack MCP** (`@modelcontextprotocol/server-slack`)
   - Channel messaging
   - User management
   - Requires bot token

4. **Amazon Q Developer MCP**
   - AI-powered assistance
   - Code analysis
   - Documentation queries

5. **Custom MCP Servers**
   - Extensible architecture
   - Add custom servers via configuration
   - Examples: Notion, Perplexity, Calendar, Gmail

### Custom Atlassian MCP Wrapper (API Token Support)

For enterprise environments where OAuth app creation is restricted, FuturisticPM includes a **custom MCP wrapper** (`custom_mcp_atlassian.py`) that:

- ✅ **Uses API tokens** instead of OAuth 2.0
- ✅ **Implements full MCP protocol** following official standards
- ✅ **Automatically activated** when API tokens are configured
- ✅ **Provides all Jira tools**: create_story, create_epic, create_release, get_issue, add_comment, update_issue, search_issues, create_sprint
- ✅ **Provides all Confluence tools**: create_page, update_page, get_page, search_pages, get_comments, add_comment
- ✅ **Works seamlessly** with the multi-agent framework

**How it works:**
1. When you configure Jira/Confluence with API tokens, the system automatically detects this
2. The custom MCP server wrapper is initialized as a stdio-based MCP server
3. The wrapper uses your existing `JiraTools` and `ConfluenceTools` classes
4. All operations go through the MCP protocol, enabling full agent-to-agent communication

**Benefits:**
- Full MCP protocol support without OAuth requirements
- Enterprise-ready for restricted environments
- Seamless integration with existing tools
- Multi-agent framework compatibility

### Adding Custom MCP Servers

You can add custom MCP servers by configuring them in the `mcp_integration.py` module or by using the `add_custom_server()` method:

```python
from mcp_integration import MCPToolsWrapper

mcp_wrapper = MCPToolsWrapper()
mcp_wrapper.add_custom_server(
    name="notion",
    command="npx -y @notionhq/notion-mcp-server",
    env_vars={"NOTION_API_KEY": "your-key"}
)
```

## 🆚 Differences from AgenticPM

FuturisticPM is built from the ground up with:
1. **Multi-Step UI**: Clear step-by-step workflow vs single-button approach
2. **Individual Step Control**: Complete each step independently
3. **Visual Progress**: Beautiful progress indicators
4. **Step Regeneration**: Regenerate individual steps without redoing everything
5. **Better Navigation**: Forward/backward navigation through steps
6. **Workflow Tracking**: Database tracking of each workflow step
7. **Rich UI**: More polished, user-friendly interface

## 📝 Example Workflow

```
Step 1: Configuration → Save & Continue
Step 2: Product Info → Save & Continue
Step 3: Strategy → Generate → Review → Next Step
Step 4: Research → Generate → Review → Next Step
Step 5: Roadmap → Generate → Review → Next Step
Step 6: Metrics → Generate → Review → Next Step
Step 7: Stakeholder → Generate → Review → Next Step
Step 8: Execution → Generate → Review → Next Step
Step 9: Publish → Choose Option → Execute → Complete
```

## 🔍 Troubleshooting

### Import Errors
```bash
pip install "pyautogen>=0.2,<0.5" streamlit==1.41.1
```

### Database Errors
- Database is automatically created on first run
- Check file permissions on `databases/` directory
- Database uses WAL mode for better concurrency

### Step Navigation Issues
- Use the navigation buttons to move between steps
- Completed steps can be revisited
- Each step validates prerequisites before allowing generation

## 📚 Additional Resources

- See `agentic_pm/README.md` for detailed integration documentation
- Refer to `requirements/Additional-Requirements.md` for agent responsibilities
- Check `requirements/AgenticPMJourney.pdf` for product management journey details

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is part of the awesome-llm-apps repository.

## 🙏 Acknowledgments

Built using [AG2](https://github.com/ag2ai/ag2) (formerly AutoGen) framework for multi-agent collaboration.

---

**FuturisticPM** - The future of AI-powered product management is here! 🚀

