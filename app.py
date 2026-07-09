import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from pypdf import PdfReader
import os
import re

st.set_page_config(page_title="Ne-Ha | Self-Healing RFP Engine", page_icon="🚀", layout="wide")

# Phase 3.5: Multi-Stage Layout & Character Sanitizer Engine
def robust_text_sanitizer(text):
    if not text:
        return ""
    # Self-Repair Layer 1: Detect and repair staggered character anomalies (e.g., "2 , 5 0 0")
    text = re.sub(r'(?<=\b\w)\s(?=\w\b)', '', text)
    # Remove control characters and clean up broken vertical margins
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]', '', text)
    # Standardize whitespace and remove repetitive empty lines
    text = re.sub(r'\n\s*\n', '\n', text)
    return text.strip()

# Autonomous Self-Repair Parser - Bulletproofed against structural routing failures
def self_healing_parser(full_text):
    # Default initialized states to ensure UI doesn't freeze or drop out
    proposal = "⚠️ State Recovery: The draft proposal matrix failed structural routing. Displaying fallback raw analysis block below.\n\n"
    risk = "⚠️ State Recovery: Risk matrix block split failure. Initiating semantic fallback sweep."
    calc = "⚠️ State Recovery: Calculation parser fallback initialized."
    
    headers_proposal = ["### [PROPOSAL_DRAFT]", "[PROPOSAL_DRAFT]", "PROPOSAL_DRAFT"]
    headers_risk = ["### [RISK_AUDIT]", "[RISK_AUDIT]", "RISK_AUDIT"]
    headers_calc = ["### [CALCULATION_LAYER]", "[CALCULATION_LAYER]", "CALCULATION_LAYER"]
    
    # Track indices and exact header lengths simultaneously
    p_idx, p_len = -1, 0
    for h in headers_proposal:
        idx = full_text.find(h)
        if idx != -1:
            p_idx = idx
            p_len = len(h)
            break
            
    r_idx, r_len = -1, 0
    for h in headers_risk:
        idx = full_text.find(h)
        if idx != -1:
            r_idx = idx
            r_len = len(h)
            break
            
    c_idx, c_len = -1, 0
    for h in headers_calc:
        idx = full_text.find(h)
        if idx != -1:
            c_idx = idx
            c_len = len(h)
            break

    # Dynamic Structural Mapping (Handles variations safely)
    if p_idx != -1:
        end_p = r_idx if r_idx != -1 else (c_idx if c_idx != -1 else len(full_text))
        proposal = full_text[p_idx + p_len:end_p].strip()
        
    if r_idx != -1:
        end_r = c_idx if c_idx != -1 else len(full_text)
        risk = full_text[r_idx + r_len:end_r].strip()
        
    if c_idx != -1:
        calc = full_text[c_idx + c_len:].strip()
        
    # Final sanity fallback check if whole partitions are absent
    if p_idx == -1 and r_idx == -1 and c_idx == -1:
        proposal = full_text
        risk = "⚠️ Warning: Document formatting was highly irregular. Review the core proposal tab for unified risks."
        calc = "⚠️ Warning: Mathematical items were combined directly inside the master response workspace."
        
    return proposal, risk, calc

# Sidebar Configuration Control Panel
with st.sidebar:
    st.title("⚙️ Commercial Panel")
    st.markdown("Welcome to **Ne-Ha**, your autonomous workspace.")
    st.write("---")
    api_key = st.text_input("Gemini API Key:", type="password", help="Enter your Google AI developer key.")
    st.write("---")
    st.markdown("### Workspace Telemetry")
    if api_key:
        st.success("Core Engine Online")
    else:
        st.warning("Awaiting Authorization")

st.title("🚀 Ne-Ha Portal")
st.caption("Commercial Multi-Modal RFP Proposal, Audit & Margin Protection Workspace [Self-Healing v3.5]")
st.write("---")

col_left, col_right = st.columns([1, 1.2], gap="large")

with col_left:
    st.subheader("📁 Snap & Audit: Document Ingestion")
    st.markdown("Drop client procurement sheets, logistics profiles, or complete heavy-equipment RFPs below.")
    
    uploaded_file = st.file_uploader(
        "Upload Client RFP Document (PDF format only):", 
        type=["pdf"], 
        key="rfp_uploader"
    )
    
    if uploaded_file is not None:
        st.info(f"📄 Target Captured: '{uploaded_file.name}'")
    
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
                
                # Active production resilient connection
                llm = ChatGoogleGenerativeAI(
                    model="gemini-2.5-flash", 
                    transport="rest",
                    temperature=0.1 # Lower temperature ensures stricter format compliance
                )
                
                raw_extracted_text = ""
                
                with st.spinner("⏳ Extracting text data layout..."):
                    reader = PdfReader(uploaded_file)
                    for page in reader.pages:
                        text = page.extract_text()
                        if text:
                            raw_extracted_text += text + "\n"
                
                # Execute layout cleaning routine
                cleaned_rfp_text = robust_text_sanitizer(raw_extracted_text)
                
                if not cleaned_rfp_text:
                    st.error("⚠️ Document Parsing Alert: The file contains no valid readable text layers.")
                else:
                    with st.spinner("🧠 Orchestrating Self-Healing Architecture Pipelines..."):
                        
                        prompt = f"""You are an elite corporate proposal specialist, risk auditor, and technical engineer. 
                        Analyze the text below. Break your analysis into three specific blocks using these exact headers:

                        ### [PROPOSAL_DRAFT]
                        Draft a highly professional, fully customized response matrix to the client's requirements.

                        ### [RISK_AUDIT]
                        Identify severe delivery penalty functions, strict timelines, safety thresholds, or hidden financial risks.

                        ### [CALCULATION_LAYER]
                        Extract and solve any mathematical equations, transport load limits, or financial pricing formulas.

                        --- EXTRACTED CLIENT RFP TEXT ---
                        {cleaned_rfp_text}
                        """
                        
                        try:
                            response_object = llm.invoke(prompt)
                            full_output = response_object.content
                        except Exception as api_err:
                            raise RuntimeError(f"Cognitive Pipeline Failure during inference: {api_err}")
                        
                        # Self-Healing Step: Dynamically recover features if formatting breaks
                        proposal_part, risk_part, calc_part = self_healing_parser(full_output)
                        
                        st.toast("Resilient Workspace Sync Complete!", icon="🚀")
                        
                        # Render Stabilized Mobile Interface Layout
                        tab1, tab2, tab3 = st.tabs([
                            "📋 Draft Proposal Matrix", 
                            "🚨 Margin & Risk Protection", 
                            "🧮 Calculation Layer"
                        ])
                        
                        with tab1:
                            st.markdown(proposal_part)
                            
                        with tab2:
                            if "State Recovery" in risk_part or "Warning" in risk_part:
                                st.warning(risk_part)
                            else:
                                st.error("⚠️ CRITICAL COMPLIANCE AND MARGIN THREATS DETECTED:")
                                st.markdown(risk_part)
                                
                        with tab3:
                            if "State Recovery" in calc_part or "Warning" in calc_part:
                                st.warning(calc_part)
                            else:
                                st.info("📊 AUTOMATED MATHEMATICAL FORMULA EVALUATION:")
                                st.markdown(calc_part)
                                
            except Exception as e:
                st.error(f"Execution Error Caught & Isolated: {e}")
    else:
        st.info("Awaiting file upload. Drop your PDF contract on the left and execute.")
