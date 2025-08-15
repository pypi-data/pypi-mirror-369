---
license: other
license_name: mit
license_link: https://huggingface.co/microsoft/rad-dino/blob/main/LICENSE
library_name: transformers
pipeline_tag: image-feature-extraction
---

# Model card for RAD-DINO

<!-- Provide a quick summary of what the model is/does. -->

## Model description

<!-- Provide a longer summary of what this model is. -->

RAD-DINO is a vision transformer model trained to encode chest X-rays using the self-supervised learning method [DINOv2](https://openreview.net/forum?id=a68SUt6zFt).

RAD-DINO is described in detail in [Exploring Scalable Medical Image Encoders Beyond Text Supervision (F. Pérez-García, H. Sharma, S. Bond-Taylor, et al., 2024)](https://www.nature.com/articles/s42256-024-00965-w).

- **Developed by:** Microsoft Health Futures
- **Model type:** Vision transformer
- **License:** [MIT](./LICENSE)
- **Finetuned from model:** [`dinov2-base`](https://huggingface.co/facebook/dinov2-base)

## Uses

<!-- Address questions around how the model is intended to be used, including the foreseeable users of the model and those affected by the model. -->

RAD-DINO is shared for research purposes only.
It is **not meant to be used for clinical practice**.

<!-- ### Downstream use -->

<!-- This section is for the model use when fine-tuned for a task, or when plugged into a larger ecosystem/app -->

The model is a vision backbone that can be plugged to other models for downstream tasks.
Some potential uses are:

- Image classification, with a classifier trained on top of the `CLS` token
- Image segmentation, with a decoder trained using the patch tokens
- Clustering, using the image embeddings directly
- Image retrieval, using nearest neighbors of the CLS token
- Report generation, with a language model to decode text

Fine-tuning RAD-DINO is typically not necessary to obtain good performance in downstream tasks.

<!-- ### Out-of-scope use -->

<!-- This section addresses misuse, malicious use, and uses that the model will not work well for. -->

## Biases, risks, and limitations

<!-- This section is meant to convey both technical and sociotechnical limitations. -->

RAD-DINO was trained with data from three countries, therefore it might be biased towards population in the training data.
Underlying biases of the training datasets may not be well characterized.

## Installation

```shell
pip install rad-dino
```

## Usage

### Encode an image

```python
>>> from rad_dino import RadDino
>>> from rad_dino.utils import download_sample_image
>>> encoder = RadDino()
>>> image = download_sample_image()
>>> image
<PIL.JpegImagePlugin.JpegImageFile image mode=RGB size=2765x2505 at 0x7CCD5C014050>
>>> cls_token, patch_tokens = encoder.extract_features(image)
>>> cls_embeddings.shape, patch_embeddings.shape
(torch.Size([1, 768]), torch.Size([1, 768, 37, 37]))
```

### Weights for fine-tuning

We have released a checkpoint compatible with [the original DINOv2 code](https://github.com/facebookresearch/dinov2) to help researchers fine-tune our model.

We can use the hub model and load the RAD-DINO weights.
Let's clone the DINOv2 repository so we can import the code for the head.

```shell
git clone https://github.com/facebookresearch/dinov2.git
```

```python
>>> import torch
>>> from rad_dino.utils import safetensors_to_state_dict
>>> rad_dino_gh = torch.hub.load("./dinov2", "dinov2_vitb14")
>>> backbone_state_dict = safetensors_to_state_dict("backbone_compatible.safetensors")
>>> rad_dino_gh.load_state_dict(backbone_state_dict, strict=True)
<All keys matched successfully>
```

The weights of the head are also released:

```python
>>> from dinov2.layers import DINOHead
>>> rad_dino_head_gh = DINOHead(
...    in_dim=768,
...    out_dim=65536,
...    hidden_dim=2048,
...    bottleneck_dim=256,
...    nlayers=3,
... )
>>> head_state_dict = safetensors_to_state_dict("dino_head.safetensors")
>>> rad_dino_head_gh.load_state_dict(head_state_dict, strict=True)
<All keys matched successfully>
```

### Configs and augmentation

The configuration files [`ssl_default_config.yaml`](./ssl_default_config.yaml) and [`vitb14_cxr.yaml`](./vitb14_cxr.yaml), and the [`augmentations`](./augmentations.py) module are also available in the repository to help researchers reproduce the training procedure with our hyperparameters.

## Training details

### Training data

<!-- This should link to a Dataset Card, perhaps with a short stub of information on what the training data is all about as well as documentation related to data pre-processing or additional filtering. -->

We used images from five public, deidentified chest X-ray datasets to train this checkpoint of RAD-DINO.

| Dataset   | Num. images |
| --------- | ----------: |
| [MIMIC-CXR](https://www.nature.com/articles/s41597-019-0322-0) | 368 960 |
| [CheXpert](https://ojs.aaai.org/index.php/AAAI/article/view/3834) | 223 648 |
| [NIH-CXR](https://openaccess.thecvf.com/content_cvpr_2017/html/Wang_ChestX-ray8_Hospital-Scale_Chest_CVPR_2017_paper.html) | 112 120 |
| [PadChest](https://www.sciencedirect.com/science/article/abs/pii/S1361841520301614) | 136 787 |
| [BRAX](https://www.nature.com/articles/s41597-022-01608-8) | 41 260 |
| **TOTAL** | 882 775 |

Images in the validation and test sets used to train [MAIRA](https://arxiv.org/abs/2311.13668) were excluded from the training set of RAD-DINO.
The list of image files used for training is available at [`./training_images.csv`](./training_images.csv).

Note this checkpoint is different from the one in the paper, where some private data was used (and fewer GPUs).
The checkpoint shared here is trained for 35 000 iterations (the total number of iterations in the run was 100 000, but we selected this checkpoint using linear probing on the validation sets of the evaluation datasets described in the paper).
We used 16 nodes with 4 A100 GPUs each, and a batch size of 40 images per GPU.

### Training procedure

<!-- This relates heavily to the Technical Specifications. Content here should link to that section when it is relevant to the training procedure. -->

We refer to the [manuscript](https://www.nature.com/articles/s42256-024-00965-w) for a detailed description of the training procedure.

#### Preprocessing

All DICOM files were resized using B-spline interpolation so that their shorter size was 518, min-max scaled to [0, 255], and stored as PNG files.

#### Training hyperparameters

- **Training regime:** fp16 using PyTorch-FSDP mixed-precision.

<!--fp32, fp16 mixed precision, bf16 mixed precision, bf16 non-mixed precision, fp16 non-mixed precision, fp8 mixed precision -->

## Evaluation

<!-- This section describes the evaluation protocols and provides the results. -->

Our evaluation is best described in the [manuscript](https://www.nature.com/articles/s42256-024-00965-w).

## Environmental impact

<!-- Total emissions (in grams of CO2eq) and additional considerations, such as electricity usage, go here. Edit the suggested text below accordingly -->

<!-- Carbon emissions can be estimated using the [Machine Learning Impact calculator](https://mlco2.github.io/impact#compute) presented in [Lacoste et al. (2019)](https://arxiv.org/abs/1910.09700). -->

<!-- Hardware type: A100 PCIe -->
<!-- Hours: 1d 16h = 40h -->
<!-- Cloud provider: Azure -->
<!-- Region: Italy North -->

- **Hardware type:** NVIDIA A100 GPUs
- **Hours used:** 40 hours/GPU × 16 nodes × 4 GPUs/node = 2560 GPU-hours
- **Cloud provider:** Azure
- **Compute region:** West US 2
- **Carbon emitted:** 222 kg CO₂ eq.

### Compute infrastructure

RAD-DINO was trained on [Azure Machine Learning](https://azure.microsoft.com/en-us/products/machine-learning).

#### Hardware

We used 16 `Standard_NC96ads_A100_v4` nodes with four NVIDIA A100 (80 GB) GPUs each.

#### Software

We leveraged the code in [DINOv2](https://openreview.net/forum?id=a68SUt6zFt) for training.
We used [SimpleITK](https://simpleitk.org/) and [Pydicom](https://pydicom.github.io/) for processing of DICOM files.

## Citation

<!-- If there is a paper or blog post introducing the model, the APA and Bibtex information for that should go in this section. -->

**BibTeX:**

```bibtex
@article{perez-garcia_exploring_2025,
 title = {Exploring scalable medical image encoders beyond text supervision},
 issn = {2522-5839},
 url = {https://doi.org/10.1038/s42256-024-00965-w},
 doi = {10.1038/s42256-024-00965-w},
 journal = {Nature Machine Intelligence},
 author = {P{\'e}rez-Garc{\'i}a, Fernando and Sharma, Harshita and Bond-Taylor, Sam and Bouzid, Kenza and Salvatelli, Valentina and Ilse, Maximilian and Bannur, Shruthi and Castro, Daniel C. and Schwaighofer, Anton and Lungren, Matthew P. and Wetscherek, Maria Teodora and Codella, Noel and Hyland, Stephanie L. and Alvarez-Valle, Javier and Oktay, Ozan},
 month = jan,
 year = {2025},
}
```

**APA:**

> Pérez-García, F., Sharma, H., Bond-Taylor, S., Bouzid, K., Salvatelli, V., Ilse, M., Bannur, S., Castro, D. C., Schwaighofer, A., Lungren, M. P., Wetscherek, M. T., Codella, N., Hyland, S. L., Alvarez-Valle, J., & Oktay, O. (2025). *Exploring scalable medical image encoders beyond text supervision*. In Nature Machine Intelligence. Springer Science and Business Media LLC. <https://doi.org/10.1038/s42256-024-00965-w>

## Model card contact

Fernando Pérez-García ([`fperezgarcia@microsoft.com`](mailto:fperezgarcia@microsoft.com)).
