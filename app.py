import streamlit as st
from pymongo import MongoClient
from datetime import datetime
import base64

# -----------------------------
#  MONGODB CONNECTION
# -----------------------------
MONGO_URI = st.secrets["mongo"]["uri"]
client = MongoClient(MONGO_URI)
db = client["college_app"]

users_collection = db["users"]
labs_collection = db["labs"]
attendance_collection = db["attendance"]
teachers_collection = db["teachers"]

# -----------------------------
#   PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="College App", layout="wide")


# -----------------------------
#   LOGIN FUNCTION
# -----------------------------
def login(username, password):
    if username == "ishu_hada" and password == "Upmanyu13":
        return "admin"
    record = users_collection.find_one({"username": username, "password": password})
    if record:
        return "user"
    return None


# -----------------------------
#   FILE ENCODING
# -----------------------------
def encode_file(uploaded_file):
    return base64.b64encode(uploaded_file.read()).decode("utf-8")


# -----------------------------
#   SIDEBAR NAVIGATION
# -----------------------------
def sidebar_menu(role):
    if role == "admin":
        return st.sidebar.selectbox(
            "Admin Menu",
            ["Dashboard", "Add Labs", "Teacher/Mentor Info", "Attendance Records"]
        )
    else:
        return st.sidebar.selectbox(
            "User Menu",
            ["Dashboard", "Labs", "Lecture Theatres", "Cafeteria", "Attendance"]
        )


# -----------------------------
#   LOGIN PAGE
# -----------------------------
def login_page():
    st.title("🔐 College App Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        role = login(username, password)
        if role:
            st.session_state["role"] = role
            st.session_state["username"] = username
            st.rerun()
        else:
            st.error("Invalid username or password")


# -----------------------------
#   REGISTRATION FORM (After Login)
# -----------------------------
def registration_form():
    st.header("📝 User/Admin Information Form")

    with st.form("registration_form"):
        name = st.text_input("Full Name")
        course = st.text_input("Course / Department")
        faculty = st.text_input("Faculty Name")
        phone = st.text_input("Phone Number")
        hostel = st.radio("Hostel / Day Scholar", ["Hostel", "Day Scholar"])

        submitted = st.form_submit_button("Save Details")

        if submitted:
            users_collection.insert_one({
                "username": st.session_state["username"],
                "name": name,
                "course": course,
                "faculty": faculty,
                "phone": phone,
                "hostel": hostel,
                "timestamp": datetime.now()
            })
            st.success("Details saved successfully!")


# -----------------------------
#   ADMIN PANEL – LAB UPLOAD
# -----------------------------
def admin_add_labs():
    st.subheader("🔬 Add Lab Materials (Assignments, PDFs, Videos)")

    lab_name = st.text_input("Lab Name (e.g., Computer Lab 3)")
    floor = st.selectbox("Floor", ["6th", "7th"])
    file = st.file_uploader("Upload File", type=["pdf", "mp4", "jpg", "png"])

    if st.button("Upload"):
        if lab_name and file:
            encoded = encode_file(file)
            labs_collection.insert_one({
                "lab_name": lab_name,
                "floor": floor,
                "filename": file.name,
                "filedata": encoded,
                "timestamp": datetime.now()
            })
            st.success("File uploaded successfully!")
        else:
            st.error("Please enter all required fields!")


# -----------------------------
#  USER – VIEW LAB MATERIALS
# -----------------------------
def user_labs():
    st.subheader("📚 Lab Materials")
    labs = labs_collection.find()

    for lab in labs:
        st.write(f"### {lab['lab_name']} (Floor: {lab['floor']})")
        st.write(lab["filename"])

        decoded = base64.b64decode(lab["filedata"])
        st.download_button("Download", data=decoded, file_name=lab["filename"])


# -----------------------------
#  LECTURE THEATRE SECTION
# -----------------------------
def lecture_theatre():
    st.subheader("🏫 Lecture Theatre Information")
    st.info("Lower 4 floors & 3rd floor are used for Lecture Theatres.")


# -----------------------------
#  CAFETERIA SECTION
# -----------------------------
def cafeteria():
    st.subheader("☕ Cafeteria Information")
    st.info("2 floors are dedicated to cafeterias.")


# -----------------------------
#  TEACHER / MENTOR SECTION
# -----------------------------
def teacher_info():
    st.subheader("👩‍🏫 Add Teacher/Mentor Information")

    with st.form("teacher_form"):
        name = st.text_input("Teacher Name")
        dept = st.text_input("Department")
        email = st.text_input("Email Address")
        phone = st.text_input("Phone Number")

        submitted = st.form_submit_button("Save Teacher Info")

        if submitted:
            teachers_collection.insert_one({
                "name": name,
                "department": dept,
                "email": email,
                "phone": phone
            })
            st.success("Teacher information saved!")

    st.divider()
    st.subheader("📄 Saved Teachers")

    for t in teachers_collection.find():
        st.write(f"**{t['name']}** – {t['department']} – {t['email']} – {t['phone']}")


# -----------------------------
#  ATTENDANCE SECTION
# -----------------------------
def attendance_page():
    st.subheader("📅 Attendance")

    with st.form("attendance_form"):
        status = st.radio("Mark Attendance", ["Present", "Absent"])
        submitted = st.form_submit_button("Submit")

        if submitted:
            attendance_collection.insert_one({
                "username": st.session_state["username"],
                "status": status,
                "timestamp": datetime.now()
            })
            st.success("Attendance recorded!")

    st.divider()
    st.subheader("📄 Your Attendance Records")

    for a in attendance_collection.find({"username": st.session_state["username"]}):
        st.write(f"{a['timestamp']} → {a['status']}")


# -----------------------------
#   MAIN APP
# -----------------------------
def main():
    if "role" not in st.session_state:
        login_page()
        return

    st.success(f"Logged in as: {st.session_state['role'].upper()}")
    registration_form()

    menu = sidebar_menu(st.session_state["role"])

    if st.session_state["role"] == "admin":
        if menu == "Dashboard":
            st.title("Admin Dashboard")
        elif menu == "Add Labs":
            admin_add_labs()
        elif menu == "Teacher/Mentor Info":
            teacher_info()
        elif menu == "Attendance Records":
            st.write(list(attendance_collection.find()))

    else:  # USER
        if menu == "Dashboard":
            st.title("Student Dashboard")
        elif menu == "Labs":
            user_labs()
        elif menu == "Lecture Theatres":
            lecture_theatre()
        elif menu == "Cafeteria":
            cafeteria()
        elif menu == "Attendance":
            attendance_page()


if __name__ == "__main__":
    main()
