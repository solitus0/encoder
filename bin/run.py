import os

import uvicorn

# Set a default port number, for instance 8000, in case API_PORT isn't set.
port = int(os.environ.get("API_PORT", 8000))

if __name__ == "__main__":
    uvicorn.run("encoder.main:api", host="0.0.0.0", port=port, reload=True)
