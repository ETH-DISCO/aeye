cd ~ || exit

echo "Downloading COCO-2017..."
export PATH=$PATH:~/.local/bin/
kaggle datasets download -d awsaf49/coco-2017-dataset

echo "Unzipping..."
unzip ~/coco-2017-dataset.zip -d ~/COCO-2017

echo "Removing zip file..."
rm ~/coco-2017-dataset.zip

echo "Moving directories..."
mv ~/COCO-2017/coco2017/* ~/COCO-2017

echo "Removing some directories..."
rm -rf ~/COCO-2017/coco2017
rm -rf ~/COCO-2017/annotations

echo "Renaming files in train2017, val2017, and test2017 directories..."
index=0
for dir in train2017 val2017 test2017; do
  for file in ~/COCO-2017/"$dir"/*; do
    # Rename file to index.extension
    mv "$file" ~/COCO-2017/"$index.${file##*.}"
    index=$((index+1))
  done
done

echo "Removing unnecessary directories..."
rm -rf ~/COCO-2017/train2017
rm -rf ~/COCO-2017/val2017
rm -rf ~/COCO-2017/test2017