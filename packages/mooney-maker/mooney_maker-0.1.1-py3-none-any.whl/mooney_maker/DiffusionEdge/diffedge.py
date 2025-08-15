# Original code:
# Copyright 2024 Yuhang Huang
# Licensed under the Apache License, Version 2.0
#
# Modified by Lars Reining (2025)
# Modifications licensed under the MIT License
import math
import os

import numpy as np
import torch
import torch.nn as nn
import yaml
from denoising_diffusion_pytorch.data import *
from denoising_diffusion_pytorch.encoder_decoder import AutoencoderKL
from denoising_diffusion_pytorch.utils import *
from fvcore.common.config import CfgNode
from torch.utils.data import DataLoader
from tqdm.auto import tqdm

from mooney_maker.utils.load_models import download_model_weights

parent_folder = os.path.dirname(os.path.abspath(__file__))


def load_conf(config_file, conf={}):
    with open(config_file) as f:
        exp_conf = yaml.load(f, Loader=yaml.FullLoader)
        for k, v in exp_conf.items():
            conf[k] = v
    return conf


CONFIG = {
    "model": {
        "model_type": "const_sde",
        "model_name": "cond_unet",
        "image_size": [320, 320],
        "input_keys": ["image", "cond"],
        "ckpt_path": None,
        "ignore_keys": [],
        "only_model": False,
        "timesteps": 1000,
        "train_sample": -1,
        "sampling_timesteps": 1,
        "loss_type": "l2",
        "objective": "pred_noise",
        "start_dist": "normal",
        "perceptual_weight": 0,
        "scale_factor": 0.3,
        "scale_by_std": True,
        "default_scale": True,
        "scale_by_softsign": False,
        "eps": 0.0001,
        "weighting_loss": False,
        "first_stage": {
            "embed_dim": 3,
            "lossconfig": {
                "disc_start": 50001,
                "kl_weight": 1e-06,
                "disc_weight": 0.5,
                "disc_in_channels": 1,
            },
            "ddconfig": {
                "double_z": True,
                "z_channels": 3,
                "resolution": [320, 320],
                "in_channels": 1,
                "out_ch": 1,
                "ch": 128,
                "ch_mult": [1, 2, 4],
                "num_res_blocks": 2,
                "attn_resolutions": [],
                "dropout": 0.0,
            },
            "ckpt_path": None,
        },
        "unet": {
            "dim": 128,
            "cond_net": "swin",
            "without_pretrain": False,
            "channels": 3,
            "out_mul": 1,
            "dim_mults": [1, 2, 4, 4],
            "cond_in_dim": 3,
            "cond_dim": 128,
            "cond_dim_mults": [2, 4],
            "window_sizes1": [[8, 8], [4, 4], [2, 2], [1, 1]],
            "window_sizes2": [[8, 8], [4, 4], [2, 2], [1, 1]],
            "fourier_scale": 16,
            "cond_pe": False,
            "num_pos_feats": 128,
            "cond_feature_size": [80, 80],
        },
    },
    "data": {
        "name": "edge",
        "img_folder": "/data/yeyunfan/edge_detection_datasets/datasets/BSDS_test",
        "augment_horizontal_flip": True,
        "batch_size": 8,
        "num_workers": 4,
    },
    "sampler": {
        "sample_type": "slide",
        "stride": [240, 240],
        "batch_size": 1,
        "sample_num": 300,
        "use_ema": True,
        "save_folder": None,
        "ckpt_path": None,
    },
}


def get_predictions(imgs, batch_size=1):
    pre_weight_path = download_model_weights(
        "perception-lab/DiffusionEdge", "DiffusionEdgeBSDS.pt"
    )
    args = {
        "cfg": os.path.join(parent_folder, "configs", "default.yaml"),
        "pre_weight": pre_weight_path,
        "sampling_timesteps": 1,
        "bs": batch_size,
    }
    cfg = CfgNode(CONFIG)
    torch.manual_seed(42)
    np.random.seed(42)
    # random.seed(seed)
    # logger = create_logger(root_dir=cfg['out_path'])
    # writer = SummaryWriter(cfg['out_path'])
    model_cfg = cfg.model
    first_stage_cfg = model_cfg.first_stage
    first_stage_model = AutoencoderKL(
        ddconfig=first_stage_cfg.ddconfig,
        lossconfig=first_stage_cfg.lossconfig,
        embed_dim=first_stage_cfg.embed_dim,
        ckpt_path=first_stage_cfg.ckpt_path,
    )

    if model_cfg.model_name == "cond_unet":
        from denoising_diffusion_pytorch.mask_cond_unet import Unet

        unet_cfg = model_cfg.unet
        unet = Unet(
            dim=unet_cfg.dim,
            channels=unet_cfg.channels,
            dim_mults=unet_cfg.dim_mults,
            learned_variance=unet_cfg.get("learned_variance", False),
            out_mul=unet_cfg.out_mul,
            cond_in_dim=unet_cfg.cond_in_dim,
            cond_dim=unet_cfg.cond_dim,
            cond_dim_mults=unet_cfg.cond_dim_mults,
            window_sizes1=unet_cfg.window_sizes1,
            window_sizes2=unet_cfg.window_sizes2,
            fourier_scale=unet_cfg.fourier_scale,
            cfg=unet_cfg,
        )
    else:
        raise NotImplementedError
    if model_cfg.model_type == "const_sde":
        from denoising_diffusion_pytorch.ddm_const_sde import LatentDiffusion
    else:
        raise NotImplementedError(f"{model_cfg.model_type} is not surportted !")
    ldm = LatentDiffusion(
        model=unet,
        auto_encoder=first_stage_model,
        train_sample=model_cfg.train_sample,
        image_size=model_cfg.image_size,
        timesteps=model_cfg.timesteps,
        sampling_timesteps=args["sampling_timesteps"],
        loss_type=model_cfg.loss_type,
        objective=model_cfg.objective,
        scale_factor=model_cfg.scale_factor,
        scale_by_std=model_cfg.scale_by_std,
        scale_by_softsign=model_cfg.scale_by_softsign,
        default_scale=model_cfg.get("default_scale", False),
        input_keys=model_cfg.input_keys,
        ckpt_path=model_cfg.ckpt_path,
        ignore_keys=model_cfg.ignore_keys,
        only_model=model_cfg.only_model,
        start_dist=model_cfg.start_dist,
        perceptual_weight=model_cfg.perceptual_weight,
        use_l1=model_cfg.get("use_l1", True),
        cfg=model_cfg,
    )
    # ldm.init_from_ckpt(cfg.sampler.ckpt_path, use_ema=cfg.sampler.get('use_ema', True))
    data_cfg = cfg.data
    if data_cfg["name"] == "edge":
        dataset = ImagesDatasetTest(imgs)
    else:
        raise NotImplementedError

    dl = DataLoader(
        dataset,
        batch_size=cfg.sampler.batch_size,
        shuffle=False,
        pin_memory=True,
    )
    # for slide sampling, we only support batch size = 1
    sampler_cfg = cfg.sampler
    sampler_cfg.ckpt_path = args["pre_weight"]
    sampler_cfg.batch_size = args["bs"]
    # sampler_cfg.sample_num = len(dataset)
    sampler = Sampler(
        ldm,
        dl,
        batch_size=sampler_cfg.batch_size,
        sample_num=sampler_cfg.sample_num,
        cfg=cfg,
    )
    return sampler.sample()


class Sampler(object):
    def __init__(
        self,
        model,
        data_loader,
        sample_num=1000,
        batch_size=16,
        rk45=False,
        cfg={},
    ):
        super().__init__()
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.sample_num = sample_num
        self.rk45 = rk45

        self.batch_size = batch_size
        self.batch_num = math.ceil(sample_num // batch_size)

        self.image_size = model.image_size
        self.cfg = cfg

        # dataset and dataloader

        # self.ds = Dataset(folder, mask_folder, self.image_size, augment_horizontal_flip = augment_horizontal_flip, convert_image_to = convert_image_to)
        # dl = DataLoader(self.ds, batch_size = train_batch_size, shuffle = True, pin_memory = True, num_workers = cpu_count())

        self.dl = data_loader

        self.model = model.to(self.device)
        data = torch.load(cfg.sampler.ckpt_path, map_location=self.device)
        if cfg.sampler.use_ema:
            sd = data["ema"]
            new_sd = {}
            for k in sd.keys():
                if k.startswith("ema_model."):
                    new_k = k[10:]  # remove ema_model.
                    new_sd[new_k] = sd[k]
            sd = new_sd
            model.load_state_dict(sd)
        else:
            model.load_state_dict(data["model"])
        if "scale_factor" in data["model"]:
            model.scale_factor = data["model"]["scale_factor"]

    def sample(self):
        device = self.device
        batch_num = self.batch_num
        preds = []
        with torch.no_grad():
            self.model.eval()
            psnr = 0.0
            num = 0
            for idx, batch in enumerate(tqdm(self.dl, leave=False)):
                for key in batch.keys():
                    if isinstance(batch[key], torch.Tensor):
                        batch[key] = batch[key].to(device)
                # image = batch["image"]
                cond = batch["cond"]
                raw_w = batch["raw_size"][0].item()  # default batch size = 1
                raw_h = batch["raw_size"][1].item()

                mask = batch["ori_mask"] if "ori_mask" in batch else None
                bs = cond.shape[0]
                if self.cfg.sampler.sample_type == "whole":
                    batch_pred = self.whole_sample(
                        cond, raw_size=(raw_h, raw_w), mask=mask
                    )
                elif self.cfg.sampler.sample_type == "slide":
                    batch_pred = self.slide_sample(
                        cond,
                        crop_size=self.cfg.sampler.get("crop_size", [320, 320]),
                        stride=self.cfg.sampler.stride,
                        mask=mask,
                        bs=self.batch_size,
                    )
                else:
                    raise NotImplementedError
                for j, (img, c) in enumerate(zip(batch_pred, cond)):
                    preds.append(img.cpu())
        return preds

    # ----------------------------------waiting revision------------------------------------
    def slide_sample(self, inputs, crop_size, stride, mask=None, bs=8):
        """Inference by sliding-window with overlap.

        If h_crop > h_img or w_crop > w_img, the small patch will be used to
        decode without padding.

        Args:
            inputs (tensor): the tensor should have a shape NxCxHxW,
                which contains all images in the batch.
            batch_img_metas (List[dict]): List of image metainfo where each may
                also contain: 'img_shape', 'scale_factor', 'flip', 'img_path',
                'ori_shape', and 'pad_shape'.
                For details on the values of these keys see
                `mmseg/datasets/pipelines/formatting.py:PackSegInputs`.

        Returns:
            Tensor: The segmentation results, seg_logits from model of each
                input image.
        """

        h_stride, w_stride = stride
        h_crop, w_crop = crop_size
        batch_size, _, h_img, w_img = inputs.size()
        out_channels = 1
        h_grids = max(h_img - h_crop + h_stride - 1, 0) // h_stride + 1
        w_grids = max(w_img - w_crop + w_stride - 1, 0) // w_stride + 1
        preds = inputs.new_zeros((batch_size, out_channels, h_img, w_img))
        # aux_out1 = inputs.new_zeros((batch_size, out_channels, h_img, w_img))
        # aux_out2 = inputs.new_zeros((batch_size, out_channels, h_img, w_img))
        count_mat = inputs.new_zeros((batch_size, 1, h_img, w_img))
        crop_imgs = []
        x1s = []
        x2s = []
        y1s = []
        y2s = []
        for h_idx in range(h_grids):
            for w_idx in range(w_grids):
                y1 = h_idx * h_stride
                x1 = w_idx * w_stride
                y2 = min(y1 + h_crop, h_img)
                x2 = min(x1 + w_crop, w_img)
                y1 = max(y2 - h_crop, 0)
                x1 = max(x2 - w_crop, 0)
                crop_img = inputs[:, :, y1:y2, x1:x2]
                crop_imgs.append(crop_img)
                x1s.append(x1)
                x2s.append(x2)
                y1s.append(y1)
                y2s.append(y2)
        crop_imgs = torch.cat(crop_imgs, dim=0)
        crop_seg_logits_list = []
        num_windows = crop_imgs.shape[0]
        bs = bs
        length = math.ceil(num_windows / bs)
        for i in range(length):
            if i == length - 1:
                crop_imgs_temp = crop_imgs[bs * i : num_windows, ...]
            else:
                crop_imgs_temp = crop_imgs[bs * i : bs * (i + 1), ...]

            if isinstance(self.model, nn.parallel.DistributedDataParallel):
                crop_seg_logits = self.model.module.sample(
                    batch_size=crop_imgs_temp.shape[0], cond=crop_imgs_temp, mask=mask
                )
            elif isinstance(self.model, nn.Module):
                crop_seg_logits = self.model.sample(
                    batch_size=crop_imgs_temp.shape[0], cond=crop_imgs_temp, mask=mask
                )
            else:
                raise NotImplementedError

            crop_seg_logits_list.append(crop_seg_logits)
        crop_seg_logits = torch.cat(crop_seg_logits_list, dim=0)
        for crop_seg_logit, x1, x2, y1, y2 in zip(crop_seg_logits, x1s, x2s, y1s, y2s):
            preds += F.pad(
                crop_seg_logit,
                (int(x1), int(preds.shape[3] - x2), int(y1), int(preds.shape[2] - y2)),
            )
            count_mat[:, :, y1:y2, x1:x2] += 1

        assert (count_mat == 0).sum() == 0
        seg_logits = preds / count_mat
        return seg_logits

    def whole_sample(self, inputs, raw_size, mask=None):
        inputs = F.interpolate(
            inputs, size=(416, 416), mode="bilinear", align_corners=True
        )

        if isinstance(self.model, nn.parallel.DistributedDataParallel):
            seg_logits = self.model.module.sample(
                batch_size=inputs.shape[0], cond=inputs, mask=mask
            )
        elif isinstance(self.model, nn.Module):
            seg_logits = self.model.sample(
                batch_size=inputs.shape[0], cond=inputs, mask=mask
            )
        seg_logits = F.interpolate(
            seg_logits, size=raw_size, mode="bilinear", align_corners=True
        )
        return seg_logits
