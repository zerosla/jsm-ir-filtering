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
        ir_columns.append("Created")
        ir_columns.append("Organizations")
        ir_columns.append("Summary")

        select_all = st.checkbox("Select all columns", value=False)
        selected_columns = st.multiselect("Select columns to display", ir_columns, default=ir_columns if select_all else [
            "Summary", "Organizations", "Created", "IR Date & Time", "IR Current NIST Incident Response Stage"])
        

        # Filter the dataframe based on selected columns
        if selected_columns:
            filtered_df = df[selected_columns]

            st.sidebar.title("Filters")

            filter_conditions = {}

            # Apply filter for "Created" column using date picker
            if "Created" in selected_columns:
                # Convert the "Created" column to datetime
                df["Created"] = pd.to_datetime(df["Created"], errors='coerce')

                # Create a date picker for the "Created" column
                start_date = st.sidebar.date_input("Select start date", df["Created"].min())
                end_date = st.sidebar.date_input("Select end date", df["Created"].max())

                # Ensure start date is earlier than end date
                if start_date > end_date:
                    st.sidebar.error("Start date must be earlier than end date.")
                else:
                    # Filter the dataframe based on the selected date range
                    filter_conditions["Created"] = (df["Created"] >= pd.to_datetime(start_date)) & \
                                                           (df["Created"] <= pd.to_datetime(end_date))
                    filtered_df = filtered_df[filter_conditions["Created"]]

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
            st.write(f"{len(filtered_df)} incidents shown.")

else:
    st.write("Please upload a CSV file.")
