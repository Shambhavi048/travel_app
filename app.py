import streamlit as st
from pymongo import MongoClient

st.set_page_config(page_title="Travel Booking App", layout="wide")

# --------------------- DATABASE CONNECTION ---------------------
client = MongoClient(st.secrets["MONGO_URI"])
db = client["travel_app"]

users_col = db["users"]
catalogue_col = db["catalogue"]
bookings_col = db["bookings"]

# --------------------- AUTH HELPERS ---------------------
def admin_login(username, password):
    return username == "shambhavi" and password == "shambhavi01"

def user_login(username, password):
    return users_col.find_one({"username": username, "password": password})

def register_user(fullname, username, password):
    if users_col.find_one({"username": username}):
        return False
    users_col.insert_one({
        "fullname": fullname,
        "username": username,
        "password": password
    })
    return True

# --------------------- UI FUNCTIONS ---------------------

# -------- ADMIN PAGES --------
def admin_dashboard():
    st.title("Admin Dashboard")

    menu = ["Create Travel Catalogue", "View Catalogue", "User Management", "Travel Bookings"]
    choice = st.sidebar.selectbox("Admin Menu", menu)

    # ---- CREATE CATALOGUE ----
    if choice == "Create Travel Catalogue":
        st.subheader("Add New Travel Catalogue Item")

        location = st.text_input("Location Name")
        hotel_name = st.text_input("Hotel Name")
        hotel_cost = st.number_input("Hotel Cost Per Night", min_value=0)
        activity_name = st.text_input("Activity Name")
        activity_cost = st.number_input("Activity Cost", min_value=0)

        if st.button("Submit"):
            catalogue_col.insert_one({
                "location": location.lower(),
                "hotel": hotel_name,
                "hotel_cost": hotel_cost,
                "activity": activity_name,
                "activity_cost": activity_cost
            })
            st.success("Catalogue added successfully!")

        st.write("---")
        st.write("### Current Catalogue")
        for item in catalogue_col.find():
            st.write(item)

    # ---- VIEW CATALOGUE ----
    elif choice == "View Catalogue":
        st.subheader("All Catalogue Entries")
        data = list(catalogue_col.find())
        st.write(data)

    # ---- USER MANAGEMENT ----
    elif choice == "User Management":
        st.subheader("Registered Users")
        users = list(users_col.find({}, {"_id": 0}))
        st.table(users)

    # ---- VIEW BOOKINGS ----
    elif choice == "Travel Bookings":
        st.subheader("All User Bookings")
        bookings = list(bookings_col.find({}, {"_id": 0}))
        st.table(bookings)


# -------- USER PAGES --------
def user_dashboard(user):
    st.title(f"Welcome, {user['fullname']} 👋")

    menu = ["Search & Book", "Manage Bookings"]
    choice = st.sidebar.selectbox("User Menu", menu)

    # ---- SEARCH AND BOOK ----
    if choice == "Search & Book":
        st.subheader("Search for a Travel Location")

        query = st.text_input("Enter Location Name")

        if st.button("Search"):
            results = list(catalogue_col.find({"location": query.lower()}))

            if not results:
                st.error("No results found for this location.")
            else:
                st.success("Results found!")
                for item in results:
                    st.write(f"### Hotel: {item['hotel']} — {item['hotel_cost']} per night")
                    st.write(f"Activity: {item['activity']} — {item['activity_cost']}")

                    if st.button(f"Book {item['hotel']} ({item['activity']})", key=str(item["_id"])):
                        total_cost = item['hotel_cost'] + item['activity_cost']
                        bookings_col.insert_one({
                            "username": user['username'],
                            "location": item['location'],
                            "hotel": item['hotel'],
                            "activity": item['activity'],
                            "total_cost": total_cost
                        })
                        st.success(f"Booking confirmed! Total cost = {total_cost}")

    # ---- MANAGE BOOKINGS ----
    elif choice == "Manage Bookings":
        st.subheader("Your Bookings")

        user_bookings = list(bookings_col.find(
            {"username": user["username"]},
            {"_id": 0}
        ))

        if user_bookings:
            st.table(user_bookings)
        else:
            st.info("You have not made any bookings yet.")


# --------------------- MAIN APP ---------------------
def main():
    st.title("🌍 Travel Booking App")

    page = st.sidebar.selectbox("Choose Login Type", ["Admin Login", "User Login"])

    # ------------------ ADMIN LOGIN ------------------
    if page == "Admin Login":
        st.subheader("Admin Login")
        admin_user = st.text_input("Username")
        admin_pass = st.text_input("Password", type="password")

        if st.button("Login as Admin"):
            if admin_login(admin_user, admin_pass):
                admin_dashboard()
            else:
                st.error("Invalid Admin Credentials")

    # ------------------ USER LOGIN ------------------
    elif page == "User Login":
        user_mode = st.radio("Choose Option", ["Existing User", "New User"])

        # ---- NEW USER ----
        if user_mode == "New User":
            st.subheader("Create New Account")
            fullname = st.text_input("Full Name")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")

            if st.button("Register"):
                if register_user(fullname, username, password):
                    st.success("Registration successful! You can now log in.")
                else:
                    st.error("Username already exists.")

        # ---- EXISTING USER ----
        else:
            st.subheader("User Login")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")

            if st.button("Login"):
                user = user_login(username, password)
                if user:
                    user_dashboard(user)
                else:
                    st.error("Invalid username or password")


if __name__ == "__main__":
    main()
