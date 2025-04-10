import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF

# Set access token
px.set_mapbox_access_token("pk.eyJ1IjoiaW52ZXN0b3JzaG9yaXpvbiIsImEiOiJjbTk5Nm80NTUwYXJ0MnJxN3AyNWk2emgxIn0.vwAB8ce5FQpxMDxNLyrrMw")

# Load filtered data
df = pd.read_excel("Socioeconomic_MappableOnly.xlsx")
df.columns = df.columns.str.strip()
df["Suburb"] = df["Suburb"].str.lower().str.strip()

# Streamlit layout
st.set_page_config(page_title="Propwealth Explorer", layout="wide")
st.title("🛰️ Propwealth Socioeconomic Explorer")

# Filters
st.sidebar.header("Filter Options")
state_options = sorted(df["State"].dropna().unique())
selected_states = st.sidebar.multiselect("Select State(s):", options=state_options, default=state_options)

filtered_df = df[df["State"].isin(selected_states)]
suburb_options = sorted(filtered_df["Suburb"].dropna().unique())
selected_suburb = st.sidebar.selectbox("Select Suburb:", options=suburb_options)

highlighted = filtered_df[filtered_df["Suburb"] == selected_suburb]
min_rank = int(df["Socio-economic Ranking"].min())
max_rank = int(df["Socio-economic Ranking"].max())

# Set map center
center_lat, center_lon = -33.8688, 151.2093  # default Sydney
if not highlighted.empty:
    center_lat = highlighted["Lat"].values[0]
    center_lon = highlighted["Long"].values[0]

# Plot using scatter_mapbox
fig = px.scatter_mapbox(
    filtered_df,
    lat="Lat",
    lon="Long",
    color="Socio-economic Ranking",
    hover_name="Suburb",
    hover_data={"State": True, "Socio-economic Ranking": True},
    color_continuous_scale=[
        "#d73027", "#f46d43", "#fdae61", "#fee08b", "#d9ef8b",
        "#a6d96a", "#66bd63", "#1a9850", "#006837", "#004529"
    ],
    range_color=(min_rank, max_rank),
    zoom=9,
    height=650,
    size_max=10,
    mapbox_style="mapbox://styles/mapbox/satellite-v9",
    center={"lat": center_lat, "lon": center_lon}
)
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
st.plotly_chart(fig, use_container_width=True)

# Summary + PDF
if not highlighted.empty:
    selected_data = highlighted.iloc[0]
    st.subheader(f"📊 Summary for {selected_data['Suburb'].title()}")
    st.markdown(f'''
    - **State**: {selected_data["State"]}
    - **Socio-economic Ranking**: {selected_data["Socio-economic Ranking"]}
    ''')

    def generate_pdf(suburb, state, score):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=f"Socioeconomic Report: {suburb}", ln=True)
        pdf.cell(200, 10, txt=f"State: {state}", ln=True)
        pdf.cell(200, 10, txt=f"Socio-economic Score: {score}/10", ln=True)
        pdf_path = f"{suburb}_report.pdf"
        pdf.output(pdf_path)
        return pdf_path

    if st.button("📥 Download PDF Report"):
        pdf_path = generate_pdf(selected_data['Suburb'].title(), selected_data["State"], selected_data["Socio-economic Ranking"])
        with open(pdf_path, "rb") as f:
            st.download_button(
                label="Download PDF",
                data=f,
                file_name=pdf_path,
                mime="application/pdf"
            )