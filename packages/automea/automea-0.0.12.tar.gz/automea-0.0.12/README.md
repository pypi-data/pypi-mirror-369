# autoMEA

*autoMEA* (Automated analysis of MEA datasets) is a open-source Python package for the analysis of Micro-Electrode Array (MEA) datasets. 

## How does autoMEA work?

Bursts are detected using the *Max Interval Method*. Users can manually set *Max Interval Parameters*, or can use a machine learning model that dynamically predicts optimal parameters for specific recording times. Several models are distributed with *automea*, and users are free to fine-tune the existing models for their specific needs, or upload new models completely.  

The machine-learning-based burst detection routine is explained in the paper accompanying the package. 

Tutorials and documentation can be found on [readthedocs](https://automea.readthedocs.io).


## Installation

The preferred way of installing `autoMEA` is to use `pip`:


```bash
pip install automea
```

## Reproducibility

All the data used to train and evaluate the machine learning models distributed with autoMEA can be found on [zenodo](https://zenodo.org/records/12685150).

## Citing

If you have used autoMEA for work that has led to a scientific publication, please cite it as

```bibtex
@article {Hernandes2024.05.08.593078,
	author = {Hernandes, Vinicius and Heuvelmans, Anouk M. and Gualtieri, Valentina and Meijer, Dimphna H. and van Woerden, Geeske M. and Greplova, Eliska},
	title = {autoMEA: Machine learning-based burst detection for multi-electrode array datasets},
	elocation-id = {2024.05.08.593078},
	year = {2024},
	doi = {10.1101/2024.05.08.593078},
	publisher = {Cold Spring Harbor Laboratory},
	URL = {https://www.biorxiv.org/content/early/2024/05/08/2024.05.08.593078},
	journal = {bioRxiv}
}

@dataset{hernandes_2024_12685150,
  author       = {Hernandes, Vinicius and
                  Heuvelmans, Anouk M. and
                  Gualtieri, Valentina and
                  Meijer, Dimphna H. and
                  van Woerden, Geeske M. and
                  Greplova, Eliska},
  title        = {{Data and scripts used in: "autoMEA: Machine 
                   learning-based burst detection for multi-electrode
                   array datasets"}},
  month        = jul,
  year         = 2024,
  publisher    = {Zenodo},
  doi          = {10.1101/2024.05.08.593078},
  url          = {https://doi.org/10.1101/2024.05.08.593078}
}
```

## Authors

Here is a list of authors who have contributed to this project:
- Vinicius Hernandes
- Anouk M. Heuvelmans
- Valentina Gualtieri
- Dimphna H. Meijer
- Geeske M. van Woerden
- Eliska Greplova

## Contributing

autoMEA is an open source package, and we invite you to contribute!
You contribute by opening [issues](https://gitlab.com/QMAI/papers/autoMEA),
fixing them, and spreading the word about `autoMEA`.

## License

This work is licensed under a [MIT License](https://opensource.org/licenses/MIT)