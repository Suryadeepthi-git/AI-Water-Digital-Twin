"""Animated, cartoon/anime-inspired 3D water-treatment plant for WaterTwin."""
import math
import numpy as np
import plotly.graph_objects as go


def _cylinder_mesh(cx, cy, z0, z1, radius, color, opacity=1.0, n=32):
    """Open-top cylinder shell / liquid volume as a Plotly mesh."""
    xs, ys, zs = [], [], []
    for z in (z0, z1):
        for i in range(n):
            a = 2 * math.pi * i / n
            xs.append(cx + radius * math.cos(a))
            ys.append(cy + radius * math.sin(a))
            zs.append(z)
    ii, jj, kk = [], [], []
    for i in range(n):
        j = (i + 1) % n
        ii.extend([i, i + n, i])
        jj.extend([j, j, i + n])
        kk.extend([j + n, j + n, j + n])
    # bottom fan; the top stays open so the water surface is visible
    center = len(xs)
    xs.append(cx); ys.append(cy); zs.append(z0)
    for i in range(n):
        j = (i + 1) % n
        ii.append(center); jj.append(j); kk.append(i)
    return go.Mesh3d(x=xs, y=ys, z=zs, i=ii, j=jj, k=kk,
                    color=color, opacity=opacity, flatshading=False,
                    lighting=dict(ambient=0.65, diffuse=0.8, specular=0.45, roughness=0.35),
                    showscale=False, hoverinfo="skip")


def _ring(cx, cy, z, radius, color, width=5, n=48):
    a = np.linspace(0, 2 * np.pi, n)
    return go.Scatter3d(x=cx + radius*np.cos(a), y=cy + radius*np.sin(a), z=np.full(n,z),
                        mode="lines", line=dict(color=color, width=width), showlegend=False,
                        hoverinfo="skip")


def _line(points, color, width=7, opacity=1):
    return go.Scatter3d(x=[p[0] for p in points], y=[p[1] for p in points], z=[p[2] for p in points],
                        mode="lines", line=dict(color=color, width=width), opacity=opacity,
                        showlegend=False, hoverinfo="skip")


def make_plant_figure(result=None):
    fig = go.Figure()
    # Stage centres and a bright, friendly industrial palette.
    stages = [
        ("RAW WATER", 0.0, "#55bce8", "Intake"),
        ("SCREENING", 2.5, "#55c9d8", "Debris removal"),
        ("SEDIMENTATION", 5.0, "#e9b75b", "Solids settle"),
        ("FILTRATION", 7.5, "#55a8d9", "Sand + carbon"),
        ("DISINFECTION", 10.0, "#9b8ce8", "UV / dosing"),
        ("CLEAN WATER", 12.5, "#43c99b", "Outlet"),
    ]
    # Soft base / floor and pipe supports.
    fig.add_trace(go.Mesh3d(x=[-1.3,13.7,13.7,-1.3], y=[-2.2,-2.2,2.2,2.2], z=[-0.12]*4,
                            i=[0,0],j=[1,2],k=[2,3],color="#dceefa",opacity=.32,showscale=False,
                            hoverinfo="skip"))

    # Main transfer pipe: dark outline plus bright water core.
    pipe_pts = [(-1.0,0,.48),(1.1,0,.48),(1.4,0,.48),(3.6,0,.48),(3.9,0,.48),
                (6.1,0,.48),(6.4,0,.48),(8.6,0,.48),(8.9,0,.48),(11.1,0,.48),(11.4,0,.48),(13.2,0,.48)]
    fig.add_trace(_line(pipe_pts, "#347baf", 13, .95))
    fig.add_trace(_line(pipe_pts, "#8ce5f5", 6, 1))

    # Tanks: transparent shells, water bodies, rims and support feet.
    tank_specs = [
        (0.0, .78, .95, "#6bc9ed", .48),
        (2.5, .70, .90, "#62d1df", .46),
        (5.0, .78, .94, "#c9a36a", .50),
        (7.5, .68, .92, "#65b9dc", .47),
        (10.0, .72, .90, "#9b91e9", .48),
        (12.5, .78, .95, "#53cba0", .55),
    ]
    for idx,(x,rad,height,water_color,water_level) in enumerate(tank_specs):
        zbase=.18; ztop=zbase+height
        # outer vessel, water, bright top rim and lower ring
        fig.add_trace(_cylinder_mesh(x,0,zbase,ztop,rad,"#7ba9c8",.23))
        fig.add_trace(_cylinder_mesh(x,0,zbase+.05,zbase+.05+height*water_level,rad*.88,water_color,.68))
        fig.add_trace(_ring(x,0,ztop,rad,"#4b82a8",5))
        fig.add_trace(_ring(x,0,zbase+.08,rad,"#8cb9d4",4))
        # water surface highlight
        fig.add_trace(_ring(x,0,zbase+.05+height*water_level,rad*.86,"#d8fbff",3))
        # support feet
        for ang in (0, 2*math.pi/3, 4*math.pi/3):
            xx=x+rad*.72*math.cos(ang); yy=rad*.72*math.sin(ang)
            fig.add_trace(_line([(xx,yy,.02),(xx,yy,zbase+.08)],"#557b9a",5))
        # cute gauge / status lamp
        fig.add_trace(go.Scatter3d(x=[x+rad*.78],y=[-.10],z=[ztop-.12],mode="markers",
            marker=dict(size=7,color=["#54d6a5" if idx in (4,5) else "#ffd166"],line=dict(color="white",width=1)),
            showlegend=False,hoverinfo="skip"))

    # Screening bars across the second tank.
    for k in range(7):
        yy=-.46+k*.15
        fig.add_trace(_line([(2.5-.40,yy,.28),(2.5+.40,yy,.72)],"#f3f8fc",3))

    # Sedimentation cone + visible sludge blanket and settled solids.
    fig.add_trace(_line([(4.35,-.52,.22),(5.0,0,.02),(5.65,.52,.22)],"#b17c48",5))
    fig.add_trace(go.Scatter3d(x=[4.55,4.8,5.05,5.3,5.5],y=[-.2,.2,-.1,.25,0],z=[.27,.25,.23,.24,.22],
        mode="markers",marker=dict(size=8,color="#9b6841",opacity=.9),showlegend=False,hoverinfo="skip"))

    # Filter media bands, visible through the transparent vessel.
    for z,col in [(.38,"#d8b77b"),(.51,"#e8e2d1"),(.64,"#303f56")]:
        fig.add_trace(_ring(7.5,0,z,.52,col,9))

    # UV lamp / disinfection beam.
    fig.add_trace(_line([(9.65,-.05,.82),(10.35,-.05,.82)],"#8e7cff",10))
    for k in range(4):
        fig.add_trace(go.Scatter3d(x=[9.72+k*.18],y=[-.1],z=[.9],mode="markers",
            marker=dict(size=5,color="#e4dcff",symbol="circle"),showlegend=False,hoverinfo="skip"))

    # Chemical storage tank and bright dosing pipe pouring into sedimentation.
    fig.add_trace(_cylinder_mesh(3.55,-1.25,.18,.92,.34,"#d2a5ed",.28))
    fig.add_trace(_cylinder_mesh(3.55,-1.25,.22,.68,.29,"#c58bea",.78))
    fig.add_trace(_ring(3.55,-1.25,.92,.34,"#9567bd",4))
    fig.add_trace(_line([(3.55,-1.25,.90),(3.55,-.95,1.12),(4.25,-.55,1.12),(4.65,-.28,.72)],"#8c5bc4",8))
    fig.add_trace(_line([(3.55,-1.25,.90),(3.55,-.95,1.12),(4.25,-.55,1.12),(4.65,-.28,.72)],"#e6c9ff",3))
    fig.add_trace(go.Scatter3d(x=[3.55],y=[-1.25],z=[1.04],mode="text",text=["CHEMICAL"],
        textfont=dict(size=9,color="#754a9c"),showlegend=False,hoverinfo="skip"))

    # Labels and small anime-style sparkle accents.
    for title,x,color,subtitle in stages:
        fig.add_trace(go.Scatter3d(x=[x],y=[0],z=[1.42],mode="text",text=[title],
            textfont=dict(size=10,color="#244e73",family="Arial Black"),showlegend=False,hoverinfo="skip"))
        fig.add_trace(go.Scatter3d(x=[x],y=[0],z=[1.25],mode="text",text=[subtitle],
            textfont=dict(size=8,color="#6284a3"),showlegend=False,hoverinfo="skip"))

    # Moving traces are appended last so frames can update only these objects.
    flow_idx=len(fig.data)
    fig.add_trace(go.Scatter3d(x=[],y=[],z=[],mode="markers",
        marker=dict(size=7,color="#e7fbff",line=dict(color="#42b9e2",width=2),opacity=.98),
        name="Moving water",showlegend=False,hoverinfo="skip"))
    chem_idx=len(fig.data)
    fig.add_trace(go.Scatter3d(x=[],y=[],z=[],mode="markers",
        marker=dict(size=7,color="#d9a5ff",line=dict(color="#8b4dc4",width=1),opacity=1),
        name="Chemical droplets",showlegend=False,hoverinfo="skip"))
    settle_idx=len(fig.data)
    fig.add_trace(go.Scatter3d(x=[],y=[],z=[],mode="markers",
        marker=dict(size=5,color="#8d5b36",opacity=.95),name="Settling solids",showlegend=False,hoverinfo="skip"))
    bubble_idx=len(fig.data)
    fig.add_trace(go.Scatter3d(x=[],y=[],z=[],mode="markers",
        marker=dict(size=5,color="#e7faff",line=dict(color="#65cde8",width=1)),
        name="Air / UV bubbles",showlegend=False,hoverinfo="skip"))

    frames=[]
    nframes=48
    for frame_no in range(nframes):
        t=frame_no/(nframes-1)
        # Water pearls travel through the full pipeline, looping continuously.
        px=[]; py=[]; pz=[]
        for p in range(24):
            u=(t*1.25+p/24)%1.0
            px.append(-.95+14.1*u)
            py.append(.04*math.sin(2*math.pi*(u*4+p*.13)))
            pz.append(.48+.035*math.sin(2*math.pi*(u*5+p*.21)))
        # Purple coagulant drops fall from the dosing pipe into the settling tank.
        cx=[]; cy=[]; cz=[]
        for p in range(8):
            phase=(t*1.5+p/8)%1
            cx.append(4.52+.045*math.sin(phase*math.pi*4+p))
            cy.append(-.28+.035*math.cos(phase*math.pi*3+p))
            cz.append(.86-.58*phase)
        # Brown particles descend through the clarifier, then remain as sludge.
        sx=[]; sy=[]; sz=[]
        for p in range(18):
            phase=(t*1.1+p/18)%1
            sx.append(4.72+(p%6)*.105)
            sy.append(-.25+(p//6)*.22)
            sz.append(.82-.58*phase)
        # Tiny air bubbles rise in the disinfection tank.
        bx=[]; by=[]; bz=[]
        for p in range(10):
            phase=(t*1.8+p/10)%1
            bx.append(9.72+(p%5)*.13)
            by.append(-.18+(p//5)*.28)
            bz.append(.28+.66*phase)
        frames.append(go.Frame(name=str(frame_no),data=[
            go.Scatter3d(x=px,y=py,z=pz),go.Scatter3d(x=cx,y=cy,z=cz),
            go.Scatter3d(x=sx,y=sy,z=sz),go.Scatter3d(x=bx,y=by,z=bz)
        ],traces=[flow_idx,chem_idx,settle_idx,bubble_idx]))
    fig.frames=frames

    fig.update_layout(
        height=650, margin=dict(l=0,r=0,t=8,b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Arial, sans-serif",color="#315b80",size=11),
        scene=dict(
            xaxis=dict(visible=False,range=[-1.5,13.8]),
            yaxis=dict(visible=False,range=[-2.0,2.0]),
            zaxis=dict(visible=False,range=[-.15,1.8]),
            bgcolor="rgba(236,248,255,.65)",
            aspectmode="manual",aspectratio=dict(x=2.8,y=1.05,z=.72),
            camera=dict(eye=dict(x=1.65,y=2.35,z=1.45),projection=dict(type="perspective")),
            dragmode="orbit"
        ),
        updatemenus=[dict(type="buttons",direction="right",x=.02,y=1.08,
            xanchor="left",yanchor="top",showactive=False,
            buttons=[
                dict(label="▶ PLAY ANIMATION",method="animate",args=[None,{
                    "frame":{"duration":90,"redraw":True},"fromcurrent":True,
                    "transition":{"duration":45,"easing":"linear"},"mode":"immediate"}]),
                dict(label="Ⅱ PAUSE",method="animate",args=[[None],{
                    "frame":{"duration":0,"redraw":False},"mode":"immediate","transition":{"duration":0}}]),
                dict(label="↺ RESTART",method="animate",args=[["0"],{
                    "frame":{"duration":0,"redraw":True},"mode":"immediate","transition":{"duration":0}}]),
            ])],
        annotations=[dict(text="ANIME-INSPIRED WATER TREATMENT SIMULATION  •  PLAY TO WATCH EACH STAGE",
            x=.5,y=1.13,xref="paper",yref="paper",showarrow=False,
            font=dict(size=12,color="#47769c"))]
    )
    # Start with a populated frame so the scene is lively before Play is pressed.
    if frames:
        for trace_index, frame_trace in zip([flow_idx,chem_idx,settle_idx,bubble_idx],frames[0].data):
            fig.data[trace_index].x=frame_trace.x
            fig.data[trace_index].y=frame_trace.y
            fig.data[trace_index].z=frame_trace.z
    return fig
