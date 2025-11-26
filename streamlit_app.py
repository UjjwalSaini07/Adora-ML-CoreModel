import streamlit as st
import requests
import base64
from PIL import Image
import io

API_URL = "http://localhost:8000"

def api_post(endpoint, files=None):
    try:
        response = requests.post(f"{API_URL}{endpoint}", files=files)
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        st.error(f"❌ API error at {endpoint}")
        st.error(str(e))
        return None


def api_get(endpoint):
    try:
        response = requests.get(f"{API_URL}{endpoint}")
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        st.error(f"❌ API error at {endpoint}")
        st.error(str(e))
        return None


def show_image(img_bytes, caption="Preview"):
    st.image(img_bytes, caption=caption, use_column_width=True)


def page_header(title, emoji="✨"):
    st.markdown(
        f"""
        <h2 style="
            font-size: 28px;
            font-weight: 700;
            margin-top: 5px;
            margin-bottom: 15px;
        ">
            {emoji} {title}
        </h2>
        """,
        unsafe_allow_html=True,
    )


st.set_page_config(page_title="Adora Creative Engine", page_icon="🎨", layout="wide")

st.markdown("""
<style>
.sidebar .sidebar-content {
    background-color: #fafafa;
}
</style>
""", unsafe_allow_html=True)


st.sidebar.markdown(
    """
    <div style="font-size:24px; font-weight:700; margin-bottom:10px;">
        🎨 Adora ML Engine
    </div>
    """,
    unsafe_allow_html=True
)

page = st.sidebar.selectbox(
    "Navigation",
    [
        "Dashboard",
        "Upload",
        "Validate",
        "Auto-Fix",
        "Render",
        "Health"
    ]
)

# FEATURE LIST
st.sidebar.markdown("---")
st.sidebar.markdown("### ⭐ Features")
st.sidebar.markdown("""
- 📤 Upload Creatives  
- 🔍 OCR + Compliance  
- 👁️ YOLOv8 Detection  
- 🛠 Auto Layout Fix  
- 🎨 Final Rendering  
- ❤️ System Health  
""")

st.sidebar.markdown("---")
st.sidebar.markdown("**Version:** 1.0.0")

if page == "Dashboard":
    page_header("Welcome to Adora ML Creative Engine", "🚀")

    st.markdown("""
    This dashboard lets you:
    
    - Upload your product packshots  
    - Validate creative rules using OCR & YOLO  
    - Detect banned phrases  
    - Auto-fix layouts intelligently  
    - Render ready-to-publish creatives  
    
    Select an option from the **left sidebar** to begin.
    """)

    # Auto-health check
    health = api_get("/health")
    if health:
        st.success("Backend Connected ✔")
        st.json(health)
    else:
        st.error("Backend Not Reachable ❌")


# Upload
elif page == "Upload":
    page_header("Upload Packshot", "📤")

    uploaded = st.file_uploader("Choose a packshot image", type=["jpg", "png"])

    if uploaded:
        bytes_data = uploaded.read()
        show_image(bytes_data, "Uploaded Packshot")

        if st.button("Send to /upload"):
            with st.spinner("Processing..."):
                resp = api_post("/upload", files={"packshot": (uploaded.name, bytes_data)})
            if resp:
                st.success("Uploaded Successfully ✔")
                st.json(resp)


# Validate
elif page == "Validate":
    page_header("Validate Creative", "🔍")

    pack = st.file_uploader("Upload packshot", type=["jpg", "png"])

    if pack:
        img_bytes = pack.read()

        st.image(img_bytes, caption="Packshot", use_column_width=True)

        if st.button("Run Validation"):
            with st.spinner("Running OCR + Object Detection + Compliance Checks..."):
                resp = api_post(
                    "/validate", 
                    files={"packshot": (pack.name, img_bytes)}
                )

        if resp:
            st.subheader("📝 Extracted Text (OCR)")
            if resp["text"].strip():
                st.code(resp["text"])
            else:
                st.warning("No readable text detected.")


            st.subheader("👁 Object Detections")
            if resp["detections"]:
                st.json(resp["detections"])
            else:
                st.info("No objects detected.")

            # ------------------------------------------------------
            # BANNED PHRASE CHECK
            # ------------------------------------------------------
            st.subheader("🚫 Banned Phrase Scan")

            banned = resp.get("banned_phrases", [])
            if len(banned) == 0:
                st.success("✔ No banned phrases detected.")
            else:
                for item in banned:
                    st.error( f"⚠ **Phrase:** {item['phrase']} **Similarity:** {item['similarity']:.2f}" )

            st.subheader("📊 Validation Summary")

            if len(banned) == 0:
                st.success("Creative Passed All Checks ✔")
            else:
                st.error("Creative Failed Compliance ❌")


# Auto-Fix
elif page == "Auto-Fix":
    page_header("Auto-Fix Layout", "🛠")

    pack = st.file_uploader("Upload packshot", type=["jpg", "png"])

    if pack:
        bytes_data = pack.read()
        show_image(bytes_data, "Original Packshot")

        if st.button("Auto-Fix Now"):
            with st.spinner("Optimizing Layout..."):
                resp = api_post("/autofix", files={"packshot": (pack.name, bytes_data)})

            if resp:
                st.success("Auto-Fix Complete ✔")

                st.subheader("📦 Best Fix Candidate")
                st.json(resp["best_candidate"])

                st.subheader("📊 Rule Check Audit")
                st.json(resp["audit"])


# Render
elif page == "Render":
    page_header("Render Final Creative", "🎨")

    col1, col2 = st.columns(2)

    with col1:
        pack = st.file_uploader("Packshot", type=["jpg", "png"])

    with col2:
        bg = st.file_uploader("Background", type=["jpg", "png"])

    if pack and bg:
        st.write("#### Image Inputs")
        st.image([pack.read(), bg.read()], width=220)

        if st.button("Render Creative"):
            with st.spinner("Rendering..."):
                resp = api_post(
                    "/render",
                    files={
                        "packshot": (pack.name, pack.getbuffer()),
                        "background": (bg.name, bg.getbuffer()),
                    }
                )

            if resp and "image_base64" in resp:
                st.success("Rendered Successfully ✔")

                img_bytes = base64.b64decode(resp["image_base64"])
                st.image(img_bytes, caption="Final Render", use_column_width=True)
            else:
                st.error("No image received from backend")
                st.write("Backend Response:", resp)
            # if resp:
            #     st.success("Rendered Successfully ✔")
            #     st.json(resp)


# Health
elif page == "Health":
    page_header("System Health Status", "❤️")

    resp = api_get("/health")

    if resp:
        st.success("Backend Online ✔")
        st.json(resp)
    else:
        st.error("Backend Offline ❌")
