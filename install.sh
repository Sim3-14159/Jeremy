# install.sh: installs Python modules and CLI tools necessary for Jeremy to work

# Create virtual environment and install packages to it.
echo -e "\t\033[33mCreating venv...033[0m"
python3 -m venv --system-site-packages venv # allow system site packages to set up easier
echo -e "\t\033[33mActivating venv...\033[0m"
source venv/bin/activate
echo -e "\t\033[33mInstalling requirements...\033[0m"
pip install -r requirements.txt
echo -e "\t\033[33mDone!\033[0m"