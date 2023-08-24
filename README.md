#executando o produto


#delete all 
kubectl delete all --all -n airflow

#dockerfiles
docker rm -vf $(docker ps -aq)
docker rmi -f $(docker images -aq)
docker system prune -a --volumes




python3.11 -m venv venv

#criar o cluster 
kind create cluster --name airflow-cluster --config kind-cluster.yaml

kubectl cluster-info
kubectl get nodes -o wide

kubectl create namespace airflow
kubectl get namespaces

#nstalando helm
helm repo add apache-airflow https://airflow.apache.org
helm repo update
helm search repo airflow
helm install airflow apache-airflow/airflow --namespace airflow --debug

kubectl apply -f pvc.yaml
