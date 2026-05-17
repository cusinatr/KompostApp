from dash import html, dcc

goodbye_layout = html.Div(
    className="page",
    children=[
        html.Div(
            className="app-container",
            children=[
                html.H1("Uf Widerluege!", className="main-title"),
                html.H3(
                    "Vielen Dank für Ihre Unterstützung der Kompostierungsinitiative!",
                    className="subtitle",
                ),
                dcc.Link(
                    html.Button("Zurück zur Anmeldung", className="verify-button"),
                    href="/",
                ),
            ],
        )
    ],
)