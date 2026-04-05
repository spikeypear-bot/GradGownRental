from src.app import create_app
from src.cli import cli

app = create_app()
app.cli.add_command(cli)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081, debug=False)
