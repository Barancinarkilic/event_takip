import streamlit as st
from streamlit.components.v1 import html
import time

st.set_page_config(layout="wide")
st.title("Kayıt Listesi")

# ——— Refresh button ———
if st.button("🔄 Yenile"):
    st.experimental_rerun()

# ——— Build a cache‑busting URL ———
ts = int(time.time())  # seconds since epoch, changes every run
base_url = "https://airtable.com/embed/appjsVC6vEzetd4Ao/shr1DUeExgx4qLsX4"
iframe_src = f"{base_url}?viewControls=on&t={ts}"

# ——— Render the iframe ———
iframe = f"""
<iframe
  class="airtable-embed"
  src="{iframe_src}"
  frameborder="0"
  width="100%"
  height="650"
  style="background: transparent; border: 1px solid #ccc;"
></iframe>
"""

html(iframe, height=700)
