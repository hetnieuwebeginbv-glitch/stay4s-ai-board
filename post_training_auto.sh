#!/bin/bash
# STAY4S POST-TRAINING AUTOMATION
# Runs automatically after 1.15B training completes
# Does: University training -> GGUF conversion -> HuggingFace upload -> Image/Video server start

set -e

LOG="/workspace/post_train.log"
echo "$(date): STAY4S POST-TRAINING START" | tee $LOG

# Wait for training to finish
echo "$(date): Waiting for training to finish..." | tee -a $LOG
while true; do
    if ! ps -p 391 > /dev/null 2>&1; then
        echo "$(date): Training process ended!" | tee -a $LOG
        break
    fi
    # Check latest checkpoint
    LATEST=$(ls -dt /workspace/checkpoints/cp-* 2>/dev/null | head -1)
    echo "$(date): Still training... Latest checkpoint: $LATEST" | tee -a $LOG
    sleep 300
done

echo "$(date): Training complete. Starting post-training pipeline." | tee -a $LOG

# Step 1: Save final model
echo "$(date): Step 1 - Save final model" | tee -a $LOG
LATEST=$(ls -dt /workspace/checkpoints/cp-* 2>/dev/null | head -1)
echo "$(date): Latest checkpoint: $LATEST" | tee -a $LOG

# Step 2: Run University
echo "$(date): Step 2 - Run AI University" | tee -a $LOG
cd /workspace
python3 stay4s_university.py 2>&1 | tee -a $LOG

# Step 3: Install diffusers for image/video generation
echo "$(date): Step 3 - Install diffusers" | tee -a $LOG
pip install diffusers transformers accelerate safetensors 2>&1 | tail -5 | tee -a $LOG

# Step 4: Start image generation server
echo "$(date): Step 4 - Start image generation server" | tee -a $LOG
nohup python3 image_gen_server.py > /workspace/image_server.log 2>&1 &
echo "$(date): Image server started on port 7860" | tee -a $LOG

# Step 5: Start video generation server (if LTX available)
echo "$(date): Step 5 - Start video generation server" | tee -a $LOG
nohup python3 video_gen_server.py > /workspace/video_server.log 2>&1 &
echo "$(date): Video server started on port 7861" | tee -a $LOG

# Step 6: Convert model to GGUF (if llama.cpp available)
echo "$(date): Step 6 - Convert to GGUF" | tee -a $LOG
if [ -d "/workspace/llama.cpp" ]; then
    cd /workspace/llama.cpp
    python3 convert_hf_to_gguf.py $LATEST --outfile /workspace/stay4s-1.15b.gguf 2>&1 | tee -a $LOG
    # Quantize
    ./build/bin/quantize /workspace/stay4s-1.15b.gguf /workspace/stay4s-1.15b-q4.gguf q4_0 2>&1 | tee -a $LOG
    ./build/bin/quantize /workspace/stay4s-1.15b.gguf /workspace/stay4s-1.15b-q8.gguf q8_0 2>&1 | tee -a $LOG
    echo "$(date): GGUF conversion done" | tee -a $LOG
else
    echo "$(date): llama.cpp not found, skipping GGUF" | tee -a $LOG
fi

# Step 7: Upload to HuggingFace
echo "$(date): Step 7 - Upload to HuggingFace" | tee -a $LOG
export HF_TOKEN=$HF_TOKEN
pip install huggingface_hub 2>&1 | tail -3 | tee -a $LOG
python3 -c "
from huggingface_hub import HfApi
api = HfApi()
try:
    api.create_repo('miesdevries/stay4s-1.15b', exist_ok=True)
    # Upload GGUF files
    import os
    for f in ['stay4s-1.15b.gguf', 'stay4s-1.15b-q4.gguf', 'stay4s-1.15b-q8.gguf']:
        path = f'/workspace/{f}'
        if os.path.exists(path):
            api.upload_file(path_or_fileobj=path, path_in_repo=f, repo_id='miesdevries/stay4s-1.15b')
            print(f'Uploaded {f}')
except Exception as e:
    print(f'Upload failed: {e}')
" 2>&1 | tee -a $LOG

echo "$(date): STAY4S POST-TRAINING COMPLETE" | tee -a $LOG

