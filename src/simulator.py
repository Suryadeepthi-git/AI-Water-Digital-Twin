METALS=["Lead (Pb)","Chromium (Cr)","Cadmium (Cd)","Arsenic (As)","Iron (Fe)","Mercury (Hg)","Copper (Cu)"]
COMPONENTS=[
("1. Screening","A coarse screen intercepts large debris such as leaves, plastics and fibres. It protects downstream equipment; it does not remove dissolved metals."),
("2. Chemical dosing","Coagulant and pH adjustment help destabilize fine particles so they form larger flocs. Actual chemicals and doses require jar testing."),
("3. Sedimentation","Water slows in a settling tank so heavier flocs and suspended solids can settle as sludge."),
("4. Filtration","Sand and activated-carbon media trap remaining particles. Dissolved-metal removal depends on the selected media and water chemistry."),
("5. Disinfection","A suitable disinfection process can inactivate many microorganisms when dose and contact time are controlled. This simulation does not validate pathogen removal."),
("6. Clean-water outlet","Outlet values are illustrative estimates. Laboratory testing is required before reuse, discharge or drinking-water decisions.")]
def clamp(x,lo,hi): return max(lo,min(hi,x))
def run_simulation(i,metals,treatment):
    turb=float(i["turbidity"]); ph=float(i["ph"]); cond=float(i["conductivity"]); dose=float(i["chemical_dose"]); age=float(i["filter_age"]); pressure=float(i["filter_pressure"]); flow=float(i["flow_rate"])
    cfg={"Balanced conventional treatment":1.0,"Enhanced metal removal":1.15,"High turbidity treatment":1.10}.get(treatment,1.0)
    dosef=clamp(.65+dose/45,.55,1.25); filt=clamp(1.05-age/2500-max(0,pressure-1.5)*.08,.55,1.05); flowf=clamp(1-max(0,flow-40)/250,.65,1)
    turbrem=clamp(.72*dosef*filt*flowf*cfg,.25,.96); metalrem=clamp((.68+.12*(treatment=="Enhanced metal removal")+.05*dosef)*filt*flowf,.35,.93)
    aftermet={}
    for m,v in metals.items():
        rem=clamp(metalrem-(.06 if m in ("Iron (Fe)","Copper (Cu)") else 0),.25,.93); aftermet[m]=round(float(v)*(1-rem),4)
    turbout=max(.1,turb*(1-turbrem)); phout=ph+(7-ph)*.55; condout=max(1,cond*(1-(.08 if treatment=="Enhanced metal removal" else .035)))
    tscore=clamp(100-turbout/2,0,100); pscore=clamp(100-abs(phout-7)*12,0,100)
    mscore=100*(1-sum(aftermet[m]/max(float(metals[m]),.0001) for m in metals)/len(metals)) if metals else 100
    quality=clamp(.45*tscore+.25*pscore+.30*mscore,0,100)
    return {"before":{"temperature":i["temperature"],"ph":ph,"turbidity":turb,"conductivity":cond,"quality":clamp(100-turb*.35-abs(ph-7)*8,0,100)},"after":{"ph":round(phout,2),"turbidity":round(turbout,2),"conductivity":round(condout,2)},"metals_before":{k:float(v) for k,v in metals.items()},"metals_after":aftermet,"efficiency":clamp(100*(.45*turbrem+.55*metalrem),0,99),"quality_score":quality,"energy":float(i["energy"])*(1+max(0,flow-40)/1000),"treatment":treatment}
def build_alerts(r):
    if not r: return ["Enter measurements and run a simulation to generate operating insights."]
    a=[]
    if r["before"]["ph"]<6.5 or r["before"]["ph"]>8.5: a.append("Initial pH is outside the illustrative 6.5–8.5 band; review pH adjustment.")
    else: a.append("Initial pH is within the illustrative operating band.")
    if r["before"]["turbidity"]>100: a.append("Raw-water turbidity is high; review screening and coagulation.")
    else: a.append("Turbidity reduction is estimated from the selected treatment settings.")
    if r["efficiency"]<65: a.append("Estimated efficiency is modest; review dose, filter age and flow.")
    else: a.append("Estimated removal performance is favourable for these simulation settings.")
    return a
