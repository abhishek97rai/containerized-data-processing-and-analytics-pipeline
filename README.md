STEPS:  
Installed minikube through this link - https://minikube.sigs.k8s.io/docs/start/  
  
minikube start gave error, related to virtualization not supported:  
X Exiting due to HOST_VIRT_UNAVAILABLE: Failed to start host: creating host: create: precreate: This computer doesn't have VT-X/AMD-v enabled. Enabling it in the BIOS is mandatory  
* Suggestion: Virtualization support is disabled on your computer. If you are running minikube within a VM, try '--driver=docker'. Otherwise, consult your systems BIOS manual for how to enable virtualization.  
  
So tried with --driver=docker:  
###minikube start --driver=docker --- Uses already installed docker desktop to create a minikube container within docker for windows  
* Creating docker container (CPUs=2, Memory=4000MB) ...  
* Preparing Kubernetes v1.26.3 on Docker 23.0.2 ...  
  
###minikube dashboard --- viewed the minikube dashboard with no running services/deployments  
  
###kubectl apply -f ./zookeeper-setup.yaml  
service/zookeeper-service created  
deployment.apps/zookeeper-deployment created  
  
###kubectl apply -f ./kafka-setup.yaml  
service/kafka-service created  
deployment.apps/kafka-deployment created  
  
Run below command in new terminal window:  
###kubectl port-forward svc/kafka-service 9092:9092  
Forwarding from 127.0.0.1:9092 -> 9092  
Forwarding from [::1]:9092 -> 9092  
Handling connection for 9092  
  
In case helm is not already installed in the environment, use below 2 commands to do the same:  

###helm repo add neo4j https://helm.neo4j.com/neo4j  
  
###helm repo update  
  
Continue with other script runs:  
  
###helm install my-neo4j-release neo4j/neo4j -f neo4j-values.yaml  
  
###kubectl rollout status --watch --timeout=600s statefulset/my-neo4j-release  
Waiting for 1 pods to be ready...  
partitioned roll out complete: 1 new pods have been updated...  
  
###kubectl apply -f neo4j-service.yaml  
service/neo4j-service created  
  
Run below command in new terminal window:  
###kubectl port-forward svc/my-neo4j-release 7687:7687 7474:7474  
Forwarding from 127.0.0.1:7687 -> 7687  
Forwarding from [::1]:7687 -> 7687  
Forwarding from 127.0.0.1:7474 -> 7474  
Forwarding from [::1]:7474 -> 7474  
Handling connection for 7474  
Handling connection for 7687  
  
Even though the kafka-neo4j-connector.yaml file uses the "ifNotPresent" imagePullPolicy, please pull the docker image that will be used in it, to be on the safe side:  
###docker pull veedata/kafka-neo4j-connect
  
###kubectl apply -f kafka-neo4j-connector.yaml  
deployment.apps/kafka-neo4j-connector-deployment created  
service/kafka-neo4j-connector-service created  
  
###kubectl get pods  
NAME                                                READY   STATUS    RESTARTS   AGE  
kafka-deployment-67667cf9d9-9jqjt                   1/1     Running   0          3m8s  
kafka-neo4j-connector-deployment-557c98f95b-8mrl6   1/1     Running   0          8s  
my-neo4j-release-0                                  1/1     Running   0          2m44s  
zookeeper-deployment-799b4bf9b9-p97zg               1/1     Running   0          3m14s  
  
###kubectl get services  
NAME                            TYPE           CLUSTER-IP       EXTERNAL-IP   PORT(S)                                        AGE  
kafka-neo4j-connector-service   ClusterIP      10.107.67.77     <none>        8083/TCP                                       14s  
kafka-service                   ClusterIP      10.97.176.4      <none>        9092/TCP,29092/TCP                             3m14s  
kubernetes                      ClusterIP      10.96.0.1        <none>        443/TCP                                        11d  
my-neo4j-release                ClusterIP      10.111.207.107   <none>        7687/TCP,7474/TCP,7473/TCP                     2m50s  
my-neo4j-release-admin          ClusterIP      10.105.182.32    <none>        6362/TCP,7687/TCP,7474/TCP,7473/TCP            2m50s  
neo4j-service                   ClusterIP      10.107.18.62     <none>        7474/TCP,7687/TCP                              35s  
neo4j-standalone-lb-neo4j       LoadBalancer   10.101.254.150   <pending>     7474:30928/TCP,7473:32663/TCP,7687:31252/TCP   2m50s  
zookeeper-service               ClusterIP      None             <none>        2181/TCP                                       3m20s  
  
Go to the directory where your python scripts are located, and open a new terminal window from there.  
In case confluent-kafka and neo4j libraries are not already installed in the environment, use below commands to install them:  

###pip install confluent-kafka  
  
###pip install neo4j  
  
Now we'll run the data_producer.py file, which will push the specified dataset into the minikube environment, basically through kafka into neo4j.  
###python data_producer.py
  
Once the data is loaded, we will run the tester.py file to test our interface.py implementations.  
###python tester.py  
  