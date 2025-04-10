import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF
from datetime import datetime

px.set_mapbox_access_token("pk.eyJ1IjoiaW52ZXN0b3JzaG9yaXpvbiIsImEiOiJjbTk5Nm80NTUwYXJ0MnJxN3AyNWk2emgxIn0.vwAB8ce5FQpxMDxNLyrrMw")

df = pd.read_excel("Socioeconomic_MappableOnly.xlsx")
df.columns = df.columns.str.strip()
df["Suburb"] = df["Suburb"].str.lower().str.strip()

st.set_page_config(page_title="Propwealth Comparison", layout="wide")
st.title("🏙️ Propwealth Multi-Suburb Comparison")

st.sidebar.header("Filter Options")
state_options = sorted(df["State"].dropna().unique())
selected_states = st.sidebar.multiselect("Select State(s):", options=state_options, default=state_options)

filtered_df = df[df["State"].isin(selected_states)]
suburb_options = sorted(filtered_df["Suburb"].dropna().unique())
selected_suburbs = st.sidebar.multiselect("Select up to 5 Suburbs", options=suburb_options, default=suburb_options[:3])

if selected_suburbs:
    compared = filtered_df[filtered_df["Suburb"].isin(selected_suburbs)]

    # Map plot
    st.subheader("🗺️ Suburb Map View")
    fig_map = px.scatter_mapbox(
        compared,
        lat="Lat",
        lon="Long",
        color="Socio-economic Ranking",
        hover_name="Suburb",
        hover_data={"State": True, "Socio-economic Ranking": True},
        zoom=5,
        height=600,
        mapbox_style="mapbox://styles/mapbox/satellite-v9",
        color_continuous_scale=["#d73027", "#f46d43", "#fdae61", "#fee08b", "#d9ef8b",
                                "#a6d96a", "#66bd63", "#1a9850", "#006837", "#004529"]
    )
    st.plotly_chart(fig_map, use_container_width=True)

    # Radar chart
    st.subheader("📊 Radar Comparison")
    fig_radar = go.Figure()
    for _, row in compared.iterrows():
        fig_radar.add_trace(go.Scatterpolar(
            r=[row["Socio-economic Ranking"]],
            theta=["Socio-economic Ranking"],
            fill='toself',
            name=row["Suburb"].title()
        ))
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
        showlegend=True,
        height=500
    )
    st.plotly_chart(fig_radar, use_container_width=True)

    # AI Summary placeholder
    st.subheader("🧠 AI-Powered Suburb Summary")
    for _, row in compared.iterrows():
        st.markdown(f"**{row['Suburb'].title()} ({row['State']})**")
        score = row["Socio-economic Ranking"]
        if score >= 8:
            note = "an excellent score indicating strong infrastructure and livability."
        elif score >= 5:
            note = "a moderate score suitable for mid-income housing and growth potential."
        else:
            note = "a lower score which may indicate socio-economic challenges or development opportunity."
        st.markdown(f"> This suburb has a score of **{score}/10**, reflecting {note}")
        st.markdown("---")

    # PDF Generator
    if st.button("📥 Download Comparison PDF"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Propwealth Suburb Comparison Report", ln=True)
        pdf.cell(200, 10, txt="Generated on: " + datetime.now().strftime("%Y-%m-%d %H:%M"), ln=True)

        for _, row in compared.iterrows():
            suburb = row["Suburb"].title()
            state = row["State"]
            score = row["Socio-economic Ranking"]
            pdf.ln(5)
            pdf.cell(200, 10, txt=f"{suburb} ({state}) - Score: {score}/10", ln=True)
        pdf.output("Suburb_Comparison_Report.pdf")

        with open("Suburb_Comparison_Report.pdf", "rb") as f:
            st.download_button("Download PDF", data=f, file_name="Suburb_Comparison_Report.pdf", mime="application/pdf")
else:
    st.warning("Please select at least one suburb to visualize.")
