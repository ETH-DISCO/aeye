cd ~ || exit

echo "Downloading best artworks..."
export PATH=$PATH:~/.local/bin/
kaggle datasets download ikarus777/best-artworks-of-all-time

echo "Unzipping..."
unzip ~/best-artworks-of-all-time.zip -d ~/best_artworks

echo "Removing zip file..."
rm ~/best_artworks-of-all-time.zip

echo "Removing directories of less famous artists..."
rm -rf ~/best_artworks/images/images/Albrecht_Du╠Иrer
rm -rf ~/best_artworks/images/images/Albrecht_DuтХа├кrer
rm -rf ~/best_artworks/images/images/Mikhail_Vrubel

echo "Moving images to main folder..."
for directory in ~/best_artworks/images/images/*; do
  if [ -d "$directory" ]; then
    mv "$directory"/* ~/best_artworks/
    rmdir "$directory"
  fi
done

echo "Removing unnecessary directories and files..."
rm -rf ~/best_artworks/images
rm -rf ~/best_artworks/artists.csv
rm -rf ~/best_artworks/resized


echo "Changing filenames..."
index=0
for file_path in ~/best_artworks/*; do
  if [ -f "$file_path" ]; then
    # Extract the filename from the path
    file_name=$(basename "$file_path")

    # Extract the filename without the extension
    filename_no_extension="${file_name%.*}"

    # Remove the final number from the filename and the underscore
    filename_no_number="${filename_no_extension%_*}"

    # Construct the new filename with the index
    new_filename="$index-$filename_no_number.${file_name##*.}"

    # Rename the file
    mv "$file_path" ~/best_artworks/"$new_filename"

    # Increment the index for the next file
    ((index++))
  fi
done