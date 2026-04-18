from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from metacrawl.utils.helpers import get_configured_pipeline
from metacrawl.models.models import CrawledData
from metacrawl.utils.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup / shutdown lifecycle."""
    logger.info("MetaCrawl API server starting up")
    yield
    logger.info("MetaCrawl API server shutting down")


app = FastAPI(title="MetaCrawl API", version="2.0.0", lifespan=lifespan)
pipeline = get_configured_pipeline()

class CrawlRequest(BaseModel):
    url: HttpUrl

@app.post("/crawl", response_model=CrawledData)
async def crawl_endpoint(request: CrawlRequest):
    logger.info(f"Received API request to crawl: {request.url}")
    try:
        data = await pipeline.process_url(str(request.url))
        if data.error and not data.content:
            logger.warning(f"API crawl failed for {request.url}: {data.error}")
            raise HTTPException(status_code=data.status_code or 500, detail=data.error)
        logger.info(f"Successfully processed API request for {request.url}")
        return data
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error in API endpoint for {request.url}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # log_config=None prevents uvicorn from overriding our logging setup
    uvicorn.run("metacrawl.api.app:app", host="0.0.0.0", port=8000, reload=True, log_config=None)
