import streamlit as st

def render_header(title: str, subtitle: str):
    """Renders top header bar with contextual dataset badge and modern typography."""
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"""
            <div style="margin-bottom: 1rem;">
                <h2 style="margin: 0; font-size: 1.6rem; font-weight: 800; color: #172033; letter-spacing: -0.025em;">{title}</h2>
                <div style="font-size: 0.9rem; color: #667085; margin-top: 0.2rem; font-weight: 500;">{subtitle}</div>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        if st.session_state.get("active_dataset_id") and st.session_state.active_dataset_id in st.session_state.get("datasets", {}):
            ds = st.session_state.datasets[st.session_state.active_dataset_id]
            st.markdown(f"""
                <div style="text-align: right; padding-top: 4px;">
                    <span class="saas-badge-info">📄 {ds['filename']} ({ds['row_count']:,} rows)</span>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <div style="text-align: right; padding-top: 4px;">
                    <span class="saas-badge-info" style="background-color: #F1F5F9; color: #475569; border-color: #E2E8F0;">🌐 Built-in Database</span>
                </div>
            """, unsafe_allow_html=True)
    st.markdown("<hr style='margin-top: 0.25rem; margin-bottom: 1.5rem; border: 0; border-top: 1px solid #E6E8EF;'>", unsafe_allow_html=True)
