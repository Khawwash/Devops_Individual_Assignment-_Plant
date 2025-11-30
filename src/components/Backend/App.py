import os
from .App_factory import create_app
from .config import PORT

def main():
    app = create_app()
    # For development; in Docker/Prod use gunicorn
    app.run(host="0.0.0.0", port=PORT, debug=os.getenv("FLASK_DEBUG") == "1")

if __name__ == "__main__":
    main()


