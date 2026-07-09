import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from pypdf import PdfReader
import os
import re

st.set_page_config(page_title="Ne-Ha | Commercial RFP Engine", page_icon="🚀", layout="wide")

# Text-Sanitizer Engine to solve the garbled/stretched text bug
def clean_extracted_text(text):
    # Fixes specific PDF extraction artifacts where letters or numbers get single spaced out
    text = re.sub(r'(?<=\b\w)\s(?=\w\b)', '', text)
    # Remove excessive blank lines or tracking layout spaces
    text = re.sub(r'\n\s*\n', '\n', text)
    return text.strip()

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
                
                llm = ChatGoogleGenerativeAI(
                    model="gemini-2.5-flash", 
                    transport="rest"
                )
                
                raw_extracted_text = ""
                
                with st.spinner("⏳ Extracting text data layout from file structure..."):
                    reader = PdfReader(uploaded_file)
                    for page_num in range(len(reader.pages)):
                        page_text = reader.pages[page_num].extract_text()
                        if page_text:
                            raw_extracted_text += page_text + "\n"
                
                # Execute text cleaning routine
                extracted_rfp_text = clean_extracted_text(raw_extracted_text)
                
                if not extracted_rfp_text.strip():
                    st.error("⚠️ Document Parsing Alert: The file was read, but no readable text layers were found.")
                else:
                    with st.spinner("🧠 Initializing Deep Risk & Multi-Modal Audit Pipelines..."):
                        
                        prompt = f"""You are an elite corporate proposal specialist, risk auditor, and technical engineer. 
                        Analyze the extracted raw text from this client RFP and break your analysis into three strictly defined sections using the exact headers below. 
                        Do not mirror any bad character spacing or weird formatting found in the raw text—print all responses cleanly:

                        ### [PROPOSAL_DRAFT]
                        Draft a highly professional, fully customized response matrix to the client's requirements found in the text. Make it crisp and executive-ready.

                        ### [RISK_AUDIT]
                        Actively protect our margins. Pinpoint severe delivery penalty functions, liquidated damages, strict timeline obligations, safety thresholds, or hidden operational risks.

                        ### [CALCULATION_LAYER]
                        Extract and solve any mathematical equations, transport load limits, fuel surcharges, or financial pricing formulas embedded in the text. Provide a clear step-by-step mathematical validation.

                        --- EXTRACTED CLIENT RFP TEXT ---
                        {extracted_rfp_text}
                        """
                        
                        response_object = llm.invoke(prompt)
                        full_output = response_object.content
                        
                        proposal_part = ""
                        risk_part = ""
                        calc_part = ""
                        
                        # Parse the structured response blocks out cleanly
                        if "### [PROPOSAL_DRAFT]" in full_output:
                            parts = full_output.split("### [PROPOSAL_DRAFT]")[1]
                            if "### [RISK_AUDIT]" in parts:
                                proposal_part, remaining = parts.split("### [RISK_AUDIT]")
                                if "### [CALCULATION_LAYER]" in remaining:
                                    risk_part, calc_part = remaining.split("### [CALCULATION_LAYER]")
                                else:
                                    risk_part = remaining
                            else:
                                proposal_part = parts
                        else:
                            proposal_part = full_output
                        
                        st.toast("Deep Workspace Audit Complete!", icon="🚀")
                        
                        # Render Premium UI Tabs
                        tab1, tab2, tab3 = st.tabs([
                            "📋 Draft Proposal Matrix", 
                            "🚨 Margin & Risk Protection", 
                            "🧮 Calculation Layer"
                        ])
                        
                        with tab1:
                            st.markdown("### 📝 Autonomously Generated Response")
                            st.markdown(proposal_part.strip() if proposal_part else "Processing complete.")
                            
                        with tab2:
                            st.markdown("### 🚨 Active Operational Risk Flags")
                            if risk_part.strip():
                                # Using error container styling for maximum risk visibility
                                st.error("⚠️ CRITICAL COMPLIANCE AND MARGIN THREATS DETECTED BELOW:")
                                st.markdown(risk_part.strip())
                            else:
                                st.success("✅ No critical operational or financial penalty risks flagged in this layout.")
                                
                        with tab3:
                            st.markdown("### 🧮 Technical & Financial Formula Sandbox")
                            if calc_part.strip():
                                st.info("📊 AUTOMATED MATHEMATICAL FORMULA EXTRACATION & EVALUATION:")
                                st.markdown(calc_part.strip())
                            else:
                                st.info("ℹ️ General mathematical analysis applied.")
                                
            except Exception as e:
                st.error(f"Execution Error: {e}")
    else:
        st.info("Awaiting file upload. Drop your PDF contract on the left and execute the workspace pipeline.")
