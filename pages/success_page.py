from dash import html

success_layout = html.Div(
    className="page",
    children=[
        html.Div(
            className="app-container",
            children=[
                html.H2(
                    "Verfügbarkeit erfolgreich eingereicht.",
                    className="success-title",
                ),
                html.Div(id="success-summary", className="success-summary"),
                html.Div(
                    className="button-row",
                    children=[
                        html.Button(
                            "Eingabe ändern",
                            id="modify-button",
                            n_clicks=0,
                            className="verify-button",
                        ),
                        html.Button(
                            "Abmelden",
                            id="logout-button",
                            n_clicks=0,
                            className="verify-button secondary-button",
                        ),
                    ],
                ),
            ],
        )
    ],
)
