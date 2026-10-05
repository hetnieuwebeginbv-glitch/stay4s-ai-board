#!/usr/bin/env python3
"""Stay4S Image Generation Server - FLUX/SD based image generation API

Runs on RunPod GPU. API endpoints:
  POST /generate  - Generate image from text
  POST /upscale   - Upscale image  
  GET  /health    - Health check
  GET  /models    - List available models
"""

import os, io, base64, time, json, logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel
from typing import Optional
import uvicorn

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("stay4s-image")

app = FastAPI(title="Stay4S Image Generation", version="1.0")

# Lazy load model
_pipe = None
_model_type = None

def get_pipe(model_name="sd"):
    global _pipe, _model_type
    if _pipe is not None and _model_type == model_name:
        return _pipe
    
    import torch
    if model_name == "flux":
        from diffusers import FluxPipeline
        logger.info("Loading FLUX.1-schnell model...")
        _pipe = FluxPipeline.from_pretrained(
            "black-forest-labs/FLUX.1-schnell",
            torch_dtype=torch.bfloat16
        ).to("cuda")
        _model_type = "flux"
    else:
        from diffusers import StableDiffusionPipeline
        logger.info("Loading Stable Diffusion 1.5 model...")
        _pipe = StableDiffusionPipeline.from_pretrained(
            "runwayml/stable-diffusion-v1-5",
            torch_dtype=torch.float16,
            safety_checker=None
        ).to("cuda")
        _model_type = "sd"
    
    return _pipe

class GenerateRequest(BaseModel):
    prompt: str
    negative_prompt: str = "blurry, bad quality, distorted, ugly"
    width: int = 512
    height: int = 512
    steps: int = 20
    model: str = "sd"
    seed: Optional[int] = None

@app.get("/health")
async def health():
    return {"status": "ok", "service": "stay4s-image-gen", "gpu": _model_type is not None}

@app.get("/models")
async def models():
    return {"models": ["sd", "flux"], "current": _model_type}

@app.post("/generate")
async def generate(req: GenerateRequest):
    try:
        import torch
        pipe = get_pipe(req.model)
        
        generator = None
        if req.seed is not None:
            generator = torch.Generator("cuda").manual_seed(req.seed)
        
        start = time.time()
        
        if req.model == "flux":
            image = pipe(
                prompt=req.prompt,
                width=req.width,
                height=req.height,
                num_inference_steps=req.steps,
                generator=generator
            ).images[0]
        else:
            image = pipe(
                prompt=req.prompt,
                negative_prompt=req.negative_prompt,
                width=req.width,
                height=req.height,
                num_inference_steps=req.steps,
                generator=generator
            ).images[0]
        
        elapsed = time.time() - start
        
        buf = io.BytesIO()
        image.save(buf, format="PNG")
        img_b64 = base64.b64encode(buf.getvalue()).decode()
        
        logger.info(f"Generated {req.width}x{req.height} in {elapsed:.1f}s")
        
        return {
            "image": img_b64,
            "prompt": req.prompt,
            "size": f"{req.width}x{req.height}",
            "model": req.model,
            "latency_ms": round(elapsed * 1000),
            "format": "png"
        }
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return HTMLResponse("""
    <html><head><title>Stay4S Image Generation</title></head>
    <body style='font-family: sans-serif; max-width: 600px; margin: 50px auto;'>
    <h1>Stay4S Image Generation API</h1>
    <p>POST /generate with JSON body:</p>
    <pre>{"prompt": "a cat in space", "width": 512, "height": 512}</pre>
    <p>Models: sd (Stable Diffusion 1.5), flux (FLUX.1-schnell)</p>
    </body></html>
    """)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)
