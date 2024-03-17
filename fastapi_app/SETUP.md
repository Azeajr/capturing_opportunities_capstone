# Containerized Development Environment
 - Prerequisites
    - Docker
    - VSCode
## VSCode
[Dev Containers Tutorial](https://code.visualstudio.com/docs/devcontainers/tutorial)
- Create a new Python3 dev container(Microsoft)
- Clone repo 
```bash
git clone https://github.com/Azeajr/capturing_opportunities_capstone.git
cd capturing_opportunities_capstone/flask_app
chmod +x setup.sh
./setup.sh
```
- I ended needing to source my bashrc file to get pyenv to work
```bash 
source ~/.bashrc
pyenv install 3.11.6
poetry shell
poetry install
ENV=dev MODEL=auto_encoder uvicorn main:app --reload 
```