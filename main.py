import json
import streamlit as st
import pandas as pd
from airtable import Airtable
from requests import HTTPError

# ——— Load Airtable creds ———
with open("secrets.json", "r", encoding="utf-8") as f:
    creds = json.load(f)
API_KEY    = creds["airtable_api_key"]
BASE_ID    = creds["airtable_base_id"]
TABLE_NAME = creds.get("table_name", "Registrations")

airtable = Airtable(BASE_ID, TABLE_NAME, API_KEY)

# ——— Streamlit setup ———
st.set_page_config(page_title="Katılım Dashboard", layout="wide")
st.title("Katılım Durumu Yönetimi")

# ——— Fetch all records ———
try:
    records = airtable.get_all()
except HTTPError as e:
    st.error("Airtable’a bağlanırken hata: lütfen yetkileri ve tablo adını kontrol edin.")
    st.stop()

# ——— Build DataFrame & keep internal record_id ———
rows = []
for rec in records:
    row = rec["fields"].copy()
    row["_rec_id"] = rec["id"]
    rows.append(row)
df = pd.DataFrame(rows)

# ——— Ensure is_attended exists and is bool dtype ———
if "is_attended" not in df.columns:
    df["is_attended"] = False
df["is_attended"] = df["is_attended"].fillna(False).astype(bool)

# ——— Sort by auto‑number “id” descending ———
if "id" in df.columns:
    df = df.sort_values("id", ascending=False).reset_index(drop=True)

# ——— Prepare display DataFrame (hide _rec_id) ———
display_df = df.drop(columns=["_rec_id"], errors="ignore").copy()

# ——— Show interactive table with checkbox column ———
st.markdown("## Kayıt Listesi (Çift tıklayıp ‘is_attended’ sütununa tıklayarak işaretleyin)")
edited_df = st.data_editor(
    display_df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "is_attended": st.column_config.CheckboxColumn(
            label="Katıldı mı?",
            help="Katılım durumunu işaretleyin"
        )
    }
)

# ——— Apply updates button ———
if st.button("Apply"):
    updates = []
    # Compare original vs edited
    for i in edited_df.index:
        before = display_df.at[i, "is_attended"]
        after  = edited_df.at[i, "is_attended"]
        if before != after:
            rec_id = df.at[i, "_rec_id"]
            updates.append((rec_id, bool(after)))   # cast to native bool here

    if not updates:
        st.info("Herhangi bir değişiklik bulunamadı.")
    else:
        errors = False
        for rec_id, val in updates:
            try:
                airtable.update(rec_id, {"is_attended": val})
            except Exception as e:
                errors = True
                st.error(f"Kayıt {rec_id} güncellenirken hata: {e}")
        if not errors:
            st.success("Değişiklikler başarıyla kaydedildi!")
            st.experimental_rerun()