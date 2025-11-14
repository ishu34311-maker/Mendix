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
#   CLEAN UI (NO TEXTURE)
# -------------------------------
clean_ui = """
<style>
    [data-testid="stAppViewContainer"] {
        background-color: #f2f2f2; /* Light grey background */
    }

    .main-header {
        color: white;
        font-size: 40px;
        padding: 20px;
        text-align: center;
        background: linear-gradient(135deg, #8B0000, #4B4B4B);
        border-radius: 10px;
        margin-bottom: 25px;
    }

    .card {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 20px;
        border: 1px solid #ddd;
        color: black;
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
st.markdown(clean_ui, unsafe_allow_html=True)

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
    password = st.text_input("Enter Password", type="password")

    if st.button("Login"):
        role = login(username, password)
        if role:
            st.session_state["role"] = role
            st.session_state["username"] = username
            st.rerun()
        else:
            st.error("❌ Invalid username or password")


# -------------------------------
#     REGISTRATION FORM
# -------------------------------
def registration_form():
    st.markdown('<div class="card"><h3>📝 Fill Your Details</h3>', unsafe_allow_html=True)

    with st.form("reg_form"):
        name = st.text_input("Full Name")
        course = st.text_input("Course / Branch")
        faculty = st.text_input("Faculty Name")
        phone = st.text_input("Phone Number")
        hostel = st.radio("Hostel / Day Scholar", ["Hostel", "Day Scholar"])

        submit = st.form_submit_button("Save Details")

        if submit:
            users.insert_one({
                "username": st.session_state["username"],
                "name": name,
                "course": course,
                "faculty": faculty,
                "phone": phone,
                "hostel": hostel,
                "timestamp": datetime.now()
            })
            st.success("✔ Details Saved Successfully")

    st.markdown("</div>", unsafe_allow_html=True)


# -------------------------------
#        ADMIN – ADD LABS
# -------------------------------
def admin_add_labs():
    st.markdown('<div class="main-header">🔬 Add Lab Materials</div>', unsafe_allow_html=True)

    lab_name = st.text_input("Lab Name")
    floor = st.selectbox("Select Floor", ["6th Floor (Labs)", "7th Floor (Labs)"])
    file = st.file_uploader("Upload Files (PDF / Video)", type=["pdf", "mp4"])

    if st.button("Upload"):
        if lab_name and file:
            encoded = encode_file(file)
            labs.insert_one({
                "lab_name": lab_name,
                "floor": floor,
                "filename": file.name,
                "data": encoded,
                "timestamp": datetime.now()
            })
            st.success("✔ Uploaded Successfully")
        else:
            st.error("Please fill all fields!")


# -------------------------------
#      USER – VIEW LABS
# -------------------------------
def user_view_labs():
    st.markdown('<div class="main-header">📚 All Labs</div>', unsafe_allow_html=True)

    for item in labs.find():
        with st.container():
            st.markdown(f"<div class='card'><h4>{item['lab_name']} – {item['floor']}</h4>", unsafe_allow_html=True)
            decoded = base64.b64decode(item['data'])
            st.download_button("Download Material", decoded, file_name=item["filename"])
            st.markdown("</div>", unsafe_allow_html=True)


# -------------------------------
#     TEACHER INFO SECTION
# -------------------------------
def admin_teacher_info():
    st.markdown('<div class="main-header">👩‍🏫 Teacher / Mentor Details</div>', unsafe_allow_html=True)

    with st.form("t_form"):
        name = st.text_input("Teacher Name")
        dept = st.text_input("Department")
        email = st.text_input("Email")
        phone = st.text_input("Phone")

        submit = st.form_submit_button("Save")

        if submit:
            teachers.insert_one({
                "name": name,
                "dept": dept,
                "email": email,
                "phone": phone
            })
            st.success("✔ Saved Successfully")

    st.subheader("Saved Teachers:")
    for t in teachers.find():
        st.markdown(f"📌 **{t['name']}** – {t['dept']} – {t['email']} – {t['phone']}")


# -------------------------------
#     ATTENDANCE SYSTEM
# -------------------------------
def attendance():
    st.markdown('<div class="main-header">📅 Attendance</div>', unsafe_allow_html=True)

    with st.form("att_form"):
        status = st.radio("Mark Attendance", ["Present", "Absent"])
        submit = st.form_submit_button("Submit")

        if submit:
            attendance_db.insert_one({
                "username": st.session_state["username"],
                "status": status,
                "time": datetime.now()
            })
            st.success("✔ Attendance Recorded")

    st.subheader("Your History:")
    for a in attendance_db.find({"username": st.session_state["username"]}):
        st.write(f"{a['time']} — {a['status']}")


# -------------------------------
#           MAIN UI
# -------------------------------
def main():
    if "role" not in st.session_state:
        login_page()
        return

    st.sidebar.title("📌 Navigation")

    if st.session_state["role"] == "admin":
        choice = st.sidebar.radio("Menu", ["Dashboard", "Add Labs", "Teacher Details"])
        registration_form()

        if choice == "Dashboard":
            st.markdown('<div class="main-header">🎓 Admin Dashboard</div>', unsafe_allow_html=True)
            st.info("Welcome Admin!")
        elif choice == "Add Labs":
            admin_add_labs()
        elif choice == "Teacher Details":
            admin_teacher_info()

    else:
        choice = st.sidebar.radio("Menu", ["Dashboard", "Labs", "Lecture Theatre", "Cafeteria", "Attendance"])
        registration_form()

        if choice == "Dashboard":
            st.markdown('<div class="main-header">🎓 Student Dashboard</div>', unsafe_allow_html=True)
        elif choice == "Labs":
            user_view_labs()
        elif choice == "Lecture Theatre":
            st.info("Lower 4 floors + 3rd floor are Lecture Theatres.")
        elif choice == "Cafeteria":
            st.info("2 Floors are Cafeteria.")
        elif choice == "Attendance":
            attendance()


if __name__ == "__main__":
    main()
