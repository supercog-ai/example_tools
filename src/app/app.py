import streamlit as st
import streamlit.components.v1 as components

def init_session_state():
    if 'messages' not in st.session_state:
        st.session_state.messages = []

def main():
    # Set page config
    st.set_page_config(
        page_title="My Agent",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Custom CSS for styling
    st.markdown("""
        <style>
        .main-container {
            padding: 2rem;
        }
        .agent-button {
            background-color: #e8f5e9;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            margin: 5px;
            width: 100%;
            text-align: left;
        }
        .connection-button {
            background-color: #e3f2fd;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            margin: 5px;
            width: 100%;
        }
        .chat-container {
            background-color: white;
            border-radius: 10px;
            padding: 20px;
            height: 600px;
            overflow-y: auto;
        }
        </style>
    """, unsafe_allow_html=True)

    # Initialize session state
    init_session_state()

    # Create three columns
    left_col, middle_col, right_col = st.columns([1, 1.5, 2])

    # Left column - Agent buttons
    with left_col:
        st.markdown("### Quick Access")
        st.button("My Agent", key="my_agent", help="Access your personal agent", use_container_width=True)
        st.button("Design Agent", key="design_agent", help="Access design tools", use_container_width=True)
        
        st.markdown("### Connections")
        st.button("connect GitHub", key="github", use_container_width=True)
        st.button("connect G Cal", key="gcal", use_container_width=True)
        st.button("connect GMail", key="gmail", use_container_width=True)
        
        st.markdown("### Tools")
        st.button("Web browser", key="browser", use_container_width=True)
        
        st.markdown("### Knowledge")
        st.button("add files", key="files", use_container_width=True)
        st.button("add sites", key="sites", use_container_width=True)

    # Middle column - Controls and settings
    with middle_col:
        st.markdown("### My Agent ⚙️")
        st.markdown("#### Connections")
        
        # Settings and controls
        with st.expander("Tools", expanded=True):
            st.text_input("Add new tool")
            st.button("Web browser", key="browser2")
        
        # Create tool link
        st.markdown("[create tool](https://example.com)")

    # Right column - Chat interface
    with right_col:
        # Chat container
        st.markdown("### How can I assist you today?")
        
        # Chat messages
        chat_placeholder = st.container()
        with chat_placeholder:
            for message in st.session_state.messages:
                st.text(message)
        
        # Input box at the bottom
        user_input = st.text_input("Type your message...")
        if user_input:
            st.session_state.messages.append(f"User: {user_input}")
            # Add response handling logic here
            if "search LinkedIn" in user_input.lower():
                st.session_state.messages.append("> Go search LinkedIn for some new ML jobs")

if __name__ == "__main__":
    main()
    