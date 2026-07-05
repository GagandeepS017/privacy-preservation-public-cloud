"""Development entry point: `python run.py` starts the API server."""
from src import create_app
from src.config import Config

app = create_app()

if __name__ == "__main__":
    app.run(host=Config.HOST, port=Config.PORT, debug=True)
