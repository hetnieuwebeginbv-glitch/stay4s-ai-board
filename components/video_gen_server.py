#!/usr/bin/env python3
"""Stay4S Video Generation Server - LTX-Video based

Runs on RunPod GPU. API endpoints:
  POST /generate  - Generate video from text
  POST /generate_from_image - Animate an image
  GET  /health    - Health check
"""

import os, io, base64, time, json, logging, tempfile
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import Optional
import uvicorn

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("stay4s-video")

app = FastAPI(title="Stay4S Video Generation", version="1.0")

_pipe = None

def get_pipe():
    global _pipe
    if _pipe is not None:
        return _pipe
    
    import torch
    from diffusers import LTXPipeline
    
    logger.info("Loading LTX-Video model...")
    _pipe = LTXPipeline.from_pretrained(
        "Lightricks/LTX-Video",
        torch_dtype=torch.bfloat16
    ).to("cuda")
    
    return _pipe

class VideoRequest(BaseModel):
    prompt: str
    negative_prompt: str = "blurry, bad quality, distorted"
    width: int = 512
    height: int = 320
    num_frames: int = 32
    steps: int = 20
    seed: Optional[int] = None

@app.get("/health")
async def health():
    return {"status": "ok", "service": "stay4s-video-gen", "model_loaded": _pipe is not None}

@app.post("/generate")
async def generate_video(req: VideoRequest):
    try:
        import torch
        pipe = get_pipe()
        
        generator = None
        if req.seed is not None:
            generator = torch.Generator("cuda").manual_seed(req.seed)
        
        start = time.time()
        
        video_frames = pipe(
            prompt=req.prompt,
            negative_prompt=req.negative_prompt,
            width=req.width,
            height=req.height,
            num_frames=req.num_frames,
            num_inference_steps=req.steps,
            generator=generator
        ).frames[0]
        
        elapsed = time.time() - start
        
        # Save as GIF (works without ffmpeg) or MP4
        output_path = tempfile.mktemp(suffix=".gif")
        
        from PIL import Image
        frames_pil = [Image.fromarray(frame) for frame in video_frames]
        frames_pil[0].save(
            output_path,
            save_all=True,
            append_images=frames_pil[1:],
            duration=1000//24,
            loop=0
        )
        
        with open(output_path, "rb") as f:
            video_b64 = base64.b64encode(f.read()).decode()
        
        os.unlink(output_path)
        
        logger.info(f"Generated {req.num_frames} frames in {elapsed:.1f}s")
        
        return {
            "video": video_b64,
            "prompt": req.prompt,
            "frames": req.num_frames,
            "size": f"{req.width}x{req.height}",
            "latency_ms": round(elapsed * 1000),
            "format": "gif"
        }
    except Exception as e:
        logger.error(f"Video generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return HTMLResponse("""
    <html><head><title>Stay4S Video Generation</title></head>
    <body style='font-family: sans-serif; max-width: 600px; margin: 50px auto;'>
    <h1>Stay4S Video Generation API</h1>
    <p>POST /generate with JSON body:</p>
    <pre>{"prompt": "sunset over amsterdam", "num_frames": 32}</pre>
    </body></html>
    """)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7861)
