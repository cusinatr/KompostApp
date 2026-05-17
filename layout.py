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

    # Python weekday:
    # Monday=0 ... Sunday=6
    #
    # Mantine weekday:
    # Sunday=0 ... Saturday=6
    #
    # Convert Python → Mantine
    mantine_weekday = (current_date.weekday() + 1) % 7

    if mantine_weekday not in ALLOWED_WEEKDAYS:

        disabled_dates.append(current_date.strftime("%Y-%m-%d"))

    current_date += timedelta(days=1)


# ---------------------------------------------------
# If submissions are closed,
# disable ALL dates
# ---------------------------------------------------

calendar_disabled_dates = disabled_dates.copy()

if not SUBMISSIONS_OPEN:

    current_date = start

    while current_date <= end:

        calendar_disabled_dates.append(current_date.strftime("%Y-%m-%d"))

        current_date += timedelta(days=1)


# ---------------------------------------------------
# Volunteer dropdown options
# ---------------------------------------------------

volunteer_options = [
    {"label": volunteer, "value": volunteer} for volunteer in VOLUNTEERS
]


# ---------------------------------------------------
# Note component
# ---------------------------------------------------

if SUBMISSIONS_OPEN:

    submission_note = dmc.Alert(
        title="Availability Submission Open",
        children=[
            html.Div(f"Scheduling period: " f"{START_DATE} → {END_DATE}"),
            html.Div(f"Submission deadline: " f"{SUBMISSION_DEADLINE}"),
        ],
        color="green",
        mb="lg",
    )

else:

    submission_note = dmc.Alert(
        title="Availability Submission Closed",
        children=[
            html.Div(
                f"The submission deadline " f"({SUBMISSION_DEADLINE}) " f"has passed."
            )
        ],
        color="red",
        mb="lg",
    )


# ---------------------------------------------------
# Layout
# ---------------------------------------------------

layout = html.Div(
    style={
        "width": "60%",
        "margin": "auto",
        "fontFamily": "Arial",
        "paddingTop": "30px",
    },
    children=[
        # -----------------------------------------
        # Title
        # -----------------------------------------
        html.H1("Compost Initiative Scheduling"),
        # -----------------------------------------
        # Submission information note
        # -----------------------------------------
        submission_note,
        # -----------------------------------------
        # Volunteer dropdown
        # -----------------------------------------
        html.Label("Volunteer Name"),
        # -----------------------------------------
        # Email verification
        # -----------------------------------------
        html.Label("Volunteer Email"),
        dcc.Input(
            id="email-input",
            type="email",
            placeholder="Enter your email",
            disabled=not SUBMISSIONS_OPEN,
            style={"width": "100%", "padding": "10px", "marginBottom": "10px"},
        ),
        html.Button(
            "Verify Email",
            id="verify-email-button",
            n_clicks=0,
            disabled=not SUBMISSIONS_OPEN,
            style={"marginBottom": "20px"},
        ),
        html.Div(id="verification-message", style={"marginBottom": "20px"}),
        # Store verified volunteer
        dcc.Store(id="verified-volunteer-store", data=None),
        # -----------------------------------------
        # Calendar
        # -----------------------------------------
        html.H3("Select Your Available Dates"),
        dmc.DatePicker(
            id="multi-date-picker",
            type="multiple",
            value=[],
            minDate=START_DATE,
            maxDate=END_DATE,
            # Open initially on first scheduling month
            defaultDate=START_DATE,
            allowDeselect=True,
            firstDayOfWeek=1,
            disabledDates=calendar_disabled_dates,
            style={"marginBottom": "30px", "pointerEvents": "none", "opacity": "0.5"},
        ),
        # -----------------------------------------
        # Internal store
        # -----------------------------------------
        dcc.Store(id="selected-dates-store", data=[]),
        # -----------------------------------------
        # Availability table
        # -----------------------------------------
        dash_table.DataTable(
            id="availability-table",
            columns=[
                {"name": "Date", "id": "date"},
                {
                    "name": "Availability",
                    "id": "availability",
                    "presentation": "dropdown",
                },
            ],
            data=[],
            editable=False,
            row_deletable=False,
            dropdown={
                "availability": {
                    "options": [
                        {"label": "Free", "value": "Free"},
                        {"label": "Can make it work", "value": "Can make it work"},
                    ]
                }
            },
            style_table={"overflowX": "auto"},
            style_cell={"textAlign": "left", "padding": "10px"},
        ),
        html.Br(),
        # -----------------------------------------
        # Submit button
        # -----------------------------------------
        html.Button(
            "Submit",
            id="submit-button",
            n_clicks=0,
            disabled=True,
            style={
                "padding": "10px 20px",
                "backgroundColor": "green",
                "color": "white",
                "border": "none",
                "cursor": "pointer",
                "opacity": ("1" if SUBMISSIONS_OPEN else "0.5"),
            },
        ),
        # -----------------------------------------
        # Submission output
        # -----------------------------------------
        # Popup confirmation dialog
        dmc.Modal(
            id="submission-modal",
            title="Availability Submitted",
            opened=False,
            centered=True,
            size="lg",
            children=[html.Div(id="submission-modal-content")],
        ),
        html.Div(id="submission-output", style={"marginTop": "30px"}),
    ],
)
