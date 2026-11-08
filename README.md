# WaterTwin — Anime-inspired animated 3D water treatment plant

An educational Streamlit dashboard for exploring an illustrative industrial water-treatment workflow. The 3D Plant View includes cartoon/anime-inspired treatment tanks and a Plotly animation with moving water, chemical droplets, sediment particles and disinfection bubbles.

## Run on macOS

```bash
cd ~/Downloads/WaterTwin
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Open the local URL printed by Streamlit (normally http://localhost:8501).

## Watch the animation

1. Choose **3D Plant View** in the sidebar (or view the Home page).
2. Click **▶ PLAY ANIMATION** above the 3D scene.
3. Use **Ⅱ PAUSE** or **↺ RESTART** as needed.
4. Drag the scene to rotate and scroll to zoom.

## Notes

- The animation is a visual illustration of treatment stages, not a physical fluid-dynamics model.
- Simulation outputs are educational estimates and are not a drinking-water safety certification or regulatory compliance result.
- Internet access may be needed the first time to install Python packages.
