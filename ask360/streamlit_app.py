"""Streamlit chat UI for Ask360."""

import streamlit as st
import json
import html
from pathlib import Path
from ask360.ask360_core import answer

st.set_page_config(page_title="Ask360", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS for navigation bar and styling
st.markdown("""
    <style>
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Hide the default sidebar */
    [data-testid="stSidebar"] {
        display: none;
    }
    
    /* Top Navigation Bar */
    .top-nav {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.5rem 1rem;
        background-color: #ffffff;
        border-bottom: 2px solid #e0e0e0;
        margin-bottom: 1rem;
        position: sticky;
        top: 0;
        z-index: 100;
    }
    
    .nav-left {
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .nav-logo-container {
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .nav-logo-container img {
        max-height: 60px;
        object-fit: contain;
    }
    
    .nav-brand-text {
        display: flex;
        flex-direction: column;
    }
    
    .nav-brand-text h2 {
        margin: 0;
        font-size: 1.5rem;
        color: #1f77b4;
    }
    
    .nav-brand-text p {
        margin: 0;
        font-size: 0.9rem;
        color: #666;
    }
    
    .nav-right {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Left sidebar styling */
    .left-sidebar {
        padding: 1rem;
        border-right: 2px solid #e0e0e0;
        height: calc(100vh - 200px);
        overflow-y: auto;
    }
    
    .sidebar-chat-item {
        padding: 0.5rem;
        margin: 0.25rem 0;
        border-radius: 0.25rem;
        cursor: pointer;
        border: 1px solid transparent;
    }
    
    .sidebar-chat-item:hover {
        background-color: #f0f0f0;
        border-color: #1f77b4;
    }
    
    .sidebar-chat-item.active {
        background-color: #e3f2fd;
        border-color: #1f77b4;
    }
    
    /* Info icon and tooltip */
    .info-icon {
        display: inline-block;
        position: relative;
        cursor: pointer;
        color: #1f77b4;
        font-size: 16px;
        margin-left: 8px;
        vertical-align: middle;
    }
    .info-icon:hover {
        color: #0d5aa7;
    }
    .tooltip {
        visibility: hidden;
        position: absolute;
        background-color: #333;
        color: #fff;
        text-align: left;
        padding: 12px;
        border-radius: 6px;
        z-index: 1000;
        bottom: 125%;
        left: 50%;
        margin-left: -200px;
        width: 400px;
        font-size: 12px;
        font-family: 'Courier New', monospace;
        white-space: pre-wrap;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        opacity: 0;
        transition: opacity 0.3s;
    }
    .tooltip::after {
        content: "";
        position: absolute;
        top: 100%;
        left: 50%;
        margin-left: -5px;
        border-width: 5px;
        border-style: solid;
        border-color: #333 transparent transparent transparent;
    }
    .info-icon:hover .tooltip {
        visibility: visible;
        opacity: 1;
    }
    
    /* Main content area */
    .main-content {
        padding: 1rem;
        height: calc(100vh - 200px);
        overflow-y: auto;
    }
    
    /* Right panel styling */
    .right-panel {
        padding: 1rem;
    }
    
    /* Chat bubble styling */
    .chat-message-wrapper {
        margin: 1rem 0;
        display: flex;
        flex-direction: column;
    }
    
    .chat-message-wrapper.user-bubble {
        align-items: flex-end;
    }
    
    .chat-message-wrapper.assistant-bubble {
        align-items: flex-start;
    }
    
    .chat-bubble {
        max-width: 75%;
        padding: 0.875rem 1.125rem;
        border-radius: 1.125rem;
        word-wrap: break-word;
        line-height: 1.6;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
        margin: 0.5rem 0;
    }
    
    .chat-bubble.user {
        background: linear-gradient(135deg, #1f77b4 0%, #0d5aa7 100%);
        color: white;
        border-bottom-right-radius: 0.25rem;
    }
    
    .chat-bubble.assistant {
        background: #f5f5f5;
        color: #1a1a1a;
        border-bottom-left-radius: 0.25rem;
        border: 1px solid #e0e0e0;
    }
    
    .chat-bubble-header {
        font-weight: 600;
        font-size: 0.8rem;
        margin-bottom: 0.5rem;
        opacity: 0.85;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .chat-bubble.user .chat-bubble-header {
        color: rgba(255, 255, 255, 0.95);
    }
    
    .chat-bubble.assistant .chat-bubble-header {
        color: #666;
    }
    
    .chat-bubble-content {
        margin: 0;
        color: inherit;
    }
    
    .chat-bubble-content p {
        margin: 0.5rem 0;
        color: inherit;
    }
    
    .chat-bubble-content p:first-child {
        margin-top: 0;
    }
    
    .chat-bubble-content p:last-child {
        margin-bottom: 0;
    }
    
    /* Style Streamlit components inside bubbles */
    .chat-bubble .stButton button {
        border-radius: 0.5rem;
        margin: 0.25rem 0;
    }
    
    .chat-bubble.assistant .stMetric {
        background: rgba(255, 255, 255, 0.9);
        padding: 0.75rem;
        border-radius: 0.5rem;
        border: 1px solid #ddd;
        margin: 0.5rem 0;
    }
    
    .chat-bubble.assistant .stExpander {
        border: 1px solid #ddd;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    
    .chat-bubble.assistant .stTabs [data-baseweb="tab-list"] {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 0.5rem 0.5rem 0 0;
        margin: 0.5rem 0 0 0;
    }
    
    .chat-bubble.assistant .stTabs [data-baseweb="tab-panel"] {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 0 0 0.5rem 0.5rem;
        padding: 0.5rem;
    }
    
    /* Ensure proper spacing between chat items */
    .chat-message-wrapper + .chat-message-wrapper {
        margin-top: 1.5rem;
    }
    
    /* Style content within bubbles - target Streamlit-generated content */
    div[data-testid="column"] > div > .chat-bubble {
        width: 100%;
    }
    
    /* Ensure text color inheritance */
    .chat-bubble.user * {
        color: white !important;
    }
    
    .chat-bubble.user p,
    .chat-bubble.user span,
    .chat-bubble.user div {
        color: white !important;
    }
    
    /* Override Streamlit default text colors in user bubbles */
    .chat-bubble.user [class*="stMarkdown"] p,
    .chat-bubble.user [class*="stText"] {
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'history' not in st.session_state:
    st.session_state.history = []

if 'use_ai_insight' not in st.session_state:
    st.session_state.use_ai_insight = False

if 'pinned_questions' not in st.session_state:
    st.session_state.pinned_questions = []

if 'saved_insights' not in st.session_state:
    st.session_state.saved_insights = []

if 'selected_chat_index' not in st.session_state:
    st.session_state.selected_chat_index = None

if 'show_settings' not in st.session_state:
    st.session_state.show_settings = False

if 'show_help' not in st.session_state:
    st.session_state.show_help = False


def generate_insight(question: str, answer_dict: dict) -> str:
    """
    Generate AI insight (placeholder - no actual LLM call per requirements).
    In a real implementation, this would call an LLM API.
    """
    # Placeholder implementation
    return f"Based on the {answer_dict['intent']} analysis, the data shows key trends in yogurt consumption patterns."


def display_chat_item(item, idx):
    """Display a single chat item with bubble-style layout."""
    # User message bubble (right-aligned)
    spacer_col, user_col = st.columns([1, 2])
    with spacer_col:
        st.empty()
    with user_col:
        # Wrap content in bubble structure
        question_html = html.escape(item['question'])
        st.markdown(f"""
            <div class="chat-message-wrapper user-bubble">
                <div class="chat-bubble user">
                    <div class="chat-bubble-header">You</div>
                    <div class="chat-bubble-content">
                        <p>{question_html}</p>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # Assistant message bubble (left-aligned)
    result = item.get('answer')
    if not result:
        assistant_col, spacer_col = st.columns([2, 1])
        with assistant_col:
            st.markdown("""
                <div class="chat-message-wrapper assistant-bubble">
                    <div class="chat-bubble assistant">
                        <div class="chat-bubble-header">Ask360</div>
                        <div class="chat-bubble-content">
                            <p>Processing...</p>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        with spacer_col:
            st.empty()
        return
    
    assistant_col, spacer_col = st.columns([2, 1])
    with assistant_col:
        # Create bubble wrapper
        st.markdown("""
            <div class="chat-message-wrapper assistant-bubble">
                <div class="chat-bubble assistant">
                    <div class="chat-bubble-header">Ask360</div>
                    <div class="chat-bubble-content">
        """, unsafe_allow_html=True)
        
        # Use container to group all content within bubble
        with st.container():
            # Action buttons
            action_col1, action_col2 = st.columns([1, 1])
            with action_col1:
                if st.button("💾 Save Insight", key=f"save_insight_{idx}"):
                    insight_title = item['question'][:50]
                    insight_content = "\n".join(result.get('text', []))
                    st.session_state.saved_insights.append({
                        'title': insight_title,
                        'content': insight_content,
                        'question': item['question']
                    })
                    st.success("Insight saved!")
                    st.rerun()
            
            # SQL Query Tooltip - Info icon with query explanation
            if result.get('sql_query'):
                sql_query = result['sql_query']
                # Escape HTML special characters
                escaped_sql = html.escape(sql_query)
                st.markdown(f"""
                    <div style="margin-bottom: 10px;">
                        <div class="info-icon">
                            ℹ️
                            <span class="tooltip">Query interpreted as:
{escaped_sql}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            
            # Metadata display
            if result.get('metadata'):
                metadata = result['metadata']
                with st.expander("📊 Query Metadata", expanded=True):
                    meta_cols = st.columns(2)
                    
                    with meta_cols[0]:
                        st.markdown("**Data Sources:**")
                        if metadata.get('data_sources'):
                            for source in metadata['data_sources']:
                                st.markdown(f"• {source}")
                        else:
                            st.markdown("*Not specified*")
                        
                        st.markdown("**Time Range:**")
                        if metadata.get('time_range'):
                            st.markdown(f"• {metadata['time_range']}")
                        else:
                            st.markdown("*Not specified*")
                    
                    with meta_cols[1]:
                        st.markdown("**Regions:**")
                        if metadata.get('regions'):
                            for region in metadata['regions']:
                                st.markdown(f"• {region}")
                        else:
                            st.markdown("*Not specified*")
                        
                        st.markdown("**Filters:**")
                        if metadata.get('filters'):
                            for filter_item in metadata['filters']:
                                st.markdown(f"• {filter_item}")
                        else:
                            st.markdown("*None applied*")
            
            # KPIs
            if result.get('kpis'):
                kpi_cols = st.columns(len(result['kpis']))
                for i, kpi in enumerate(result['kpis']):
                    with kpi_cols[i]:
                        st.metric(kpi['label'], kpi['value'])
            
            # Text summary
            if result.get('text'):
                for line in result['text']:
                    st.write(line)
            
            # Tabs for Chart, Table, Raw JSON
            if result.get('chart_path') or result.get('table'):
                tab1, tab2, tab3 = st.tabs(["Chart", "Table", "Raw JSON"])
                
                with tab1:
                    if result.get('chart_path') and Path(result['chart_path']).exists():
                        st.image(result['chart_path'])
                    else:
                        st.write("No chart available.")
                
                with tab2:
                    if result.get('table'):
                        st.dataframe(result['table'])
                    else:
                        st.write("No table data available.")
                
                with tab3:
                    st.json(result)
            
            # AI Insight (if enabled)
            if item.get('insight'):
                st.markdown("#### AI Insight")
                st.write(item['insight'])
            
            # Analyst notes
            with st.expander("📝 Analyst Notes"):
                st.text_area(
                    "Add notes",
                    key=f"notes_{idx}",
                    height=100
                )
        
        # Close bubble wrapper
        st.markdown("""
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    with spacer_col:
        st.empty()


# Top Navigation Bar
image_path = Path(__file__).parent / "assets" / "images" / "characters.jpg"

nav_col1, nav_col2 = st.columns([3, 1])
with nav_col1:
    nav_left_col1, nav_left_col2 = st.columns([0.3, 2], gap="small")
    with nav_left_col1:
        if image_path.exists():
            st.image(str(image_path), use_container_width=True)
    with nav_left_col2:
        st.markdown("""
            <div class="nav-brand-text">
                <h2>GlobalPack - Ask360</h2>
                <p>Query Insights360 data</p>
            </div>
        """, unsafe_allow_html=True)

with nav_col2:
    nav_right_col1, nav_right_col2, nav_right_col3 = st.columns(3, gap="small")
    with nav_right_col1:
        if st.button("⚙️", key="settings_btn", help="Settings", use_container_width=True):
            st.session_state.show_settings = not st.session_state.show_settings
            st.session_state.show_help = False
    with nav_right_col2:
        if st.button("❓", key="help_btn", help="Help", use_container_width=True):
            st.session_state.show_help = not st.session_state.show_help
            st.session_state.show_settings = False
    with nav_right_col3:
        if st.button("🧠 New Chat", key="new_chat_btn", use_container_width=True):
            st.session_state.selected_chat_index = None
            st.rerun()

# Settings Modal
if st.session_state.show_settings:
    with st.expander("⚙️ Settings", expanded=True):
        st.session_state.use_ai_insight = st.toggle("Use AI-generated insight", value=st.session_state.use_ai_insight)
        if st.button("Clear All History"):
            st.session_state.history = []
            st.session_state.pinned_questions = []
            st.session_state.saved_insights = []
            st.session_state.selected_chat_index = None
            st.rerun()

# Help Modal
if st.session_state.show_help:
    with st.expander("❓ Help", expanded=True):
        st.markdown("""
        ### How to use Ask360
        
        **Ask Questions:** Type your question in the chat input at the bottom of the screen.
        
        **Example Questions:**
        - "How is yogurt doing at FreshFoods? Show the last 12 months trend."
        - "Which were the top 3 growth markets for yogurt last year?"
        - "Among 18–34 vs 35–54, who has higher repeat rate for yogurt?"
        
        **Features:**
        - View chat history in the left sidebar
        - Pin important questions for quick access
        - Save insights from your queries
        - View charts, tables, and metadata for each response
        
        **Navigation:**
        - Click on any chat in the sidebar to view it
        - Use the "New Chat" button to start fresh
        - Use settings to toggle AI insights
        """)

# Two-Column Layout: Left Sidebar + Right Panel
left_col, right_col = st.columns([0.3, 0.7], gap="medium")

# Left Column: Chat History, Pinned Questions, Saved Insights
with left_col:
    st.markdown("### 💬 Chat History")
    
    # Display pinned questions first
    if st.session_state.pinned_questions:
        st.markdown("#### 📌 Pinned")
        for pin_idx, pin_item in enumerate(st.session_state.pinned_questions):
            pin_key = f"pin_{pin_idx}"
            if st.button(f"📌 {pin_item['question'][:50]}...", key=pin_key, use_container_width=True):
                # Find this item in history and select it
                for idx, hist_item in enumerate(st.session_state.history):
                    if hist_item['question'] == pin_item['question']:
                        st.session_state.selected_chat_index = idx
                        st.rerun()
    
    # Display regular chat history
    if st.session_state.history:
        st.markdown("#### All Chats")
        for idx, item in enumerate(st.session_state.history):
            is_selected = st.session_state.selected_chat_index == idx
            chat_text = item['question'][:55] + "..." if len(item['question']) > 55 else item['question']
            is_pinned = any(p['question'] == item['question'] for p in st.session_state.pinned_questions)
            
            # Create a row with chat button and pin button
            chat_col1, chat_col2 = st.columns([5, 1])
            with chat_col1:
                if st.button(chat_text, key=f"chat_{idx}", use_container_width=True):
                    st.session_state.selected_chat_index = idx
                    st.rerun()
            with chat_col2:
                pin_btn_text = "📌" if not is_pinned else "📌✓"
                if st.button(pin_btn_text, key=f"pin_toggle_{idx}", help="Pin/Unpin this question", use_container_width=True):
                    if is_pinned:
                        st.session_state.pinned_questions = [p for p in st.session_state.pinned_questions if p['question'] != item['question']]
                    else:
                        st.session_state.pinned_questions.append({
                            'question': item['question'],
                            'answer': item.get('answer')
                        })
                    st.rerun()
    else:
        st.info("No chat history yet. Start asking questions!")
    
    st.markdown("---")
    
    # Saved Insights section
    st.markdown("### 💾 Saved Insights")
    if st.session_state.saved_insights:
        for insight_idx, insight in enumerate(st.session_state.saved_insights):
            with st.expander(f"💾 {insight.get('title', 'Insight')[:30]}..."):
                st.write(insight.get('content', ''))
                if st.button("🗑️ Delete", key=f"delete_insight_{insight_idx}"):
                    st.session_state.saved_insights.pop(insight_idx)
                    st.rerun()
    else:
        st.info("No saved insights yet.")

# Right Column: Active Chat + Visual Outputs
with right_col:
    # Example questions section
    example_questions = [
        "How is yogurt doing at FreshFoods? Show the last 12 months trend.",
        "Which were the top 3 growth markets for yogurt last year?",
        "Among 18–34 vs 35–54, who has higher repeat rate for yogurt?",
        "What are the top consumption occasions for shelf-stable yogurt?",
        "In e-commerce vs retail, which channel grew faster for multipack yogurt?"
    ]

    st.markdown("#### Quick Questions")
    example_cols = st.columns(len(example_questions))
    for i, example in enumerate(example_questions):
        with example_cols[i]:
            if st.button(example[:40] + "...", key=f"example_{i}", use_container_width=True):
                # Process example question
                result = answer(example)
                st.session_state.history.append({
                    'question': example,
                    'answer': result,
                    'insight': generate_insight(example, result) if st.session_state.use_ai_insight else None
                })
                st.session_state.selected_chat_index = len(st.session_state.history) - 1
                st.rerun()

    st.markdown("---")

    # Display selected chat or all chats
    if st.session_state.selected_chat_index is not None and st.session_state.selected_chat_index < len(st.session_state.history):
        # Display only the selected chat
        item = st.session_state.history[st.session_state.selected_chat_index]
        display_chat_item(item, st.session_state.selected_chat_index)
    else:
        # Display all chat history (default view)
        if st.session_state.history:
            for idx, item in enumerate(st.session_state.history):
                display_chat_item(item, idx)
        else:
            st.info("👋 Welcome to Ask360! Start by asking a question or selecting one of the example questions above.")

    # Chat input at the bottom of right panel
    if prompt := st.chat_input("Ask a question here..."):
        # Add user message
        st.session_state.history.append({
            'question': prompt,
            'answer': None,
            'insight': None
        })
        
        # Get answer
        result = answer(prompt)
        
        # Generate insight if enabled
        insight = None
        if st.session_state.use_ai_insight:
            insight = generate_insight(prompt, result)
        
        # Update history
        st.session_state.history[-1]['answer'] = result
        st.session_state.history[-1]['insight'] = insight
        
        # Select the new chat
        st.session_state.selected_chat_index = len(st.session_state.history) - 1
        
        st.rerun()
