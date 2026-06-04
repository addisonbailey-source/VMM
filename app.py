# =========================================================
# 1. IMPORTS
# =========================================================
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import joypy  # Make sure to run 'pip install joypy' in your terminal if you haven't!
import warnings

warnings.filterwarnings("ignore")

# =========================================================
# 2. PAGE SETTINGS
# =========================================================
st.set_page_config(
    page_title="VMM Survey Summary Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown('<h1 style="text-align: center; color: #1E293B;">📊 VMM Survey Summary Dashboard</h1>', unsafe_allow_html=True)

# =========================================================
# 3. DATA LOADING (THE REAL EXCEL/CSV DATA)
# =========================================================
@st.cache_data
def load_survey_data():
    # Make sure your spreadsheet file is in the same folder as this app.py script!
    # If using your Excel file:
    return pd.read_excel("Use Me VMM Mock Data.xlsx")
    
    # If you converted it to a CSV, use this instead:
    # return pd.read_csv("VMM_Feedback_Survey_Updated.csv")

df = load_survey_data()

# =========================================================
# 4. SIDEBAR FILTERS
# =========================================================
st.sidebar.header("🎯 Filters")

# Clean drop-down filter based directly on the 'Role' column from your data
available_roles = ["All Roles"] + list(df['Role'].dropna().unique())
selected_role = st.sidebar.selectbox("Select Role Filter", options=available_roles)

# Filter the data dynamically
if selected_role != "All Roles":
    filtered_data = df[df['Role'] == selected_role]
else:
    filtered_data = df.copy()

# =========================================================
# 5. DASHBOARD LAYOUT
# =========================================================
col1, col2 = st.columns([1, 1.3], gap="large")

# --- LEFT COLUMN: VMM Category Averages ---
with col1:
    st.subheader("📌 Category Averages")
    
    # Calculate averages dynamically from your actual (1-5) ratings data
    gw_avg = filtered_data['Generational Wisdom Rating (1-5)'].mean()
    v_avg  = filtered_data['Vision Rating (1-5)'].mean()
    c_avg  = filtered_data['Community Rating (1-5)'].mean()
    t_avg  = filtered_data['Traditions Rating (1-5)'].mean()
    tr_avg = filtered_data['Transformation Rating (1-5)'].mean()

    # Display clean 2-column metrics
    m_col1, m_col2 = st.columns(2)
    with m_col1:
        st.metric(label="Generational Wisdom", value=f"{gw_avg:.2f} / 5")
        st.metric(label="Vision", value=f"{v_avg:.2f} / 5")
        st.metric(label="Transformation", value=f"{tr_avg:.2f} / 5")
    with m_col2:
        st.metric(label="Community", value=f"{c_avg:.2f} / 5")
        st.metric(label="Traditions", value=f"{t_avg:.2f} / 5")

# --- RIGHT COLUMN: Distribution Waves (Joypy Plot) ---
with col2:
    st.subheader("📈 Distribution Trends")
    
    # Target the exact Rating column names from your notebook
    target_wave_cols = [
        'Generational Wisdom Rating (1-5)',
        'Vision Rating (1-5)',
        'Community Rating (1-5)',
        'Traditions Rating (1-5)',
        'Transformation Rating (1-5)'
    ]
    
    # Rename columns temporarily just for chart labels so they look clean on the dashboard
    rename_dict = {
        'Generational Wisdom Rating (1-5)': 'Generational Wisdom',
        'Vision Rating (1-5)': 'Vision',
        'Community Rating (1-5)': 'Community',
        'Traditions Rating (1-5)': 'Traditions',
        'Transformation Rating (1-5)': 'Transformation'
    }
    
    # Prepare the data subset for plotting
    plot_data = filtered_data[target_wave_cols].rename(columns=rename_dict)

    if len(plot_data) > 1:
        # Generate the exact wavy mountain plot using joypy
        fig, axes = joypy.joyplot(
            plot_data,
            colormap=plt.cm.autumn_r,  # Beautiful fiery orange-red gradient waves
            fade=True,
            grid=False,
            figsize=(7, 4.5),
            title="Score Spread Densities (1 to 5)"
        )
        
        # Streamlit's native command to display Matplotlib figures cleanly!
        st.pyplot(fig)
    else:
        st.info("Not enough records found to generate distribution waves. Try picking another role or 'All Roles'.")

# =========================================================
# 6. FOOTER
# =========================================================
st.markdown("---")
st.caption(f"Showing data for: {selected_role} | Dataset size: {len(filtered_data)} rows")