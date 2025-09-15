import streamlit as st
from GROQ import GroqClient

# Use wide layout without sidebar
st.set_page_config(layout="centered", page_title="LLM Central Hub")

# Main title and subtitle using pure Streamlit
st.title("🤖 LLM Central Hub")
st.markdown("**Where questions become conversations across models**")
#st.write("")
    

# Initialize chat history and expand states
if "history" not in st.session_state:
    st.session_state.history = []
if "clear_prompt" not in st.session_state:
    st.session_state.clear_prompt = False
if "expanded_responses" not in st.session_state:
    st.session_state.expanded_responses = {}
if "show_export_dropdown" not in st.session_state:
     st.session_state.show_export_dropdown = False

# Helper function to truncate text
def truncate_text(text, max_length=150):
    """Truncate text to specified length and add ellipsis if needed"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."

# Helper function to create expandable content using Streamlit's built-in expander
def create_expandable_content(content, response_id, max_length=150, message_type="user"):
    """Create expandable content using Streamlit's expander component"""
    # Truncated content for the expander title
    truncated_content = truncate_text(content, max_length)
    
    with st.expander(
        f"{'👤 You' if message_type == 'user' else '🤖 AI'}: {truncated_content}",
        expanded=False  # Start collapsed by default
    ):
        st.markdown(content)

# Clear the prompt safely BEFORE rendering the input widget
if st.session_state.clear_prompt and "prompt_input" in st.session_state:
    st.session_state.prompt_input = ""
    st.session_state.clear_prompt = False

# Model selection using pure Streamlit
st.divider()
st.subheader("🤖 Select AI Model")
model = st.selectbox(
    "Choose your AI model:",
    [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant", 
        "gemma2-9b-it",
        "meta-llama/llama-4-maverick-17b-128e-instruct",
        "deepseek-r1-distill-llama-70b",
        "openai/gpt-oss-120b",
    ],
    key="model_select",
    help="Select the AI model you want to use for generating responses"
)

# Prompt input using pure Streamlit
st.write("")
st.subheader("💬 Enter Your Prompt")
prompt_col, action_col = st.columns([6, 1])
with prompt_col:
    prompt = st.text_input(
        "Your message:",
        placeholder="Enter your prompt here...",
        key="prompt_input",
        label_visibility="collapsed",
    )
with action_col:
    submit = st.button("🚀", help="Generate Response", use_container_width=True)

# Generate and display response
if submit:
    if model and prompt:
        with st.spinner(f"🤖 Generating response using {model}..."):
            groq_client = GroqClient(model, prompt)
            # Build role-wise messages from history + new user content
            messages = []
            for m in st.session_state.history:
                messages.append({"role": m["role"], "content": m["content"]})
            messages.append({"role": "user", "content": prompt})
            response = groq_client.generate_text(messages=messages)
            if response:
                # Save to history
                st.session_state.history.append({"role": "user", "model": model, "content": prompt})
                st.session_state.history.append({"role": "assistant", "model": model, "content": response})
                # Schedule input clear on next rerun to avoid modifying after instantiation
                st.session_state.clear_prompt = True
                st.success("✅ Response generated successfully!")
                st.rerun()
            else:
                st.error("❌ Failed to generate text. Please try again.")
    else:
        st.warning("⚠️ Please select a model and enter a prompt.")

# Spacer and history section
st.write("")
st.divider()

# History display section
if st.session_state.history:
    # Header row with action buttons
    header_col, export_col, clear_col = st.columns([6, 3, 2])
    with header_col:
        st.subheader("💬 Conversation History")
    with export_col:
            export_clicked = st.button("📋 Export History", use_container_width=False, help="Export conversation history")
            if export_clicked:
                st.session_state.show_export_dropdown = not st.session_state.show_export_dropdown
        # Render dropdown overlay if toggled
    if st.session_state.show_export_dropdown:
        history_text = "\n\n".join([f"{msg['role'].title()}: {msg['content']}" for msg in reversed(st.session_state.history)])
        st.subheader("Exported History")
        if st.button("📋 Copy History", key="copy_export_history", help="Copy history"):
            st.session_state.copied_history = history_text
            st.success("History ready to copy! Select and copy from here:")
            st.code(history_text)
    with clear_col:
            if st.button("🗑️ Clear All", use_container_width=True, help="Clear all conversation history"):
                st.session_state.history = []
                st.session_state.expanded_responses = {}
                st.session_state.show_export_dropdown = False
                st.rerun()
    
    # Show conversation count
    total_conversations = len([h for h in st.session_state.history if h["role"] == "user"])
    st.caption(f"📊 Total conversations: {total_conversations}")

    # Render messages using pure Streamlit
    history_container = st.container(height=600)
    
    # Get all conversation pairs (latest first)
    history = st.session_state.history
    conversation_pairs = []
    
    # Process history to create pairs (user + assistant)
    i = 0
    while i < len(history):
        if history[i]["role"] == "user":
            user_msg = history[i]
            ai_msg = history[i + 1] if i + 1 < len(history) and history[i + 1]["role"] == "assistant" else None
            conversation_pairs.append((user_msg, ai_msg))
            i += 2 if ai_msg else 1
        else:
            i += 1
    
    # Display conversation pairs (latest first)
    for idx, (user_msg, ai_msg) in enumerate(conversation_pairs):
        # Create a container for each conversation pair
        with history_container:
            st.markdown("---")  # Separator line
            
            # Create two columns: AI on left, User on right
            ai_col, user_col = st.columns([1, 1])
            
            # AI message (left side)
            with ai_col:
                if ai_msg:
                    model_name = ai_msg.get('model', 'Unknown Model')
                    st.markdown(f"**🤖 AI ({model_name}):**")
                    create_expandable_content(ai_msg['content'], f"ai_{idx}", max_length=200, message_type="ai")
                else:
                    st.markdown("**🤖 AI:** *No response yet*")
            
            # User message (right side)
            with user_col:
                st.markdown("**👤 You:**")
                create_expandable_content(user_msg['content'], f"user_{idx}", max_length=200, message_type="user")
            
            st.write("")  # Add some space between conversations