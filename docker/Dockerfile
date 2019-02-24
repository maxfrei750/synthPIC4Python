# =======================================================================================================================
# Nvidia Docker Image
# Source: https://gitlab.com/nvidia/cuda/blob/3f492a50c70c9b07f5dfb72f3dc3368b80ddd8e7/10.0/runtime/Dockerfile
# =======================================================================================================================
FROM nvidia/cuda:10.0-runtime-ubuntu18.04

LABEL maintainer="Max Frei <max.frei@uni-due.de>"


# =======================================================================================================================
# Jupyter Notebook Base Image
# Source: https://github.com/jupyter/docker-stacks/blob/7f1482f5a1360865bd36def104fcd716d8a89e4a/base-notebook/Dockerfile
# =======================================================================================================================
ARG NB_USER="jovyan"
ARG NB_UID="1000"
ARG NB_GID="100"

USER root

# Install all OS dependencies for notebook server that starts but lacks all
# features (e.g., download as all possible file formats)
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && apt-get -yq dist-upgrade \
 && apt-get install -yq --no-install-recommends \
    wget \
    bzip2 \
    ca-certificates \
    sudo \
    locales \
    fonts-liberation \
 && rm -rf /var/lib/apt/lists/*

RUN echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && \
    locale-gen

# Configure environment
ENV CONDA_DIR=/opt/conda \
    SHELL=/bin/bash \
    NB_USER=$NB_USER \
    NB_UID=$NB_UID \
    NB_GID=$NB_GID \
    LC_ALL=en_US.UTF-8 \
    LANG=en_US.UTF-8 \
    LANGUAGE=en_US.UTF-8
ENV PATH=$CONDA_DIR/bin:$PATH \
    HOME=/home/$NB_USER

ADD fix-permissions /usr/local/bin/fix-permissions
# Create jovyan user with UID=1000 and in the 'users' group
# and make sure these dirs are writable by the `users` group.
RUN groupadd wheel -g 11 && \
    echo "auth required pam_wheel.so use_uid" >> /etc/pam.d/su && \
    useradd -m -s /bin/bash -N -u $NB_UID $NB_USER && \
    mkdir -p $CONDA_DIR && \
    chown $NB_USER:$NB_GID $CONDA_DIR && \
    chmod g+w /etc/passwd && \
    fix-permissions $HOME && \
    fix-permissions "$(dirname $CONDA_DIR)"

USER $NB_UID

# Setup work directory for backward-compatibility
RUN mkdir /home/$NB_USER/work && \
    fix-permissions /home/$NB_USER

# Install conda as jovyan and check the md5 sum provided on the download site
ENV MINICONDA_VERSION 4.5.11
RUN cd /tmp && \
    wget --quiet https://repo.continuum.io/miniconda/Miniconda3-${MINICONDA_VERSION}-Linux-x86_64.sh && \
    echo "e1045ee415162f944b6aebfe560b8fee *Miniconda3-${MINICONDA_VERSION}-Linux-x86_64.sh" | md5sum -c - && \
    /bin/bash Miniconda3-${MINICONDA_VERSION}-Linux-x86_64.sh -f -b -p $CONDA_DIR && \
    rm Miniconda3-${MINICONDA_VERSION}-Linux-x86_64.sh && \
    $CONDA_DIR/bin/conda config --system --prepend channels conda-forge && \
    $CONDA_DIR/bin/conda config --system --set auto_update_conda false && \
    $CONDA_DIR/bin/conda config --system --set show_channel_urls true && \
    $CONDA_DIR/bin/conda install --quiet --yes conda="${MINICONDA_VERSION%.*}.*" && \
    $CONDA_DIR/bin/conda update --all --quiet --yes && \
    conda clean -tipsy && \
    rm -rf /home/$NB_USER/.cache/yarn && \
    fix-permissions $CONDA_DIR && \
    fix-permissions /home/$NB_USER

# Install Tini
RUN conda install --quiet --yes 'tini=0.18.0' && \
    conda list tini | grep tini | tr -s ' ' | cut -d ' ' -f 1,2 >> $CONDA_DIR/conda-meta/pinned && \
    conda clean -tipsy && \
    fix-permissions $CONDA_DIR && \
    fix-permissions /home/$NB_USER

# Install Jupyter Notebook, Lab, and Hub
# Generate a notebook server config
# Cleanup temporary files
# Correct permissions
# Do all this in a single RUN command to avoid duplicating all of the
# files across image layers when the permissions change
RUN conda install --quiet --yes \
    'notebook=5.7.2' \
    'jupyterhub=0.9.4' \
    'jupyterlab=0.35.4' && \
    conda clean -tipsy && \
    jupyter labextension install @jupyterlab/hub-extension@^0.12.0 && \
    npm cache clean --force && \
    jupyter notebook --generate-config && \
    rm -rf $CONDA_DIR/share/jupyter/lab/staging && \
    rm -rf /home/$NB_USER/.cache/yarn && \
    fix-permissions $CONDA_DIR && \
    fix-permissions /home/$NB_USER

USER root

EXPOSE 8888
WORKDIR $HOME

# Configure container startup
ENTRYPOINT ["tini", "-g", "--"]
CMD ["start-notebook.sh"]

# Add local files as late as possible to avoid cache busting
COPY start.sh /usr/local/bin/
COPY start-notebook.sh /usr/local/bin/
COPY start-singleuser.sh /usr/local/bin/
COPY jupyter_notebook_config.py /etc/jupyter/
RUN fix-permissions /etc/jupyter/

# Switch back to jovyan to avoid accidental container runs as root
USER $NB_UID


# =======================================================================================================================
# Jupyter Notebook Minimal Image
# Source: https://github.com/jupyter/docker-stacks/blob/7f1482f5a1360865bd36def104fcd716d8a89e4a/base-notebook/Dockerfile
# =======================================================================================================================

USER root

# Install all OS dependencies for fully functional notebook server
RUN apt-get update && apt-get install -yq --no-install-recommends \
    build-essential \
    emacs \
    git \
    inkscape \
    jed \
    libsm6 \
    libxext-dev \
    libxrender1 \
    lmodern \
    netcat \
    pandoc \
    python-dev \
    texlive-fonts-extra \
    texlive-fonts-recommended \
    texlive-generic-recommended \
    texlive-latex-base \
    texlive-latex-extra \
    texlive-xetex \
    unzip \
    nano \
    && rm -rf /var/lib/apt/lists/*

# Switch back to jovyan to avoid accidental container runs as root
USER $NB_UID


# =======================================================================================================================
# PyMesh
# Source: https://github.com/PyMesh/PyMesh/blob/a0047402e38751d0636d70d1270c61f318d68891/docker/py3.6/Dockerfile
# =======================================================================================================================
WORKDIR /root/
ARG BRANCH="master"

RUN echo "deb http://ftp.us.debian.org/debian unstable main contrib non-free" >> /etc/apt/sources.list.d/unstable.list &&\
    apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    cmake \
    libgmp-dev \
    libmpfr-dev \
    libgmpxx4ldbl \
    libboost-dev \
    libboost-thread-dev && \
    apt-get clean && \
    git clone --single-branch -b $BRANCH https://github.com/PyMesh/PyMesh.git

ENV PYMESH_PATH /root/PyMesh
WORKDIR $PYMESH_PATH

RUN git submodule update --init && \
    pip install -r $PYMESH_PATH/python/requirements.txt && \
    ./setup.py bdist_wheel && \
    rm -rf build third_party/build && \
    pip install dist/pymesh2*.whl && \
    python -c "import pymesh; pymesh.test()" && \
    python $PYMESH_PATH/docker/patches/patch_wheel.py

# =======================================================================================================================
# Blender
# Source: https://launchpad.net/~thomas-schiex/+archive/ubuntu/blender/
# =======================================================================================================================
RUN add-apt-repository ppa:thomas-schiex/blender
RUN apt-get update && apt-get install -yq --no-install-recommends \
    blender \
    nvidia-modprobe

# Add users to the video group for Blender to support CUDA.
RUN adduser root video
RUN adduser jovyan video

# =======================================================================================================================
# Final Settings
# =======================================================================================================================
WORKDIR $HOME
USER $NB_UID