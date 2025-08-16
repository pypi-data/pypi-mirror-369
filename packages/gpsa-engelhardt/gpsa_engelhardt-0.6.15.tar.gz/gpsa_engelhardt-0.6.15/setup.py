from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="gpsa-engelhardt",
    version="0.6.15",  
    author="Andy Jones and Barbara Engelhardt",
    author_email="engelhardtgpsa@gmail.com",
    description="Gaussian Process Spatial Alignment (GPSA)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/engelhardtgpsa/spatial-alignment",
    packages=find_packages(
        include=["gpsa", "gpsa.*"],
        exclude=("tests", "tests.*", "gpsa.tests", "gpsa.tests.*"),
    ),  # <-- CLOSES find_packages HERE
    python_requires=">=3.10, <3.12",
    license="Apache-2.0",  # keep consistent with classifier & README
    install_requires=[
        "torch==2.2.2",        # keep pinned if you want “just works” installs
        "numpy==1.26.4",
        "pandas==2.2.2",
        "scikit-learn==1.3.2",
        "pcpca==0.3",
        "plottify==1.1",
        "scanpy==1.9.1",
        "scipy==1.12.0",
        "seaborn>=0.13.2",
        "statsmodels==0.14.0",
        "anndata==0.8.0",
        "auto_mix_prep==0.2.0",
        "matplotlib>=3.8.0",
        "tqdm==4.64.0",
        "squidpy==1.1.2",
    ],
    extras_require={
        "dev": ["flake8", "pytest", "pip-tools"],
        "docs": ["pdoc", "py-cpuinfo", "Cython", "numpy"],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: Apache Software License",
    ],
    include_package_data=True,
)
