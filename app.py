import dash
import dash_mantine_components as dmc

from layout import layout
from callbacks import register_callbacks

from database import initialize_database

# ---------------------------------------------------
# Initialize database
# ---------------------------------------------------

initialize_database()


# ---------------------------------------------------
# Create app
# ---------------------------------------------------

app = dash.Dash(__name__)
server = app.server


# ---------------------------------------------------
# Layout
# ---------------------------------------------------

app.layout = dmc.MantineProvider(children=layout)


# ---------------------------------------------------
# Register callbacks
# ---------------------------------------------------

register_callbacks(app)


# ---------------------------------------------------
# Run app
# ---------------------------------------------------

if __name__ == "__main__":

    app.run(debug=True)
