import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="SSC CGL 2025 Predictor", layout="wide")

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
        
        # Pre-calculating Computer Pass Status
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
    # Full data for analysis
    return [
        ("L-7", "CSS - ASO", 273, 104, 52, 185, 68, 682, True, False),
        ("L-7", "MEA - ASO", 44, 13, 0, 33, 10, 100, True, False),
        ("L-7", "CBIC - Inspector (Examiner)", 68, 18, 24, 13, 14, 137, True, False),
        ("L-7", "CBIC - Inspector (PO)", 138, 75, 20, 91, 29, 353, True, False),
        ("L-7", "CBIC - Inspector (Excise)", 611, 175, 82, 269, 169, 1306, True, False),
        ("L-7", "CBDT - IT Inspector", 176, 52, 39, 95, 27, 389, False, False),
        ("L-6", "Executive Assistant", 89, 24, 12, 40, 18, 183, True, False),
        ("L-5", "CAG - Auditor", 148, 55, 27, 98, 37, 365, False, False),
        ("L-5", "CGDA - Auditor", 477, 176, 88, 316, 117, 1174, False, False),
        ("L-4", "Tax Assistant (CBIC)", 256, 136, 82, 203, 94, 771, True, False),
        ("L-4", "Tax Assistant (CBDT)", 572, 171, 80, 340, 86, 1249, False, False),
        # You can paste the rest of the 51 posts here
    ]

st.title("🛡️ SSC CGL 2025: Final Corrected Predictor")

st.sidebar.header("Your Score")
u_marks = st.sidebar.number_input("Main Marks", 0.0, 390.0, 310.0)
u_stat = st.sidebar.number_input("Stat Marks", 0.0, 200.0, 0.0)
u_comp = st.sidebar.number_input("Comp Marks", 0.0, 60.0, 25.0)
u_cat = st.sidebar.selectbox("Category", ["UR", "OBC", "EWS", "SC", "ST"])

df = get_processed_database()

if df is not None:
    results = []
    cat_rules = {'UR': (18, 27), 'OBC': (15, 24), 'EWS': (15, 24), 'SC': (12, 21), 'ST': (12, 21)}
    u_b_min, u_c_min = cat_rules.get(u_cat, (12, 21))

    for lvl, name, ur_v, sc_v, st_v, obc_v, ews_v, tot_v, is_cpt, is_stat in get_all_posts():
        score_col = 'Total_Stat_Score' if is_stat else 'Main Paper Marks'
        user_val = (u_marks + u_stat) if is_stat else u_marks
        
        eligible_df = df[df['Passed_C']] if is_cpt else df[df['Passed_B']]
        
        # Calculate Cutoffs
        ur_cut = eligible_df[score_col].iloc[min(ur_v, len(eligible_df))-1] if ur_v > 0 else 999
        cat_df = eligible_df[eligible_df['Category'] == u_cat]
        cat_vac = {'SC': sc_v, 'ST': st_v, 'OBC': obc_v, 'EWS': ews_v}.get(u_cat, 0)
        cat_cut = cat_df[score_col].iloc[min(cat_vac, len(cat_df))-1] if cat_vac > 0 else 999
        
        final_cutoff = min(ur_cut, cat_cut)
        
        # FIXED CHANCE LOGIC
        req_c = u_c_min if is_cpt else u_b_min
        if u_comp < req_c: res = "❌ Computer Fail"
        elif user_val >= final_cutoff: res = "✅ High Chance"
        elif user_val >= (final_cutoff - 5): res = "🟡 Borderline"
        else: res = "📉 Low Chance"

        results.append({"Post": name, "Level": lvl, "Est. Cutoff": final_cutoff, "Prediction": res})

    st.dataframe(pd.DataFrame(results), use_container_width=True, hide_index=True)
