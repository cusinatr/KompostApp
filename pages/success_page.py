from dash import html


success_layout = html.Div(

    style={
        "height": "100vh",
        "display": "flex",
        "flexDirection": "column",
        "justifyContent": "center",
        "alignItems": "center",
        "fontFamily": "Arial"
    },

    children=[

        html.H1(
            "Availability Submitted Successfully"
        ),

        html.Br(),

        html.Div(
            id="success-summary",
            style={
                "marginBottom": "30px"
            }
        ),

        html.Div(

            style={
                "display": "flex",
                "gap": "20px"
            },

            children=[

                html.Button(
                    "Modify Submission",
                    id="modify-button",
                    n_clicks=0,
                    style={
                        "padding": "10px 20px"
                    }
                ),

                html.Button(
                    "Logout",
                    id="logout-button",
                    n_clicks=0,
                    style={
                        "padding": "10px 20px"
                    }
                )
            ]
        )
    ]
)