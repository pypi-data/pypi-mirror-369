# **************************************************************************
# *
# * Authors:     James M. Krieger (jamesmkrieger@gmail.com)
# *
# * This program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation; either version 2 of the License, or
# * (at your option) any later version.
# *
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with this program; if not, write to the Free Software
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
# * 02111-1307  USA
# *
# *  All comments concerning this program package may be sent to the
# *  e-mail address 'scipion@cnb.csic.es'
# *
# **************************************************************************

import os
import pyworkflow.utils as pwutils
import pwem

from emmivox.constants import *

__version__ = "0.1"  # plugin version
_logo = "icon.png"
_references = ['hoff2024']

file_path = os.path.abspath(__file__)
dir_path = os.path.split(os.path.split(file_path)[0])[0]

class Plugin(pwem.Plugin):
    _homeVar = EMMIVOX_HOME
    _pathVars = [EMMIVOX_HOME]
    _url = "https://github.com/scipion-em/scipion-em-emmivox"
    _supportedVersions = [V1]  # binary version

    @classmethod
    def _defineVariables(cls):
        cls._defineVar(EMMIVOX_BINARY, "program")
        cls._defineEmVar(EMMIVOX_HOME, f"emmivox-{V1}")
        cls._defineVar(EMMIVOX_ENV_ACT, "conda activate emmivox-{0}".format(V1))

    @classmethod
    def getEnviron(cls):
        """ Setup the environment variables needed to launch my program. """
        environ = pwutils.Environ(os.environ)
        return environ

    @classmethod
    def getDependencies(cls):
        """ Return a list of dependencies. """
        condaActivationCmd = cls.getCondaActivationCmd()
        neededProgs = []
        if not condaActivationCmd:
            neededProgs.append('conda')
        return neededProgs

    @classmethod
    def defineBinaries(cls, env):
        for ver in VERSIONS:
            cls.addEmmiVoxPackage(env, ver,
                                  default=(ver==V1))

    @classmethod
    def addEmmiVoxPackage(cls, env, version, default=False):
        ENV_NAME = getEmmiVoxEnvName(version)
        ENV_YAML_PATH = os.path.join(dir_path, 'environment.yaml')

        EMMIVOX_ENV_INSTALLED = "emmivox_env_installed"
        EMMIVOX_PYTORCH_INSTALLED = "emmivox_pytorch_installed"
        EMMIVOX_PLUMED_INSTALLED = "emmivox_plumed_installed"
        EMMIVOX_GROMACS_INSTALLED = "emmivox_gromacs_installed"

        # ---------------------------
        # Conda environment
        # ---------------------------
        installEnv = [
            cls.getCondaActivationCmd(),
            f'conda env create -f {ENV_YAML_PATH} -n {ENV_NAME} &&',
            f'conda activate {ENV_NAME} &&',
            f'export CONDA_PREFIX=$(conda info --base)/envs/{ENV_NAME} &&',
            f'touch {EMMIVOX_ENV_INSTALLED}'
        ]

        # ---------------------------
        # PyTorch installation
        # ---------------------------
        installPytorch = [
            # Detect available GPU architectures and set TORCH_CUDA_ARCH_LIST
            'export TORCH_CUDA_ARCH_LIST=$(nvidia-smi --query-gpu=compute_cap --format=csv,noheader | '
            'sort -u | awk \'{printf "%s;", $1}\' | sed "s/;$//") &&',
            'git clone --recursive https://github.com/pytorch/pytorch.git &&',
            'cd pytorch &&',
            'git checkout v2.0.0 &&',
            'git pull &&',
            'git submodule sync &&',
            'git submodule update --init --recursive &&',
            'pip install -U -r requirements.txt &&',
            # Fix for vec256_bfloat16.h
            "sed -i 's/return map(Sleef_lgammaf8_u10);/return map((const __m256 (*)(__m256))Sleef_lgammaf8_u10);/' aten/src/ATen/cpu/vec/vec256/vec256_bfloat16.h &&",
            'python setup.py install VERBOSE=1 &&',
            f'touch {EMMIVOX_PYTORCH_INSTALLED}'
        ]

        # ---------------------------
        # PLUMED installation
        # ---------------------------
        installPlumed = []
        installPlumed.append('cd .. && wget https://github.com/plumed/plumed2/releases/download/v2.9.2/plumed-2.9.2.tgz &&')
        installPlumed.append('tar -xzf plumed-2.9.2.tgz && cd plumed-2.9.2 &&')
        installPlumed.append('export LIBTORCH_HOME=$(pwd)/../pytorch &&')  # manually compiled libtorch
        installPlumed.append('./configure --enable-libtorch &&')
        installPlumed.append('make -j$(nproc) && make install &&')
        installPlumed.append(f'touch {EMMIVOX_PLUMED_INSTALLED}')

        # ---------------------------
        # GROMACS installation patched with PLUMED
        # ---------------------------
        installGromacs = []
        installGromacs.append('cd .. && wget ftp://ftp.gromacs.org/pub/gromacs/gromacs-2023.6.tar.gz &&')
        installGromacs.append('tar -xzf gromacs-2023.6.tar.gz && cd gromacs-2023.6 &&')
        installGromacs.append('mkdir build && cd build &&')
        installGromacs.append('export PLUMED_ROOT=$(pwd)/../../plumed-2.9.2 &&')  # PLUMED path
        installGromacs.append('cmake .. -DGMX_BUILD_OWN_FFTW=ON -DGMX_GPU=ON -DGMX_USE_OPENCL=OFF -DGMX_PREFER_STATIC_LIBS=ON -DPLUMED_EXECUTABLE=$PLUMED_ROOT/bin/plumed &&')
        installGromacs.append('make -j$(nproc) && make install &&')
        installGromacs.append(f'touch {EMMIVOX_GROMACS_INSTALLED}')

        commands = []
        commands.append((" ".join(installEnv), [EMMIVOX_PYTORCH_INSTALLED]))
        commands.append((" ".join(installPytorch), [EMMIVOX_PYTORCH_INSTALLED]))
        commands.append((" ".join(installPlumed), [EMMIVOX_PLUMED_INSTALLED]))
        commands.append((" ".join(installGromacs), [EMMIVOX_GROMACS_INSTALLED]))

        env.addPackage('emmivox', version=V1,
                       tar='void.tgz',
                       commands=commands,
                       default=True)

    @classmethod
    def getEnvActivation(cls):
        return cls.getVar(EMMIVOX_ENV_ACT)

    @classmethod
    def getProgram(cls, program, script=False):
        """Create command line with conda and environment activation. """
        return '%s %s && %s' % (
                cls.getCondaActivationCmd(), cls.getEnvActivation(),
                program)
