import os
import uvicorn

if __name__ == "__main__":
    # Render automatically provides a PORT environment variable
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("api.main:app", host="127.0.0.1", port=port)
