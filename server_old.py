import os
import __init__  # noqa
from app import server

api_app = server.init_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8062))
    server.run("0.0.0.0", port)
