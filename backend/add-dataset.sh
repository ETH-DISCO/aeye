sudo echo "Starting adding dataset..."

# Check that the script is being run from the backend directory using pwd
if [ "$(pwd)" != "$HOME/image-viz/backend" ]; then
  echo "Please run this script from the backend directory."
  exit
fi

# Read variables from new-dataset-info.env
directory=$(grep "DIRECTORY=" ./new-dataset-info.env | cut -d '=' -f2)
dataset_name=$(grep "DATASET_NAME=" ./new-dataset-info.env | cut -d '=' -f2)
website_name=$(grep "WEBSITE_NAME=" ./new-dataset-info.env | cut -d '=' -f2)
overwrite=$(grep "OVERWRITE_IF_EXISTS=" ./new-dataset-info.env | cut -d '=' -f2)
class_name=$(grep "CLASS_NAME=" ./new-dataset-info.env | cut -d '=' -f2)
collate_fn=$(grep "COLLATE_FN=" ./new-dataset-info.env | cut -d '=' -f2)
batch_size=$(grep "BATCH_SIZE=" ./new-dataset-info.env | cut -d '=' -f2)
resize=$(grep "RESIZE=" ./new-dataset-info.env | cut -d '=' -f2)

# Check if the directory exists
if [ ! -d "$HOME/$directory" ]; then
  echo "The directory does not exist. Please make sure the dataset is in HOME."
  exit
fi
# Check dataset name for white spaces or special characters and check that the name is shorter than 20 characters and
# not empty
if [[ ! "$dataset_name" =~ ^[a-zA-Z0-9_]+$ ]] || [ ${#dataset_name} -gt 20 ] || [ -z "$dataset_name" ]; then
  echo "The dataset name can only contain letters, numbers, and underscores, and must be 20 characters or less."
  exit
fi

# Export the environment variable
export ENV_FILE_LOCATION=$HOME/image-viz/.env

result=$(python3 -m src.dataset_creation.check_if_dataset_exists -c "$dataset_name")
if [ $? -ne 0 ]; then
  exit
fi

if [ "$result" != "All good." ]; then
  if [ "$overwrite" != "y" ]; then
    echo "The dataset already exists. If you want to overwrite it, set OVERWRITE_IF_EXISTS=y in new-dataset-info.env."
    exit
  fi
fi

# Run the script to add the dataset to datasets.json
if ! python3 -m src.dataset_creation.add_dataset_to_list -c "$dataset_name" -s "$class_name" -f "$collate_fn" -l "$directory" -w "$website_name"; then
  exit
fi

# Create dataset with embeddings
echo "Creating dataset with embeddings..."
if ! python3 -m src.db_utilities.create_and_populate_embeddings_collection -c "$dataset_name" -b "$batch_size" -r y; then
  exit
fi

# Create tiles and image-to-tile collections
echo "Creating tiles and image-to-tile collections..."
if ! python3 -m src.db_utilities.create_and_populate_clusters_collection -c "$dataset_name" -r y; then
  exit
fi

if [ "$resize" == "y" ]; then
  # Resize images
  echo "Resizing images..."
  if ! python3 -m src.resize_images -d "$dataset_name" -o n; then
    exit
  fi
fi

echo "Creating minimap..."
python3 -m src.report.scatter -c "$dataset_name"

# Add location to the nginx.conf.template file
echo "Adding location to nginx.conf.template..."
# First, update the nginx.conf.json file
python3 -m src.dataset_creation.add_location -n "$dataset_name" -d "$directory" -r "$resize"
# Then, update the nginx.conf.template file
python3 -m src.dataset_creation.generate_nginx_conf > "$HOME"/image-viz/nginx/nginx.conf.template
# Then, update the docker-compose.yml file
python3 -m src.dataset_creation.add_volume_to_nginx_service -d "$directory"
echo "Dataset added successfully."