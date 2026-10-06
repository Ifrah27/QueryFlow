import streamlit as st

def render_sidebar(dataset_mgr, check_db_func):
    """Renders the dark deep navy/indigo sidebar with Lucide SVG iconography."""
    with st.sidebar:
        # Logo & Brand Header with Lucide Sparkles SVG
        st.markdown("""
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 1.75rem; padding: 0.5rem 0.2rem;">
                <div style="background: linear-gradient(135deg, #5B5CE2 0%, #7C5CFC 100%); color: #FFFFFF; width: 38px; height: 38px; border-radius: 10px; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 14px rgba(91, 92, 226, 0.4);">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/>
                    </svg>
                </div>
                <div>
                    <div style="font-weight: 800; font-size: 1.1rem; color: #FFFFFF; letter-spacing: -0.025em; line-height: 1.15;">AI Data Agent</div>
                    <div style="font-size: 0.75rem; color: #94A3B8; font-weight: 500;">Intelligent data workspace</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Navigation Options with clean text (No emojis)
        nav_options = {
            "overview": "Overview",
            "chat": "Ask Data",
            "datasets": "Datasets",
            "history": "Query History"
        }
        
        if "current_page" not in st.session_state:
            st.session_state.current_page = "overview"

        st.markdown("<div style='font-size: 0.725rem; font-weight: 700; color: #64748B; letter-spacing: 0.08em; margin-bottom: 0.5rem;'>WORKSPACE</div>", unsafe_allow_html=True)
        
        for key, label in nav_options.items():
            btn_kind = "primary" if st.session_state.current_page == key else "secondary"
            if st.button(label, key=f"nav_{key}", use_container_width=True, type=btn_kind):
                st.session_state.current_page = key
                st.rerun()

        st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
        st.markdown("<div style='font-size: 0.725rem; font-weight: 700; color: #64748B; letter-spacing: 0.08em; margin-bottom: 0.5rem;'>DATA UPLOAD</div>", unsafe_allow_html=True)

        # File Upload Zone
        uploaded_file = st.file_uploader(
            "Upload CSV",
            type=["csv"],
            help="Upload a custom CSV file to import into PostgreSQL."
        )

        if uploaded_file is not None:
            file_key = f"{uploaded_file.name}_{uploaded_file.size}"
            if file_key not in st.session_state.get("uploaded_file_keys", set()):
                if "uploaded_file_keys" not in st.session_state:
                    st.session_state.uploaded_file_keys = set()
                
                with st.spinner("Importing dataset into PostgreSQL..."):
                    success, msg, ds_info = dataset_mgr.process_and_upload_csv(uploaded_file, uploaded_file.name)
                    if success:
                        st.session_state.uploaded_file_keys.add(file_key)
                        st.session_state.datasets[ds_info["id"]] = ds_info
                        st.session_state.active_dataset_id = ds_info["id"]
                        st.success(f"Loaded `{uploaded_file.name}`!")
                        st.session_state.current_page = "chat"
                        st.rerun()
                    else:
                        st.error(f"Import failed: {msg}")

        # Active Dataset Context Selector
        if st.session_state.datasets:
            st.markdown("<div style='margin-top: 0.75rem;'></div>", unsafe_allow_html=True)
            dataset_options = {"builtin": "Built-in Database"}
            for ds_id, ds in st.session_state.datasets.items():
                dataset_options[ds_id] = ds['filename']
            
            curr_sel = st.session_state.active_dataset_id if st.session_state.active_dataset_id in dataset_options else "builtin"

            selected_id = st.selectbox(
                "Active Dataset",
                options=list(dataset_options.keys()),
                format_func=lambda x: dataset_options[x],
                index=list(dataset_options.keys()).index(curr_sel) if curr_sel in dataset_options else 0
            )
            
            if selected_id != st.session_state.active_dataset_id:
                st.session_state.active_dataset_id = None if selected_id == "builtin" else selected_id
                st.rerun()

        # Footer Status Card in Sidebar
        st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
        db_ok, db_name = check_db_func()
        
        status_color = "#12B76A" if db_ok else "#F04438"
        status_text = "PostgreSQL Connected" if db_ok else "PostgreSQL Disconnected"
        
        st.markdown(f"""
            <div style="background-color: #151D2A; border: 1px solid #1E293B; border-radius: 10px; padding: 0.85rem; margin-top: 1rem;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <div style="width: 8px; height: 8px; border-radius: 50%; background-color: {status_color};"></div>
                    <div style="font-weight: 600; font-size: 0.825rem; color: #F8FAFC;">{status_text}</div>
                </div>
                <div style="font-size: 0.75rem; color: #94A3B8; margin-top: 0.3rem;">Target DB: <code>{db_name}</code></div>
                <div style="margin-top: 0.6rem; padding-top: 0.6rem; border-top: 1px solid #1E293B; display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 0.7rem; color: #64748B;">Powered by Gemini</span>
                    <span style="font-size: 0.7rem; color: #5B5CE2; font-weight: 600;">v2.0 SaaS</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
