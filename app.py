import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
import os

st.set_page_config(page_title="Ne-Ha | RFP Engine", page_icon="🚀", layout="wide")

with st.sidebar:
    st.title("⚙️ Control Panel")
    st.markdown("Welcome to **Ne-Ha**, your autonomous workspace.")
    st.write("---")
    api_key = st.text_input("Gemini API Key:", type="password", help="Enter your Google AI developer key to authorize the engine.")
    st.write("---")
    st.markdown("### Engine Status")
    if api_key:
        st.success("API Key Loaded")
    else:
        st.warning("Awaiting API Key")

st.title("🚀 Ne-Ha")
st.caption("Enterprise Autonomous RFP Proposal & Audit Engine")
st.write("---")

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("📋 Input Criteria")
    default_reqs = """1. System architecture must use AES-256 bit encryption.
2. Infrastructure must provide 99.99% uptime guarantees."""
    
    requirements = st.text_area(
        "Paste Client RFP Requirements Here:", 
        value=default_reqs, 
        height=250
    )
    
    generate_btn = st.button("Generate & Audit Proposal", type="primary", use_container_width=True)

with col2:
    st.subheader("✨ Generated Output")
    
    if generate_btn:
        if not api_key:
            st.error("🔑 Configuration missing: Please input your Gemini API Key in the left sidebar.")
        else:
            try:
                # Inject key to system environment variables
                os.environ["GOOGLE_API_KEY"] = api_key
                
                # Updated to the current production model 'gemini-2.0-flash' to resolve the 404 error
                llm = ChatGoogleGenerativeAI(
                    model="gemini-2.0-flash", 
                    transport="rest"
                )
                
                with st.spinner("🧠 Analyzing requirements and structuring enterprise response..."):
                    prompt = f"Generate a highly professional corporate RFP proposal response explicitly addressing these requirements:\n{requirements}"
                    
                    response_object = llm.invoke(prompt)
                    clean_response_text = response_object.content
                    
                    st.toast("Proposal Drafted Successfully!", icon="✅")
                    st.markdown("### Draft Response")
                    st.markdown(clean_response_text)
                    st.write("---")
                    st.download_button(
                        label="📥 Download Proposal (.txt)",
                        data=clean_response_text,
                        file_name="Ne-Ha_RFP_Proposal.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
            except Exception as e:
                st.error(f"Execution Error: {e}")
    else:
        st.info("Awaiting your input criteria. Click 'Generate & Audit Proposal' to execute the draft workspace.")
