import streamlit as st
import random
import math

# === Session State Initialization ===
if "reroll_limit" not in st.session_state:
    st.session_state.reroll_limit = 3
if "reroll_count" not in st.session_state:
    st.session_state.reroll_count = 0
if "results" not in st.session_state:
    st.session_state.results = [None] * 8
if "luck" not in st.session_state:
    st.session_state.luck = ""
if "career_skill_points" not in st.session_state:
    st.session_state.career_skill_points = ""
if "free_skill_points" not in st.session_state:
    st.session_state.free_skill_points = ""
if "special_trait_results" not in st.session_state:
    st.session_state.special_trait_results = []
if "special_trait_text" not in st.session_state:
    st.session_state.special_trait_text = ""
if "monthly_wage" not in st.session_state:
    st.session_state.monthly_wage = ""
if "magazine" not in st.session_state:
    st.session_state.magazine = 15

# --- Global Headline ---
st.title("Space Gothic Character Generator")
st.subheader("Mercenary Class")


# === Calculation Functions ===
def calculate_attributes():
    """Calculate the base attributes and reset rerolls & special traits."""
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
    """Reroll a specific attribute (if within reroll limit) and update dependents."""
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

        if index == 2:  # Update Luck if Willpower is rerolled.
            st.session_state.luck = math.ceil(st.session_state.results[2] / 2 + 20 + random.randint(3, 30))
        if index in [5, 7]:  # Update skill points if Experience or Intelligence changes.
            st.session_state.career_skill_points = math.ceil(3 * st.session_state.results[5])
            st.session_state.free_skill_points = math.ceil(st.session_state.results[5] + st.session_state.results[7])
    else:
        st.warning("Reroll limit reached!")


def roll_special_trait():
    """Roll and record a random special trait (if within reroll limit)."""
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
    """Calculate a random monthly wage."""
    st.session_state.monthly_wage = random.randint(3, 30) + 20


# === Inventory/Attacking Page Functions ===
def display_magazine():
    """Display the magazine as a single strip with filled/empty blocks."""
    bullets_left = st.session_state.magazine
    total_bullets = 15
    filled = "🟩"
    empty = "⬜"
    magazine_display = filled * bullets_left + empty * (total_bullets - bullets_left)
    st.markdown("**Magazine:** " + magazine_display)


def inventory_page():
    st.title("Inventory")
    st.subheader("Weapon: Luger .357 Automagnum")
    # Top row: Labels for weapon stats
    cols_top = st.columns([1, 1, 1, 1, 1])
    cols_top[0].markdown("**Damage:**")
    cols_top[1].markdown("**Range:**")
    cols_top[2].markdown("**Fire Rate:**")
    cols_top[3].markdown("**Burst Rate:**")
    cols_top[4].markdown("**Magazine Size:**")
    # Bottom row: Values
    cols_bottom = st.columns([1, 1, 1, 1, 1])
    cols_bottom[0].markdown("1d10+2")
    cols_bottom[1].markdown("Short 20m <br> Medium 40m <br> Long 60m", unsafe_allow_html=True)
    cols_bottom[2].markdown("3")
    cols_bottom[3].markdown("5")
    cols_bottom[4].markdown("15")

    st.markdown("---")
    # --- Shooting Skill Section ---
    range_option = st.radio("Select Range", ("Short", "Medium", "Long"), index=1)
    if range_option == "Short":
        range_modifier = 10
    elif range_option == "Medium":
        range_modifier = 0
    else:  # Long
        range_modifier = -10
    base_chance = 65
    final_chance = base_chance + range_modifier
    st.write("Adjusted Shooting Chance:", final_chance, "%")

    # --- Firing Mode Buttons Row ---
    firing_cols = st.columns(4)
    with firing_cols[0]:
        single_fire = st.button("Single Fire")
    with firing_cols[1]:
        semi_burst = st.button("Semi Burst")
    with firing_cols[2]:
        full_burst = st.button("Full Burst")
    with firing_cols[3]:
        reload_btn = st.button("Reload")

    # --- Fixed Results Container (Always reserved) ---
    results_container = st.container()
    results_cols = results_container.columns(3)
    # Reserve space (3 line breaks) in each result column even if nothing is displayed yet.
    for rc in results_cols:
        rc.markdown("<br>" * 3, unsafe_allow_html=True)

    # --- Process Firing Logic ---
    if single_fire:
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
                    d = random.randint(3, 12)  # Simplified damage roll
                    damage_rolls.append(d)
                    total_damage += d
                else:
                    damage_rolls.append(0)
            results_cols[0].write(
                f"**Single Fire**\n"
                f"Hit Rolls: {hit_rolls}\n"
                f"Total Hits: {hits}\n"
                f"Damage Rolls: {damage_rolls}\n"
                f"Total Damage: {total_damage}"
            )
        else:
            st.warning("Out of bullets!")

    if semi_burst:
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
            results_cols[1].write(
                f"**Semi Burst**\n"
                f"Hit Rolls: {hit_rolls}\n"
                f"Total Hits: {hits}\n"
                f"Damage Rolls: {damage_rolls}\n"
                f"Total Damage: {total_damage}"
            )
        else:
            st.warning("Not enough bullets for Semi Burst!")

    if full_burst:
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
            results_cols[2].write(
                f"**Full Burst**\n"
                f"Hit Rolls: {hit_rolls}\n"
                f"Total Hits: {hits}\n"
                f"Damage Rolls: {damage_rolls}\n"
                f"Total Damage: {total_damage}"
            )
        else:
            st.warning("Not enough bullets for Full Burst!")

    if reload_btn:
        st.session_state.magazine = 15

    # --- Add Vertical Spacing ---
    st.markdown("<br><br><br>", unsafe_allow_html=True)

    # --- Display the Updated Magazine ---
    display_magazine()


# === Attributes Page ===
def attributes_page():
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


# === Personal Dossier Page ===
def personal_dossier_page():
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


# === Navigation via Sidebar ===
page = st.sidebar.radio("Navigate", ("Attributes", "Inventory/Attacking", "Personal Dossier"))

if page == "Attributes":
    attributes_page()
elif page == "Inventory/Attacking":
    inventory_page()
elif page == "Personal Dossier":
    personal_dossier_page()
