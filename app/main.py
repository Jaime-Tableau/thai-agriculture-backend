from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse, StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import pandas as pd
import numpy as np
import io
import tempfile
import os
from datetime import datetime

print("🚀 Running main.py")

app = FastAPI()

# ✅ Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your Vercel frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Hello, this is FastAPI!"}

@app.get("/debug_path")
def debug_path():
    return {"current_directory": os.getcwd()}

# ✅ Load CSV for dropdowns
df_dropdowns = pd.read_csv("agriculture_prices_cleaned.csv", encoding="utf-8-sig")
df_dropdowns['progroup_text'] = df_dropdowns['progroup_text'].astype(str).str.strip()
df_dropdowns['proname'] = df_dropdowns['proname'].astype(str).str.strip()

@app.get("/prices")
def read_prices(
    product: Optional[str] = Query(None),
    group: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
):
    df = pd.read_csv("agriculture_prices_cleaned.csv", encoding="utf-8-sig")
    df.replace({np.nan: None, np.inf: None, -np.inf: None}, inplace=True)
    df['progroup_text'] = df['progroup_text'].astype(str).str.strip()
    df['proname'] = df['proname'].astype(str).str.strip()

    if product:
        df = df[df['proname'].str.contains(product.strip(), na=False)]
    if group:
        df = df[df['progroup_text'].str.contains(group.strip(), na=False)]
    try:
        if start_date:
            datetime.strptime(start_date, "%Y-%m-%d")
            df = df[df['date'] >= start_date]
        if end_date:
            datetime.strptime(end_date, "%Y-%m-%d")
            df = df[df['date'] <= end_date]
    except ValueError:
        print("⚠️ Invalid date format. Use YYYY-MM-DD.")

    return JSONResponse(content=df.to_dict(orient="records"))

@app.get("/export")
def export_csv(
    product: Optional[str] = Query(None),
    group: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
):
    df = pd.read_csv("agriculture_prices_cleaned.csv", encoding="utf-8-sig")
    df['progroup_text'] = df['progroup_text'].astype(str).str.strip()
    df['proname'] = df['proname'].astype(str).str.strip()

    if product:
        df = df[df['proname'].str.contains(product.strip(), na=False)]
    if group:
        df = df[df['progroup_text'].str.contains(group.strip(), na=False)]
    try:
        if start_date:
            datetime.strptime(start_date, "%Y-%m-%d")
            df = df[df['date'] >= start_date]
        if end_date:
            datetime.strptime(end_date, "%Y-%m-%d")
            df = df[df['date'] <= end_date]
    except ValueError:
        print("⚠️ Invalid date format. Use YYYY-MM-DD.")

    output = io.StringIO()
    df.to_csv(output, index=False, encoding="utf-8-sig")
    output.seek(0)

    return StreamingResponse(output, media_type="text/csv", headers={
        "Content-Disposition": "attachment; filename=filtered_data.csv"
    })

@app.get("/export_excel", summary="Download filtered data as Excel", response_class=FileResponse)
def export_excel(
    product: Optional[str] = Query(None),
    group: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
):
    df = pd.read_csv("agriculture_prices_cleaned.csv", encoding="utf-8-sig")
    df['progroup_text'] = df['progroup_text'].astype(str).str.strip()
    df['proname'] = df['proname'].astype(str).str.strip()

    if product:
        df = df[df['proname'].str.contains(product.strip(), na=False)]
    if group:
        df = df[df['progroup_text'].str.contains(group.strip(), na=False)]
    try:
        if start_date:
            datetime.strptime(start_date, "%Y-%m-%d")
            df = df[df['date'] >= start_date]
        if end_date:
            datetime.strptime(end_date, "%Y-%m-%d")
            df = df[df['date'] <= end_date]
    except ValueError:
        print("⚠️ Invalid date format. Use YYYY-MM-DD.")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
        file_path = tmp.name
        df.to_excel(file_path, index=False, engine='openpyxl')

    return FileResponse(
        path=file_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename="filtered_data.xlsx"
    )

@app.get("/dropdowns/product-types")
def get_product_types():
    unique_types = df_dropdowns[['protype', 'protype_text']].drop_duplicates()
    return [{"value": row.protype, "label": row.protype_text} for _, row in unique_types.iterrows()]

@app.get("/dropdowns/product-groups")
def get_product_groups(type: str = Query(...)):
    try:
        type_int = int(type)
    except ValueError:
        return []
    filtered = df_dropdowns[df_dropdowns['protype'] == type_int]
    unique_groups = filtered[['progroup_text']].drop_duplicates()
    return [{"value": row.progroup_text, "label": row.progroup_text} for _, row in unique_groups.iterrows()]

@app.get("/dropdowns/product-names")
def get_product_names(group: str = Query(...)):
    group = group.strip()
    filtered = df_dropdowns[df_dropdowns['progroup_text'].str.contains(group, na=False)]
    unique_names = filtered[['proname']].drop_duplicates()
    return [{"value": row.proname, "label": row.proname} for _, row in unique_names.iterrows()]


print("✅ Routes loaded:")
for route in app.routes:
    print(route.path)
