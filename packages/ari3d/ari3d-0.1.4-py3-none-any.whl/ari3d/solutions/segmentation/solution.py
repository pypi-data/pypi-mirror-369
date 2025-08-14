from album.runner.api import get_args, setup

env_file = """name:  particleSeg3D
channels:
  - pytorch
  - nvidia
  - conda-forge
dependencies:
  - python=3.9
  - gxx
  - cxx-compiler
  - pytorch
  - torchvision
  - torchaudio
  - pytorch-cuda=11.
  - pip
  - numpy~=1.24
  - pip:
    - ParticleSeg3D==0.2.16
"""


# gxx is needed for some pip packages to compile C++ code
# cxx-compiler is needed for some pip packages to compile C++ code
# Note: GeodisTK, a dependency of ParticleSeg3D has a bug in the version 0.1.7 where numpy is missing.
# Hence, an installation of numpy via conda-forge first


def zarr2tiff(load_dir: str, save_dir: str, stack=True) -> None:
    import os
    from pathlib import Path

    import numpy as np
    import zarr
    from tifffile import imwrite
    from tqdm import tqdm

    Path(save_dir).mkdir(parents=True, exist_ok=True)
    image_zarr = zarr.open(load_dir, mode="r")
    num_slices = image_zarr.shape[0]

    if stack:
        # stack all slices in one tiff file
        stacked_tiff = np.stack(
            [image_zarr[i].astype(np.uint16) for i in tqdm(range(num_slices))], axis=0
        )
        imwrite(os.path.join(save_dir, "instance_mask.tiff"), stacked_tiff)
    else:
        for i in tqdm(range(num_slices)):
            imwrite(os.path.join(save_dir, f"{i}.tiff"), image_zarr[i])


def run():
    import os

    os.environ["KMP_DUPLICATE_LIB_OK"] = "True"
    import warnings
    from pathlib import Path

    from particleseg3d.conversion.nifti2zarr import nifti2zarr
    from particleseg3d.inference.inference import predict_cases, setup_model
    from tqdm import tqdm

    args = get_args()

    if os.name == "nt":
        print("Windows detected. Setting number of processes to `0`.")
        args.processes = 0

    images_path = Path(args.input).joinpath("images")  # needs to be images folder

    name = None
    if args.name:
        name = args.name.split()

    if not images_path.exists():
        raise ValueError(
            'The given input path does not exits or has the right content. Must have an "images" folder.'
        )

    if Path(args.output).exists() and any(Path(args.output).iterdir()):
        warnings.warn(
            "The given output path is not empty. This may lead to overwriting existing files."
        )

    if any(images_path.glob("*.nii*")) and not any(images_path.glob("*.zarr")):
        for nii in tqdm(
            Path(images_path).glob("*.nii*"), desc="Converting Nifti to Zarr"
        ):
            nifti2zarr(nii, Path(images_path) / (nii.stem + ".zarr"))

    z_score = tuple(float(num) for num in args.zscore.split())

    trainer, model, config = setup_model(args.model, args.fold.split())
    predict_cases(
        load_dir=args.input,
        save_dir=args.output,
        names=name,
        trainer=trainer,
        model=model,
        config=config,
        target_particle_size=float(args.target_particle_size),
        target_spacing=float(args.target_spacing),
        batch_size=int(args.batch_size),
        processes=int(args.processes),
        min_rel_particle_size=float(args.min_rel_particle_size),
        zscore=z_score,
    )

    # optional: convert output zarr to tiff
    if args.save_tiff:
        for dir in tqdm(Path(args.output).iterdir(), desc="Converting Zarr to Tiff"):
            # avoid replacing segmentation output by input
            if str(dir) == str(Path(args.input).joinpath("images")):
                continue
            for z in dir.glob("*.zarr"):
                zarr2tiff(z, Path(args.save_tiff), stack=True)


setup(
    group="de.mdc",
    name="particleSeg3D-predict",
    version="0.1.0",
    title="particleSeg3D Predict",
    description="A solution to provide the particleSeg3D environment",
    solution_creators=["Jan Philipp Albrecht", "Maximilian Otto"],
    cite=[
        {
            "text": "Scalable, out-of-the box segmentation of individual particles from mineral samples acquired with micro CT, Karol Gotkowski and Shuvam Gupta and Jose R. A. Godinho and Camila G. S. Tochtrop and Klaus H. Maier-Hein and Fabian Isensee, 2023",
            "doi": "10.48550/arXiv.2301.13319",
        }
    ],
    tags=["unet", "machine_learning", "images", "segmentation", "particleSeg3D", "3D"],
    license="Apache v2",
    documentation=["https://github.com/MIC-DKFZ/ParticleSeg3D/tree/main"],
    covers=[],
    album_api_version="0.7.0",
    args=[
        {
            "name": "input",
            "description": "Absolute input path to the base folder that contains the dataset structured in the form of the directories `images` and the metadata.json. In the `images` folder, ZARR of NIFTI data is expected.",
            "type": "string",
            "required": True,
        },
        {
            "name": "output",
            "description": "Absolute output path of the save folder.",
            "type": "string",
            "required": True,
        },
        {
            "name": "model",
            "description": "Absolute path to the directory where the model folder is stored in. If there is no folder with a model found, the pretrained model from ParticleSeg3D gets downloaded. Example: /path/to/model/Task310_particle_seg",
            "type": "string",
            "required": True,
        },
        {
            "name": "name",
            "description": "(Optional) The name(s) without extension (.zarr) of the image(s) that should be used for inference. Multiple names must be separated by spaces.",
            "type": "string",
            "required": False,
        },
        {
            "name": "zscore",
            "description": "(Optional) The target spacing in millimeters given as three numbers separate by spaces.",
            "type": "string",
            "required": False,
            "default": "5850.29762143569 7078.294543817302",
        },
        {
            "name": "target_particle_size",
            "description": "(Optional) The target particle size in pixels given as three numbers separate by spaces.",
            "type": "float",
            "required": False,
            "default": 60,
        },
        {
            "name": "target_spacing",
            "description": "(Optional) The target spacing in millimeters given as three numbers separate by spaces.",
            "type": "float",
            "required": False,
            "default": 0.1,
        },
        {
            "name": "fold",
            "description": "(Optional) The folds to use. 0, 1, 2, 3, 4 or a combination.",
            "type": "string",
            "required": False,
            "default": "0 1 2 3 4",
        },
        {
            "name": "batch_size",
            "description": "(Optional) The batch size to use during each inference iteration. A higher batch size decreases inference time, but increases the required GPU memory.",
            "type": "integer",
            "required": False,
            "default": 6,
        },
        {
            "name": "processes",
            "description": "(Optional) Number of processes to use for parallel processing. Zero to disable multiprocessing.",
            "type": "integer",
            "required": False,
            "default": 2,
        },
        {
            "name": "min_rel_particle_size",
            "description": "(Optional) Minimum relative particle size used for filtering.",
            "type": "float",
            "required": False,
            "default": 0.005,
        },
        {
            "name": "save_tiff",
            "description": "(Optional) Path where to save the predictions as TIFF files. If not set, the TIFF files will not be saved.",
            "type": "string",
            "required": False,
        },
    ],
    run=run,
    dependencies={"environment_file": env_file},
)
