import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="SSC CGL 2025 - Official Predictor", layout="wide")

# --- PART 1: OPTIMIZED DATA LOADING ---
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
        
        key_col = df.columns[0]

        if os.path.exists(stat_file):
            df_s = pd.read_csv(stat_file, encoding='latin1')
            df_s.columns = [str(c).strip() for c in df_s.columns]
            s_key = df_s.columns[0]
            df_s = df_s[[s_key, df_s.columns[-1]]].rename(columns={df_s.columns[-1]: 'Stat Marks'})
            df_s['Stat Marks'] = pd.to_numeric(df_s['Stat Marks'], errors='coerce').fillna(0)
            
            df = pd.merge(df, df_s, left_on=key_col, right_on=s_key, how='left').fillna(0)
            df['Total_Stat_Score'] = df['Main Paper Marks'] + df['Stat Marks']
        else:
            df['Total_Stat_Score'] = df['Main Paper Marks']
            df['Stat Marks'] = 0

        return df.sort_values(by='Main Paper Marks', ascending=False).reset_index(drop=True)
    except Exception as e:
        st.error(f"Error in Database: {e}")
        return None

# --- PART 2: FULL 51 POST LIST ---
def get_full_vacancy_list():    
    return [
        ("L-7", "CSS (DoPT) - ASO", 273, 104, 52, 185, 68, 682, True, False),
        ("L-7", "MEA - ASO", 44, 13, 0, 33, 10, 100, True, False),
        ("L-7", "CBIC - Inspector (Examiner)", 68, 18, 24, 13, 14, 137, True, False),
        ("L-7", "CBIC - Inspector (Preventive Officer)", 138, 75, 20, 91, 29, 353, True, False),
        ("L-7", "CBIC - Inspector (Central Excise)", 611, 175, 82, 269, 169, 1306, True, False),
        ("L-7", "CBDT - IT Inspector", 176, 52, 39, 95, 27, 389, False, False),
        ("L-7", "ED - Assistant Enforcement Officer", 1, 2, 2, 13, 0, 18, False, False),
        ("L-7", "IB - ASO", 100, 24, 19, 39, 15, 197, False, False),
        ("L-7", "Railways - ASO", 23, 4, 4, 14, 3, 48, False, False),
        ("L-7", "AFHQ - ASO", 3, 0, 0, 1, 1, 5, True, False),
        ("L-7", "EPFO - ASO", 36, 17, 5, 30, 6, 94, False, False),
        ("L-7", "CBI - Sub Inspector", 52, 12, 5, 18, 6, 93, False, False),
        ("L-7", "NIC - ASO", 2, 0, 0, 0, 1, 3, False, False),
        ("L-7", "CAT - ASO", 0, 0, 0, 0, 1, 1, False, False),
        ("L-7", "CBN - Inspector", 1, 1, 0, 1, 1, 4, False, False),
        ("L-7", "ECI - ASO", 0, 0, 0, 5, 1, 6, False, False),
        ("L-7", "MeitY - ASO", 2, 0, 1, 0, 0, 3, False, False),
        ("L-7", "Other Min. - ASO", 12, 5, 2, 8, 3, 30, False, False),
        ("L-6", "CBIC - Executive Assistant", 89, 24, 12, 40, 18, 183, True, False),
        ("L-6", "CBDT - Office Superintendent", 2766, 1012, 496, 1822, 657, 6753, False, False),
        ("L-6", "RGI - Statistical Investigator Gr. II", 50, 18, 12, 28, 10, 118, False, True),
        ("L-6", "MoSPI - Junior Statistical Officer", 124, 47, 15, 36, 27, 249, False, True),
        ("L-6", "ED - Assistant", 0, 0, 0, 3, 0, 3, False, False),
        ("L-6", "TRAI - Assistant", 2, 1, 0, 0, 0, 3, False, False),
        ("L-6", "Official Language - Assistant", 4, 0, 0, 1, 0, 5, False, False),
        ("L-6", "MCA - Assistant", 0, 1, 0, 0, 0, 1, False, False),
        ("L-6", "Mines - Assistant", 11, 2, 2, 3, 4, 22, True, False),
        ("L-6", "Textiles - Assistant", 1, 0, 0, 0, 0, 1, False, False),
        ("L-6", "Indian Coast Guard - Assistant", 8, 3, 1, 5, 1, 18, False, False),
        ("L-6", "DFSS - Assistant", 1, 0, 0, 1, 1, 3, False, False),
        ("L-6", "NCB - ASO", 7, 1, 1, 2, 0, 11, False, False),
        ("L-6", "NCB - Sub-Inspector/JIO", 10, 3, 4, 8, 5, 30, False, False),
        ("L-6", "NIA - Sub Inspector", 6, 2, 1, 3, 2, 14, False, False),
        ("L-6", "MoSPI - Assistant", 0, 0, 0, 2, 0, 2, False, False),
        ("L-6", "C&AG - Div. Accountant", 35, 12, 6, 21, 8, 82, False, False),
        ("L-5", "C&AG - Auditor", 148, 55, 27, 98, 37, 365, False, False),
        ("L-5", "CGDA - Auditor", 477, 176, 88, 316, 117, 1174, False, False),
        ("L-5", "Other - Auditor", 15, 5, 2, 8, 3, 33, False, False),
        ("L-5", "C&AG - Accountant", 86, 31, 17, 28, 18, 180, False, False),
        ("L-5", "Posts - Accountant", 42, 13, 6, 12, 3, 76, False, False),
        ("L-5", "CGCA - Accountant", 15, 6, 3, 9, 3, 36, False, False),
        ("L-4", "CBIC - Tax Assistant", 256, 136, 82, 203, 94, 771, True, False),
        ("L-4", "CBDT - Tax Assistant", 572, 171, 80, 340, 86, 1249, False, False),
        ("L-4", "MSME - UDC/SSA", 25, 4, 5, 16, 5, 55, False, False),
        ("L-4", "Science & Tech - UDC/SSA", 24, 9, 4, 16, 6, 59, False, False),
        ("L-4", "CBN - UDC/SSA", 12, 2, 0, 5, 2, 21, False, False),
        ("L-4", "CBN - Sub-Inspector", 11, 2, 0, 6, 0, 19, False, False),
        ("L-4", "Mines - UDC/SSA", 13, 2, 3, 4, 4, 26, False, False),
        ("L-4", "DGDE - UDC/SSA", 7, 2, 1, 3, 1, 14, False, False),
        ("L-4", "MeitY - UDC/SSA", 5, 1, 1, 2, 1, 10, False, False),
        ("L-4", "Textiles - UDC/SSA", 4, 0, 1, 1, 2, 8, False, False),
    ]

# --- UI & LOGIC ---
st.title("🎯 SSC CGL 2025: Premium Post Predictor")

st.sidebar.header("Step 1: User Profile")
u_marks = st.sidebar.number_input("Main Marks", 0.0, 390.0, 310.0, key="m")
u_stat = st.sidebar.number_input("Stat Marks", 0.0, 200.0, 0.0, key="s")
u_comp = st.sidebar.number_input("Comp Marks", 0.0, 60.0, 25.0, key="c")
u_cat = st.sidebar.selectbox("Category", ["UR", "OBC", "EWS", "SC", "ST"], key="cat")

df = get_processed_database()

if df is not None:
    o_rank = (df['Main Paper Marks'] > u_marks).sum() + 1
    st.sidebar.metric("Global Rank", f"#{o_rank}")
    
    rules = {'UR': (18, 27), 'OBC': (15, 24), 'EWS': (15, 24), 'SC': (12, 21), 'ST': (12, 21)}
    u_b_min, u_c_min = rules.get(u_cat, (12, 21))
    
    results = []
    allocated_indices = set()
    
    for lvl, name, ur_v, sc_v, st_v, obc_v, ews_v, tot_v, is_cpt, is_stat in get_full_vacancy_list():
        pool = df[~df.index.isin(allocated_indices)].copy()
        score_col = 'Total_Stat_Score' if is_stat else 'Main Paper Marks'
        user_val = (u_marks + u_stat) if is_stat else u_marks
        pool = pool.sort_values(by=score_col, ascending=False)
        
        # UR Merit
        ur_allot = pool.head(ur_v)
        allocated_indices.update(ur_allot.index)
        ur_cut = ur_allot[score_col].min() if not ur_allot.empty else 0
        
        # Category Merit
        rem = pool[~pool.index.isin(ur_allot.index)]
        cat_v = {'SC': sc_v, 'ST': st_v, 'OBC': obc_v, 'EWS': ews_v}.get(u_cat, 0)
        cat_allot = rem[rem['Category'] == u_cat].head(cat_v)
        cat_cut = cat_allot[score_col].min() if not cat_allot.empty else 0
        
        req_c = u_c_min if is_cpt else u_b_min
        if u_comp < req_c: res = "❌ FAIL (Comp)"
        elif is_stat and u_stat == 0: res = "⚠️ Stat Absent"
        elif user_val >= ur_cut and ur_cut > 0: res = "⭐ HIGH (UR)"
        elif user_val >= cat_cut and cat_cut > 0: res = "✅ HIGH (Cat)"
        else: res = "📉 LOW"

        results.append({"Post": name, "Level": lvl, "UR Cutoff": ur_cut, f"{u_cat} Cutoff": cat_cut, "Chance": res})

    # Convert results to DataFrame
    res_df = pd.DataFrame(results)

    # SEARCH & DOWNLOAD BAR
    col1, col2 = st.columns([3, 1])
    with col1:
        search_query = st.text_input("🔍 Search Post Name (e.g., ASO, Inspector, Auditor)", "")
    with col2:
        csv = res_df.to_csv(index=False).encode('utf-8')
        st.download_button("📂 Download Report", data=csv, file_name="SSC_CGL_Prediction.csv", mime='text/csv')

    # Filtering data based on search
    filtered_df = res_df[res_df['Post'].str.contains(search_query, case=False)]
    
    # Display
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)

else:
    st.error("Missing CSV files in the folder!")
