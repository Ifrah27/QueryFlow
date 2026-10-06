import streamlit as st
import pandas as pd

def render_visualization(df: pd.DataFrame, key_prefix: str = "chart"):
    """
    Renders smart minimal charts for tabular database query output when useful.
    - Categorical string column + 1 numeric column -> Bar Chart
    - 2 Numeric columns -> Scatter / Line Chart
    - Date column + numeric column -> Line Chart
    """
    if df is None or df.empty or len(df.columns) < 2:
        return

    num_cols = df.select_dtypes(include=['number']).columns.tolist()
    cat_cols = df.select_dtypes(include=['object', 'string', 'category']).columns.tolist()

    if not num_cols:
        return

    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
    with st.expander("📊 Smart Visualization", expanded=False):
        try:
            if cat_cols and num_cols:
                x_col = cat_cols[0]
                y_col = num_cols[0]
                st.caption(f"Bar Chart: **{x_col}** vs **{y_col}**")
                chart_data = df[[x_col, y_col]].set_index(x_col)
                st.bar_chart(chart_data)
            elif len(num_cols) >= 2:
                x_col = num_cols[0]
                y_col = num_cols[1]
                st.caption(f"Line Chart: **{x_col}** vs **{y_col}**")
                chart_data = df[[x_col, y_col]].set_index(x_col)
                st.line_chart(chart_data)
        except Exception:
            pass
