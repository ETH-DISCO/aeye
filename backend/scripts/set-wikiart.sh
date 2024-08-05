# Download the dataset from drive
# Check if the wikiart folder does not exist
if [ ! -d "$HOME/wikiart" ]; then
  echo "!!! IMPORTANT !!!Place curl command here followed by '--compressed -o ~/wikiart.tar.gz'. Then, remove this line" \
   "and the 'exit 1' line below."
  exit 1
  # Extract everything
  # First, download tar package if not present
  apt-get install unzip
  unzip ~/wikiart.tar.gz -d ~

  # Remove tar package
  rm ~/wikiart.tar.gz
fi

# The folder comes with a lot of directories. We only need the images, so move all the files outside of the directories
echo "Moving images to main folder..."
for directory in ~/wikiart/*; do
  if [ -d "$directory" ]; then
    # Extract the name of the directory from the path
    directory_name=$(basename "$directory")
    # Create new variable with the name of the directory by replacing _ with -
    directory_name="${directory_name//_/-}"
    # Add the name of the directory to the names of the files inside the directory
    for file in "$directory"/*; do
      # Extract the name of the file from the path
      file_name=$(basename "$file")
      # Add the name of the directory to the name of the file, and place and underscore between them
      file_name="${directory_name}_${file_name}"
      # Move the file to the main directory
      mv "$file" ~/wikiart/"$file_name"
    done
    # Remove the directory
    rmdir "$directory"
  fi
done

# Rename all the files. Keep everything and simply add the index at the beginning of the filename
echo "Changing filenames..."
index=0
for file_path in ~/wikiart/*; do
  # Extract the filename from the path
  file_name=$(basename "$file_path")
  # Add the index to the filename. Keep everything else
  mv "$file_path" ~/wikiart/"${index}_${file_name}"
  # Increment the index for the next file
  ((index++))
done
