from dash import html, dash_table, dcc
import dash_mantine_components as dmc
import yaml
from datetime import datetime, timedelta, date
from config import SETTINGS_PATH

# ---------------------------------------------------
# Load configuration
# ---------------------------------------------------

with open(SETTINGS_PATH, "r") as file:
    settings = yaml.safe_load(file)

schedule_settings = settings["schedule"]

START_DATE = schedule_settings["start_date"]
END_DATE = schedule_settings["end_date"]

SUBMISSION_DEADLINE = schedule_settings["submission_deadline"]

ALLOWED_WEEKDAYS = schedule_settings["allowed_weekdays"]

VOLUNTEERS = settings["volunteers"]


# ---------------------------------------------------
# Determine if submissions are still open
# ---------------------------------------------------

today = date.today()

deadline_date = datetime.strptime(SUBMISSION_DEADLINE, "%Y-%m-%d").date()

SUBMISSIONS_OPEN = today <= deadline_date


# ---------------------------------------------------
# Generate disabled dates
# ---------------------------------------------------

start = datetime.strptime(START_DATE, "%Y-%m-%d")
end = datetime.strptime(END_DATE, "%Y-%m-%d")

disabled_dates = []

current_date = start

while current_date <= end:

    mantine_weekday = (current_date.weekday() + 1) % 7

    if mantine_weekday not in ALLOWED_WEEKDAYS:

        disabled_dates.append(current_date.strftime("%Y-%m-%d"))

    current_date += timedelta(days=1)


# ---------------------------------------------------
# If submissions are closed, disable ALL dates
# ---------------------------------------------------

calendar_disabled_dates = disabled_dates.copy()

if not SUBMISSIONS_OPEN:

    current_date = start

    while current_date <= end:

        calendar_disabled_dates.append(current_date.strftime("%Y-%m-%d"))

        current_date += timedelta(days=1)


# ---------------------------------------------------
# Submission note
# ---------------------------------------------------

if SUBMISSIONS_OPEN:

    submission_note = html.Div(
        className="submission-note submission-note-open",
        children=[
            html.Strong("Anmeldung offen — "),
            f"Planungszeitraum: {START_DATE} → {END_DATE}   |   Einreichungsfrist: {SUBMISSION_DEADLINE}",
        ],
    )

else:

    submission_note = html.Div(
        className="submission-note submission-note-closed",
        children=[
            html.Strong("Anmeldung geschlossen — "),
            f"Die Einreichungsfrist ({SUBMISSION_DEADLINE}) ist abgelaufen.",
        ],
    )


# ---------------------------------------------------
# Layout
# ---------------------------------------------------

scheduling_layout = html.Div(
    className="page overview-page",
    children=[
        html.Div(
            className="overview-container",
            children=[
                # -----------------------------------------
                # Navigation bar
                # -----------------------------------------
                html.Div(
                    className="navbar",
                    children=[
                        dcc.Link(
                            "Einsatzplanung",
                            href="/schedule",
                            className="nav-link nav-link-active",
                        ),
                        dcc.Link(
                            "Übersicht",
                            href="/overview",
                            className="nav-link",
                        ),
                        html.A(
                            "Abmelden",
                            id="logout-link",
                            className="nav-link nav-link-logout",
                        ),
                    ],
                ),
                # -----------------------------------------
                # Submission note
                # -----------------------------------------
                submission_note,
                # -----------------------------------------
                # Welcome message
                # -----------------------------------------
                html.Div(id="welcome-message", className="welcome-message"),
                # -----------------------------------------
                # Calendar + Table side by side
                # -----------------------------------------
                dcc.Store(id="selected-dates-store", data=[]),
                html.Div(
                    className="scheduling-main",
                    children=[
                        # Calendar
                        html.Div(
                            className="calendar-wrapper",
                            children=[
                                dmc.DatePicker(
                                    id="multi-date-picker",
                                    type="multiple",
                                    value=[],
                                    minDate=START_DATE,
                                    maxDate=END_DATE,
                                    defaultDate=START_DATE,
                                    allowDeselect=True,
                                    firstDayOfWeek=1,
                                    disabledDates=calendar_disabled_dates,
                                    styles={
                                        "calendarHeader": {
                                            "display": "flex",
                                            "justifyContent": "center",
                                            "alignItems": "center",
                                            "width": "100%",
                                        },
                                        "calendarHeaderLevel": {
                                            "flex": "1",
                                            "textAlign": "center",
                                            "whiteSpace": "nowrap",
                                            "fontWeight": "bold",
                                        },
                                    },
                                ),
                                html.Div(
                                    id="service-hours-reminder",
                                    className="service-hours-reminder",
                                ),
                            ],
                        ),
                        # Table
                        html.Div(
                            className="scheduling-table-wrapper",
                            children=[
                                dash_table.DataTable(
                                    id="availability-table",
                                    fixed_rows={"headers": True},
                                    columns=[
                                        {"name": "Datum", "id": "date"},
                                        {
                                            "name": "Präferenz",
                                            "id": "availability",
                                            "presentation": "dropdown",
                                        },
                                    ],
                                    data=[],
                                    editable=True,
                                    row_deletable=True,
                                    dropdown={
                                        "availability": {
                                            "options": [
                                                {"label": "Frei", "value": "Free"},
                                                {
                                                    "label": "Kann funktionieren",
                                                    "value": "Can make it work",
                                                },
                                            ]
                                        }
                                    },
                                    style_table={
                                        "overflowX": "auto",
                                        "overflowY": "auto",
                                        "height": "100%",
                                        "borderRadius": "0.6rem",
                                        "border": "1px solid #90A4AE",
                                    },
                                    style_header={
                                        "backgroundColor": "#546E7A",
                                        "color": "white",
                                        "fontWeight": "bold",
                                        "textAlign": "center",
                                        "padding": "0.8rem 1.2rem",
                                        "fontFamily": "Arial",
                                        "fontSize": "1.1rem",
                                        "border": "none",
                                    },
                                    style_cell={
                                        "textAlign": "center",
                                        "padding": "0.7rem 1.2rem",
                                        "fontFamily": "Arial",
                                        "fontSize": "1.1rem",
                                        "border": "none",
                                        "borderTop": "1px solid #90A4AE",
                                        "color": "#1C2B33",
                                    },
                                    style_data_conditional=[
                                        {
                                            "if": {"row_index": "odd"},
                                            "backgroundColor": "#B0BEC5",
                                        },
                                        {
                                            "if": {"row_index": "even"},
                                            "backgroundColor": "#CFD8DC",
                                        },
                                        {
                                            "if": {"state": "selected"},
                                            "backgroundColor": "#90A4AE",
                                            "border": "none",
                                        },
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),
                # -----------------------------------------
                # Submit button
                # -----------------------------------------
                html.Div(
                    className="submit-wrapper",
                    children=[
                        html.Button(
                            "Einreichen",
                            id="submit-button",
                            n_clicks=0,
                            disabled=not SUBMISSIONS_OPEN,
                            className="verify-button"
                            + ("" if SUBMISSIONS_OPEN else " button-disabled"),
                        ),
                    ],
                ),
                # -----------------------------------------
                # Submission output
                # -----------------------------------------
                html.Div(id="submission-output", className="submission-output"),
            ],
        )
    ],
)
