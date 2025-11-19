"""
Rich UI Components for FuturisticPM
Modern, beautiful UI components with animations and rich interactions
"""

import streamlit as st
from typing import Dict, List, Optional, Any, Callable
import time

def apply_custom_css():
    """Apply custom CSS for rich, modern UI"""
    # Inject CSS at the beginning
    st.markdown("""
    <style>
    /* Main theme colors */
    :root {
        --primary-color: #6366f1;
        --secondary-color: #8b5cf6;
        --success-color: #10b981;
        --warning-color: #f59e0b;
        --error-color: #ef4444;
        --bg-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Main container styling */
    .main-container {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    }
    
    /* Card components */
    .agent-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        border-left: 4px solid var(--primary-color);
    }
    
    .agent-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 15px rgba(0,0,0,0.2);
    }
    
    .agent-card.active {
        border-left-color: var(--success-color);
        background: linear-gradient(135deg, #f0fdf4 0%, #ffffff 100%);
    }
    
    .agent-card.working {
        border-left-color: var(--warning-color);
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    /* Step indicator */
    .step-indicator {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: 2rem 0;
        position: relative;
    }
    
    .step-item {
        flex: 1;
        text-align: center;
        position: relative;
        z-index: 1;
    }
    
    .step-item.completed .step-icon {
        background: var(--success-color);
        color: white;
        transform: scale(1.1);
    }
    
    .step-item.active .step-icon {
        background: var(--primary-color);
        color: white;
        animation: bounce 1s infinite;
    }
    
    .step-item.pending .step-icon {
        background: #e5e7eb;
        color: #9ca3af;
    }
    
    .step-icon {
        width: 50px;
        height: 50px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 0.5rem;
        font-size: 24px;
        transition: all 0.3s ease;
    }
    
    @keyframes bounce {
        0%, 100% { transform: translateY(0) scale(1.1); }
        50% { transform: translateY(-10px) scale(1.1); }
    }
    
    /* Progress bar */
    .progress-container {
        background: #e5e7eb;
        border-radius: 10px;
        height: 8px;
        overflow: hidden;
        margin: 1rem 0;
    }
    
    .progress-bar {
        height: 100%;
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
        border-radius: 10px;
        transition: width 0.5s ease;
        animation: shimmer 2s infinite;
    }
    
    @keyframes shimmer {
        0% { background-position: -1000px 0; }
        100% { background-position: 1000px 0; }
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    
    /* Output editor */
    .output-editor {
        background: white;
        border: 2px solid #e5e7eb;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        transition: border-color 0.3s ease;
    }
    
    .output-editor:focus-within {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
    }
    
    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.875rem;
        font-weight: 600;
        margin: 0.25rem;
    }
    
    .status-badge.success {
        background: #d1fae5;
        color: #065f46;
    }
    
    .status-badge.warning {
        background: #fef3c7;
        color: #92400e;
    }
    
    .status-badge.error {
        background: #fee2e2;
        color: #991b1b;
    }
    
    .status-badge.info {
        background: #dbeafe;
        color: #1e40af;
    }
    
    /* Agent interaction visualization */
    .agent-interaction {
        display: flex;
        align-items: center;
        margin: 1rem 0;
        padding: 1rem;
        background: #f9fafb;
        border-radius: 8px;
    }
    
    .agent-arrow {
        margin: 0 1rem;
        font-size: 24px;
        color: var(--primary-color);
        animation: slide 1s infinite;
    }
    
    @keyframes slide {
        0%, 100% { transform: translateX(0); }
        50% { transform: translateX(10px); }
    }
    
    /* Tooltip */
    .tooltip {
        position: relative;
        display: inline-block;
    }
    
    .tooltip:hover .tooltip-text {
        visibility: visible;
        opacity: 1;
    }
    
    .tooltip-text {
        visibility: hidden;
        opacity: 0;
        background-color: #1f2937;
        color: white;
        text-align: center;
        border-radius: 6px;
        padding: 0.5rem;
        position: absolute;
        z-index: 1000;
        bottom: 125%;
        left: 50%;
        transform: translateX(-50%);
        transition: opacity 0.3s;
        white-space: nowrap;
    }
    
    /* Fade in animation */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in {
        animation: fadeIn 0.5s ease-in;
    }
    
    /* Loading spinner */
    .spinner {
        border: 3px solid #f3f4f6;
        border-top: 3px solid var(--primary-color);
        border-radius: 50%;
        width: 40px;
        height: 40px;
        animation: spin 1s linear infinite;
        margin: 0 auto;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    </style>
    """, unsafe_allow_html=True)


def render_agent_card(agent_name: str, status: str, icon: str, description: str, output: Optional[str] = None):
    """Render a beautiful agent card"""
    status_class = {
        'idle': 'pending',
        'working': 'working',
        'completed': 'active',
        'error': 'error'
    }.get(status, 'pending')
    
    st.markdown(f"""
    <div class="agent-card {status_class} fade-in">
        <div style="display: flex; align-items: center; margin-bottom: 1rem;">
            <div style="font-size: 32px; margin-right: 1rem;">{icon}</div>
            <div>
                <h3 style="margin: 0; color: #1f2937;">{agent_name}</h3>
                <span class="status-badge {status_class}">{status.upper()}</span>
            </div>
        </div>
        <p style="color: #6b7280; margin: 0.5rem 0;">{description}</p>
    </div>
    """, unsafe_allow_html=True)
    
    if output:
        with st.expander(f"📄 View {agent_name} Output", expanded=False):
            st.markdown(output)


def render_step_indicator(steps: List[Dict], current_step: int):
    """Render beautiful step indicator"""
    # Build the step indicator HTML - ensure proper formatting
    step_items_html = []
    for i, step in enumerate(steps):
        if i < current_step:
            status = 'completed'
            icon = '✅'
        elif i == current_step:
            status = 'active'
            icon = step.get('icon', '🔄')
        else:
            status = 'pending'
            icon = step.get('icon', '⏳')
        
        # Escape step name to prevent HTML injection
        step_name = str(step.get('name', '')).replace('<', '&lt;').replace('>', '&gt;')
        
        step_items_html.append(
            f'<div class="step-item {status}">'
            f'<div class="step-icon">{icon}</div>'
            f'<div style="font-weight: 600; color: #1f2937;">{step_name}</div>'
            f'</div>'
        )
    
    # Combine all step items
    step_html = f'<div class="step-indicator">{"".join(step_items_html)}</div>'
    
    # Render the step indicator
    st.markdown(step_html, unsafe_allow_html=True)
    
    # Progress bar
    progress = (current_step + 1) / len(steps) if steps else 0
    progress_pct = int(progress * 100)
    progress_html = (
        f'<div class="progress-container">'
        f'<div class="progress-bar" style="width: {progress_pct}%;"></div>'
        f'</div>'
        f'<div style="text-align: center; margin-top: 0.5rem; color: #6b7280;">'
        f'Step {current_step + 1} of {len(steps)} ({progress_pct}%)'
        f'</div>'
    )
    st.markdown(progress_html, unsafe_allow_html=True)


def render_editable_output(title: str, content: str, key: str, help_text: str = None) -> str:
    """Render an editable output area"""
    st.markdown(f"### {title}")
    if help_text:
        st.caption(help_text)
    
    edited_content = st.text_area(
        label="",
        value=content,
        height=300,
        key=f"editor_{key}",
        help="Edit the content above before proceeding to the next step"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Save Changes", key=f"save_{key}"):
            st.success("Changes saved!")
            return edited_content
    with col2:
        if st.button("🔄 Reset to Original", key=f"reset_{key}"):
            st.info("Content reset to original")
            return content
    
    return edited_content


def render_agent_interaction_flow(interactions: List[Dict]):
    """Visualize agent-to-agent interactions"""
    if not interactions:
        return
    
    st.markdown("### 🤝 Agent Interactions")
    
    for i, interaction in enumerate(interactions[-5:]):  # Show last 5
        from_agent = interaction.get('from', 'User')
        to_agent = interaction.get('to', 'Unknown')
        
        st.markdown(f"""
        <div class="agent-interaction fade-in">
            <div style="flex: 1; text-align: right;">
                <strong>{from_agent}</strong>
            </div>
            <div class="agent-arrow">→</div>
            <div style="flex: 1;">
                <strong>{to_agent}</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_status_dashboard(agents: Dict[str, Dict]):
    """Render agent status dashboard"""
    st.markdown("### 📊 Agent Status Dashboard")
    
    cols = st.columns(min(len(agents), 4))
    
    for i, (name, info) in enumerate(agents.items()):
        with cols[i % len(cols)]:
            status = info.get('status', 'idle')
            interactions = info.get('interactions', 0)
            
            status_color = {
                'idle': '#6b7280',
                'working': '#f59e0b',
                'completed': '#10b981',
                'error': '#ef4444'
            }.get(status, '#6b7280')
            
            st.markdown(f"""
            <div style="background: white; padding: 1rem; border-radius: 8px; border-left: 4px solid {status_color};">
                <div style="font-weight: 600; margin-bottom: 0.5rem;">{name}</div>
                <div style="font-size: 0.875rem; color: #6b7280;">Status: {status}</div>
                <div style="font-size: 0.875rem; color: #6b7280;">Interactions: {interactions}</div>
            </div>
            """, unsafe_allow_html=True)


def render_success_message(message: str, duration: int = 3):
    """Render animated success message"""
    st.markdown(f"""
    <div class="fade-in" style="background: linear-gradient(135deg, #10b981, #059669); color: white; padding: 1rem; border-radius: 8px; margin: 1rem 0; text-align: center; font-weight: 600;">
        ✅ {message}
    </div>
    """, unsafe_allow_html=True)
    time.sleep(duration)


def render_info_box(title: str, content: str, icon: str = "ℹ️"):
    """Render an info box"""
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #dbeafe, #bfdbfe); padding: 1.5rem; border-radius: 8px; border-left: 4px solid #3b82f6; margin: 1rem 0;">
        <div style="display: flex; align-items: start;">
            <div style="font-size: 24px; margin-right: 1rem;">{icon}</div>
            <div>
                <h4 style="margin: 0 0 0.5rem 0; color: #1e40af;">{title}</h4>
                <p style="margin: 0; color: #1e3a8a;">{content}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

