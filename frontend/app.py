import streamlit as st
import requests
import uuid
from typing import List
from PIL import Image

BACKEND_URL = "http://localhost:8000"

st.set_page_config(page_title="Retail Media Creative Tool", layout="wide")

st.title("🧠 Retail Media Creative Tool")

# Simple multi-user session id
if "user_id" not in st.session_state:
    st.session_state["user_id"] = str(uuid.uuid4())

user_id = st.session_state["user_id"]

st.sidebar.subheader("Session")
st.sidebar.write(f"User ID: `{user_id}`")

st.sidebar.subheader("Creative Settings")
fmt = st.sidebar.selectbox("Format", ["story", "feed", "banner"])
canvas_id = st.sidebar.text_input("Canvas ID", value="canvas-" + user_id[:8])
width, height = {
    "story": (1080, 1920),
    "feed": (1080, 1080),
    "banner": (1200, 628),
}[fmt]

st.sidebar.markdown("### Packshot & Background")
packshot_file = st.sidebar.file_uploader("Packshot image", type=["png", "jpg", "jpeg"])
bg_file = st.sidebar.file_uploader("Background image (optional)", type=["png", "jpg", "jpeg"])

st.subheader("Text Blocks")
text_blocks: List[dict] = []

cols = st.columns(3)
with cols[0]:
    headline = st.text_input("Headline", "Fresh Strawberries")
with cols[1]:
    price = st.text_input("Price", "£2.50")
with cols[2]:
    tag = st.text_input("Tag", "Available at Tesco")

text_blocks.append({
    "id": "headline",
    "text": headline,
    "font_size": 24,
    "color": "#000000",
    "x": 100,
    "y": 220,
})
text_blocks.append({
    "id": "price",
    "text": price,
    "font_size": 32,
    "color": "#FF0000",
    "x": 100,
    "y": height - 200,
})
text_blocks.append({
    "id": "tag",
    "text": tag,
    "font_size": 18,
    "color": "#000000",
    "x": 100,
    "y": 80,
})

canvas = {
    "id": canvas_id,
    "user_id": user_id,
    "format": fmt,
    "width": width,
    "height": height,
    "background_image_id": None,
    "packshot_ids": ["packshot1"] if packshot_file else [],
    "text_blocks": text_blocks,
    "extra": {},
}

st.subheader("Preview (conceptual)")
st.write("This is a conceptual preview; backend handles true rendering & validation.")

with st.expander("Canvas JSON (for debugging)", expanded=False):
    st.json(canvas)

cols2 = st.columns(3)
with cols2[0]:
    if st.button("✅ Validate"):
        resp = requests.post(f"{BACKEND_URL}/validate", json=canvas)
        if resp.ok:
            data = resp.json()
            st.success(f"Passed: {data.get('passed', True)}")
            for issue in data.get("issues", []):
                if issue["severity"] == "error":
                    st.error(f"{issue['code']}: {issue['message']}")
                else:
                    st.warning(f"{issue['code']}: {issue['message']}")
        else:
            st.error(f"Backend error: {resp.status_code} {resp.text}")

with cols2[1]:
    if st.button("🛠 Auto-Fix"):
        resp = requests.post(f"{BACKEND_URL}/autofix", json={"canvas": canvas})
        if resp.ok:
            data = resp.json()
            st.success(f"Applied fixes: {data['applied_fixes']}")
            st.json(data["canvas"])
        else:
            st.error(f"Backend error: {resp.status_code} {resp.text}")

with cols2[2]:
    if st.button("🎨 Render"):
        resp = requests.post(f"{BACKEND_URL}/render", json={"canvas": canvas, "formats": [fmt]})
        if resp.ok:
            data = resp.json()
            st.success("Rendered creatives:")
            for c in data["creatives"]:
                st.write(f"{c['format']} → {c['path']} ({c['size_bytes']} bytes)")
            st.write(f"Audit log: {data['audit_log_path']}")
        else:
            st.error(f"Backend error: {resp.status_code} {resp.text}")

# ---------- BACKEND HEALTH SECTION ----------
st.subheader("🩺 Backend Health")

if st.button("🔍 Check Backend Health"):
    try:
        resp = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if resp.ok:
            data = resp.json()
            st.success(f"Status: {data.get('status', 'Unknown')}")
            st.write(f"Timestamp: {data.get('timestamp', 'N/A')}")
            st.write(f"Python: {data.get('python_version', 'N/A')}")
            st.write(f"System: {data.get('system', 'N/A')} ({data.get('machine', 'N/A')})")

            st.markdown("**Components:**")
            components = data.get("components", {})
            for name, status_text in components.items():
                st.write(f"- `{name}`: {status_text}")
        else:
            st.error(f"Health endpoint error: {resp.status_code} {resp.text}")
    except Exception as e:
        st.error(f"Failed to reach backend health endpoint: {e}")
