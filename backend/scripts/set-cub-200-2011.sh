cd ~ || exit

echo "Downloading CUB-200-2011 dataset..."
export PATH=$PATH:~/.local/bin/
kaggle datasets download -d wenewone/cub2002011

echo "Unzipping..."
unzip ~/cub2002011.zip -d ~/cub2002011

echo "Removing zip file..."
rm ~/cub2002011.zip

echo "Removing some directories..."
rm -rf ~/cub2002011/cvpr2016_cub
rm -rf ~/cub2002011/segmentations

# For every image in ~/cub2002011/CUB_200_2011/images, move it to ~/cub2002011. Then, remove ~/cub2002011/CUB_200_2011.
echo "Moving images..."
for dir in ~/cub2002011/CUB_200_2011/images/*; do
  for file in "$dir"/*; do
    mv "$file" ~/cub2002011
  done
done

rm -rf ~/cub2002011/CUB_200_2011

# Check that all files left are either png or jpg
echo "Checking file extensions..."
for file in ~/cub2002011/*; do
  if [[ ! "$file" =~ \.png$ ]] && [[ ! "$file" =~ \.jpg$ ]]; then
    echo "The file $file is not a png or jpg file."
    exit
  fi
done