import dash
from dash import html, dcc, Input, Output, State, no_update

import dash_mantine_components as dmc

from pages.login_page import login_layout
from pages.scheduling_page import scheduling_layout
from pages.overview_page import overview_layout
from pages.success_page import success_layout
from pages.goodbye_page import goodbye_layout

from callbacks import register_callbacks

from database import initialize_database


import yaml

# ---------------------------------------------------
# Load volunteers
# ---------------------------------------------------

with open("settings.yaml", "r") as file:
    settings = yaml.safe_load(file)

VOLUNTEERS = settings["volunteers"]


# ---------------------------------------------------
# Initialize database
# ---------------------------------------------------

initialize_database()


# ---------------------------------------------------
# Create app
# ---------------------------------------------------

app = dash.Dash(__name__, suppress_callback_exceptions=True)


# ---------------------------------------------------
# Main app layout
# ---------------------------------------------------

app.layout = dmc.MantineProvider(
    children=[
        dcc.Location(id="url", refresh=False),
        dcc.Store(id="verified-volunteer-store", data=None),
        dcc.Store(id="submitted-data-store", data=[]),
        html.Div(id="page-content"),
    ]
)


# ---------------------------------------------------
# Router
# ---------------------------------------------------


@app.callback(
    Output("page-content", "children"),
    Output("url", "pathname", allow_duplicate=True),
    Input("url", "pathname"),
    State("verified-volunteer-store", "data"),
    prevent_initial_call=True,
)
def display_page(pathname, volunteer):

    # -----------------------------------------
    # Protected pages
    # -----------------------------------------

    protected_pages = ["/schedule", "/overview", "/success"]

    # -----------------------------------------
    # Redirect unauthenticated users
    # -----------------------------------------

    if pathname in protected_pages and not volunteer:

        return (login_layout, "/")

    # -----------------------------------------
    # Scheduling page
    # -----------------------------------------

    if pathname == "/schedule":

        return (scheduling_layout, pathname)

    # -----------------------------------------
    # Overview page
    # -----------------------------------------

    elif pathname == "/overview":

        return (overview_layout, pathname)

    # -----------------------------------------
    # Success page
    # -----------------------------------------

    elif pathname == "/success":

        return (success_layout, pathname)

    # -----------------------------------------
    # Goodbye page
    # -----------------------------------------

    elif pathname == "/goodbye":

        return (goodbye_layout, pathname)

    # -----------------------------------------
    # Default login page
    # -----------------------------------------

    return (login_layout, "/")


# ---------------------------------------------------
# Email verification callback
# ---------------------------------------------------


@app.callback(
    Output("verification-message", "children"),
    Output("verified-volunteer-store", "data"),
    Output("url", "pathname"),
    Input("verify-email-button", "n_clicks"),
    State("email-input", "value"),
    prevent_initial_call=True,
)
def verify_email(n_clicks, email):

    if not email:

        return ("", None, no_update)

    email = email.strip().lower()

    for volunteer in VOLUNTEERS:

        volunteer_email = volunteer["email"].strip().lower()

        if email == volunteer_email:

            volunteer_name = volunteer["name"]

            return ("", volunteer_name, "/schedule")

    # -----------------------------------------
    # Email not recognized
    # -----------------------------------------

    return (
        html.Div("E-Mail-Adresse nicht erkannt.", style={"color": "red"}),
        None,
        no_update,
    )


# ---------------------------------------------------
# Register scheduling callbacks
# ---------------------------------------------------

register_callbacks(app)


# ---------------------------------------------------
# Run app
# ---------------------------------------------------

if __name__ == "__main__":

    app.run(debug=True)