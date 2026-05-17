from dash import html, dcc

overview_layout = html.Div(
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
                            "Einsatzplanung", href="/schedule", className="nav-link"
                        ),
                        dcc.Link(
                            "Übersicht",
                            href="/overview",
                            className="nav-link nav-link-active",
                        ),
                        html.A(
                            "Abmelden",
                            id="logout-link",
                            className="nav-link nav-link-logout",
                        ),
                    ],
                ),
                # -----------------------------------------
                # Title
                # -----------------------------------------
                html.H1(
                    "Zusammenfassung der Verfügbarkeitsmeldung",
                    className="overview-title",
                ),
                # -----------------------------------------
                # Table
                # -----------------------------------------
                html.Div(
                    id="overview-table-container", className="overview-table-wrapper"
                ),
            ],
        )
    ],
)
