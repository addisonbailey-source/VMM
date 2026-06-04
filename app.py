# =========================================================
# 1. IMPORTS
# =========================================================
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde
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
    # Load the CSV data file
    return pd.read_csv("Use Me VMM Mock Data.csv")

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
        # Create ridgeline plot using matplotlib (joypy-compatible visualization)
        fig, ax = plt.subplots(figsize=(10, 6))
        
        x = np.linspace(1, 5, 200)
        colors = plt.cm.autumn_r(np.linspace(0, 1, len(plot_data.columns)))
        
        for i, col in enumerate(plot_data.columns):
            data = pd.to_numeric(plot_data[col], errors='coerce').dropna()
            if len(data) > 1:
                kde = gaussian_kde(data)
                density = kde(x)
                density = density / density.max() * 0.8  # Normalize height
                ax.fill_between(x, i, i + density, alpha=0.6, color=colors[i], label=col)
                ax.plot(x, i + density, color=colors[i], linewidth=2)
        
        ax.set_ylim(-0.5, len(plot_data.columns))
        ax.set_xlim(0.5, 5.5)
        ax.set_xlabel('Score (1-5)', fontsize=12)
        ax.set_title('Score Spread Densities (1 to 5)', fontsize=14)
        ax.set_yticks(range(len(plot_data.columns)))
        ax.set_yticklabels(plot_data.columns, fontsize=10)
        plt.tight_layout()
        st.pyplot(fig)
    else:
        st.info("Not enough records found to generate distribution waves. Try picking another role or 'All Roles'.")

# =========================================================
# 6. FOOTER
# =========================================================
st.markdown("---")
st.caption(f"Showing data for: {selected_role} | Dataset size: {len(filtered_data)} rows")