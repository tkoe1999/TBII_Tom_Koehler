import streamlit as st
import random
import math

# ---------------------------------------------------------------------
# SESSION STATE INITIALIZATION
# ---------------------------------------------------------------------
# These variables are saved in "session_state" so they keep their value
# even when the page reruns (for example, after a button click).

if "reroll_limit" not in st.session_state:
    st.session_state.reroll_limit = 3  # Maximum number of rerolls allowed
if "reroll_count" not in st.session_state:
    st.session_state.reroll_count = 0  # How many rerolls have been used
if "results" not in st.session_state:
    st.session_state.results = [None] * 8  # Placeholder for 8 attribute values
if "luck" not in st.session_state:
    st.session_state.luck = ""  # Calculated luck value
if "career_skill_points" not in st.session_state:
    st.session_state.career_skill_points = ""  # Calculated career skill points
if "free_skill_points" not in st.session_state:
    st.session_state.free_skill_points = ""  # Calculated free skill points
if "special_trait_results" not in st.session_state:
    st.session_state.special_trait_results = []  # List to store special traits
if "special_trait_text" not in st.session_state:
    st.session_state.special_trait_text = ""  # Combined special traits text
if "monthly_wage" not in st.session_state:
    st.session_state.monthly_wage = ""  # Random monthly wage
if "magazine" not in st.session_state:
    st.session_state.magazine = 15  # Magazine capacity (bullets available)

# ---------------------------------------------------------------------
# GLOBAL HEADER
# ---------------------------------------------------------------------
st.title("Space Gothic Character Generator")
st.subheader("Mercenary Class")


# ---------------------------------------------------------------------
# LOAD CUSTOM CSS
# ---------------------------------------------------------------------
# This function reads a CSS file and injects its contents into the app.
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


# Load the CSS file "style.css" (make sure it's in the same folder as this script)
local_css("style.css")

# Insert an image with a custom ID so that our CSS can position it.
st.markdown(
    '<img id="custom-image" src="https://raw.githubusercontent.com/tkoe1999/TBII_Tom_Koehler/main/Mercenary_SpaceGothic_Art.png" alt="Mercenary Art">',
    unsafe_allow_html=True
)


# ---------------------------------------------------------------------
# CALCULATION FUNCTIONS (for attributes and skills)
# ---------------------------------------------------------------------

def calculate_attributes():
    """
    Calculate character attributes by generating random values.
    This resets reroll count and special traits.
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
    Reroll a specific attribute (if allowed) and update related values.
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

        # Update Luck if Willpower (index 2) was rerolled.
        if index == 2:
            st.session_state.luck = math.ceil(st.session_state.results[2] / 2 + 20 + random.randint(3, 30))
        # Update skill points if Experience (index 5) or Intelligence (index 7) changed.
        if index in [5, 7]:
            st.session_state.career_skill_points = math.ceil(3 * st.session_state.results[5])
            st.session_state.free_skill_points = math.ceil(st.session_state.results[5] + st.session_state.results[7])
    else:
        st.warning("Reroll limit reached!")


def roll_special_trait():
    """
    Choose a random special trait from a list.
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
    Calculate a random monthly wage.
    """
    st.session_state.monthly_wage = random.randint(3, 30) + 20


# ---------------------------------------------------------------------
# INVENTORY/ATTACKING PAGE FUNCTIONS (weapon and firing logic)
# ---------------------------------------------------------------------

def display_magazine():
    """
    Display the magazine status as a row of blocks.
    Green block (🟩) = bullet available.
    White block (⬜) = empty slot.
    """
    bullets_left = st.session_state.magazine
    total_bullets = 15
    filled = "🟩"
    empty = "⬜"
    magazine_display = filled * bullets_left + empty * (total_bullets - bullets_left)
    st.markdown("**Magazine:** " + magazine_display)


def inventory_page():
    """
    Show the Inventory page with weapon stats and firing controls.
    This page lets you simulate firing the Luger .357 Automagnum.
    """
    st.title("Inventory")
    st.subheader("Weapon: Luger .357 Automagnum")

    # --------------------------
    # Display Weapon Statistics
    # --------------------------
    # First row: labels
    cols_top = st.columns([1, 1, 1, 1, 1])
    cols_top[0].markdown("**Damage:**")
    cols_top[1].markdown("**Range:**")
    cols_top[2].markdown("**Fire Rate:**")
    cols_top[3].markdown("**Burst Rate:**")
    cols_top[4].markdown("**Magazine Size:**")
    # Second row: values
    cols_bottom = st.columns([1, 1, 1, 1, 1])
    cols_bottom[0].markdown("1d10+2")
    cols_bottom[1].markdown("Short 20m <br> Medium 40m <br> Long 60m", unsafe_allow_html=True)
    cols_bottom[2].markdown("3")
    cols_bottom[3].markdown("5")
    cols_bottom[4].markdown("15")

    st.markdown("---")

    # --------------------------
    # Shooting Skill Section
    # --------------------------
    # The user chooses a range. This adjusts the shooting chance.
    range_option = st.radio("Select Range", ("Short", "Medium", "Long"), index=1)
    if range_option == "Short":
        range_modifier = 10
    elif range_option == "Medium":
        range_modifier = 0
    else:
        range_modifier = -10
    base_chance = 65  # Base chance (in percent) for pistol shooting.
    final_chance = base_chance + range_modifier
    st.write("Adjusted Shooting Chance:", final_chance, "%")

    # --------------------------
    # Firing Mode Buttons
    # --------------------------
    # Buttons for Single Fire, Semi Burst, Full Burst, and Reload.
    firing_cols = st.columns(4)
    single_fire_btn = firing_cols[0].button("Single Fire")
    semi_burst_btn = firing_cols[1].button("Semi Burst")
    full_burst_btn = firing_cols[2].button("Full Burst")
    reload_btn = firing_cols[3].button("Reload")

    # Use a session state variable to store firing results.
    if "fire_results" not in st.session_state:
        st.session_state.fire_results = ""

    # --------------------------
    # Firing Logic for Each Mode
    # --------------------------
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

    # --------------------------
    # Display the Magazine
    # --------------------------
    # Show the current bullet status above the firing results.
    display_magazine()

    # --------------------------
    # Fixed Results Container
    # --------------------------
    # Reserve a fixed space for firing results so the layout doesn't jump.
    st.markdown(
        f'<div style="min-height:150px;">{st.session_state.fire_results}</div>',
        unsafe_allow_html=True
    )


# ---------------------------------------------------------------------
# ATTRIBUTES PAGE FUNCTIONS
# ---------------------------------------------------------------------
def attributes_page():
    """
    Show character attributes and allow recalculation and rerolls.
    """
    st.title("Attributes & Rolls")
    if st.button("Calculate Attributes"):
        calculate_attributes()

    if st.session_state.results and None not in st.session_state.results:
        # List of attribute names.
        attribute_names = ["Strength", "Agility", "Willpower", "Endurance",
                           "Luck (base)", "Experience", "Weight", "Intelligence"]
        # Display each attribute with a reroll button.
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


# ---------------------------------------------------------------------
# PERSONAL DOSSIER PAGE FUNCTIONS
# ---------------------------------------------------------------------
def personal_dossier_page():
    """
    Show a form to fill in personal details.
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
# PAGE NAVIGATION (Sidebar)
# ---------------------------------------------------------------------
# This radio button in the sidebar lets you choose which page to view.
page = st.sidebar.radio("Navigate", ("Attributes", "Inventory/Attacking", "Personal Dossier"))

if page == "Attributes":
    attributes_page()
elif page == "Inventory/Attacking":
    inventory_page()
elif page == "Personal Dossier":
    personal_dossier_page()
