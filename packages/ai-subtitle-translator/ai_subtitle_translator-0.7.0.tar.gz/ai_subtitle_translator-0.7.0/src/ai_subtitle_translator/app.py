"""
FastAPI web service for subtitle translation.
"""

import json
import logging
import os
import tempfile
import time
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi import (
    BackgroundTasks,
    FastAPI,
    File,
    Form,
    HTTPException,
    Request,
    Response,
    UploadFile,
)
from pydantic import BaseModel

from .translate_subtitles import translate_subtitles

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def log_and_raise_http_error(request: Request, status_code: int, detail: str):
    """Log error with request context and raise HTTPException."""
    request_id = getattr(request.state, "request_id", "unknown")

    # Log the error with context
    logger.error(f"[{request_id}] HTTP {status_code}: {detail}")

    # Raise the HTTPException
    raise HTTPException(status_code=status_code, detail=detail)


def generate_translation_filename(input_path: str) -> str:
    """
    Generate smart output filename for translated subtitles.

    Handles cases where input already has language codes to avoid duplication.

    Examples:
        movie.srt -> movie.en-zh.ass
        movie.en.srt -> movie.en-zh.ass
        movie.zh.srt -> movie.en-zh.ass
        movie.fr.srt -> movie.en-zh.ass
    """
    input_file = Path(input_path)

    # Get base name by removing all suffixes (.en.srt becomes just the base name)
    # This handles double extensions automatically
    base_name = input_file.name
    for suffix in input_file.suffixes:
        base_name = base_name.replace(suffix, "", 1)

    # Generate the new filename with .en-zh.ass
    return f"{base_name}.en-zh.ass"


app = FastAPI(
    title="Bazarr AI Translate API",
    description="Advanced subtitle translator with AI support",
    version="0.1.0",
)


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    """Log detailed request information and add performance metrics."""
    # Generate unique request ID
    request_id = str(uuid4())[:8]
    start_time = time.perf_counter()

    # Extract client information
    client_ip = request.client.host if request.client else "unknown"

    # Log basic request info
    logger.info(f"[{request_id}] {request.method} {request.url.path} from {client_ip}")

    # Store request ID for error correlation
    request.state.request_id = request_id

    # Note: Parameter logging moved to endpoint to avoid consuming request body

    # Process request
    try:
        response = await call_next(request)
        process_time = time.perf_counter() - start_time

        # Log response with processing time
        logger.info(
            f"[{request_id}] Response: {response.status_code} ({process_time:.4f}s)"
        )

        # Add headers for client debugging
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(process_time)

        return response

    except Exception as e:
        logger.error(f"[{request_id}] Request failed with exception: {e}")
        raise


# In-memory job store
jobs: dict[str, dict] = {}


def create_job(job_type: str = "translation") -> str:
    """Create a new job and return its ID."""
    job_id = str(uuid4())
    jobs[job_id] = {
        "id": job_id,
        "type": job_type,
        "status": "pending",
        "progress": 0,
        "total": 0,
        "current_batch": 0,
        "message": "Job created",
        "result_file": None,
        "error": None,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }
    return job_id


def update_job(job_id: str, **updates) -> None:
    """Update job status and progress."""
    if job_id in jobs:
        jobs[job_id].update(updates)
        jobs[job_id]["updated_at"] = datetime.now().isoformat()


class TranslationResponse(BaseModel):
    """Response model for translation results."""

    success: bool
    message: str
    output_filename: str | None = None


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "🔤 Bazarr AI Translate API 🚀",
        "version": "0.1.0",
        "endpoints": {
            "translate": "/translate 🌐",
            "health": "/health ✅",
            "docs": "/docs 📚",
            "providers": "/providers ⚙️",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "✅ healthy"}


def progress_callback(job_id: str, current_batch: int, total_batches: int):
    """Callback function to update job progress."""
    progress = int((current_batch / total_batches) * 100) if total_batches > 0 else 0

    # Log progress milestones (every 25%)
    if progress > 0 and progress % 25 == 0:
        logger.info(
            f"[Job {job_id[:8]}] Progress: {progress}% (batch {current_batch}/{total_batches})"
        )

    update_job(
        job_id,
        status="processing",
        progress=progress,
        current_batch=current_batch,
        total=total_batches,
        message=f"Processing batch {current_batch} of {total_batches}",
    )


def process_translation_background(
    job_id: str,
    input_file_path: str,
    output_file_path: str,
    provider: str,
    fallback_provider: str | None,
    model: str | None,
    translation_mode: str,
    prompt_template: str,
    batch_size: int,
    request_id: str = None,
):
    """Background task to process translation."""
    try:
        # Log job start with request correlation
        input_filename = Path(input_file_path).name
        output_filename = Path(output_file_path).name
        req_info = f"[{request_id}] " if request_id else ""
        logger.info(
            f"{req_info}[Job {job_id[:8]}] Started: {input_filename} → {output_filename} "
            f"(provider: {provider}, mode: {translation_mode}, batch_size: {batch_size})"
        )

        update_job(job_id, status="processing", message="Starting translation...")

        # Create progress callback for this job
        def job_progress_callback(current_batch: int, total_batches: int):
            progress_callback(job_id, current_batch, total_batches)

        success = translate_subtitles(
            input_file=input_file_path,
            output_file=output_file_path,
            provider=provider,
            fallback_provider=fallback_provider,
            model=model,
            translation_mode=translation_mode,
            prompt_template=prompt_template,
            batch_size=batch_size,
            progress_callback=job_progress_callback,
        )

        if success:
            logger.info(
                f"{req_info}[Job {job_id[:8]}] Completed: {Path(output_file_path).name}"
            )
            update_job(
                job_id,
                status="completed",
                progress=100,
                message="Translation completed successfully",
                result_file=output_file_path,
            )
        else:
            logger.error(
                f"{req_info}[Job {job_id[:8]}] Failed: Translation failed for unknown reason"
            )
            update_job(
                job_id, status="failed", error="Translation failed for unknown reason"
            )

    except Exception as e:
        logger.error(f"{req_info}[Job {job_id[:8]}] Failed: {str(e)}")
        update_job(
            job_id,
            status="failed",
            error=str(e),
            message=f"Translation failed: {str(e)}",
        )
    finally:
        # Cleanup only input file for file upload mode, keep output file for download
        input_path = Path(input_file_path)
        if "/tmp" in str(input_path) and input_path.parent.name.startswith("tmp"):
            try:
                # Only remove input file, keep output file for download
                input_path.unlink(missing_ok=True)
                # Note: Output file is kept for result download
            except Exception:
                pass  # Don't fail if cleanup fails


@app.post("/translate")
async def translate_subtitle(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile | None = File(None, description="SRT subtitle file to upload"),
    input_path: str | None = Form(
        None, description="Path to SRT subtitle file on server"
    ),
    output_path: str | None = Form(
        None, description="Output path for translated file (file path mode only)"
    ),
):
    """
    Translate an SRT subtitle file to ASS format with AI translation (async).

    Two modes supported:
    1. File upload mode: Provide 'file' parameter with uploaded SRT file
    2. File path mode: Provide 'input_path' and optionally 'output_path' for server-side files

    Returns a job ID immediately for async processing. Use /jobs/{job_id} to check progress
    and /jobs/{job_id}/result to download the completed file.

    Args:
        background_tasks: FastAPI background tasks handler
        file: SRT subtitle file to upload (upload mode)
        input_path: Path to SRT subtitle file on server (file path mode)
        output_path: Output path for translated file (file path mode only, optional)

    Environment Variables:
        DEFAULT_PROVIDER: AI provider to use (openai, gemini, deepseek) - defaults to "deepseek"
        FALLBACK_PROVIDER: Secondary AI provider for automatic failover (optional)
        DEFAULT_MODEL: Specific model name (optional, uses provider default if not set)
        DEFAULT_TRANSLATION_MODE: Translation mode (bilingual, monolingual) - defaults to "bilingual"
        DEFAULT_PROMPT_TEMPLATE: Prompt template (full_text, selective_difficulty) - defaults to "full_text"
        DEFAULT_BATCH_SIZE: Number of lines to process per API call - defaults to "80"

    Returns:
        Job information with job_id for async processing
    """

    request_id = getattr(request.state, "request_id", "unknown")

    # Read all configuration from environment variables
    provider: str = os.getenv("DEFAULT_PROVIDER", "deepseek")
    fallback_provider: str | None = os.getenv("FALLBACK_PROVIDER")
    model: str | None = os.getenv("DEFAULT_MODEL")
    translation_mode: str = os.getenv("DEFAULT_TRANSLATION_MODE", "bilingual")
    prompt_template: str = os.getenv("DEFAULT_PROMPT_TEMPLATE", "full_text")
    batch_size: int = int(os.getenv("DEFAULT_BATCH_SIZE", "80"))

    # Log request parameters safely
    safe_params = {}
    if file is not None:
        safe_params["file"] = f"<file: {file.filename}>" if file.filename else "<file>"
    if input_path is not None:
        safe_params["input_path"] = input_path
    if output_path is not None:
        safe_params["output_path"] = output_path
    safe_params.update(
        {
            "provider": provider,
            "model": model,
            "translation_mode": translation_mode,
            "prompt_template": prompt_template,
            "batch_size": batch_size,
        }
    )

    logger.info(
        f"[{request_id}] Request parameters: {json.dumps(safe_params, default=str)}"
    )

    # Basic validation
    if file is None and input_path is None:
        log_and_raise_http_error(
            request, 400, "❌ Either 'file' or 'input_path' must be provided"
        )

    if file is not None and input_path is not None:
        log_and_raise_http_error(
            request, 400, "❌ Provide either 'file' OR 'input_path', not both"
        )

    # Validate parameters
    valid_providers = ["openai", "gemini", "deepseek"]
    if provider not in valid_providers:
        log_and_raise_http_error(
            request, 400, f"⚠️ Provider must be one of: {valid_providers}"
        )

    valid_modes = ["bilingual", "monolingual"]
    if translation_mode not in valid_modes:
        log_and_raise_http_error(
            request, 400, f"⚠️ Translation mode must be one of: {valid_modes}"
        )

    valid_templates = ["full_text", "selective_difficulty"]
    if prompt_template not in valid_templates:
        log_and_raise_http_error(
            request, 400, f"⚠️ Prompt template must be one of: {valid_templates}"
        )

    # Handle file upload mode
    if file is not None:
        # Validate file type
        if not file.filename.lower().endswith(".srt"):
            log_and_raise_http_error(
                request, 400, "❌ File must be an SRT subtitle file (.srt)"
            )

        # Create persistent temporary files for async processing
        temp_dir = tempfile.mkdtemp()

        # Save uploaded file
        input_file_path = Path(temp_dir) / file.filename
        with open(input_file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Generate smart output filename
        output_filename = generate_translation_filename(str(input_file_path))
        output_file_path = Path(temp_dir) / output_filename

        # Create job and start background task
        job_id = create_job("translation")

        background_tasks.add_task(
            process_translation_background,
            job_id,
            str(input_file_path),
            str(output_file_path),
            provider,
            fallback_provider,
            model,
            translation_mode,
            prompt_template,
            batch_size,
            getattr(request.state, "request_id", None),
        )

        return {
            "job_id": job_id,
            "status": "started",
            "message": f"Translation job started. Check progress at /jobs/{job_id}",
        }

    # Handle file path mode
    else:
        # Validate input file exists
        input_file_path = Path(input_path)
        if not input_file_path.exists():
            log_and_raise_http_error(
                request, 400, f"❌ Input file not found: {input_path}"
            )

        # Validate file type
        if not input_file_path.name.lower().endswith(".srt"):
            log_and_raise_http_error(
                request, 400, "❌ Input file must be an SRT subtitle file (.srt)"
            )

        # Determine output path
        if output_path is None:
            output_filename = generate_translation_filename(str(input_file_path))
            output_file_path = input_file_path.parent / output_filename
        else:
            output_file_path = Path(output_path)
            # Create output directory if it doesn't exist
            output_file_path.parent.mkdir(parents=True, exist_ok=True)

        # Create job and start background task
        job_id = create_job("translation")

        background_tasks.add_task(
            process_translation_background,
            job_id,
            str(input_file_path),
            str(output_file_path),
            provider,
            fallback_provider,
            model,
            translation_mode,
            prompt_template,
            batch_size,
            getattr(request.state, "request_id", None),
        )

        return {
            "job_id": job_id,
            "status": "started",
            "message": f"Translation job started. Check progress at /jobs/{job_id}",
        }


@app.get("/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Get job status and progress."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs[job_id]
    return {
        "job_id": job_id,
        "status": job["status"],
        "progress": job["progress"],
        "current_batch": job["current_batch"],
        "total_batches": job["total"],
        "message": job["message"],
        "created_at": job["created_at"],
        "updated_at": job["updated_at"],
        "error": job.get("error"),
    }


@app.get("/jobs/{job_id}/result")
async def get_job_result(job_id: str):
    """Download the result file for a completed job."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs[job_id]

    if job["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Job is not completed. Current status: {job['status']}",
        )

    result_file = job.get("result_file")
    if not result_file or not Path(result_file).exists():
        raise HTTPException(status_code=404, detail="Result file not found")

    # Read and return the file
    with open(result_file, "rb") as f:
        content = f.read()

    filename = Path(result_file).name
    return Response(
        content=content,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@app.get("/jobs")
async def list_jobs():
    """List all jobs."""
    return {"jobs": list(jobs.values())}


@app.get("/providers")
async def get_providers():
    """Get available AI providers and their status."""
    providers = {
        "openai": {
            "emoji": "🤖",
            "available": bool(os.getenv("OPENAI_API_KEY")),
            "models": ["Latest GPT models available"],
        },
        "gemini": {
            "emoji": "💎",
            "available": bool(os.getenv("GEMINI_API_KEY")),
            "models": ["Latest Gemini models available"],
        },
        "deepseek": {
            "emoji": "🧠",
            "available": bool(os.getenv("DEEPSEEK_API_KEY")),
            "models": ["Latest DeepSeek models available"],
        },
    }
    return providers
