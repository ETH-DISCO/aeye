# Execute command on docker container
read -rp "Enter service name: " service_name
read -rp "Enter command to execute on $service_name: " command
docker exec -it "$service_name" bash -c "$command"
