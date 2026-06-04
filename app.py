import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.colors import ListedColormap
from scipy.stats import gaussian_kde

# Page config
st.set_page_config(
    page_title="VMM Feedback Survey Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----- Load Data -----
try:
    df = pd.read_csv(r"C:\Users\addis\Documents\notepad\VMM\Use Me VMM Mock Data.csv")
except Exception as e:
    st.error(f"Error loading CSV file: {e}")
    st.stop()

# ----- Define Constants -----
VALUES_COLS = ['Generational Wisdom Rating (1-5)', 'Vision Rating (1-5)',
               'Community Rating (1-5)', 'Traditions Rating (1-5)']
VALUES_COLORS = ['#70CBD3', '#4A4B4D', '#EB4223', '#F88A61']
VALUES_LABELS = ['Gen. Wisdom', 'Vision', 'Community', 'Traditions']

GROWTH_COLS = ['Skills Growth Rating (1-5)', 'Knowledge Growth Rating (1-5)',
               'Transformation Rating (1-5)']
GROWTH_COLORS = ['#148281', '#A8462F', '#F16029']
GROWTH_LABELS = ['Skills Growth', 'Knowledge Growth', 'Transformation']

# Get unique roles
ALL_ROLES = ['All Roles'] + sorted(df['Role'].dropna().unique().tolist())

# ----- Helper Functions -----
def calc_percentage_4_or_5(series):
    """Calculate percentage of responses that are 4 or 5"""
    numeric_col = pd.to_numeric(series, errors='coerce')
    count_4_or_5 = numeric_col.isin([4, 5]).sum()
    total_valid = numeric_col.count()
    
    if total_valid > 0:
        percentage = (count_4_or_5 / total_valid) * 100
        return f"{percentage:.0f}%"
    else:
        return "N/A"

def plot_ridgeline(ax, data_df, cols, colors, title, x_label='Rating (1-5)'):
    """Create KDE ridgeline plot"""
    x_range = np.linspace(0, 6, 300)
    overlap = 1.5
    n = len(cols)
    
    for i, (col, color) in enumerate(zip(cols, colors)):
        vals = pd.to_numeric(data_df[col], errors='coerce').dropna()
        if len(vals) < 2:
            continue
        
        kde = gaussian_kde(vals, bw_method=0.4)
        y = kde(x_range)
        y = y / y.max()
        base = (n - 1 - i) * overlap * 0.6
        
        ax.fill_between(x_range, base, base + y, color=color, alpha=0.75)
        ax.plot(x_range, base + y, color='white', linewidth=0.8)
        ax.axhline(base, color='white', linewidth=0.3, alpha=0.4)
        ax.text(-0.05, base + 0.1,
                col.replace(' Rating (1-5)', ''),
                ha='right', va='bottom', fontsize=8.5, color='#333333',
                transform=ax.get_yaxis_transform())
    
    ax.set_xlim(0.5, 5.5)
    ax.set_ylim(-0.1, n * overlap * 0.6 + 0.8)
    ax.set_xlabel(x_label, fontsize=10)
    ax.set_title(title, fontsize=13, fontweight='bold', pad=8)
    ax.set_yticks([])
    ax.spines[['top', 'right', 'left']].set_visible(False)
    ax.set_facecolor('#F9F9F9')

def plot_percentage_panel(ax, data_df, cols, colors, labels, title):
    """Display percentages of 4 or 5 ratings in a clean panel"""
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.set_title(title, fontsize=13, fontweight='bold', pad=8)
    ax.set_facecolor('#F9F9F9')
    
    n = len(cols)
    spacing = 1.0 / (n + 1)
    
    for i, (col, color, label) in enumerate(zip(cols, colors, labels)):
        y_pos = 1 - (i + 1) * spacing
        percentage = calc_percentage_4_or_5(data_df[col])
        
        # Label
        ax.text(0.5, y_pos + 0.08, label,
                ha='center', va='center', fontsize=10,
                color='#333333', fontweight='bold')
        
        # Percentage in brand color
        ax.text(0.5, y_pos - 0.02, percentage,
                ha='center', va='center', fontsize=28,
                color=color, fontweight='bold')

# ----- Sidebar Filter -----
st.sidebar.header("🎯 Filters")
selected_role = st.sidebar.selectbox(
    "Select Role:",
    options=ALL_ROLES,
    index=0
)

# Filter data based on role
if selected_role != 'All Roles':
    filtered_df = df[df['Role'] == selected_role].copy()
    subtitle = f'Role: {selected_role} (n={len(filtered_df)})'
else:
    filtered_df = df.copy()
    subtitle = 'All Roles'

# ----- Title -----
st.title("📊 VMM Feedback Survey Dashboard")
st.markdown(f"**{subtitle}**")

# ----- Main Dashboard -----
fig = plt.figure(figsize=(16, 10))
fig.patch.set_facecolor('white')

# Create grid: 2 rows (Values top, Growth bottom) x 2 cols (Ridgeline left, Percentages right)
gs = gridspec.GridSpec(2, 2, figure=fig,
                      height_ratios=[1, 1],
                      width_ratios=[2.5, 1],
                      hspace=0.35, wspace=0.25,
                      left=0.08, right=0.95, top=0.90, bottom=0.2)

# VALUES ROW (top)
ax_values_ridge = fig.add_subplot(gs[0, 0])
ax_values_pct = fig.add_subplot(gs[0, 1])

plot_ridgeline(ax_values_ridge, filtered_df, VALUES_COLS, VALUES_COLORS, 'Values')
plot_percentage_panel(ax_values_pct, filtered_df, VALUES_COLS, VALUES_COLORS,
                     VALUES_LABELS, 'Experienced the Value')

# GROWTH ROW (bottom)
ax_growth_ridge = fig.add_subplot(gs[1, 0])
ax_growth_pct = fig.add_subplot(gs[1, 1])

plot_ridgeline(ax_growth_ridge, filtered_df, GROWTH_COLS, GROWTH_COLORS, 'Growth')
plot_percentage_panel(ax_growth_pct, filtered_df, GROWTH_COLS, GROWTH_COLORS,
                     GROWTH_LABELS, 'Experienced Growth')

st.pyplot(fig)

# ----- Summary Stats -----
st.sidebar.markdown("---")
st.sidebar.subheader("📈 Summary Stats")
st.sidebar.metric("Total Responses", len(filtered_df))

if 'Total VMM Projects Participated' in filtered_df.columns:
    avg_projects = filtered_df['Total VMM Projects Participated'].mean()
    st.sidebar.metric("Avg Projects Participated", f"{avg_projects:.1f}")
