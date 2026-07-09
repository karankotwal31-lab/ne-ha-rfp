import streamlit as st
import os
import re
import json
import pandas as pd
from pypdf import PdfReader
import pdfplumber
from docx import Document
from openpyxl import Workbook
from io import BytesIO
from supabase import create_client, Client
from langchain_google_genai import ChatGoogleGenerativeAI

# Set global structural app page configurations
st.set_page_config(
    page_title="Ne-Ha | Commercial Enterprise Platform", 
    page_icon="🚀", 
    layout="wide"
)

# --- SECURE CLOUD CONNECTION BOOTSTRAPPING ---
# In production, these are retrieved safely from Streamlit Secrets or Environment Variables
SUPABASE_URL = st.sidebar.text_input("Supabase URL:", type="default")
SUPABASE_KEY = st.sidebar.text_input("Supabase Anon Key:", type="password")
GEMINI_MASTER_KEY = st.sidebar.text_input("Master Gemini API Key:", type="password")

def get_supabase() -> Client:
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None
    return create_client(SUPABASE_URL, SUPABASE_KEY)

# --- AUTHENTICATION INTERFACE MANAGER ---
def render_auth_portal(supabase: Client):
    st.title("🔐 Ne-Ha Enterprise Identity Portal")
    tabs = st.tabs(["Existing User Sign-In", "Create Enterprise Account"])
    
    with tabs[0]:
        email = st.text_input("Corporate Email:", key="login_email")
        password = st.text_input("Password:", type="password", key="login_password")
        if st.button("Authenticate Workspace Access", type="primary", use_container_width=True):
            try:
                res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                st.session_state["user"] = res.user
                st.rerun()
            except Exception as e:
                st.error(f"Authentication Denied: {e}")
                
    with tabs[1]:
        new_email = st.text_input("Corporate Email Address:", key="reg_email")
        new_password = st.text_input("Secure Password (Min 8 chars):", type="password", key="reg_password")
        if st.button("Provision New Account Environment", use_container_width=True):
            try:
                supabase.auth.sign_up({"email": new_email, "password": new_password})
                st.success("Account created! Please verify your corporate email before signing in.")
            except Exception as e:
                st.error(f"Provisioning Failed: {e}")

if "user" not in st.session_state:
    st.session_state["user"] = None

supabase_client = get_supabase()

if not supabase_client:
    st.warning("⚠️ Critical Configuration Missing: Please insert your Supabase connection parameters in the sidebar panel.")
    st.stop()

if st.session_state["user"] is None:
    render_auth_portal(supabase_client)
    st.stop()

# Cache active session credentials safely
active_user_id = st.session_state["user"].id

# --- SUPABASE DATA RETENTION MATRIX PLUMBING ---
def save_dataframe_to_cloud(df, doc_name):
    if df is None or df.empty:
        return
    # Delete older cached iterations safely using client row policies
    supabase_client.table("rfp_matrix").delete().eq("doc_name", doc_name).execute()
    
    records = df.copy()
    records["doc_name"] = doc_name
    records_dict = records.to_dict(orient="records")
    
    # Commit changes safely into PostgreSQL
    supabase_client.table("rfp_matrix").insert(records_dict).execute()

def load_document_from_cloud(doc_name):
    res = supabase_client.table("rfp_matrix").select("*").eq("doc_name", doc_name).execute()
    if res.data:
        return pd.DataFrame(res.data).drop(columns=["id", "user_id", "created_at"], errors="ignore")
    return None

# --- PHASE 3.5: LAYOUT TEXT SANITIZER ---
def robust_text_sanitizer(text):
    if not text:
        return ""
    text = re.sub(r'(?<=\b\w)\s(?=\w\b)', '', text)
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]', '', text)
    text = re.sub(r'\n\s*\n', '\n', text)
    return text.strip()

def extract_json_array(response_text):
    cleaned_text = response_text.strip()
    cleaned_text = re.sub(r'^```json\s*', '', cleaned_text, flags=re.IGNORECASE)
    cleaned_text = re.sub(r'^```\s*', '', cleaned_text, flags=re.IGNORECASE)
    cleaned_text = re.sub(r'\s*```$', '', cleaned_text, flags=re.IGNORECASE)
    try:
        match = re.search(r'\[\s*\{.*\}\s*\]', cleaned_text, re.DOTALL)
        return json.loads(match.group(0)) if match else json.loads(cleaned_text)
    except Exception as e:
        return [{
            "section": "Structural Parse Alert",
            "requirement_extracted": f"JSON Normalization Exception Intercept: {str(e)}",
            "category": "Proposal Draft",
            "assigned_team": "Sales Planning",
            "status": "Pending Review",
            "risk_multiplier": 1.00,
            "historical_match": "0%"
        }]

def sync_matrix_edits():
    if "interactive_matrix_editor" in st.session_state and st.session_state.get("active_doc_name"):
        edits = st.session_state["interactive_matrix_editor"]
        df = st.session_state["rfp_data_matrix"]
        doc_name = st.session_state["active_doc_name"]
        
        for row_idx, changed_cols in edits.get("edited_rows", {}).items():
            for col_name, new_val in changed_cols.items():
                df.iat[row_idx, df.columns.get_loc(col_name)] = new_val
                
        for added_row in edits.get("added_rows", {}):
            df = pd.concat([df, pd.DataFrame([added_row])], ignore_index=True)
            
        st.session_state["rfp_data_matrix"] = df
        save_dataframe_to_cloud(df, doc_name)

def generate_enterprise_excel(df):
    output = BytesIO()
    wb = Workbook()
    ws = wb.active
    ws.title = "RFP Requirements Matrix"
    ws.views.sheetView[0].showGridLines = True
    ws.append(list(df.columns))
    for _, row in df.iterrows():
        ws.append(list(row))
    wb.save(output)
    return output.getvalue()

# --- MAIN WORKSPACE UI ---
st.sidebar.markdown(f"**Authenticated As:**\n`{st.session_state['user'].email}`")
if st.sidebar.button("Log Out of Workspace"):
    supabase_client.auth.sign_out()
    st.session_state["user"] = None
    st.rerun()

if "rfp_data_matrix" not in st.session_state:
    st.session_state["rfp_data_matrix"] = None
if "active_doc_name" not in st.session_state:
    st.session_state["active_doc_name"] = None

st.title("🚀 Ne-Ha Enterprise Portal")
st.caption("Secure Multi-Tenant Commercial Requirements Management Framework [SaaS Core v1.0]")
st.write("---")

col_left, col_right = st.columns([1, 1.5], gap="large")

with col_left:
    st.subheader("📁 Ingest Procurement Assets")
    uploaded_file = st.file_uploader("Upload Document (.pdf, .docx, .xlsx):", type=["pdf", "docx", "xlsx"], key="rfp_uploader")
    
    if uploaded_file is not None and st.session_state["active_doc_name"] != uploaded_file.name:
        cached_df = load_document_from_cloud(uploaded_file.name)
        if cached_df is not None:
            st.session_state["rfp_data_matrix"] = cached_df
            st.session_state["active_doc_name"] = uploaded_file.name
            st.toast("Retrieved Workspace State from Cloud Database! ☁️")

    generate_btn = st.button("Execute Data Matrix Shredder", type="primary", use_container_width=True)

with col_right:
    st.subheader("✨ Workspace Grid Matrix")
    
    if generate_btn:
        if not GEMINI_MASTER_KEY:
            st.error("🔑 Master Key missing. Configure your AI parameters in the side panel.")
        elif uploaded_file is None:
            st.error("❌ Document missing. Please upload a target file first.")
        else:
            try:
                os.environ["GOOGLE_API_KEY"] = GEMINI_MASTER_KEY
                st.session_state["active_doc_name"] = uploaded_file.name
                
                llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", transport="rest", temperature=0.1)
                raw_extracted_text = ""
                file_extension = uploaded_file.name.split(".")[-1].lower()
                is_scanned_pdf = False
                pdf_page_images = []
                
                with st.spinner("⏳ Extracting document elements..."):
                    if file_extension == "pdf":
                        reader = PdfReader(uploaded_file)
                        for page in reader.pages[:15]:
                            txt = page.extract_text()
                            if txt: raw_extracted_text += txt + "\n"
                        
                        if len(robust_text_sanitizer(raw_extracted_text)) < 150:
                            is_scanned_pdf = True
                            uploaded_file.seek(0)
                            with pdfplumber.open(uploaded_file) as pdf:
                                for page in pdf.pages[:5]:
                                    pdf_page_images.append(page.to_image(resolution=150).original)
                                    
                    elif file_extension == "docx":
                        doc = Document(uploaded_file)
                        for p in doc.paragraphs:
                            if p.text.strip(): raw_extracted_text += p.text + "\n"
                        for table in doc.tables:
                            seen_cells = set()
                            for row in table.rows:
                                r_text = []
                                for cell in row.cells:
                                    if cell not in seen_cells:
                                        seen_cells.add(cell)
                                        if cell.text.strip(): r_text.append(cell.text.strip())
                                if r_text: raw_extracted_text += " | ".join(r_text) + "\n"
                                
                    elif file_extension == "xlsx":
                        excel_file = pd.ExcelFile(uploaded_file)
                        for sheet_name in excel_file.sheet_names:
                            excel_df = pd.read_excel(uploaded_file, sheet_name=sheet_name)
                            if not excel_df.empty:
                                raw_extracted_text += f"\n--- Sheet: {sheet_name} ---\n" + excel_df.to_markdown(index=False) + "\n"

                if is_scanned_pdf:
                    base_prompt = "Analyze the uploaded page image and extract 10-15 core requirements, commercial liabilities, or conditions into a clean raw JSON array. Do not use markdown blocks or backticks."
                    payload = [base_prompt] + pdf_page_images
                    response = llm.invoke(payload)
                    full_output = response.content
                else:
                    cleaned_text = robust_text_sanitizer(raw_extracted_text)
                    prompt = f"Analyze the following text block. Extract 15-20 core requirements into a raw JSON array schema. No backticks.\n\nText:\n{cleaned_text}"
                    response = llm.invoke(prompt)
                    full_output = response.content
                
                compiled_df = pd.DataFrame(extract_json_array(full_output))
                st.session_state["rfp_data_matrix"] = compiled_df
                save_dataframe_to_cloud(compiled_df, uploaded_file.name)
                st.toast("Stateful Cloud Grid Sync Complete!")
                
            except Exception as e:
                st.error(f"System Error Handled: {e}")

    if st.session_state["rfp_data_matrix"] is not None:
        current_df = st.session_state["rfp_data_matrix"]
        
        st.data_editor(
            current_df,
            column_config={
                "category": st.column_config.SelectboxColumn("Workspace", options=["Proposal Draft", "Risk Audit", "Calculation Layer"], required=True),
                "assigned_team": st.column_config.SelectboxColumn("Department", options=["Sales Planning", "Legal/Compliance", "Technical Ops", "Commercial Finance"], required=True),
                "status": st.column_config.SelectboxColumn("Workflow Status", options=["Pending Review", "Approved", "Escalated/Risk Flagged"], required=True),
                "risk_multiplier": st.column_config.NumberColumn("Risk Index", min_value=1.00, max_value=3.00, format="%.2f"),
                "requirement_extracted": st.column_config.TextColumn("Extracted Text", width="large")
            },
            hide_index=True, use_container_width=True, on_change=sync_matrix_edits, key="interactive_matrix_editor"
        )
        
        st.write("---")
        st.download_button(
            label="📥 Export Certified Commercial Sheet (.xlsx)",
            data=generate_enterprise_excel(current_df),
            file_name="finalized_commercial_matrix.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            type="primary"
        )
    else:
        st.info("Awaiting file processing execution loop.")
