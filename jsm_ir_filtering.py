import streamlit as st
import pandas as pd
from io import StringIO

# Set the title of the app
st.title("JSM IR CSV Filtering")

# File uploader to upload CSV file
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

        # Filter columns to only include those that start with "IR " and add "Organizations"
        ir_columns = [col for col in df.columns if col.startswith("IR ")]
        if "Organizations" in df.columns:
            ir_columns.append("Organizations")

        # Allow the user to select which columns to display from the 'IR' columns and 'Organizations'
        selected_columns = st.multiselect("Select columns to display", ir_columns, default=ir_columns)

        # Filter the dataframe based on selected columns
        if selected_columns:
            filtered_df = df[selected_columns]

            # Move the filter options to the sidebar
            st.sidebar.title("Filters")

            # Dictionary to store selected filters
            filter_conditions = {}

            # Apply filter for "IR Date & Time" column using date picker
            if "IR Date & Time" in selected_columns:
                # Convert the "IR Date & Time" column to datetime (if not already)
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

            # Apply filter for "Organizations" column (categorical filter)
            if "Organizations" in selected_columns:
                unique_organizations = df["Organizations"].unique()
                selected_organizations = st.sidebar.multiselect("Filter by Organizations (select multiple values)",
                                                               unique_organizations.tolist(), default=unique_organizations.tolist())
                filter_conditions["Organizations"] = selected_organizations
                if len(selected_organizations) > 0:
                    filtered_df = filtered_df[filtered_df["Organizations"].isin(selected_organizations)]

            # Show the filtered data only
            st.write("Filtered Data:", filtered_df)

            # Optional: Create a basic chart if applicable (ensure consistent data types)
            if len(selected_columns) == 1:
                try:
                    st.line_chart(filtered_df)
                except Exception as e:
                    st.error(f"Error in plotting chart: {str(e)}")

            # Create a button to download the filtered data as a CSV
            csv_data = filtered_df.to_csv(index=False)  # Convert DataFrame to CSV format
            st.download_button(
                label="Download Filtered Data as CSV",
                data=csv_data,
                file_name="filtered_data.csv",
                mime="text/csv"
            )
        else:
            st.write("Please select at least one column to display.")
else:
    st.write("Please upload a CSV file.")
