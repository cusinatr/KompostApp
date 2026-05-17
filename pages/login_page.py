from dash import html, dcc


login_layout = html.Div(

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
            "Compost Initiative Scheduling"
        ),

        html.H3(
            "Please provide your email"
        ),

        dcc.Input(

            id="email-input",

            type="email",

            placeholder="Enter your email",

            style={
                "width": "300px",
                "padding": "10px",
                "marginBottom": "20px"
            }
        ),

        html.Button(

            "Verify Email",

            id="verify-email-button",

            n_clicks=0
        ),

        html.Div(
            id="verification-message",
            style={
                "marginTop": "20px"
            }
        )
    ]
)