import streamlit as st
import pandas as pd
from io import StringIO

st.title("JSM IR CSV Filtering")

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file is not None:
    # Load the CSV file into a pandas DataFrame
    df = pd.read_csv(uploaded_file)

    # Check if the DataFrame is empty
    if len(df) == 0:
        st.write("No data found in the CSV file. Please check your CSV.")
    else:
        # Strip the "Custom field " prefix and parentheses from the column names
        columns = [col.replace("Custom field ", "").replace("(", "").replace(")", "") for col in df.columns]

        # Rename the columns in the DataFrame
        df.columns = columns

        # Filter columns to only include those that start with "IR " and "Organizations" (more fields to be added later)
        ir_columns = [col for col in df.columns if col.startswith("IR ")]
        ir_columns.append("Organizations")
        ir_columns.append("Summary")

        # Allow the user to select which columns to display from the 'IR' columns and 'Organizations'
        selected_columns = st.multiselect("Select columns to display", ir_columns, default=[
            "Summary", "Organizations", "IR Date & Time", "IR Current NIST Incident Response Stage"])

        # Filter the dataframe based on selected columns
        if selected_columns:
            filtered_df = df[selected_columns]

            st.sidebar.title("Filters")

            filter_conditions = {}

            # Apply filter for "IR Date & Time" column using date picker
            if "IR Date & Time" in selected_columns:
                # Convert the "IR Date & Time" column to datetime
                df["IR Date & Time"] = pd.to_datetime(df["IR Date & Time"], errors='coerce')

                # Create a date picker for the "IR Date & Time" column
                start_date = st.sidebar.date_input("Select start date", df["IR Date & Time"].min())
                end_date = st.sidebar.date_input("Select end date", df["IR Date & Time"].max())

                # Ensure start date is earlier than end date
                if start_date > end_date:
                    st.sidebar.error("Start date must be earlier than end date.")
                else:
                    # Filter the dataframe based on the selected date range
                    filter_conditions["IR Date & Time"] = (df["IR Date & Time"] >= pd.to_datetime(start_date)) & \
                                                           (df["IR Date & Time"] <= pd.to_datetime(end_date))
                    filtered_df = filtered_df[filter_conditions["IR Date & Time"]]

            # Apply filter for "Organizations" column
            if "Organizations" in selected_columns:
                unique_organizations = df["Organizations"].unique()
                selected_organizations = st.sidebar.multiselect("Filter by Organizations (select multiple values)",
                                                               unique_organizations.tolist(), default=unique_organizations.tolist())
                filter_conditions["Organizations"] = selected_organizations
                if len(selected_organizations) > 0:
                    filtered_df = filtered_df[filtered_df["Organizations"].isin(selected_organizations)]

            # Show the filtered data only
            st.write("Filtered Data:", filtered_df)

else:
    st.write("Please upload a CSV file.")
