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
        # Create joypy-style ridgeline plot with beautiful overlapping density curves
        fig, ax = plt.subplots(figsize=(8, 5))
        
        x = np.linspace(0.5, 5.5, 300)
        colors = plt.cm.autumn_r(np.linspace(0, 1, len(plot_data.columns)))
        
        n_cols = len(plot_data.columns)
        
        for i, col in enumerate(plot_data.columns):
            data = pd.to_numeric(plot_data[col], errors='coerce').dropna()
            if len(data) > 1:
                # Calculate KDE
                kde = gaussian_kde(data, bw_method='scott')
                density = kde(x)
                
                # Normalize and offset for ridgeline effect
                density_norm = density / density.max() * 0.85
                y_offset = n_cols - i - 1
                
                # Create the wavy mountain effect with fill
                ax.fill_between(x, y_offset, y_offset + density_norm, 
                               alpha=0.7, color=colors[i], edgecolor='white', linewidth=1.5)
                ax.plot(x, y_offset + density_norm, color=colors[i], linewidth=2)
        
        # Styling to match joypy
        ax.set_xlim(0.5, 5.5)
        ax.set_ylim(-0.3, n_cols)
        ax.set_xlabel('Score (1-5)', fontsize=11)
        ax.set_ylabel('')
        ax.set_title('Score Spread Densities (1 to 5)', fontsize=13, pad=15)
        
        # Set y-axis labels to category names
        ax.set_yticks(range(n_cols))
        ax.set_yticklabels(list(reversed(plot_data.columns)), fontsize=10)
        
        # Clean up styling
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.grid(axis='x', alpha=0.2, linestyle='--')
        
        plt.tight_layout()
        st.pyplot(fig)
    else:
        st.info("Not enough records found to generate distribution waves. Try picking another role or 'All Roles'.")

# =========================================================
# 6. FOOTER
# =========================================================
st.markdown("---")
st.caption(f"Showing data for: {selected_role} | Dataset size: {len(filtered_data)} rows")