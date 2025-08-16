# Gaussian Process Spatial Alignment (GPSA)

The **`gpsa-engelhardt`** package implements Gaussian Process Spatial Alignment, a probabilistic model for aligning spatial genomics data into a shared coordinate system using deep Gaussian processes.

> **Install name:** `gpsa-engelhardt`  
> **Import name:** `gpsa`

Paper: **Alignment of spatial genomics and histology data using deep Gaussian processes**  
➤️ https://www.biorxiv.org/content/10.1101/2022.01.10.475692v1

[View the Code on GitHub](https://github.com/engelhardtgpsa/spatial-alignment)

---

## 🚀 Installation

```bash
pip install gpsa-engelhardt
```

```python
# Usage
import gpsa
from gpsa.models import GPSA, VariationalGPSA
```

> Requires **Python 3.10+** and **[PyTorch](https://pytorch.org/)**.

---

## 🔬 Overview

`gpsa` provides two primary classes:

- **`GPSA`** — core generative model for probabilistic spatial alignment  
- **`VariationalGPSA`** — variational approximation for scalable inference

Use GPSA to jointly model multiple spatial genomics datasets and correct spatial misalignments across experiments or modalities.

---

## 🧪 Example (Test the published PyPI package)

A minimal, runnable example is provided in [`examples/grid_example.py`](examples/grid_example.py). It simulates a small synthetic dataset and runs GPSA alignment.

```bash
# Make a new virtual environment (Python 3.11 shown; 3.10 also works)
python3.11 -m venv gpsa_test_venv

# Activate the virtual environment
source gpsa_test_venv/bin/activate

# (optional) Upgrade pip
pip install --upgrade pip

# Clone the repository (for the example script)
git clone https://github.com/engelhardtgpsa/spatial-alignment.git
cd spatial-alignment

# Install GPSA from PyPI (pin to a specific version if desired)
pip install gpsa-engelhardt==0.6.15

# Run the example
python examples/grid_example.py

# Deactivate the virtual environment when done
deactivate
```

---

## 📊 Visualization

Example output showing the alignment of two misaligned spatial views:

![Synthetic Data Example](https://raw.githubusercontent.com/engelhardtgpsa/spatial-alignment/main/examples/synthetic_data_example.png)


The aligned coordinates converge during training:

![Alignment Animation](https://raw.githubusercontent.com/engelhardtgpsa/spatial-alignment/main/examples/alignment_animation.gif)

> Note that GUI backends (e.g., matplotlib with tkinter) may require extra setup on some systems.

---

## 🐞 Bug Reports

Please open issues at:  
https://github.com/engelhardtgpsa/spatial-alignment/issues

---

## 📔 Citation

If you use GPSA in your work, please cite:

> Jones, A. C., et al. **Alignment of spatial genomics and histology data using deep Gaussian processes.** *bioRxiv* (2022).  
> https://www.biorxiv.org/content/10.1101/2022.01.10.475692v1

---

## 📜 License

Apache-2.0
