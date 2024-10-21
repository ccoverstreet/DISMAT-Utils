# DISMAT Utils

This repository contains scripts and data processing procedures used by the DISMAT group (Dr. Maik Lang) at the University of Tennessee Knoxville. The goal of this repository is to have a common place for procedures and document different methods for future students


## Linked Repositories

These repositories also contain code/programs relevant for the DISMAT group that have either been isolated due to complexity or for producing isolated packages (ex. Python package for PyPI).

- [CCO SRIM Utility](https://github.com/ccoverstreet/CCOSRIMUTIL)
- [horiba_raman_ccoverstreet](https://github.com/ccoverstreet/horiba-raman): Python package for Raman spectra processing (particularly useful for mapping)
    - This package provides utilities for reading the various files needed to fully reproduce a Raman map with image overlay
- [AMORPH](https://github.com/ccoverstreet/AMORPH): Program for using Bayesian inference to determine amorphous and crystalline components of diffraction patterns

## Contributing

1. Create GitHub account and create SSH key or Personal Access Token
2. Fork the repository
    - Click the "Fork" button near the top right of the GitHub repository page
3. Download your forked directory using `git clone URLTOYOURFORKEDREPO` or GitHub desktop
4. Make additions/changes and **DOCUMENT changes using commits** 
5. Push your changes to your forked repository
6. Once you have all the changes completed and wish to sync your changes to the main repository (currently owned by ccoverstreet), you can create a pull request through GitHub

It is helpful to add the original repository as an upstream repository to pull changes made.

1. `git remote add upstream https://github.com/ccoverstreet/DISMAT-Utils`
2. To pull changes run `git pull upstream main`
