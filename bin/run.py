import os

import uvicorn

port = int(os.environ.get("API_PORT", 8090))

if __name__ == "__main__":
    uvicorn.run("encoder.main:api", host="0.0.0.0", port=port, reload=True)
