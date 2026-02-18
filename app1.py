import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="SSC CGL 2025 - Smart Predictor", layout="wide")

# --- PART 1: HIGH-SPEED DATA LOADING ---
@st.cache_data
def get_processed_database():
    main_file = "CSV - SSC CGL Mains 2025 Marks List.xlsx - in.csv"
    stat_file = "CSV - SSC CGL Mains 2025 Statistics Paper Marks List (1).csv"
    
    if not os.path.exists(main_file):
        return None

    try:
        df = pd.read_csv(main_file, encoding='latin1', on_bad_lines='skip')
        df.columns = [str(c).strip() for c in df.columns]
        df['Main Paper Marks'] = pd.to_numeric(df['Main Paper Marks'], errors='coerce')
        df['Computer Marks'] = pd.to_numeric(df['Computer Marks'], errors='coerce')
        df = df.dropna(subset=['Main Paper Marks', 'Category', 'Computer Marks'])
        
        if os.path.exists(stat_file):
            df_s = pd.read_csv(stat_file, encoding='latin1')
            df_s.columns = [str(c).strip() for c in df_s.columns]
            s_key = df_s.columns[0]
            df_s = df_s[[s_key, df_s.columns[-1]]].rename(columns={df_s.columns[-1]: 'Stat Marks'})
            df_s['Stat Marks'] = pd.to_numeric(df_s['Stat Marks'], errors='coerce').fillna(0)
            df = pd.merge(df, df_s, left_on=df.columns[0], right_on=s_key, how='left').fillna(0)
            df['Total_Stat_Score'] = df['Main Paper Marks'] + df['Stat Marks']
        else:
            df['Total_Stat_Score'] = df['Main Paper Marks']
        return df.sort_values(by='Main Paper Marks', ascending=False)
    except Exception as e:
        st.error(f"Error: {e}")
        return None

# --- PART 2: FULL POST LIST ---
def get_posts():
    return [
        ("L-7", "CSS (DoPT) - ASO", 273, 104, 52, 185, 68, 682, True, False),
        ("L-7", "MEA - ASO", 44, 13, 0, 33, 10, 100, True, False),
        ("L-7", "CBIC - Inspector (Examiner)", 68, 18, 24, 13, 14, 137, True, False),
        ("L-7", "CBIC - Inspector (Preventive Officer)", 138, 75, 20, 91, 29, 353, True, False),
        ("L-7", "CBIC - Inspector (Central Excise)", 611, 175, 82, 269, 169, 1306, True, False),
        ("L-7", "CBDT - IT Inspector", 176, 52, 39, 95, 27, 389, False, False),
        ("L-7", "ED - AEO", 1, 2, 2, 13, 0, 18, False, False),
        ("L-7", "IB - ASO", 100, 24, 19, 39, 15, 197, False, False),
        ("L-7", "Railways - ASO", 23, 4, 4, 14, 3, 48, False, False),
        ("L-7", "EPFO - ASO", 36, 17, 5, 30, 6, 94, False, False),
        ("L-7", "CBI - Sub Inspector", 52, 12, 5, 18, 6, 93, False, False),
        ("L-6", "CBIC - Executive Assistant", 89, 24, 12, 40, 18, 183, True, False),
        ("L-6", "CBDT - Office Superintendent", 2766, 1012, 496, 1822, 657, 6753, False, False),
        ("L-6", "RGI - Stat. Investigator Gr. II", 50, 18, 12, 28, 10, 118, False, True),
        ("L-6", "MoSPI - JSO", 124, 47, 15, 36, 27, 249, False, True),
        ("L-5", "CGDA - Auditor", 477, 176, 88, 316, 117, 1174, False, False),
        ("L-5", "C&AG - Accountant", 86, 31, 17, 28, 18, 180, False, False),
        ("L-4", "CBIC - Tax Assistant", 256, 136, 82, 203, 94, 771, True, False),
        ("L-4", "CBDT - Tax Assistant", 572, 171, 80, 340, 86, 1249, False, False),
        # ... You can add all 51 here
    ]

# --- MAIN UI ---
st.title("🎯 SSC CGL 2025 Improved Predictor")

st.sidebar.header("User Details")
u_marks = st.sidebar.number_input("Main Marks", 0.0, 390.0, 310.0)
u_stat = st.sidebar.number_input("Stat Marks", 0.0, 200.0, 0.0)
u_comp = st.sidebar.number_input("Comp Marks", 0.0, 60.0, 25.0)
u_cat = st.sidebar.selectbox("Category", ["UR", "OBC", "EWS", "SC", "ST"])

df = get_processed_database()

if df is not None:
    # 1. Global Rank
    o_rank = (df['Main Paper Marks'] > u_marks).sum() + 1
    st.sidebar.metric("Your Global Rank", f"#{o_rank}")
    
    # 2. Cutoff Rules
    rules = {'UR': (18, 27), 'OBC': (15, 24), 'EWS': (15, 24), 'SC': (12, 21), 'ST': (12, 21)}
    u_b_min, u_c_min = rules.get(u_cat, (12, 21))
    
    results = []
    
    # IMPROVED LOGIC: Individual Hurdle per Post
    for lvl, name, ur_v, sc_v, st_v, obc_v, ews_v, tot_v, is_cpt, is_stat in get_posts():
        score_col = 'Total_Stat_Score' if is_stat else 'Main Paper Marks'
        user_val = (u_marks + u_stat) if is_stat else u_marks
        
        # Filter for candidates eligible for THIS post (Computer/CPT check)
        def can_hold_post(row):
            b_min, c_min = rules.get(row['Category'], (12, 21))
            return row['Computer Marks'] >= (c_min if is_cpt else b_min)

        eligible_df = df[df.apply(can_hold_post, axis=1)]
        
        # Determine UR and Category Cutoffs for this specific post
        ur_cut = eligible_df[score_col].iloc[ur_v-1] if len(eligible_df) >= ur_v else 0
        
        cat_df = eligible_df[eligible_df['Category'] == u_cat]
        cat_vac = {'SC': sc_v, 'ST': st_v, 'OBC': obc_v, 'EWS': ews_v}.get(u_cat, 0)
        cat_cut = cat_df[score_col].iloc[cat_vac-1] if len(cat_df) >= cat_vac else 0
        
        # User prediction
        req_c = u_c_min if is_cpt else u_b_min
        if u_comp < req_c: res = "❌ FAIL (Comp)"
        elif is_stat and u_stat == 0: res = "⚠️ Stat Absent"
        elif user_val >= ur_cut and ur_cut > 0: res = "⭐ VERY HIGH"
        elif user_val >= cat_cut and cat_cut > 0: res = "✅ GOOD CHANCE"
        else: res = "📉 LOW"

        results.append({"Post": name, "Lvl": lvl, "Projected Cutoff": max(ur_cut, cat_cut), "Chance": res})

    # Search & Display
    search = st.text_input("🔍 Search Post", "")
    final_df = pd.DataFrame(results)
    st.dataframe(final_df[final_df['Post'].str.contains(search, case=False)], use_container_width=True, hide_index=True)
    
    csv = final_df.to_csv(index=False).encode('utf-8')
    st.download_button("📂 Download Results", data=csv, file_name="Prediction.csv")
