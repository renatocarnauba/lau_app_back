import os

import uvicorn
from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv()
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "app.main:app", host="0.0.0.0", port=port, log_level="info", reload=True
    )
