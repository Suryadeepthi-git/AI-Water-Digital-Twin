import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from src.simulator import METALS, run_simulation, build_alerts, COMPONENTS
from src.plant_3d import make_plant_figure

st.set_page_config(page_title="WaterTwin",page_icon="💧",layout="wide")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Manrope:wght@500;600;700;800&display=swap');
.stApp{background:linear-gradient(130deg,#f3f9ff,#fafaff 55%,#effaf8);color:#173f6c}
html,body,[class*="css"]{font-family:'DM Sans',sans-serif}
/* Keep the custom masthead below Streamlit toolbar with clear top spacing. */
.block-container, div[data-testid="stAppViewBlockContainer"] .block-container{
  padding-top:5rem !important; padding-bottom:2rem !important; max-width:1600px;
}
section[data-testid="stSidebar"]{background:linear-gradient(180deg,#eaf5ff,#f2f3ff);border-right:1px solid #dceafa}
h1,h2,h3{font-family:Manrope;color:#174b80}
div[data-testid="stMetric"]{background:white;border:1px solid #deebfa;border-radius:15px;padding:12px;box-shadow:0 3px 14px #386b9910}
div[data-testid="stMetricValue"]{color:#087f8c}
.stButton>button,.stDownloadButton>button{border-radius:11px;background:linear-gradient(100deg,#dcefff,#e5f7f2);border:1px solid #c9e2f7;color:#174b80;font-weight:700}
.whead{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;min-height:88px;box-sizing:border-box;padding:18px 22px;background:#ffffffdd;border:1px solid #deebfa;border-radius:17px;margin:0 0 18px;overflow:visible}
.whead > div:first-child{min-width:0;padding:2px 0 4px}
.brand{display:block;font:800 30px/1.4 Manrope,sans-serif;color:#174b80;padding:2px 0 3px;white-space:nowrap}
.sub{display:block;font-size:12px;line-height:1.6;color:#6683a8;letter-spacing:1px}
.pill{flex-shrink:0}
@media(max-width:700px){.whead{align-items:flex-start;flex-direction:column;min-height:0}.brand{font-size:26px}.sub{font-size:10px;letter-spacing:.5px}.pill{white-space:normal}}
.pill{padding:8px 13px;border-radius:20px;background:#effaf5;color:#16845f;font-size:12px}
.welcome{padding:20px 23px;min-height:145px;border-radius:17px;background:linear-gradient(110deg,#eef7ff,#e4f3ff 70%,#effaf8);border:1px solid #dfedfb}
.card{background:#ffffffed;border:1px solid #deebfa;border-radius:16px;padding:15px 17px;box-shadow:0 4px 16px #2c68a00d;margin-bottom:12px}
</style>
""",unsafe_allow_html=True)

PAGES=["Home","3D Plant View","Input & Simulation","Metal Comparison","Predictions & Analytics","Components Guide","Reports"]
if "page" not in st.session_state: st.session_state.page="Home"
if "result" not in st.session_state: st.session_state.result=None
with st.sidebar:
    st.markdown("## 💧 WaterTwin")
    st.caption("Industrial water treatment digital twin")
    st.session_state.page=st.radio("NAVIGATION",PAGES,index=PAGES.index(st.session_state.page))
    st.divider()
    treatment=st.selectbox("Treatment configuration",["Balanced conventional treatment","Enhanced metal removal","High turbidity treatment"])
    st.caption("Simulation mode · illustrative data only")

st.markdown('<div class="whead"><div><div class="brand">💧 WaterTwin</div><div class="sub">SMART MONITORING　•　CLEANER WATER　•　SUSTAINABLE FUTURE</div></div><div class="pill">● Simulation Mode　 (illustrative data)</div></div>',unsafe_allow_html=True)

def run_input_form():
    st.markdown("### 💧 Water quality input")
    st.caption("Enter raw-water measurements before treatment.")
    with st.form("input_form"):
        tab1,tab2=st.tabs(["Basic parameters","Metal concentrations"])
        with tab1:
            a,b=st.columns(2)
            with a:
                temp=st.number_input("Temperature (°C)",0.,60.,28.,.5)
                ph=st.number_input("Initial pH",0.,14.,7.2,.1)
                turb=st.number_input("Turbidity (NTU)",0.,2000.,35.,1.)
                cond=st.number_input("Conductivity (µS/cm)",0.,10000.,750.,10.)
            with b:
                flow=st.number_input("Flow rate (L/min)",.1,10000.,40.,1.)
                dose=st.number_input("Chemical dose (mg/L)",0.,500.,20.,1.)
                age=st.number_input("Filter age (hours)",0.,50000.,150.,10.)
                pressure=st.number_input("Filter pressure (bar)",0.,20.,1.6,.1)
                energy=st.number_input("Energy consumption (kWh)",0.,10000.,4.5,.1)
        with tab2:
            st.caption("Concentration before treatment (mg/L)")
            defaults=[.32,.24,.12,.18,.76,.05,.28]
            metals={}
            cols=st.columns(2)
            for i,m in enumerate(METALS):
                with cols[i%2]: metals[m]=st.number_input(m,0.,1000.,defaults[i],.01,format="%.3f",key="metal_"+m)
        submitted=st.form_submit_button("▶ Run treatment simulation",use_container_width=True)
    if submitted:
        st.session_state.result=run_simulation({"temperature":temp,"ph":ph,"turbidity":turb,"conductivity":cond,"flow_rate":flow,"chemical_dose":dose,"filter_age":age,"filter_pressure":pressure,"energy":energy},metals,treatment)
        st.success("Simulation completed. Dashboard results have been updated.")
    return st.session_state.result

def summary(r):
    if not r:
        st.info("Run a simulation from **Input & Simulation** to display results.")
        return
    a,b,c,d=st.columns(4)
    a.metric("Purification efficiency",f'{r["efficiency"]:.1f}%')
    b.metric("Outlet turbidity",f'{r["after"]["turbidity"]:.2f} NTU')
    c.metric("Water quality score",f'{r["quality_score"]:.0f} / 100')
    d.metric("Energy estimate",f'{r["energy"]:.2f} kWh')

def plant(r):
    st.markdown('<div class="card"><b>🏭 Animated 3D Water Purification Plant</b><br><small>Anime-inspired tanks, moving water, chemical dosing, settling particles, filter media and disinfection bubbles</small></div>',unsafe_allow_html=True)
    st.caption("Use ▶ PLAY ANIMATION above the 3D scene to watch the water-treatment process. Drag to rotate; scroll to zoom.")
    st.plotly_chart(make_plant_figure(r),use_container_width=True,key="watertwin_3d_plant",config={"displayModeBar":True,"scrollZoom":True})
    st.markdown("💧 Raw water　→　🧺 Screening　→　🧪 Chemical dosing + sedimentation　→　🪨 Filtration　→　✨ Disinfection　→　🌿 Clean-water outlet")

def metals_view(r):
    if not r: st.info("Run a simulation to compare metal concentrations."); return
    df=pd.DataFrame([{"Metal":m,"Before (mg/L)":r["metals_before"][m],"After (mg/L)":r["metals_after"][m],"Reduction (%)":100*(1-r["metals_after"][m]/r["metals_before"][m]) if r["metals_before"][m] else 0} for m in METALS])
    st.dataframe(df.style.format({"Before (mg/L)":"{:.3f}","After (mg/L)":"{:.3f}","Reduction (%)":"{:.1f}"}),use_container_width=True,hide_index=True)
    fig=go.Figure()
    fig.add_bar(name="Before",x=METALS,y=[r["metals_before"][m] for m in METALS],marker_color="#91c7e8")
    fig.add_bar(name="After",x=METALS,y=[r["metals_after"][m] for m in METALS],marker_color="#70c9a8")
    fig.update_layout(barmode="group",height=320,margin=dict(l=10,r=10,t=20,b=10),paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig,use_container_width=True,key="metal_comparison_chart")

r=st.session_state.result
page=st.session_state.page
if page=="Home":
    a,b=st.columns([1.7,1])
    with a: st.markdown('<div class="welcome"><span style="color:#5889bd">Welcome to</span><h2 style="margin:2px 0">WaterTwin</h2><p>An interactive digital twin for industrial water purification with process simulation, monitoring and optimization.</p></div>',unsafe_allow_html=True)
    with b:
        st.markdown('<div class="card"><b>Plant status</b><h2 style="color:#1caa7b;margin:8px 0">'+("Simulation complete" if r else "Awaiting inputs")+'</h2><small>Illustrative digital process model</small></div>',unsafe_allow_html=True)
    x,y=st.columns([.85,1.8])
    with x:
        st.markdown('<div class="card"><b>Water quality input</b><br><small>Basic parameters and metal concentrations</small></div>',unsafe_allow_html=True)
        run_input_form()
    with y: plant(r)
    p,q=st.columns([1.2,1])
    with p:
        st.markdown('<div class="card"><b>📈 Prediction and process results</b></div>',unsafe_allow_html=True); summary(r)
    with q:
        st.markdown('<div class="card"><b>🔔 Key alerts and insights</b></div>',unsafe_allow_html=True)
        for msg in build_alerts(r): st.write("• "+msg)
    st.caption("Educational simulation only. It cannot certify drinking-water safety or regulatory compliance.")
elif page=="Input & Simulation":
    run_input_form(); summary(st.session_state.result)
elif page=="3D Plant View":
    plant(r)
    st.markdown("### Process stages")
    for title,desc in COMPONENTS:
        with st.expander(title): st.write(desc)
elif page=="Metal Comparison":
    st.markdown("### Metal contents before and after treatment"); metals_view(r)
elif page=="Predictions & Analytics":
    st.markdown("### Prediction and analytics"); summary(r)
    if r:
        x,y=st.columns(2); x.metric("Before-treatment quality index",f'{r["before"]["quality"]:.0f}/100'); y.metric("After-treatment quality index",f'{r["quality_score"]:.0f}/100')
        st.caption("These values are transparent illustrative estimates, not output from a trained or validated industrial prediction model.")
elif page=="Components Guide":
    st.markdown("### Treatment components guide")
    for title,desc in COMPONENTS:
        with st.expander(title): st.write(desc)
elif page=="Reports":
    st.markdown("### Simulation report")
    if r:
        summary(r)
        df=pd.DataFrame([{"Metal":m,"Before (mg/L)":r["metals_before"][m],"After (mg/L)":r["metals_after"][m]} for m in METALS])
        st.dataframe(df,use_container_width=True,hide_index=True)
        st.download_button("⬇ Download metal report (CSV)",df.to_csv(index=False).encode(), "watertwin_metal_report.csv","text/csv")
    else: st.info("Run a simulation to create a report.")
