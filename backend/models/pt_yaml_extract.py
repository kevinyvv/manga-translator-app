import torch

pt_path = "detect_bubble.pt"
state = torch.load(pt_path, map_location="cpu", weights_only=False)

# Look for model metadata
if 'model' in state:
    model_obj = state['model']
    # Some YOLO versions store 'yaml' inside model_obj
    if hasattr(model_obj, 'yaml'):
        print(model_obj.yaml)
    else:
        print("No YAML stored in model object. You may need original YAML file.")
import yaml

with open("detect_bubble.yaml", "w") as f:
    yaml.dump(model_obj.yaml, f)
