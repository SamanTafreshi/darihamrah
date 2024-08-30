
from plotly_app import create_dash_app

def execute_project():
    app = create_dash_app()
    app.run_server(debug=True)  # Runs the Dash app on the local server

if __name__ == "__main__":
    execute_project()