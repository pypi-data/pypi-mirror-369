=======================
Scipion ProDy plugin
=======================

This plugin provides a wrapper around EMMIVox software for ensemble refinement using Gromacs and Plumed.

Installation
-------------

You will need to use 3.0+ version of Scipion to be able to run these protocols. To install the plugin, you have one option so far:

Developer's version

   * download repository

    .. code-block::

        git clone https://github.com/scipion-em/scipion-em-emmivox.git

   * install

    .. code-block::

       scipion3 installp -p ./scipion-em-emmivox --devel

ProDy software will be installed automatically with the plugin but you can also use an another version 
by installing that one in your scipion3 environment.

**Important:** you need to have conda (miniconda3 or anaconda3) pre-installed to use this program.

Configuration variables
-----------------------
*CONDA_ACTIVATION_CMD*: If undefined, it will rely on conda command being in the
PATH (not recommended), which can lead to execution problems mixing scipion
python with conda ones. One example of this could can be seen below but
depending on your conda version and shell you will need something different:
CONDA_ACTIVATION_CMD = eval "$(/extra/miniconda3/bin/conda shell.bash hook)"

*PRODY_ENV_ACT*: If undefined, it will point to the prody-github as the default:
PRODY_ENV_ACT = conda activate emmivox-1.0

It could be changed as follows:
PRODY_ENV_ACT = conda activate emmivox-1.0


Protocols
----------
There are currently no protocols, besides a hello world. These will be added later.

Right now the plugin is being used for installation.
