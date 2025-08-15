import requests
import torch
from PIL import Image
from safetensors import safe_open


def download_sample_image() -> Image.Image:
    """Download chest X-ray with CC license."""
    base_url = "https://upload.wikimedia.org/wikipedia/commons"
    path = "2/20/Chest_X-ray_in_influenza_and_Haemophilus_influenzae.jpg"
    image_url = f"{base_url}/{path}"
    headers = {"User-Agent": "RAD-DINO"}
    response = requests.get(image_url, headers=headers, stream=True)
    return Image.open(response.raw)


def safetensors_to_state_dict(checkpoint_path: str) -> dict[str, torch.Tensor]:
    state_dict = {}
    with safe_open(checkpoint_path, framework="pt") as ckpt_file:
        for key in ckpt_file.keys():
            state_dict[key] = ckpt_file.get_tensor(key)
    return state_dict
