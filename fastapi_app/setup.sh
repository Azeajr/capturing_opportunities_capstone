#!/bin/bash

sudo apt-get update -y && sudo apt-get upgrade -y && sudo apt-get dist-upgrade -y && sudo apt-get autoremove -y

sudo apt-get install -y build-essential git libssl-dev zlib1g-dev \
libbz2-dev libreadline-dev libsqlite3-dev curl \
libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev 

# Install Python Version Manager
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
export PYENV_ROOT="$HOME/.pyenv"
curl https://pyenv.run | bash


# Setup Python Version Manager to bashrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc
command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"


# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc


# Install Python
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
pyenv install 3.11.6 && pyenv global 3.11.6