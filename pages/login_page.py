from dash import html, dcc

login_layout = html.Div(
    className="login-page",
    style={
        "minHeight": "100vh",
        "display": "flex",
        "flexDirection": "column",
        "justifyContent": "center",
        "alignItems": "center",
        "backgroundColor": "#4CAF50",
        "fontFamily": "Arial",
        "color": "white",
        "padding": "20px",
        "boxSizing": "border-box",
    },
    children=[
        html.Div(
            className="app-container",
            children=[
                # -----------------------------------------
                # Title row
                # -----------------------------------------
                html.Div(
                    className="title-row",
                    children=[
                        html.Img(
                            src="/assets/compost_left.png", className="title-image"
                        ),
                        html.H1(
                            ["MORILLON", html.Br(), "KOMPOSTPLATZ"],
                            className="main-title",
                        ),
                        html.Img(
                            src="/assets/compost_right.png", className="title-image"
                        ),
                    ],
                ),
                html.H2("EINSATZPLANERSTELLER", className="subtitle"),
                dcc.Input(
                    id="email-input",
                    type="text",
                    placeholder="Geben Sie Ihre E-Mail-Adresse ein",
                    className="email-input",
                ),
                html.Button(
                    "Anmelden",
                    id="verify-email-button",
                    n_clicks=0,
                    className="verify-button",
                ),
                html.Div(id="verification-message", className="verification-message"),
            ],
        )
    ],
)
