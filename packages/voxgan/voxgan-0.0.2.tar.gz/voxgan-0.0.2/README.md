# voxgan

[![DOI:10.25919/cdgf-cw44](http://img.shields.io/badge/DOI-10.25919/cdgf--cw44-B31B1B.svg)](https://doi.org/10.25919/cdgf-cw44)

voxgan is a Python package to generate 2D and 3D images using Generative Adversarial Networks and PyTorch. It was developed to help along the project [FluvGAN](https://github.com/grongier/fluvgan), with no specific development planned beyond this project.

## Installation

You can directly install voxgan from pip:

    pip install voxgan

Or from GitHub using pip:

    pip install git+https://github.com/grongier/voxgan.git

To run the Jupyter notebook in [examples](examples) you will also need pandas, matplotlib, and jupyter, which you can install from pip too:

    pip install pandas matplotlib jupyter

## Usage

Here's a basic example of voxgan's API:

```
from voxgan.models.dcgan import DCGAN3d

# Define a PyTorch dataset for training
training_dataset = # TO DEFINE

# Define a GAN based on DCGAN, which includes generator and discriminator
gan = DCGAN3d()
# Configure the GAN for training, including the optimizers
gan.configure()
# Train the GAN
gan.train(training_dataset)
# Generate 10 samples
samples = gan.predict(num_samples=10)
```

For a more complete example, see the Jupyter notebook [using_voxgan.ipynb](examples/using_voxgan.ipynb) in [examples](examples). For more advanced uses of voxgan, see [FluvGAN](https://github.com/grongier/fluvgan).

## Citation

If you use voxgan in your research, please cite the original article(s) describing the method(s) you used (see the docstrings for the references). You can also cite voxgan itself:

> Rongier, G. (2021) voxgan. v1. CSIRO. Software Collection. https://doi.org/10.25919/cdgf-cw44

Here is the corresponding BibTex entry if you use LaTex:

    @misc{Rongier2021,
        author = "Rongier, Guillaume",
        title = "voxgan",
        number = "v1",
        institution = "CSIRO",
        type = "Software Collection",
        year = "2021",
        doi = "10.25919/cdgf-cw44"
    }

## Credits

This software was written by:

| [Guillaume Rongier](https://github.com/grongier) <br>[![ORCID Badge](https://img.shields.io/badge/ORCID-A6CE39?logo=orcid&logoColor=fff&style=flat-square)](https://orcid.org/0000-0002-5910-6868)</br> |
| :---: |

## License

Copyright notice: Technische Universiteit Delft hereby disclaims all copyright interest in the program voxgan written by the Author(s). Prof.dr.ir. S.G.J. Aarninkhof, Dean of the Faculty of Civil Engineering and Geosciences

&#169; 2021-2025, Guillaume Rongier  
&#169; 2020-2021, Commonwealth Scientific and Industrial Research Organisation (CSIRO) ABN 41 687 119 230

This work is licensed under a MIT OSS licence, see [LICENSE](LICENSE) for more information.
