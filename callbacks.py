from dash import Input, Output, State, html, callback_context
from dash.exceptions import PreventUpdate

from database import save_availability_submission


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
        Input("submit-button", "n_clicks"),
        State("name-input", "value"),
        State("availability-table", "data"),
        prevent_initial_call=True,
    )
    def submit_form(n_clicks, volunteer, table_data):

        if not volunteer:
            return html.Div("Please select your name.")

        if not table_data:
            return html.Div("Please select dates.")

        # Save submission to SQLite
        save_availability_submission(volunteer, table_data)

        return html.Div(
            [
                html.H3("Submission Successful"),
                html.P(f"Availability saved for {volunteer}."),
                html.H4("Submitted Availability:"),
                html.Ul(
                    [
                        html.Li(f"{row['date']} → {row['availability']}")
                        for row in table_data
                    ]
                ),
            ]
        )
