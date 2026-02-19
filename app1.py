import streamlit as st
import pandas as pd
import numpy as np
import os

st.set_page_config(page_title="SSC CGL 2025 Fast Predictor", layout="wide")

# --- PART 1: DATA LOADING & CLEANING ---
@st.cache_data
def load_and_clean_data(file_name):
    if not os.path.exists(file_name):
        return None, None
    df = pd.read_csv(file_name, encoding='latin1', on_bad_lines='skip')
    df.columns = [str(c).strip() for c in df.columns]

    if 'Main Paper Marks' not in df.columns:
        df = pd.read_csv(file_name, skiprows=1, encoding='latin1')
        df.columns = [str(c).strip() for c in df.columns]

    key_col = 'Roll Number' if 'Roll Number' in df.columns else df.columns[0]
    df['Main Paper Marks'] = pd.to_numeric(df['Main Paper Marks'], errors='coerce')
    df['Computer Marks'] = pd.to_numeric(df['Computer Marks'], errors='coerce')
    df = df.dropna(subset=['Main Paper Marks', 'Category', 'Computer Marks'])

    rules = {'UR': (18, 27), 'OBC': (15, 24), 'EWS': (15, 24), 'SC': (12, 21), 'ST': (12, 21)}
    def get_pass_status(row):
        b, c = rules.get(row['Category'], (12, 21))
        return pd.Series([row['Computer Marks'] >= b, row['Computer Marks'] >= c])
    df[['Pass_B', 'Pass_C']] = df.apply(get_pass_status, axis=1)
    return df, key_col

@st.cache_data
def load_stat_data(file_name):
    if not os.path.exists(file_name): 
        return None, None
    df = pd.read_csv(file_name, encoding='latin1', on_bad_lines='skip')
    df.columns = [str(c).strip() for c in df.columns]
    key_col = 'Roll Number' if 'Roll Number' in df.columns else df.columns[0]
    df['Stat Marks'] = pd.to_numeric(df.get('Stat Marks', df.iloc[:, -1]), errors='coerce')
    return df[[key_col, 'Stat Marks']], key_col

# --- PART 2: VACANCY STRUCTURE ---
def get_full_vacancy_list():    
    return [
        # Level, Post, UR, SC, ST, OBC, EWS, Total, IsCPT, IsStat
        ("L-7", "CSS (DoPT) - ASO", 273, 104, 52, 185, 68, 682, True, False),
        ("L-7", "MEA - ASO", 44, 13, 0, 33, 10, 100, True, False),
        ("L-7", "CBIC - Inspector (Examiner)", 68, 18, 24, 13, 14, 137, True, False),
        ("L-7", "CBIC - Inspector (Preventive Officer)", 138, 75, 20, 91, 29, 353, True, False),
        ("L-7", "CBIC - Inspector (Central Excise)", 611, 175, 82, 269, 169, 1306, True, False),
        ("L-7", "CBDT - IT Inspector", 176, 52, 39, 95, 27, 389, False, False),
        ("L-7", "ED - Assistant Enforcement Officer", 1, 2, 2, 13, 0, 18, False, False),
        ("L-7", "IB - ASO", 100, 24, 19, 39, 15, 197, False, False),
        ("L-6", "CBIC - Executive Assistant", 89, 24, 12, 40, 18, 183, True, False),
        ("L-6", "CBDT - Office Superintendent", 2766, 1012, 496, 1822, 657, 6753, False, False),
        ("L-6", "RGI - Statistical Investigator Gr. II", 50, 18, 12, 28, 10, 118, False, True),
        ("L-6", "MoSPI - Junior Statistical Officer", 124, 47, 15, 36, 27, 249, False, True),
        ("L-5", "CGDA - Auditor", 477, 176, 88, 316, 117, 1174, False, False),
        ("L-5", "C&AG - Accountant", 86, 31, 17, 28, 18, 180, False, False),
        ("L-4", "CBIC - Tax Assistant", 256, 136, 82, 203, 94, 771, False, False),
        ("L-4", "CBDT - Tax Assistant", 572, 171, 80, 340, 86, 1249, False, False)
        # Add more posts as needed...
    ]

# --- PART 3: STREAMLIT UI ---
st.title("📊 SSC CGL 2025 Optimized Predictor")

st.sidebar.header("Step 1: Your Profile")
u_marks = st.sidebar.number_input("Main Paper Marks", 0.0, 390.0, 310.0)
u_stat = st.sidebar.number_input("Statistics Marks", 0.0, 200.0, 0.0)
u_cat = st.sidebar.selectbox("Category", ["UR", "OBC", "EWS", "SC", "ST"])
u_comp = st.sidebar.number_input("Computer Marks", 0.0, 60.0, 25.0)

MAIN_FILE = "CSV - SSC CGL Mains 2025 Marks List.xlsx - in.csv"
STAT_FILE = "CSV - SSC CGL Mains 2025 Statistics Paper Marks List (1).csv"

df_main, main_key = load_and_clean_data(MAIN_FILE)
df_stat, stat_key = load_stat_data(STAT_FILE)

if df_main is not None:
    if df_stat is not None:
        df_final = pd.merge(df_main, df_stat, left_on=main_key, right_on=stat_key, how='left').fillna(0)
        df_final['Total_Stat_Marks'] = df_final['Main Paper Marks'] + df_final['Stat Marks']
    else:
        df_final = df_main.copy()
        df_final['Total_Stat_Marks'] = df_final['Main Paper Marks']

    cutoffs_rules = {'UR': (18, 27), 'OBC': (15, 24), 'EWS': (15, 24), 'SC': (12, 21), 'ST': (12, 21)}
    u_b_min, u_c_min = cutoffs_rules.get(u_cat, (12, 21))

    # --- PART 4: PROCESS UNIQUE POSTS & ALLOCATE ---
    posts = get_full_vacancy_list()
    posts_df = pd.DataFrame(posts, columns=[
        'Level', 'Post', 'UR', 'SC', 'ST', 'OBC', 'EWS', 'Total', 'IsCPT', 'IsStat'
    ])
    # Aggregate duplicates (if any)
    posts_df = posts_df.groupby(['Level', 'Post'], as_index=False).agg({
        'UR': 'sum', 'SC': 'sum', 'ST': 'sum', 'OBC': 'sum', 'EWS': 'sum',
        'Total': 'sum', 'IsCPT': 'max', 'IsStat': 'max'
    })

    allocated_indices = set()
    display_data = []

    for _, row in posts_df.iterrows():
        lvl = row['Level']
        name = row['Post']
        ur_v, sc_v, st_v, obc_v, ews_v = row['UR'], row['SC'], row['ST'], row['OBC'], row['EWS']
        is_cpt, is_stat = row['IsCPT'], row['IsStat']

        pool = df_final.copy() if is_stat else df_final[~df_final.index.isin(allocated_indices)]
        eligible = pool[pool['Pass_C']] if is_cpt else pool[pool['Pass_B']]
        score_col = 'Total_Stat_Marks' if is_stat else 'Main Paper Marks'
        user_score = (u_marks + u_stat) if is_stat else u_marks

        # --- UR allocation ---
        ur_candidates = eligible.sort_values(by=score_col, ascending=False).head(ur_v)
        ur_cut = ur_candidates[score_col].min() if not ur_candidates.empty else 0
        allocated_indices.update(ur_candidates.index)

        # --- Category allocation ---
        cat_v_map = {'SC': sc_v, 'ST': st_v, 'OBC': obc_v, 'EWS': ews_v}
        target_vac = cat_v_map.get(u_cat, 0)
        remaining_pool = eligible[~eligible.index.isin(ur_candidates.index)]
        cat_candidates = remaining_pool[remaining_pool['Category'] == u_cat].sort_values(by=score_col, ascending=False).head(target_vac)
        cat_cut = cat_candidates[score_col].min() if not cat_candidates.empty else 0
        allocated_indices.update(cat_candidates.index)

        # --- User Prediction ---
        req_comp = u_c_min if is_cpt else u_b_min
        if u_comp < req_comp:
            chance = "❌ FAIL (Comp)"
        elif is_stat and u_stat == 0:
            chance = "⚠️ Stat Paper Absent"
        elif user_score >= ur_cut and ur_cut > 0:
            chance = "⭐ HIGH (UR Merit)"
        elif user_score >= cat_cut and cat_cut > 0:
            chance = "✅ HIGH CHANCE"
        else:
            chance = "📉 LOW CHANCE"

        display_data.append({
            "Level": lvl,
            "Post": name,
            "Type": "Stat" if is_stat else "Main",
            "UR Cutoff": ur_cut if ur_cut > 0 else "N/A",
            f"{u_cat} Cutoff": cat_cut if cat_cut > 0 else "N/A",
            "Prediction": chance
        })

    st.subheader("📋 Post-wise Allocation Report")
    final_df_display = pd.DataFrame(display_data)
    final_df_display = final_df_display.sort_values(['Level', 'Post'])
    st.dataframe(final_df_display, use_container_width=True, hide_index=True)
else:
    st.error(f"File '{MAIN_FILE}' not found!")
