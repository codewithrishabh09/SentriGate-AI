# app/middleware/validation.py
@app.middleware("http")
async def validate_content_type(request: Request, call_next):
    if request.method in ["POST", "PUT", "PATCH"]:
        content_type = request.headers.get("content-type", "")
        if "application/json" not in content_type:
            return JSONResponse(
                status_code=415,
                content={"detail": "Content-Type must be application/json"}
            )
    return await call_next(request)