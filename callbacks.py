import yaml
from dash import Input, Output, State, html, callback_context
from dash.exceptions import PreventUpdate

from database import save_availability_submission

with open("settings.yaml", "r") as file:
    settings = yaml.safe_load(file)

VOLUNTEERS = settings["volunteers"]


def register_callbacks(app):

    # ---------------------------------------------------
    # Verify volunteer email
    # ---------------------------------------------------

    @app.callback(
        Output("verification-message", "children"),
        Output("verified-volunteer-store", "data"),
        Output("multi-date-picker", "style"),
        Output("availability-table", "editable"),
        Output("availability-table", "row_deletable"),
        Output("submit-button", "disabled"),
        Input("verify-email-button", "n_clicks"),
        State("email-input", "value"),
        prevent_initial_call=True,
    )
    def verify_email(n_clicks, email):

        if not email:

            return (
                html.Div("Please enter an email.", style={"color": "red"}),
                None,
                {"marginBottom": "30px", "pointerEvents": "none", "opacity": "0.5"},
                False,
                False,
                True,
            )

        email = email.strip().lower()

        for volunteer in VOLUNTEERS:

            volunteer_email = volunteer["email"].strip().lower()

            if email == volunteer_email:

                volunteer_name = volunteer["name"]

                return (
                    html.Div(f"Welcome {volunteer_name}!", style={"color": "green"}),
                    volunteer_name,
                    {"marginBottom": "30px"},
                    True,
                    True,
                    False,
                )

        return (
            html.Div("Email not recognized.", style={"color": "red"}),
            None,
            {"marginBottom": "30px", "pointerEvents": "none", "opacity": "0.5"},
            False,
            False,
            True,
        )

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
        Output("submission-modal", "opened"),
        Output("submission-modal-content", "children"),
        Input("submit-button", "n_clicks"),
        State("verified-volunteer-store", "data"),
        State("availability-table", "data"),
        prevent_initial_call=True,
    )
    def submit_form(n_clicks, volunteer, table_data):

        if not volunteer:

            return (html.Div("Please select your name."), False, None)

        if not table_data:

            return (html.Div("Please select dates."), False, None)

        # -----------------------------------------
        # Save submission to SQLite
        # -----------------------------------------

        save_availability_submission(volunteer, table_data)

        # -----------------------------------------
        # Modal content
        # -----------------------------------------

        modal_content = html.Div(
            [
                html.H4(f"Thank you {volunteer}!"),
                html.P("Your availability has been saved " "successfully."),
                html.Hr(),
                html.H5("Submitted Availability"),
                html.Ul(
                    [
                        html.Li(f"{row['date']} " f"→ " f"{row['availability']}")
                        for row in table_data
                    ]
                ),
            ]
        )

        return (
            html.Div([html.H3("Submission Successful")]),
            # Open modal
            True,
            # Modal content
            modal_content,
        )
