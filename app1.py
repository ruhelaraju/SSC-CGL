import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="SSC CGL 2025 - Professional Predictor", layout="wide")

@st.cache_data
def get_processed_database():
    main_file = "CSV - SSC CGL Mains 2025 Marks List.xlsx - in.csv"
    stat_file = "CSV - SSC CGL Mains 2025 Statistics Paper Marks List (1).csv"
    if not os.path.exists(main_file): return None

    try:
        df = pd.read_csv(main_file, encoding='latin1', on_bad_lines='skip')
        df.columns = [str(c).strip() for c in df.columns]
        df['Main Paper Marks'] = pd.to_numeric(df['Main Paper Marks'], errors='coerce')
        df['Computer Marks'] = pd.to_numeric(df['Computer Marks'], errors='coerce')
        df = df.dropna(subset=['Main Paper Marks', 'Category', 'Computer Marks'])
        
        # Pre-calculate Computer Eligibility for ALL candidates at once (FAST)
        rules = {'UR': (18, 27), 'OBC': (15, 24), 'EWS': (15, 24), 'SC': (12, 21), 'ST': (12, 21)}
        df['Passed_B'] = df.apply(lambda r: r['Computer Marks'] >= rules.get(r['Category'], (12, 21))[0], axis=1)
        df['Passed_C'] = df.apply(lambda r: r['Computer Marks'] >= rules.get(r['Category'], (12, 21))[1], axis=1)

        if os.path.exists(stat_file):
            df_s = pd.read_csv(stat_file, encoding='latin1')
            df_s.columns = [str(c).strip() for c in df_s.columns]
            df_s = df_s[[df_s.columns[0], df_s.columns[-1]]].rename(columns={df_s.columns[-1]: 'Stat Marks'})
            df_s['Stat Marks'] = pd.to_numeric(df_s['Stat Marks'], errors='coerce').fillna(0)
            df = pd.merge(df, df_s, left_on=df.columns[0], right_on=df_s.columns[0], how='left').fillna(0)
            df['Total_Stat_Score'] = df['Main Paper Marks'] + df['Stat Marks']
        else:
            df['Total_Stat_Score'] = df['Main Paper Marks']
        
        return df.sort_values(by='Main Paper Marks', ascending=False)
    except Exception as e:
        st.error(f"Error: {e}"); return None

def get_all_posts():
    # Adding all major posts to fill the 51-post requirement
    return [
        ("L-7", "CSS - ASO", 273, 104, 52, 185, 68, 682, True, False),
        ("L-7", "MEA - ASO", 44, 13, 0, 33, 10, 100, True, False),
        ("L-7", "CBIC - Inspector (Examiner)", 68, 18, 24, 13, 14, 137, True, False),
        ("L-7", "CBIC - Inspector (PO)", 138, 75, 20, 91, 29, 353, True, False),
        ("L-7", "CBIC - Inspector (Excise)", 611, 175, 82, 269, 169, 1306, True, False),
        ("L-7", "CBDT - IT Inspector", 176, 52, 39, 95, 27, 389, False, False),
        ("L-7", "IB - ASO", 100, 24, 19, 39, 15, 197, False, False),
        ("L-7", "CBI - Sub Inspector", 52, 12, 5, 18, 6, 93, False, False),
        ("L-6", "Executive Assistant", 89, 24, 12, 40, 18, 183, True, False),
        ("L-6", "JSO (MoSPI)", 124, 47, 15, 36, 27, 249, False, True),
        ("L-5", "CAG - Auditor", 148, 55, 27, 98, 37, 365, False, False),
        ("L-5", "CGDA - Auditor", 477, 176, 88, 316, 117, 1174, False, False),
        ("L-4", "Tax Assistant (CBIC)", 256, 136, 82, 203, 94, 771, True, False),
        ("L-4", "Tax Assistant (CBDT)", 572, 171, 80, 340, 86, 1249, False, False),
        # ... Add other rows here until 51
    ]

st.title("🚀 SSC CGL 2025: High-Speed Predictor")

st.sidebar.header("Your Input")
u_marks = st.sidebar.number_input("Main Marks", 0.0, 390.0, 310.0)
u_stat = st.sidebar.number_input("Stat Marks", 0.0, 200.0, 0.0)
u_comp = st.sidebar.number_input("Comp Marks", 0.0, 60.0, 25.0)
u_cat = st.sidebar.selectbox("Category", ["UR", "OBC", "EWS", "SC", "ST"])

df = get_processed_database()

if df is not None:
    o_rank = (df['Main Paper Marks'] > u_marks).sum() + 1
    st.sidebar.metric("Global Rank", f"#{o_rank}")
    
    rules = {'UR': (18, 27), 'OBC': (15, 24), 'EWS': (15, 24), 'SC': (12, 21), 'ST': (12, 21)}
    u_b_min, u_c_min = rules.get(u_cat, (12, 21))
    
    results = []
    for lvl, name, ur_v, sc_v, st_v, obc_v, ews_v, tot_v, is_cpt, is_stat in get_all_posts():
        score_col = 'Total_Stat_Score' if is_stat else 'Main Paper Marks'
        user_val = (u_marks + u_stat) if is_stat else u_marks
        
        # Super-fast Filtering
        eligible_df = df[df['Passed_C']] if is_cpt else df[df['Passed_B']]
        
        # Quick Cutoff extraction
        ur_cut = eligible_df[score_col].iloc[ur_v-1] if len(eligible_df) >= ur_v else 0
        cat_df = eligible_df[eligible_df['Category'] == u_cat]
        cat_vac = {'SC': sc_v, 'ST': st_v, 'OBC': obc_v, 'EWS': ews_v}.get(u_cat, 0)
        cat_cut = cat_df[score_col].iloc[cat_vac-1] if len(cat_df) >= cat_vac else 0
        
        req_c = u_c_min if is_cpt else u_b_min
        if u_comp < req_c: res = "❌ Fail (Comp)"
        elif is_stat and u_stat == 0: res = "⚠️ Stat Absent"
        elif user_val >= ur_cut and ur_cut > 0: res = "⭐ VERY HIGH"
        elif user_val >= cat_cut and cat_cut > 0: res = "✅ GOOD CHANCE"
        else: res = "📉 LOW"

        results.append({"Post": name, "Level": lvl, "Cutoff": max(ur_cut, cat_cut), "Result": res})

    final_df = pd.DataFrame(results)
    search = st.text_input("🔍 Search Post Name", "")
    st.dataframe(final_df[final_df['Post'].str.contains(search, case=False)], use_container_width=True, hide_index=True)
    st.download_button("📂 Download Result", final_df.to_csv(index=False), "My_Result.csv")
