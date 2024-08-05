cd ~ || exit

echo "Downloading CIFAR-100..."
export PATH=$PATH:~/.local/bin/
kaggle datasets download -d fedesoriano/cifar100

echo "Unzipping..."
unzip ~/cifar100.zip -d ~/CIFAR-100

echo "Removing zip file..."
rm ~/cifar100.zip

echo "Removing unnecessary files..."
rm ~/CIFAR-100/meta
rm ~/CIFAR-100/file.txt

echo "Removing any directory"
find ~/CIFAR-100/* -type d -exec rm -rf {} \;

echo "Saving images to mnist folder..."
cd ~/image-viz || exit
export ENV_FILE_LOCATION=$HOME/image-viz/.env && python3 -m backend.scripts.save-cifar-100