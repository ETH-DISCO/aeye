cd ~ || exit

echo "Downloading MNIST..."
export PATH=$PATH:~/.local/bin/
kaggle datasets download -d hojjatk/mnist-dataset

echo "Unzipping..."
unzip ~/mnist-dataset.zip -d ~/MNIST

echo "Removing zip file..."
rm ~/mnist-dataset.zip

echo "Removing any file or directory whose name contains the word label..."
find ~/MNIST -name "*label*" -exec rm -rf {} \;

echo "Removing any directory"
find ~/MNIST/* -type d -exec rm -rf {} \;

echo "Saving images to mnist folder..."
cd ~/image-viz || exit
export ENV_FILE_LOCATION=$HOME/image-viz/.env && python -m backend.scripts.save-mnist
