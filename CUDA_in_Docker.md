# CUDA in a Docker container
1. Install or update WSL 2
	- If you don't have WSL 2, follow https://learn.microsoft.com/en-us/windows/wsl/install
	- Otherwise, update with `wsl --update` and `wsl --shutdown`
	- To test, run `wsl --list --verbose` in terminal. Starred distro should be version 2
2. (PD*) Install Docker
3. (PD*) Set Docker WSL 2 backend
	- `Settings>General>Use the WSL 2 based engine`
	- `Settings>Resources>WSL Integration>Enable integration with my default WSL distro`
4. (PD*) Install NVIDIA drivers (To test, run `nvidia-smi` in terminal)
5. Install NVIDIA Container Toolkit
	- Run `wsl` in a terminal
	- Follow https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html#installing-with-apt
	- `sudo nvidia-ctk runtime configure --runtime=docker`
6. Maximize WSL 2 resources
	- Create a file `.wslconfig` in `%UserProfile%`
	- Calculate the ram to use as your total ram - 4GB. This is CUSTOM_RAM
	- Add the following content to the file:
```
[wsl2]
memory=[CUSTOM_RAM]GB
gpu=true
```
7. Restart WSL (`wsl --shutdown`) and Docker Desktop
8. Create a Dockerfile:
```
FROM nvidia/cuda:12.1.1-base-ubuntu22.04

COPY main.py /app/main.py

RUN apt-get update && apt-get install -y python3 python3-pip
RUN python3 -m pip install --upgrade pip
RUN pip3 install torch==2.4.1 torchvision==0.19.1 torchaudio==2.4.1 --index-url https://download.pytorch.org/whl/cu121

WORKDIR /app

CMD ["python3", "main.py"]
```
9. Create main.py:
```
import torch

device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
print(f"Using device: {device}")
```
10. Start the docker container
	- `docker build -t example .` in the folder with the Dockerfile and main script
	- `docker run --gpus all example`. It should output `Using device: cuda`

PD*: Probably already done.