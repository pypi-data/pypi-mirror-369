FROM jupyter/minimal-notebook:lab-4.0.7

USER root

RUN set -x \
    && apt-get update \
    && apt-get install -y curl vim less

# setup package, enable classic extension, build lab extension
USER "${NB_USER}"

RUN set -x \
    && mamba install -q -c conda-forge -y jupyter-server-proxy \
    && fix-permissions /opt/conda

WORKDIR "${HOME}/jupyter-brat-proxy"
COPY . .
RUN set -x \
    && python3 -m pip install "${HOME}/jupyter-brat-proxy" \
    && fix-permissions /opt/conda

WORKDIR "${HOME}"
RUN jupyter server extension enable --sys-prefix jupyter_server_proxy
RUN jupyter labextension disable "@jupyterlab/apputils-extension:announcements"

# copy configs, update permissions as root
USER root
RUN rm -rf "${HOME}/jupyter-brat-proxy"
RUN cp /etc/jupyter/jupyter_server_config.py /etc/jupyter/jupyter_server_config_base.py
COPY setup/jupyter_server_config.py /etc/jupyter/jupyter_server_config.py
RUN fix-permissions /etc/jupyter

USER "${NB_USER}"
WORKDIR "${HOME}"
