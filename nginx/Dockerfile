# Base image is nginx
FROM nginx

# Create new directory for caching
RUN mkdir -p /data/nginx/cache
# Assign write permissions to the new directory
RUN chmod -R 777 /data/nginx/cache

# Copy start script and make it executable
COPY ./start.sh start.sh
RUN chmod +x ./start.sh

CMD ["./start.sh"]
