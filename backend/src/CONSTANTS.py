CLIP_MODEL = "openai/clip-vit-base-patch16"
DEFAULT_N_NEIGHBORS = 100
DEFAULT_DIM = 2
DEFAULT_MIN_DIST = 0.1
DEFAULT_PROJECTION_METHOD = "umap"
UMAP_PROJ = "umap"
RANDOM_STATE = 42
BATCH_SIZE = 32
DEVICE = "cpu"
NUM_WORKERS = 0
MAX_IMAGE_PIXELS = 110000000
DATASETS_JSON_NAME = "image-viz/backend/datasets.json"
NGINX_CONF_JSON_NAME = "image-viz/nginx/nginx.conf.json"
DOCKER_COMPOSE_YML_NAME = "image-viz/docker-compose.yaml"

# Database constants
INSERT_SIZE = 500
SEARCH_LIMIT = 16384
ROOT_USER = "root"
ROOT_PASSWD = "Milvus"
DEFAULT_DATABASE_NAME = "aiplusart"
COSINE_METRIC = "COSINE"
L2_METRIC = "L2"
INDEX_TYPE = "FLAT"

# Environment variables names
MILVUS_IP = "MILVUS_IP"
MILVUS_PORT = "MILVUS_PORT"
ROOT = "ROOT"
ENV_FILE_LOCATION = "ENV_FILE_LOCATION"
HOME = "HOME"

# UMAP data variables
UMAP_COLLECTION_NAME = "umap"
N_NEIGHBORS = [3, 5, 10, 15, 20, 50, 100, 200]
MIN_DISTS = [0.0, 0.1, 0.25, 0.5, 0.8, 0.99]

# Variables for zoom levels collection
WINDOW_SIZE_IN_CELLS_PER_DIM = 10
IMAGE_WIDTH = 1280
IMAGE_HEIGHT = 920

# Variables for resizing images
RESIZING_WIDTH = 384
RESIZING_HEIGHT = 276
