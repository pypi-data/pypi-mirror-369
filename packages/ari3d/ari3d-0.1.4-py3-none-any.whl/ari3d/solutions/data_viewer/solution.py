from album.runner.api import get_args, get_package_path, setup

env_file = """name:  data_viewer
channels:
  - conda-forge
dependencies:
  - python=3.9
  - setuptools<=80.0
  - pip
  - pip:
      - pillow
      - numpy
      - pandas
      - altair
      - streamlit
      - anndata
      - tqdm
      - joblib
      - scipy
      - PyYAML
"""


def run():
    args = get_args()

    # importing all the required packages
    import os
    import runpy
    import subprocess
    import sys

    streamlit_script_path = os.path.join(
        str(get_package_path()), "streamlit_data_viewer.py"
    )

    # build argv for streamlit
    if args.run_online:
        sys.argv = [
            "streamlit",
            "run",
            streamlit_script_path,
            args.data_path,
            args.report_path,
            args.parameter_yml,
            str(args.run_online),
        ]
        runpy.run_module("streamlit", run_name="__main__")
        # additional code can never be reached!
    else:
        # run streamlit script as standalone script
        subprocess.run(
            [
                "python",
                streamlit_script_path,
                args.data_path,
                args.report_path,
                args.parameter_yml,
                str(args.run_online),
            ],
            check=True,
        )


setup(
    group="de.mdc",
    name="data_viewer",
    version="0.1.0",
    title="Data Viewer for 3D Mineral Quantification",
    description="3D mineral quantification of particulate materials via streamlit",
    solution_creators=["Jose R.A. Godinho", "Jan Philipp Albrecht"],
    cite=[
        {
            "text": "3D mineral quantification of particulate materials with rare earth mineral inclusions: Achieving sub-voxel resolution by considering the partial volume and blurring effect: Shuvam Gupta, Vivian Moutinho, Jose R.A. Godinho, Bradley M. Guy, Jens Gutzmer, Tomography of Materials and Structures, 2025",
            "doi": "10.1016/j.tmater.2025.100050",
        }
    ],
    tags=[
        "interactivity",
        "streamlit",
        "workflow",
        "3D mineral quantification",
        "mspacman",
    ],
    license="MIT",
    documentation=[],
    covers=[],
    album_api_version="0.7.0",
    run=run,
    args=[
        {
            "name": "data_path",
            "type": "string",
            "required": True,
            "description": "Path to the histogram files",
        },
        {
            "name": "report_path",
            "type": "string",
            "required": True,
            "description": "Path used as reporting output",
        },
        {
            "name": "parameter_yml",
            "type": "string",
            "required": True,
            "description": "The path to the parameter json holding default values",
        },
        {
            "name": "run_online",
            "type": "boolean",
            "required": False,
            "default": True,
            "description": "Whether to run online or offline",
        },
    ],
    dependencies={"environment_file": env_file},
)
