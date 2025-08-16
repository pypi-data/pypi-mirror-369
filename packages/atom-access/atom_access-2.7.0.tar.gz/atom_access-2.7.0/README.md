`atom_access` is a python package for assessing the steric hindrance at any atom in a molecule or molecular fragment.

We request that any results obtained through the use of `atom_access` are accompanied by the following reference:
> Gransbury, G. K.; Corner, S. C.; Kragskow, J. G. C., Evans, P.; Yeung, H. M.; Blackmore, W. J. A.; Whitehead, G. F. S.; Vitorica-Yrezabal, I. J.; Chilton, N. F.; Mills, D. P. *AtomAccess*: A predictive tool for molecular design and its application to the targeted synthesis of dysprosium single-molecule magnets. *ChemRxiv* **2023**, DOI: 10.26434/chemrxiv-2023-28z84.

This code was developed under the ERC CoG-816268 grant with PI [David P. Mills](https://millsgroup.weebly.com/). We acknowledge Ken Gransbury for help conceptualising the `atom_access` logo. 

# Web interface

The `atom_access` [web interface](https://atom-access.com/) allows you to use AtomAccess in a browser with all the same functionality as the python package,
plus the ability to visualise rays/clusters on top of molecular models. The website's repository can be found [here](https://gitlab.com/atomaccess/atomaccess-web).

# Installation via `pip`

The easiest way to install atom_access is to use `pip`

```shell
pip install atom_access
```

some users, such as those on shared machines, may need to use the `--user` argument after `install`

# Updating via `pip`

Update the code using `pip` 

```shell
pip install --upgrade atom_access
```

some users, such as those on shared machines, may need to use the `--user` argument after `install`

# Usage

`atom_access` takes an xyz file as the input and can be run in the command line

```shell
atom_access <molecule.xyz>
```

Use `atom_access -h` to see all available options

# Developers: Installation with `pip` editable install

Clone a copy of this repository, preferably while within a directory called git

```shell
mkdir -p git; cd git
git clone https://gitlab.com/atomaccess/atomaccess
```

Navigate to the package directory

```shell
cd atom_access
```

and install the package in editable mode

```shell
pip install -e .
```
some users, such as those on shared machines, may need to use the `--user` argument after `install`

To uninstall this editable copy, use

```shell
pip uninstall atom_access
```

# Documentation

The [documentation](https://atomaccess.gitlab.io/atomaccess/) for this package is hosted by gitlab, and is automatically generated whenever new code is committed to the `main` branch.

# Bugs

If you believe you have a bug, *please check that you are using the most up to date version of the code*. 

If that does not fix the problem, please create an issue on GitLab detailing the following:
 - The commands you entered
 - The error message

If possible, try to simplify the problem as much as possible, e.g. providing an example for a small molecule rather than one with 1000 atoms.
