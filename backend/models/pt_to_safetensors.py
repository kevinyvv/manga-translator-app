import torch
from safetensors.torch import save_file

# Path to your original checkpoint
pt_path = "detect_bubble.pt"
safetensor_path = "detect_bubble.safetensors"

# Load the checkpoint
state = torch.load(pt_path, map_location="cpu", weights_only=False)

# Extract the model weights only
model_state_dict = state['model'].state_dict()

# Save as safetensors
save_file(model_state_dict, safetensor_path)

print(f"Saved safetensors weights to {safetensor_path}")
