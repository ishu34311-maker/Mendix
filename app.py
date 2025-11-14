import streamlit as st
from pymongo import MongoClient
from datetime import datetime
import base64

# -------------------------------
#        PAGE CONFIG
# -------------------------------
st.set_page_config(
    page_title="College Management App",
    layout="wide"
)

# -------------------------------
#   CUSTOM CSS FOR BEAUTIFUL UI
# -------------------------------
page_bg = """
<style>
    [data-testid="stAppViewContainer"] {
        background-image: url("https://www.transparenttextures.com/patterns/asfalt-dark.png");
        background-size: cover;
        background-repeat: repeat;
    }

    .main-header {
        color: white;
        font-size: 40px;
        padding: 20px;
        text-align: center;
        background: linear-gradient(135deg, #8B0000, #3D3D3D);
        border-radius: 10px;
        margin-bottom: 25px;
    }

    .card {
        background-color: rgba(255,255,255,0.15);
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 20px;
        backdrop-filter: blur(10px);
        color: white;
        border: 1px solid rgba(255,255,255,0.3);
    }

    .stButton button {
        background-color: #8B0000 !important;
        color: white !important;
        border-radius: 8px !important;
        height: 45px;
        font-size: 18px;
    }
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

# -------------------------------
#         MONGO CONNECTION
# -------------------------------
MONGO_URI = st.secrets["mongo"]["uri"]
client = MongoClient(MONGO_URI)
db = client["college_app"]
users = db["users"]
labs = db["labs"]
teachers = db["teachers"]
attendance_db = db["attendance"]


# -------------------------------
#       LOGIN FUNCTION
# -------------------------------
def login(username, password):
    if username == "ishu_hada" and password == "Upmanyu13":
        return "admin"

    record = users.find_one({"username": username, "password": password})
    if record:
        return "user"
    return None


# -------------------------------
#   FILE ENCODER FOR UPLOADS
# -------------------------------
def encode_file(file):
    return base64.b64encode(file.read()).decode("utf-8")


# -------------------------------
#     LOGIN PAGE UI
# -------------------------------
def login_page():
    st.markdown('<div class="main-header">🔐 College App Login</div>', unsafe_allow_html=True)

    username = st.text_input("Enter Username")



