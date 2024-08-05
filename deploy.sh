echo -n "Do you want to build the app? (y/n) "
read -r answer

if [ "$answer" = "y" ]; then
  echo "Building react application..."
  cd frontend || exit
  npm ci
  npm run build
  # Navigate back to image-viz directory
  cd ..
fi

# If there is no build directory in frontend, then the app has not been built. Exit.
if [ ! -d "frontend/build" ]; then
  echo "The react app has not been built. Please run 'npm run build' in the frontend directory."
  exit 1
fi

docker compose up -d