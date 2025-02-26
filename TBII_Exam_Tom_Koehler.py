import streamlit as st
import random
import math
from pymongo import MongoClient
import bcrypt

# ---------------------------------------------------------------------
# MONGODB CONNECTION SETUP
# ---------------------------------------------------------------------
# Replace <db_password> with your actual password.
connection_string = "mongodb+srv://tomkoehler:<db_password>@tb-ii.dw57u.mongodb.net/?retryWrites=true&w=majority&appName=TB-II"
client = MongoClient(connection_string)

# Choose your database name. For example, "CharacterSheets".
db = client["CharacterSheets"]

# Use your collections: "userdata" for user info and "charactersheets" for saving character data.
users_col = db["userdata"]
sheets_col = db["charactersheets"]

# ---------------------------------------------------------------------
# SESSION STATE INITIALIZATION
# ---------------------------------------------------------------------
# These values persist between interactions (page reloads)
if "reroll_limit" not in st.session_state:
    st.session_state.reroll_limit = 3  # Maximum number of attribute rerolls
if "reroll_count" not in st.session_state:
    st.session_state.reroll_count = 0  # Number of rerolls used
if "results" not in st.session_state:
    st.session_state.results = [None] * 8  # Placeholder for 8 attribute values
if "luck" not in st.session_state:
    st.session_state.luck = ""  # Calculated luck value
if "career_skill_points" not in st.session_state:
    st.session_state.career_skill_points = ""  # Calculated career skill points
if "free_skill_points" not in st.session_state:
    st.session_state.free_skill_points = ""  # Calculated free skill points
if "special_trait_results" not in st.session_state:
    st.session_state.special_trait_results = []  # List for special traits
if "special_trait_text" not in st.session_state:
    st.session_state.special_trait_text = ""  # Combined special traits text
if "monthly_wage" not in st.session_state:
    st.session_state.monthly_wage = ""  # Random monthly wage
if "magazine" not in st.session_state:
    st.session_state.magazine = 15  # Bullet count in the magazine
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False  # Login status
if "user_id" not in st.session_state:
    st.session_state.user_id = None  # MongoDB user ID for logged-in user

# ---------------------------------------------------------------------
# GLOBAL HEADER & CUSTOM CSS
# ---------------------------------------------------------------------
st.title("Space Gothic Character Generator")
st.subheader("Mercenary Class")


# Helper function to load local CSS from a file.
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


# Load your CSS file (make sure style.css is in the same folder as this script)
local_css("style.css")

# Insert an image with a custom id so our CSS can position it.
st.markdown(
    '<img id="custom-image" src="https://raw.githubusercontent.com/tkoe1999/TBII_Tom_Koehler/main/Mercenary_SpaceGothic_Art.png" alt="Mercenary Art">',
    unsafe_allow_html=True
)


# ---------------------------------------------------------------------
# USER REGISTRATION & LOGIN PAGES
# ---------------------------------------------------------------------
def registration_page():
    st.title("Register")
    username = st.text_input("Username", key="reg_username")
    email = st.text_input("Email", key="reg_email")
    password = st.text_input("Password", type="password", key="reg_password")
    if st.button("Register"):
        if username and email and password:
            # Check if user already exists.
            existing_user = users_col.find_one({"email": email})
            if existing_user:
                st.error("A user with that email already exists!")
            else:
                # Hash the password for security.
                hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
                # Insert new user into the "userdata" collection.
                users_col.insert_one({
                    "username": username,
                    "email": email,
                    "password": hashed
                })
                st.success("Registration successful!")
        else:
            st.error("Please fill in all fields.")


def login_page():
    st.title("Login")
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")
    if st.button("Login"):
        user = users_col.find_one({"email": email})
        if user and bcrypt.checkpw(password.encode("utf-8"), user["password"]):
            st.session_state.logged_in = True
            st.session_state.user_id = str(user["_id"])
            st.success("Logged in successfully!")
        else:
            st.error("Invalid credentials!")


def save_character_sheet():
    """
    Save the current character sheet into the "charactersheets" collection,
    linking it to the logged-in user.
    """
    if st.session_state.logged_in:
        sheet_data = {
            "user_id": st.session_state.user_id,
            "attributes": st.session_state.results,
            "luck": st.session_state.luck,
            "career_skill_points": st.session_state.career_skill_points,
            "free_skill_points": st.session_state.free_skill_points,
            "special_traits": st.session_state.special_trait_results,
            "monthly_wage": st.session_state.monthly_wage
        }
        sheets_col.insert_one(sheet_data)
        st.success("Character sheet saved!")
    else:
        st.error("You must be logged in to save your character sheet.")


# ---------------------------------------------------------------------
# CALCULATION FUNCTIONS (for character attributes)
# ---------------------------------------------------------------------
def calculate_attributes():
    """
    Generate random values for character attributes.
    Resets reroll count and clears special traits.
    """
    st.session_state.reroll_count = 0
    st.session_state.special_trait_results = []
    st.session_state.special_trait_text = ""
    equations = [
        lambda: random.randint(4, 40) + 50,  # Strength
        lambda: random.randint(5, 50) + 40,  # Agility
        lambda: random.randint(5, 50) + 30,  # Willpower
        lambda: random.randint(3, 30) + 60,  # Endurance
        lambda: random.randint(6, 60) + 20,  # Luck (placeholder)
        lambda: random.randint(3, 30) + 70,  # Experience
        lambda: random.randint(8, 80) + 40,  # Weight
        lambda: random.randint(5, 50) + 30  # Intelligence
    ]
    st.session_state.results = [eq() for eq in equations]
    st.session_state.luck = math.ceil(st.session_state.results[2] / 2 + 20 + random.randint(3, 30))
    st.session_state.career_skill_points = math.ceil(3 * st.session_state.results[5])
    st.session_state.free_skill_points = math.ceil(st.session_state.results[5] + st.session_state.results[7])


def reroll_attribute(index):
    """
    Reroll a specific attribute if under the reroll limit.
    Also updates dependent values (luck, skill points).
    """
    if st.session_state.reroll_count < st.session_state.reroll_limit:
        equations = [
            lambda: random.randint(4, 40) + 50,
            lambda: random.randint(5, 50) + 40,
            lambda: random.randint(5, 50) + 30,
            lambda: random.randint(3, 30) + 60,
            lambda: random.randint(6, 60) + 20,
            lambda: random.randint(3, 30) + 70,
            lambda: random.randint(8, 80) + 40,
            lambda: random.randint(5, 50) + 30
        ]
        new_val = equations[index]()
        st.session_state.results[index] = new_val
        st.session_state.reroll_count += 1

        if index == 2:
            st.session_state.luck = math.ceil(st.session_state.results[2] / 2 + 20 + random.randint(3, 30))
        if index in [5, 7]:
            st.session_state.career_skill_points = math.ceil(3 * st.session_state.results[5])
            st.session_state.free_skill_points = math.ceil(st.session_state.results[5] + st.session_state.results[7])
    else:
        st.warning("Reroll limit reached!")


def roll_special_trait():
    """
    Choose a random special trait and add it to the list.
    """
    if st.session_state.reroll_count < st.session_state.reroll_limit:
        traits = [
            "Greater Endurance", "Plasma Gunner", "Sharpshooter", "Sniper",
            "Sixth Sense", "Cyborg", "Combat Fatigue", "Greed",
            "Khirf Addiction", "Bully"
        ]
        trait = random.choice(traits)
        st.session_state.special_trait_results.append(trait)
        st.session_state.special_trait_text = "\n".join(st.session_state.special_trait_results)
        st.session_state.reroll_count += 1
    else:
        st.warning("Reroll limit reached!")


def roll_monthly_wage():
    """
    Generate a random monthly wage.
    """
    st.session_state.monthly_wage = random.randint(3, 30) + 20


# ---------------------------------------------------------------------
# INVENTORY/ATTACKING PAGE FUNCTIONS (weapon and shooting simulation)
# ---------------------------------------------------------------------
def display_magazine():
    """
    Display the magazine status as a row of green (bullets) and white (empty slots) blocks.
    """
    bullets_left = st.session_state.magazine
    total_bullets = 15
    filled = "🟩"
    empty = "⬜"
    magazine_display = filled * bullets_left + empty * (total_bullets - bullets_left)
    st.markdown("**Magazine:** " + magazine_display)


def inventory_page():
    """
    Inventory page:
    - Shows the weapon's stats.
    - Allows the user to simulate firing the Luger .357 Automagnum.
    - Displays hit and damage results in a fixed container.
    """
    st.title("Inventory")
    st.subheader("Weapon: Luger .357 Automagnum")

    # Weapon Stats: Display labels and values
    cols_top = st.columns(5)
    cols_top[0].markdown("**Damage:**")
    cols_top[1].markdown("**Range:**")
    cols_top[2].markdown("**Fire Rate:**")
    cols_top[3].markdown("**Burst Rate:**")
    cols_top[4].markdown("**Magazine Size:**")

    cols_bottom = st.columns(5)
    cols_bottom[0].markdown("1d10+2")
    cols_bottom[1].markdown("Short 20m <br> Medium 40m <br> Long 60m", unsafe_allow_html=True)
    cols_bottom[2].markdown("3")
    cols_bottom[3].markdown("5")
    cols_bottom[4].markdown("15")

    st.markdown("---")

    # Shooting Skill Section: Adjust shooting chance based on range selection.
    range_option = st.radio("Select Range", ("Short", "Medium", "Long"), index=1)
    if range_option == "Short":
        range_modifier = 10
    elif range_option == "Medium":
        range_modifier = 0
    else:
        range_modifier = -10
    base_chance = 65
    final_chance = base_chance + range_modifier
    st.write("Adjusted Shooting Chance:", final_chance, "%")

    # Firing Mode Buttons: Single Fire, Semi Burst, Full Burst, Reload.
    firing_cols = st.columns(4)
    single_fire_btn = firing_cols[0].button("Single Fire")
    semi_burst_btn = firing_cols[1].button("Semi Burst")
    full_burst_btn = firing_cols[2].button("Full Burst")
    reload_btn = firing_cols[3].button("Reload")

    # Fixed results storage (for a consistent display area)
    if "fire_results" not in st.session_state:
        st.session_state.fire_results = ""

    # Firing Logic:
    if single_fire_btn:
        if st.session_state.magazine >= 1:
            st.session_state.magazine -= 1
            shots = 1
            hits = 0
            total_damage = 0
            hit_rolls = []
            damage_rolls = []
            for _ in range(shots):
                roll = random.randint(1, 100)
                hit_rolls.append(roll)
                if roll <= final_chance:
                    hits += 1
                    d = random.randint(3, 12)  # Damage between 3 and 12
                    damage_rolls.append(d)
                    total_damage += d
                else:
                    damage_rolls.append(0)
            st.session_state.fire_results = (
                f"**Single Fire**<br>"
                f"Hit Rolls: {hit_rolls}<br>"
                f"Total Hits: {hits}<br>"
                f"Damage Rolls: {damage_rolls}<br>"
                f"Total Damage: {total_damage}"
            )
        else:
            st.session_state.fire_results = "Out of bullets!"

    if semi_burst_btn:
        if st.session_state.magazine >= 3:
            st.session_state.magazine -= 3
            shots = 3
            hits = 0
            total_damage = 0
            hit_rolls = []
            damage_rolls = []
            for _ in range(shots):
                roll = random.randint(1, 100)
                hit_rolls.append(roll)
                if roll <= final_chance:
                    hits += 1
                    d = random.randint(3, 12)
                    damage_rolls.append(d)
                    total_damage += d
                else:
                    damage_rolls.append(0)
            st.session_state.fire_results = (
                f"**Semi Burst**<br>"
                f"Hit Rolls: {hit_rolls}<br>"
                f"Total Hits: {hits}<br>"
                f"Damage Rolls: {damage_rolls}<br>"
                f"Total Damage: {total_damage}"
            )
        else:
            st.session_state.fire_results = "Not enough bullets for Semi Burst!"

    if full_burst_btn:
        if st.session_state.magazine >= 5:
            st.session_state.magazine -= 5
            shots = 5
            hits = 0
            total_damage = 0
            hit_rolls = []
            damage_rolls = []
            for _ in range(shots):
                roll = random.randint(1, 100)
                hit_rolls.append(roll)
                if roll <= final_chance:
                    hits += 1
                    d = random.randint(3, 12)
                    damage_rolls.append(d)
                    total_damage += d
                else:
                    damage_rolls.append(0)
            st.session_state.fire_results = (
                f"**Full Burst**<br>"
                f"Hit Rolls: {hit_rolls}<br>"
                f"Total Hits: {hits}<br>"
                f"Damage Rolls: {damage_rolls}<br>"
                f"Total Damage: {total_damage}"
            )
        else:
            st.session_state.fire_results = "Not enough bullets for Full Burst!"

    if reload_btn:
        st.session_state.magazine = 15
        st.session_state.fire_results = "Magazine reloaded."

    # Display Magazine above results.
    display_magazine()

    # Fixed Results Container: Reserve fixed space for firing results.
    st.markdown(
        f'<div style="min-height:150px;">{st.session_state.fire_results}</div>',
        unsafe_allow_html=True
    )


# ---------------------------------------------------------------------
# ATTRIBUTES PAGE FUNCTIONS (for character attributes)
# ---------------------------------------------------------------------
def attributes_page():
    """
    Attributes page:
    - Calculate and display character attributes.
    - Allows rerolls and shows computed skill points.
    - Provides options for special traits and monthly wage.
    - Option to save the character sheet if logged in.
    """
    st.title("Attributes & Rolls")
    if st.button("Calculate Attributes"):
        calculate_attributes()

    if st.session_state.results and None not in st.session_state.results:
        attribute_names = ["Strength", "Agility", "Willpower", "Endurance",
                           "Luck (base)", "Experience", "Weight", "Intelligence"]
        for i, name in enumerate(attribute_names):
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                st.write(name)
            with col2:
                st.write(st.session_state.results[i])
            with col3:
                if st.button("Reroll", key=f"reroll_{i}"):
                    reroll_attribute(i)
        st.markdown("---")
        st.write("**Computed Luck:**", st.session_state.luck)
        st.write("**Career Skill Points:**", st.session_state.career_skill_points)
        st.write("**Free Skill Points:**", st.session_state.free_skill_points)
        st.write(f"**Rerolls used:** {st.session_state.reroll_count} / {st.session_state.reroll_limit}")
    else:
        st.info("Click 'Calculate Attributes' to begin.")

    st.markdown("## Special Traits")
    if st.button("Roll Special Trait"):
        roll_special_trait()
    if st.session_state.special_trait_text:
        st.text(st.session_state.special_trait_text)

    st.markdown("## Monthly Wage")
    if st.button("Roll Monthly Wage"):
        roll_monthly_wage()
    if st.session_state.monthly_wage:
        st.write("Monthly Wage:", st.session_state.monthly_wage)

    # Button to save the character sheet (only if the user is logged in)
    if st.button("Save Character Sheet"):
        save_character_sheet()


# ---------------------------------------------------------------------
# PERSONAL DOSSIER PAGE FUNCTIONS
# ---------------------------------------------------------------------
def personal_dossier_page():
    """
    Personal Dossier page:
    - Allows the user to enter personal details.
    """
    st.title("Personal Dossier of the Terran Security Archive")
    fields = [
        "Name", "Surname", "Gender", "Date of birth", "Place of birth",
        "Home Planet", "Hair Color", "Eye Color", "Height", "Weight",
        "Body Type", "Marital Status", "Age", "Handedness", "Religion",
        "Monthly Wage (Energy Units)", "Savings (Energy Units)", "Skillpoints",
        "Usual Whereabouts", "Educational Level", "Military Service", "Rank",
        "Unit", "Criminal Record", "Hobbies", "Miscellaneous Information"
    ]
    dossier = {}
    for field in fields:
        dossier[field] = st.text_input(field)
    st.markdown("### Your Entered Dossier")
    st.json(dossier)


# ---------------------------------------------------------------------
# PAGE NAVIGATION (SIDEBAR)
# ---------------------------------------------------------------------
# The sidebar lets users switch between pages: Login, Register, Attributes,
# Inventory/Attacking, and Personal Dossier.
pages = ["Login", "Register", "Attributes", "Inventory/Attacking", "Personal Dossier"]
page = st.sidebar.radio("Navigate", pages)

if page == "Login":
    login_page()
elif page == "Register":
    registration_page()
elif page == "Attributes":
    attributes_page()
elif page == "Inventory/Attacking":
    inventory_page()
elif page == "Personal Dossier":
    personal_dossier_page()
