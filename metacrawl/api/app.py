from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, HttpUrl
from metacrawl.utils.helpers import get_configured_pipeline
from metacrawl.models.models import CrawledData, ErrorResponse
from metacrawl.utils.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup / shutdown lifecycle."""
    logger.info("MetaCrawl API server starting up")
    yield
    logger.info("MetaCrawl API server shutting down")


app = FastAPI(
    title="MetaCrawl API", 
    version="2.0.0", 
    lifespan=lifespan,
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal Server Error",
            detail=str(exc),
            status_code=500
        ).model_dump()
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(f"HTTP exception: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=str(exc.detail),
            status_code=exc.status_code
        ).model_dump()
    )

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
            return JSONResponse(
                status_code=data.status_code or 500,
                content=ErrorResponse(
                    error=data.error,
                    status_code=data.status_code or 500,
                    url=str(request.url)
                ).model_dump()
            )
        logger.info(f"Successfully processed API request for {request.url}")
        return data
    except Exception as e:
        logger.exception(f"Unexpected error in API endpoint for {request.url}: {e}")
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                error="Internal processing error",
                detail=str(e),
                status_code=500,
                url=str(request.url)
            ).model_dump()
        )

if __name__ == "__main__":
    import uvicorn
    # log_config=None prevents uvicorn from overriding our logging setup
    uvicorn.run("metacrawl.api.app:app", host="0.0.0.0", port=8000, reload=True, log_config=None)
