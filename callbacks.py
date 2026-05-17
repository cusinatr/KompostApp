import yaml
from dash import Input, Output, State, html, callback_context
from dash.exceptions import PreventUpdate
import pandas as pd
import plotly.express as px

from database import (
    save_availability_submission,
    load_volunteer_availability,
    load_submitted_volunteers,
)
from config import SETTINGS_PATH

# ---------------------------------------------------
# Load settings
# ---------------------------------------------------

with open(SETTINGS_PATH, "r") as file:

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

        if not volunteer or not table_data:
            raise PreventUpdate

        # Save submission
        save_availability_submission(volunteer, table_data)

        # Redirect to success page
        return (html.Div(), table_data, "/success")

    # ---------------------------------------------------
    # Success Summary
    # ---------------------------------------------------

    AVAILABILITY_LABELS = {
        "Free": "Frei",
        "Can make it work": "Geht notfalls",
    }

    @app.callback(
        Output("success-summary", "children"),
        Input("submitted-data-store", "data"),
        State("verified-volunteer-store", "data"),
    )
    def display_submission_summary(table_data, volunteer):

        if not table_data:
            return html.Div("Keine Einreichungsdaten verfügbar.")

        return html.Div(
            className="summary-container",
            children=[
                html.H2(f"Merci, {volunteer}!", className="thank-you-title"),
                html.H4("Eingereichte Verfügbarkeit:", className="summary-subtitle"),
                html.Div(
                    className="summary-table-wrapper",
                    children=[
                        html.Table(
                            className="summary-table",
                            children=[
                                html.Thead(
                                    html.Tr(
                                        [
                                            html.Th("Datum", className="summary-th"),
                                            html.Th("Verfügbarkeit", className="summary-th"),
                                        ]
                                    )
                                ),
                                html.Tbody(
                                    [
                                        html.Tr(
                                            className="summary-row",
                                            children=[
                                                html.Td(row["date"], className="summary-td"),
                                                html.Td(
                                                    AVAILABILITY_LABELS.get(
                                                        row["availability"],
                                                        row["availability"]
                                                    ),
                                                    className="summary-td",
                                                ),
                                            ],
                                        )
                                        for row in table_data
                                    ]
                                ),
                            ],
                        )
                    ],
                ),
            ],
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
        Output("welcome-message", "children"),
        Output("service-hours-reminder", "children"),
        Input("verified-volunteer-store", "data"),
    )
    def update_welcome_message(volunteer):

        if not volunteer:
            return "", ""

        service_lines = []

        for weekday, info in SERVICE_INFORMATION.items():
            time = info["time"]
            service_lines.append(html.Li(f"{weekday}: {time}"))

        welcome = html.Div(
            [
                html.H3(f"{volunteer}, herzlich willkommen!"),
            ]
        )

        reminder = html.Div(
            [
                html.P("Einsatzzeiten:", className="reminder-title"),
                html.Ul(service_lines),
            ]
        )

        return welcome, reminder

    # ---------------------------------------------------
    # Overview submission table
    # ---------------------------------------------------

    @app.callback(
        Output("overview-table-container", "children"), Input("url", "pathname")
    )
    def update_overview_table(pathname):

        if pathname != "/overview":

            raise PreventUpdate

        # -----------------------------------------
        # Load all volunteers from settings
        # -----------------------------------------

        with open(SETTINGS_PATH, "r") as file:

            settings = yaml.safe_load(file)

        volunteers = sorted([volunteer["name"] for volunteer in settings["volunteers"]])

        # -----------------------------------------
        # Load submitted volunteers
        # -----------------------------------------

        submitted_volunteers = load_submitted_volunteers()

        # -----------------------------------------
        # Create table rows
        # -----------------------------------------

        table_rows = []

        for volunteer in volunteers:

            submitted = volunteer in submitted_volunteers

            table_rows.append(
                html.Tr(
                    children=[
                        html.Td(volunteer),
                        html.Td("✅" if submitted else "❌"),
                    ]
                )
            )

        # -----------------------------------------
        # Return table
        # -----------------------------------------

        return html.Table(
            children=[
                html.Thead(
                    html.Tr(
                        children=[
                            html.Th("Freiwillige/r", style={"textAlign": "center"}),
                            html.Th("Eingereicht", style={"textAlign": "center"}),
                        ]
                    )
                ),
                html.Tbody(table_rows),
            ],
        )

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
