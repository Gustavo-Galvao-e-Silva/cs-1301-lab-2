import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import json
import os


def _file_data_is_valid(file_path: str) -> bool:
    return os.path.exists(file_path) and os.path.getsize(file_path) > 0


def _get_bmi_statistics(locations: list[str], bmi_dict: dict[str, any]) -> dict:
    if not bmi_dict:
        raise ValueError("BMI data is unavailable.")
    if not locations:
        location_dict = bmi_dict.get("United States", {})
        return {
            "Underweight": location_dict.get("Underweight", 0),
            "Normal weight": location_dict.get("Normal Weight", 0),
            "Overweight": location_dict.get("Overweight", 0),
            "Obese": location_dict.get("Obese", 0),
            "Severely obese": bmi_dict.get("United States", {}).get("Severely Obese", 0),
        }

    underweight_total = 0
    normal_total = 0
    overweight_total = 0
    obese_total = 0
    severe_obese_total = 0

    for location in locations:
        if location in bmi_dict:
            underweight_total += bmi_dict[location].get("Underweight", 0)
            normal_total += bmi_dict[location].get("Normal Weight", 0)
            overweight_total += bmi_dict[location].get("Overweight", 0)
            obese_total += bmi_dict[location].get("Obese", 0)
            severe_obese_total += bmi_dict[location].get("Severely Obese", 0)

    return {
        "Underweight": underweight_total/len(locations),
        "Normal weight": normal_total/len(locations),
        "Overweight": overweight_total/len(locations),
        "Obese": obese_total/len(locations),
        "Severely obese": severe_obese_total/len(locations),
    }


def _get_bmi_gdp_data(bmi_dict: dict[str, any]) -> dict[str, tuple[float, float]]:
    bmi_gdp_data = {}
    for location, data in bmi_dict.items():
        bad_bmi_count = (
            data.get("Overweight", 0) +
            data.get("Obese", 0) +
            data.get("Severely Obese", 0)
        ) * 100
        gdp_per_capita = data.get("GDP per Capita", 0)
        bmi_gdp_data[location] = (bad_bmi_count, gdp_per_capita)

    return bmi_gdp_data


def display_bmi_gdp_scatter_plot(bmi_gdp_data: dict[str, tuple[float, float]]) -> None:
    line_chart_data = pd.DataFrame(
        {
            "Above BMI": [bmi for bmi, _ in bmi_gdp_data.values()],
            "GDP Per Capita": [gdp for _, gdp in bmi_gdp_data.values()],
        },
        index=bmi_gdp_data.keys()
    )
    st.line_chart(
        data=line_chart_data,
        x="GDP Per Capita",
        y="Above BMI",
        x_label="GDP Per Capita (USD)",
        y_label="People with BMI above 25 (%)",
    )


def display_bmi_pie_chart(bmi_stats: dict[str, any]) -> None:
    labels = list(bmi_stats.keys())
    sizes = [float(v) for v in bmi_stats.values()]

    fig, ax = plt.subplots(figsize=(6, 6))
    colors = plt.cm.Set3.colors[:len(labels)]
    wedges, texts, autotexts = ax.pie(
        sizes,
        autopct='%1.1f%%',
        startangle=140,
        colors=colors,
        pctdistance=0.75,
        textprops={'fontsize': 10}
    )

    centre_circle = plt.Circle((0, 0), 0.60, fc='white', linewidth=0)
    ax.add_artist(centre_circle)
    ax.legend(wedges, labels, title="BMI Categories", loc="center", bbox_to_anchor=(1, 0, 0.5, 1))

    st.pyplot(fig)


def display_healthy_habits_graph(health_df: pd.DataFrame, current_statistic: str) -> None:
    display_data = {}

    if current_statistic == "Exercise Frequency":
        sedentary_mask = health_df[health_df["exercise_frequency"] <= 1]
        lightly_active_mask = health_df[(health_df["exercise_frequency"] == 2)]
        moderately_active_mask = health_df[(health_df["exercise_frequency"] >= 3) & (health_df["exercise_frequency"] <= 4)]
        very_active_mask = health_df[health_df["exercise_frequency"] >= 5]

        display_data = {
            "Sedentary (0-1 days/week)": len(sedentary_mask),
            "Lightly Active (2 days/week)": len(lightly_active_mask),
            "Moderately Active (3-4 days/week)": len(moderately_active_mask),
            "Very Active (5-7 days/week)": len(very_active_mask),
        }

    elif current_statistic == "Fruit Consumption":
        low_fruit_mask = health_df[health_df["fruit_consumption"] <= 1]
        moderate_fruit_mask = health_df[(health_df["fruit_consumption"] == 2)]
        high_fruit_mask = health_df[health_df["fruit_consumption"] >= 3]

        display_data = {
            "Low (0-1 servings/day)": len(low_fruit_mask),
            "Moderate (2 servings/day)": len(moderate_fruit_mask),
            "High (3+ servings/day)": len(high_fruit_mask),
        }

    elif current_statistic == "Sleep Duration":
        short_sleep_mask = health_df[health_df["sleep_duration"] < 6]
        adequate_sleep_mask = health_df[(health_df["sleep_duration"] >= 6) & (health_df["sleep_duration"] <= 8)]
        long_sleep_mask = health_df[health_df["sleep_duration"] > 8]

        display_data = {
            "Short Sleep (<6 hours/night)": len(short_sleep_mask),
            "Adequate Sleep (6-8 hours/night)": len(adequate_sleep_mask),
            "Long Sleep (>8 hours/night)": len(long_sleep_mask),
        }
        

    st.bar_chart(
        data=display_data,
        x_label=current_statistic,
        y_label="Number of Respondents",
        sort=False
    )


st.set_page_config(
    page_title="Visualizations",
    page_icon="📈",
)

necessary_session_keys = ["selected_locations", "current_health_statistic", "json_data_dict", "survey_data_df", "locations_list"]

for key in necessary_session_keys:
    if key not in st.session_state:
        if key == "selected_locations":
            st.session_state[key] = []
        elif key == "current_health_statistic":
            st.session_state[key] = ""
        elif key == "json_data_dict":
            st.session_state[key] = {}
        elif key == "survey_data_df":
            st.session_state[key] = pd.DataFrame()
        elif key == "locations_list":
            st.session_state[key] = []

st.title("Data Visualizations 📈")
st.write("Graphs made with health data from our survey and KFF BMI data")
st.divider()

data_is_available = False

if _file_data_is_valid("data.csv") and _file_data_is_valid("data.json") and _file_data_is_valid("locations.json"):
    data_is_available = True
    st.session_state.survey_data_df = pd.read_csv("data.csv")
    with open("data.json", 'r') as f:
        st.session_state.json_data_dict = json.load(f)

    with open("locations.json", 'r') as f:
        st.session_state.locations_list = json.load(f)

st.header("Graphs")
    
if data_is_available:
    st.subheader("Graph 1: GDP vs Above Normal BMI")
    st.write("This scatter plot shows the relationship between GDP per capita and above normal BMI for selected locations based on KFF BMI and BEA GDP data. This shows how increased wealth can lead to better health outcomes in terms of BMI.")

    bmi_gdp_data = _get_bmi_gdp_data(st.session_state.json_data_dict)
    display_bmi_gdp_scatter_plot(bmi_gdp_data)

    st.divider()

    st.subheader("Graph 2: BMI Distribution Among US Adults")
    st.write("This pie chart illustrates the distribution of BMI categories among US adults based on selected locations from KFF BMI statistics.")

    st.session_state.selected_locations = st.multiselect(
        "Select Locations for BMI Data",
        options=st.session_state.locations_list,
        default=None
    )

    bmi_stats = _get_bmi_statistics(st.session_state.selected_locations, st.session_state.json_data_dict)

    display_bmi_pie_chart(bmi_stats)

    st.divider()

    st.subheader("Graph 3: Healthy Habits")
    st.write("This graph showcases healthy habits data from our survey respondents. It highlights the exercise frequency, fruit consumption, and sleep duration among participants.")

    st.session_state.current_statistic = st.selectbox(
        "Select which healthy habit statistic to display:",
        options=[
            "Exercise Frequency",
            "Fruit Consumption",
            "Sleep Duration"
        ],
        index=0
    )

    display_healthy_habits_graph(st.session_state.survey_data_df, st.session_state.current_statistic)

else:
    st.warning("Unfortunately, our data is not fully available at this moment :(")