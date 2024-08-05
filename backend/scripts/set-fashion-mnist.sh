cd ~ || exit

echo "Downloading Fashion-MNIST..."
export PATH=$PATH:~/.local/bin/
kaggle datasets download -d zalando-research/fashionmnist

echo "Unzipping..."
unzip ~/fashionmnist.zip -d ~/Fashion-MNIST

echo "Removing zip file..."
rm ~/fashionmnist.zip

echo "Removing any file or directory whose name contains the word label..."
find ~/Fashion-MNIST -name "*label*" -exec rm -rf {} \;

echo "Removing csv files..."
find ~/Fashion-MNIST -name "*.csv" -exec rm -rf {} \;

echo "Renaming files..."
mv ~/Fashion-MNIST/train-images-idx3-ubyte ~/Fashion-MNIST/train-images.idx3-ubyte
mv ~/Fashion-MNIST/t10k-images-idx3-ubyte ~/Fashion-MNIST/t10k-images.idx3-ubyte

echo "Saving images to mnist folder..."
cd ~/image-viz || exit
export ENV_FILE_LOCATION=$HOME/image-viz/.env && python3 -m backend.scripts.save-mnist --directory Fashion-MNIST