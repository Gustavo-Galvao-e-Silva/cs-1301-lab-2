import streamlit as st
import pandas as pd
import os
import datetime
import uuid


def _generate_new_data(fruits: int, sleep: int, exercise: int) -> pd.DataFrame:
    new_data = {
        "id": uuid.uuid4().hex,
        "fruit_consumption": [fruits],
        "sleep_duration": [sleep],
        "exercise_frequency": [exercise],
        "timestamp": [datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")]
    }

    st.success("Your data has been submitted!")
    st.write(f"You entered: **Fruits:** {fruits}, **Sleep:** {sleep}, **Exercise:** {exercise}")
    
    return pd.DataFrame(new_data)


def _write_data_to_csv(data: pd.DataFrame, filename='data.csv'):
    if os.path.exists(filename) and os.path.getsize(filename) > 0:
        existing_data_df = pd.read_csv(filename)
        updated_data_df = pd.concat([existing_data_df, data], ignore_index=True)
        updated_data_df.to_csv(filename, index=False)
    else:
        data.to_csv(filename, index=False)


st.set_page_config(
    page_title="Survey",
    page_icon="📝",
)


st.title("❤️ General Health Survey 📝")
st.write("Please fill out the form below to add your health data to our records")

with st.form("survey_form"):
    fruits_input = st.number_input(
        label="How many servings of fruits do you eat in a day? (0-10)", 
        min_value=0, 
        max_value=10, 
        step=1, 
        value=None,
        icon="🍎"
    )
    sleep_input = st.slider(
        label="How many hours do you sleep on average per night? (0-24)", 
        min_value=0, 
        max_value=24, 
        step=1, 
        value=0,
        icon="🛌"
    )
    exercise_input = st.number_input(
        label="How many days a week do you exercise? (0-7)", 
        min_value=0, 
        max_value=7, 
        step=1, 
        value=None,
        icon="💪"
    )

    submitted = st.form_submit_button("Submit Data")
    if submitted:
        if fruits_input is None or sleep_input == 0 or exercise_input is None:
            st.error("Please fill out all fields before submitting.")
        else:
            new_data_df = _generate_new_data(fruits_input, sleep_input, exercise_input)
            _write_data_to_csv(new_data_df)
        


st.divider()
st.header("🩺 Current Health Data 📊")
st.write("Below is the current health data collected from all users")

if os.path.exists('data.csv') and os.path.getsize('data.csv') > 0 and not pd.DataFrame(pd.read_csv('data.csv')).empty:
    current_data_df = pd.read_csv('data.csv')
    current_data_df.drop(columns=['id'], inplace=True, errors='ignore')
    st.dataframe(
        current_data_df,
        hide_index=True,
        column_config={
            "fruit_consumption": st.column_config.NumberColumn("Fruit (servings/day)"),
            "sleep_duration": st.column_config.NumberColumn("Sleep (hours/night)"),
            "exercise_frequency": st.column_config.NumberColumn("Exercise (days/week)"),
            "timestamp": st.column_config.DatetimeColumn("Timestamp")
        }
    )
else:
    st.warning("The 'data.csv' file is empty or does not exist yet.")   