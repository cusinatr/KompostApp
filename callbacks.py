import yaml
from dash import Input, Output, State, html, callback_context
from dash.exceptions import PreventUpdate
import pandas as pd
import plotly.express as px

from database import (
    save_availability_submission,
    load_volunteer_availability,
    load_availability_statistics,
)

# ---------------------------------------------------
# Load settings
# ---------------------------------------------------

with open("settings.yaml", "r") as file:

    settings = yaml.safe_load(file)

SERVICE_INFORMATION = settings["service_information"]


def register_callbacks(app):

    # ---------------------------------------------------
    # Synchronize calendar and table
    # ---------------------------------------------------

    @app.callback(
        Output("selected-dates-store", "data"),
        Output("availability-table", "data"),
        Output("multi-date-picker", "value"),
        Input("multi-date-picker", "value"),
        Input("availability-table", "data"),
        State("selected-dates-store", "data"),
        prevent_initial_call=True,
    )
    def sync_dates(calendar_dates, table_data, stored_dates):
        trigger = callback_context.triggered[0]["prop_id"]

        # -----------------------------------------
        # Calendar changed
        # -----------------------------------------

        if "multi-date-picker" in trigger:

            if not calendar_dates:
                return [], [], []

            availability_lookup = {}

            if table_data:

                availability_lookup = {
                    row["date"]: row["availability"] for row in table_data
                }

            updated_table = []

            for date in sorted(calendar_dates):

                updated_table.append(
                    {
                        "date": date,
                        "availability": availability_lookup.get(date, "Free"),
                    }
                )

            return (calendar_dates, updated_table, calendar_dates)

        # -----------------------------------------
        # Table changed
        # -----------------------------------------

        elif "availability-table" in trigger:

            if not table_data:
                return [], [], []

            updated_dates = [row["date"] for row in table_data]

            return (updated_dates, table_data, updated_dates)

        raise PreventUpdate

    # ---------------------------------------------------
    # Submit form
    # ---------------------------------------------------

    @app.callback(
        Output("submission-output", "children"),
        Output("submitted-data-store", "data"),
        Output("url", "pathname", allow_duplicate=True),
        Input("submit-button", "n_clicks"),
        State("verified-volunteer-store", "data"),
        State("availability-table", "data"),
        prevent_initial_call=True,
    )
    def submit_form(n_clicks, volunteer, table_data):

        if not volunteer:

            return (html.Div("Volunteer not recognized."), [], "/schedule")

        if not table_data:

            return (html.Div("Please select dates."), [], "/schedule")

        # Save submission
        save_availability_submission(volunteer, table_data)

        # Redirect to success page
        return (html.Div(), table_data, "/success")

    # ---------------------------------------------------
    # Success Summary
    # ---------------------------------------------------

    @app.callback(
        Output("success-summary", "children"),
        Input("submitted-data-store", "data"),
        State("verified-volunteer-store", "data"),
    )
    def display_submission_summary(table_data, volunteer):

        if not table_data:
            return html.Div("No submission data available.")

        return html.Div(
            [
                html.H3(f"Thank you {volunteer}!"),
                html.H4("Submitted Availability"),
                html.Ul(
                    [
                        html.Li(f"{row['date']} → {row['availability']}")
                        for row in table_data
                    ]
                ),
            ]
        )

    # ---------------------------------------------------
    # Navigation Buttons
    # ---------------------------------------------------

    @app.callback(
        Output("url", "pathname", allow_duplicate=True),
        Input("modify-button", "n_clicks", allow_optional=True),
        Input("logout-button", "n_clicks", allow_optional=True),
        prevent_initial_call=True,
    )
    def handle_success_navigation(modify_clicks, logout_clicks):

        trigger = callback_context.triggered[0]["prop_id"]

        if "modify-button" in trigger:

            return "/schedule"

        return "/goodbye"

    # ---------------------------------------------------
    # Load volunteer availability
    # ---------------------------------------------------

    @app.callback(
        Output("availability-table", "data", allow_duplicate=True),
        Output("multi-date-picker", "value", allow_duplicate=True),
        Input("url", "pathname"),
        State("verified-volunteer-store", "data"),
        prevent_initial_call=True,
    )
    def load_existing_availability(pathname, volunteer):

        # Only run on schedule page
        if pathname != "/schedule":

            raise PreventUpdate

        if not volunteer:

            return [], []

        # Load from database
        table_data = load_volunteer_availability(volunteer)

        if not table_data:

            return [], []

        selected_dates = [row["date"] for row in table_data]

        return (table_data, selected_dates)

    # ---------------------------------------------------
    # Welcome message
    # ---------------------------------------------------

    @app.callback(
        Output("welcome-message", "children"), Input("verified-volunteer-store", "data")
    )
    def update_welcome_message(volunteer):

        if not volunteer:

            return ""

        # -----------------------------------------
        # Build service description dynamically
        # -----------------------------------------

        service_lines = []

        for weekday, info in SERVICE_INFORMATION.items():

            time = info["time"]

            service_lines.append(html.Li(f"{weekday}: {time}"))

        return html.Div(
            [
                html.H3(f"Dear {volunteer}, welcome!"),
                html.P("Please let us know your availability!"),
                html.P("Remember that the compost service takes place during:"),
                html.Ul(service_lines),
            ]
        )

    # ---------------------------------------------------
    # Overview graph
    # ---------------------------------------------------

    @app.callback(
        Output("availability-overview-graph", "figure"), Input("url", "pathname")
    )
    def update_overview_graph(pathname):

        if pathname != "/overview":

            raise PreventUpdate

        # -----------------------------------------
        # Load all volunteers from settings
        # -----------------------------------------

        with open("settings.yaml", "r") as file:

            settings = yaml.safe_load(file)

        volunteers = sorted([volunteer["name"] for volunteer in settings["volunteers"]])

        # -----------------------------------------
        # Load statistics from database
        # -----------------------------------------

        rows = load_availability_statistics()

        # -----------------------------------------
        # Build dataframe from DB
        # -----------------------------------------

        if rows:

            df = pd.DataFrame(rows, columns=["Volunteer", "Availability", "Count"])

        else:

            df = pd.DataFrame(columns=["Volunteer", "Availability", "Count"])

        # -----------------------------------------
        # Ensure ALL volunteers appear
        # -----------------------------------------

        complete_rows = []

        availability_types = ["Free", "Can make it work"]

        for volunteer in volunteers:

            for availability in availability_types:

                # Check if row exists
                matching_rows = df[
                    (df["Volunteer"] == volunteer)
                    & (df["Availability"] == availability)
                ]

                if len(matching_rows) > 0:

                    count = matching_rows.iloc[0]["Count"]

                else:

                    count = 0

                complete_rows.append(
                    {
                        "Volunteer": volunteer,
                        "Availability": availability,
                        "Count": count,
                    }
                )

        df_complete = pd.DataFrame(complete_rows)

        # -----------------------------------------
        # Create figure
        # -----------------------------------------

        fig = px.bar(
            df_complete,
            x="Count",
            y="Volunteer",
            color="Availability",
            orientation="h",
            barmode="stack",
            category_orders={"Volunteer": volunteers},
            title="Submitted Availabilities by Volunteer",
        )

        fig.update_layout(
            height=max(400, 80 * len(volunteers)),
            yaxis_title="Volunteer",
            xaxis_title="Number of Availabilities",
        )

        return fig

    # ---------------------------------------------------
    # Logout
    # ---------------------------------------------------

    @app.callback(
        Output("verified-volunteer-store", "data", allow_duplicate=True),
        Output("url", "pathname", allow_duplicate=True),
        Input("logout-link", "n_clicks", allow_optional=True),
        prevent_initial_call=True,
    )
    def logout_user(n_clicks):

        if not n_clicks:

            raise PreventUpdate

        return (None, "/goodbye")
