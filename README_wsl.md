Chcete-li nainstalovat nvcc (NVIDIA CUDA Compiler) verze 11.7, postupujte podle následujících kroků:

1. Přidání NVIDIA repozitáře
Nejprve přidejte repozitář NVIDIA CUDA na váš systém:

wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/cuda-ubuntu2004.pin
sudo mv cuda-ubuntu2004.pin /etc/apt/preferences.d/cuda-repository-pin-600
wget https://developer.download.nvidia.com/compute/cuda/11.7.0/local_installers/cuda-repo-ubuntu2004-11-7-local_11.7.0-515.43.04-1_amd64.deb
sudo dpkg -i cuda-repo-ubuntu2004-11-7-local_11.7.0-515.43.04-1_amd64.deb
sudo cp /var/cuda-repo-ubuntu2004-11-7-local/cuda-*-keyring.gpg /usr/share/keyrings/
sudo apt-get update

2. Instalace CUDA Toolkitu
Nainstalujte CUDA Toolkit 11.7:
sudo apt-get install -y cuda-11-7

3. Nastavení proměnných prostředí
Přidejte CUDA do PATH a LD_LIBRARY_PATH. Otevřete svůj ~/.bashrc nebo ~/.zshrc a přidejte:
export PATH=/usr/local/cuda-11.7/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda-11.7/lib64:$LD_LIBRARY_PATH

Poté načtěte změny:
source ~/.bashrc

4. Ověření instalace
Zkontrolujte, zda je nvcc správně nainstalován:
source ~/.bashrc

Měli byste vidět výstup potvrzující verzi nvcc 11.7.
nvcc --version

Similar code found with 2 license types - View matches