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

# Main Input Layout Split
col_left, col_right = st.columns([1, 1.2], gap="large")

with col_left:
    st.subheader("📁 Snap & Audit: Document Ingestion")
    st.markdown("Drop client procurement sheets, logistics profiles, or complete heavy-equipment RFPs below.")
    
    uploaded_file = st.file_uploader(
        "Upload Client RFP Document (PDF format only):", 
        type=["pdf"], 
        help="Drag & Drop or browse files from your computer or screenshot folders."
    )
    
    if uploaded_file is not None:
        st.info(f"📄 File captured: '{uploaded_file.name}'")
    
    generate_btn = st.button("Execute Ingestion & Response", type="primary", use_container_width=True)

with col_right:
    st.subheader("✨ Generated Output Workspace")
    
    if generate_btn:
        if not api_key:
            st.error("🔑 Configuration missing: Please input your Gemini API Key in the left sidebar.")
        elif uploaded_file is None:
            st.error("❌ Document missing: Please upload a PDF file on the left before running execution.")
        else:
            try:
                os.environ["GOOGLE_API_KEY"] = api_key
                
                # Active production model
                llm = ChatGoogleGenerativeAI(
                    model="gemini-2.5-flash", 
                    transport="rest"
                )
                
                raw_extracted_text = ""
                
                with st.spinner("⏳ Extracting text data layout..."):
                    reader = PdfReader(uploaded_file)
                    for page in reader.pages:
                        text = page.extract_text()
                        if text:
                            raw_extracted_text += text + "\n"
                
                if not raw_extracted_text.strip():
                    st.error("⚠️ Document Parsing Alert: The file was read, but no readable text layers were found.")
                else:
                    with st.spinner("🧠 Analyzing Layout via Gemini..."):
                        
                        prompt = f"""You are an elite corporate proposal specialist, risk auditor, and technical engineer. 
                        Analyze the text below. Break your analysis into three sections using these exact headers:

                        ### [PROPOSAL_DRAFT]
                        Draft a highly professional, fully customized response matrix to the client's requirements.

                        ### [RISK_AUDIT]
                        Identify severe delivery penalty functions, strict timelines, safety thresholds, or hidden financial risks.

                        ### [CALCULATION_LAYER]
                        Extract and solve any mathematical equations, transport load limits, or financial pricing formulas.

                        --- EXTRACTED CLIENT RFP TEXT ---
                        {raw_extracted_text}
                        """
                        
                        response_object = llm.invoke(prompt)
                        full_output = response_object.content
                        
                        proposal_part = "Processing completed."
                        risk_part = "No risks flagged."
                        calc_part = "No mathematical parameters extracted."
                        
                        # Bulletproof splitting logic
                        if "### [PROPOSAL_DRAFT]" in full_output:
                            proposal_part = full_output.split("### [PROPOSAL_DRAFT]")[1]
                            if "### [RISK_AUDIT]" in proposal_part:
                                proposal_part, risk_part = proposal_part.split("### [RISK_AUDIT]")
                                if "### [CALCULATION_LAYER]" in risk_part:
                                    risk_part, calc_part = risk_part.split("### [CALCULATION_LAYER]")
                        else:
                            proposal_part = full_output
                        
                        st.toast("Analysis Completed!", icon="🚀")
                        
                        # Clean UI Workspace Tabs
                        tab1, tab2, tab3 = st.tabs([
                            "📋 Draft Proposal Matrix", 
                            "🚨 Margin & Risk Protection", 
                            "🧮 Calculation Layer"
                        ])
                        
                        with tab1:
                            st.markdown(proposal_part.strip())
                            
                        with tab2:
                            st.error("⚠️ CRITICAL COMPLIANCE AND MARGIN THREATS DETECTED:")
                            st.markdown(risk_part.strip())
                                
                        with tab3:
                            st.info("📊 AUTOMATED MATHEMATICAL FORMULA EVALUATION:")
                            st.markdown(calc_part.strip())
                                
            except Exception as e:
                st.error(f"Execution Error: {e}")
    else:
        st.info("Awaiting file upload. Drop your PDF contract on the left and execute.")
