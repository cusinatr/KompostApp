from dash import html, dcc

overview_layout = html.Div(
    style={
        "width": "80%",
        "margin": "auto",
        "paddingTop": "30px",
        "fontFamily": "Arial",
    },
    children=[
        # -----------------------------------------
        # Navigation bar
        # -----------------------------------------
        html.Div(
            style={
                "display": "flex",
                "gap": "30px",
                "marginBottom": "30px",
                "borderBottom": "1px solid lightgray",
                "paddingBottom": "10px",
            },
            children=[
                dcc.Link(
                    "Scheduling",
                    href="/schedule",
                    style={
                        "fontSize": "20px",
                        "textDecoration": "none",
                        "color": "gray",
                    },
                ),
                dcc.Link(
                    "Overview",
                    href="/overview",
                    style={
                        "fontWeight": "bold",
                        "fontSize": "20px",
                        "textDecoration": "none",
                        "color": "black",
                    },
                ),
                html.A(
                    "Logout",
                    id="logout-link",
                    style={
                        "fontSize": "20px",
                        "color": "red",
                        "cursor": "pointer",
                        "textDecoration": "none",
                    },
                ),
            ],
        ),
        # -----------------------------------------
        # Title
        # -----------------------------------------
        html.H1("Volunteer Availability Overview"),
        html.Br(),
        # -----------------------------------------
        # Table
        # -----------------------------------------
        html.Div(id="overview-table-container"),
    ],
)
