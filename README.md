# AEye: A visualization tool for image datasets.

## How to Add a New Dataset

1. **Download the Dataset:**
   - Download the new dataset. The dataset should be saved at `~` and contain only images, with no subdirectory structure.

2. **Navigate to the Backend Directory:**
   - Go to the backend directory.

3. **Update the `new-dataset-info.env` File:**
   - Fill the `new-dataset-info.env` file. Do not change the name of the variables, only the content.
   - Leave `CLASS_NAME=SupportDatasetForImagesCommon` and `COLLATE_FN=common_collate_fn` if you have not defined a new class or collate function for the dataset.
   - Go to `src/db_utilities/datasets.py` to check the available classes and functions, or to create new ones.

4. **Run the `add-dataset.sh` Script:**
   - Run `./add-dataset.sh` from the backend directory with sudo privileges.
