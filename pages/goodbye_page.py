from dash import html, dcc

goodbye_layout = html.Div(
    style={
        "height": "100vh",
        "display": "flex",
        "flexDirection": "column",
        "justifyContent": "center",
        "alignItems": "center",
        "fontFamily": "Arial",
    },
    children=[
        html.H1("Goodbye!"),
        html.H3("Thank you for supporting the compost initiative."),
        html.Br(),
        dcc.Link(
            html.Button(
                "Return to Login", style={"padding": "10px 20px", "cursor": "pointer"}
            ),
            href="/",
        ),
    ],
)
