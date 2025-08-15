import sys

from . import denoising_diffusion_pytorch, taming

sys.modules["denoising_diffusion_pytorch"] = denoising_diffusion_pytorch
sys.modules["taming"] = taming
