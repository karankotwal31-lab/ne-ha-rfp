import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from pypdf import PdfReader
import os

st.set_page_config(page_title="Ne-Ha | Commercial RFP Engine", page_icon="🚀", layout="wide")

# Sidebar Configuration Control Panel
with st.sidebar:
    st.title("⚙️ Commercial Panel")
    st.markdown("Welcome to **Ne-Ha**, your autonomous workspace.")
    st.write("---")
    api_key = st.text_input("Gemini API Key:", type="password", help="Enter your Google AI developer key.")
    st.write("---")
    st.markdown("### Engine Status")
    if api_key:
        st.success("API Key Loaded")
    else:
        st.warning("Awaiting API Key")

st.title("🚀 Ne-Ha Portal")
st.caption("Commercial Multi-Modal RFP Proposal, Audit & Margin Protection Workspace")
st.write("---")

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("📁 Snap & Audit: Document Ingestion")
    st.markdown("Drop client procurement sheets, logistics profiles, or complete heavy-equipment RFPs below.")
    
    # Feature 1: The native Drag-and-Drop file ingestion panel
    uploaded_file = st.file_uploader(
        "Upload Client RFP Document (PDF format only):", 
        type=["pdf"], 
        help="Drag & Drop or browse files from your computer or screenshot folders."
    )
    
    if uploaded_file is not None:
        st.info(f"📄 File captured: '{uploaded_file.name}'")
    
    generate_btn = st.button("Execute Ingestion & Response", type="primary", use_container_width=True)

with col2:
    st.subheader("✨ Generated Output Workspace")
    
    if generate_btn:
        if not api_key:
            st.error("🔑 Configuration missing: Please input your Gemini API Key in the left sidebar.")
        elif uploaded_file is None:
            st.error("❌ Document missing: Please upload a PDF file on the left before running execution.")
        else:
            try:
                # Lock in API Authorization
                os.environ["GOOGLE_API_KEY"] = api_key
                
                # Active production long-term-support model
                llm = ChatGoogleGenerativeAI(
                    model="gemini-2.5-flash", 
                    transport="rest"
                )
                
                extracted_rfp_text = ""
                
                # Processing Module: Ingesting and reading the PDF file content
                with st.spinner("⏳ Extracting text data layout from file structure..."):
                    reader = PdfReader(uploaded_file)
                    # Loop through pages and extract plain text string layouts
                    for page_num in range(len(reader.pages)):
                        page_text = reader.pages[page_num].extract_text()
                        if page_text:
                            extracted_rfp_text += page_text + "\n"
                
                # Error check to verify if document contained clean readable text
                if not extracted_rfp_text.strip():
                    st.error("⚠️ Document Parsing Alert: The file was read, but no readable text layers were found. Ensure it is not an un-scanned flattened picture file.")
                else:
                    with st.spinner("🧠 Initializing Gemini Cognitive Engine..."):
                        # Structuring corporate prompt instruction
                        prompt = f"""You are an elite corporate proposal specialist. Analyze this extracted raw text from a client RFP and formulate a completely structured, highly professional response matrix:
                        
                        --- EXTRACTED CLIENT RFP TEXT ---
                        {extracted_rfp_text}
                        """
                        
                        response_object = llm.invoke(prompt)
                        clean_response_text = response_object.content
                        
                        st.toast("Document Audited & Responded!", icon="✅")
                        st.markdown("### Draft Proposal Response Matrix")
                        st.markdown(clean_response_text)
                        st.write("---")
                        st.download_button(
                            label="📥 Download Proposal Matrix (.txt)",
                            data=clean_response_text,
                            file_name="Ne-Ha_Ingested_Proposal.txt",
                            mime="text/plain",
                            use_container_width=True
                        )
            except Exception as e:
                st.error(f"Execution Error: {e}")
    else:
        st.info("Awaiting file upload. Drop your PDF contract on the left and execute the workspace pipeline.")
    
