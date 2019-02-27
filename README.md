# Building and Deploying a Deep Learning Model on Kubernetes using Docker

This project demonstrates a basic example on building a Deep Learning model on Keras and deploy it using Docker and Kubernetes.

This is NOT a robust, production example. This is a quick guide for anyone out there who has heard about Kubernetes but hasn’t tried it out yet.

To that end, we will use Google Cloud Platform for every step of this process.

## Quick Outline

(1) Serve a Deep Learning model as a REST API using Keras, Flask, and Docker

(2) Create your environment with Google Cloud Platform to run Docker or Run Docker Locally

(3) Deploy the model with Kubernetes Cluster on GCP

## Step - 1: Deep Learning Model API

In this tutorial, we will present a simple method to take a Keras model and deploy it as a REST API.

Specifically, we will learn:

- How to (and how not to) load a Keras model into memory so it can be efficiently used for inference

- How to use the Flask web framework to create an endpoint for our API

- How to make predictions using our model, JSON-ify them, and return the results to the client

- How to call our Keras REST API using both cURL and Python

By the end of this tutorial you'll have a good understanding of the components (in their simplest form) that go into a creating Keras REST API.

Feel free to use the code presented in this guide as a starting point for your own Deep Learning REST API.

Note: The method covered here is intended to be instructional. It is not meant to be production-level and capable of scaling under heavy load. If you're interested in a more advanced Keras REST API that leverages message queues and batching, please refer to this tutorial(https://www.pyimagesearch.com/2018/01/29/scalable-keras-deep-learning-rest-api/)

To run the server:  `python app.py`

You can now access the REST API via `http://127.0.0.1:5000`

### Submitting requests to the Keras server:

There are 2 ways you can do this

1 - Using cURL to send data to API: `curl -X POST -F image=@images/dog.jpg 'http://localhost:5000/predict'`

2 - Programmatically: `python request.py`


## Step - 2: Creating an environment on GCP/ Running on local system

### If you are running Docker locally, you can skip these steps and move on to creating `requirements.txt` step

- To start a Google Cloud VM, click on the hamburger button on the left side of your screen.

- Select Compute Engine. Then choose “Create Instance”.

- The next step is to select the compute size we want to use. The default (read: cheapest) settings should work just fine, but given that we only need this VM for ~1 hour at most, I chose 4vCPUs with 15GBs of memory.

- Select “Boot Disk” to edit the defaults. I choose Centos 7 for my operating system and increase the amount of disk from 10GB to 100GB.

- The final step before we create the VM is to set our Firewall rules to allow HTTP/S to full transparency.

- Click on "create".

Now that our VM is created, let us SSH into it and start building our model. The easiest way to do this is to click on the SSH icon next
to you VM. It should open up a new window with a CLI.

- Remove the existing version of docker: `sudo yum remove docker docker-client docker-client-latest docker-common docker-latest docker-latest-logrotate docker-logrotate docker-selinux docker-engine-selinux docker-engine`
Note that if you choose an operating system other than Centos 7, these commands will vary.

- Install the latest version of Docker:
  Before you install Docker CE for the first time on a new host machine, you need to set up the Docker repository. Afterward, you can install and update Docker from the repository.

SET UP THE REPOSITORY: -

(1) Install required packages. `yum-utils` provides the `yum-config-manager` utility, and `device-mapper-persistent-data` and `lvm2` are required by the devicemapper storage driver.

`sudo yum install -y yum-utils device-mapper-persistent-data lvm2`

(2) Use the following command to set up the stable repository.

`sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo`

INSTALL DOCKER CE: -

(3) Install the latest version of Docker CE and containerd, or go to the next step to install a specific version:

`$ sudo yum install docker-ce docker-ce-cli containerd.io`

If prompted to accept the GPG key, verify that the fingerprint matches 060A 61C5 1B55 8A7F 742B 77AA C52F EB6B 621E 9F35, and if so, accept it.

(4) Start Docker and run the test script to verify a installation

`sudo systemctl start docker`
`sudo docker run hello-world`

#### Creating `requirements.txt` file

Now that Docker is installed, go to you Flask app directory: -

- Create a `requirements.txt`

- Create a `Dockerfile`

- Build the Docker container `sudo docker build -t keras-app:latest .` (Yes! there is a period at the end xD)
  This command should take a couple of minutes

- Run the Docker Container `sudo docker run -d -p 5000:5000 keras-app`

(NOTE: To remove a Docker container: `sudo docker container rm 'containerID without quotes'`)
(Alternately, you can use Docker-Compose, for which you would just need an additional `docker-compose.yml` file,
  In that case run `sudo docker-compose up`)

- Check for predictions: `curl -X POST -F image=@images/dog.jpg 'http://localhost:5000/predict'`

- To stop the container: `sudo docker-compose down`


### Bravo! You have successfully run a trained a deep learning model with Keras, served it with Flask, and wrapped it with Docker. The hard part is over. Now let’s deploy this container with Kubernetes



## Step - 3: Deploy model with Kubernetes

(1) Create a Docker-Hub account first
  - The first thing we do is upload our model to Docker Hub. (If you don’t have a Docker Hub account, create one now — don’t worry, it’s free). The reason we do this is that we won’t physically move our container to our Kubernetes cluster. Instead, we will instruct Kubernetes to install our container from a centrally hosted server, i.e., Docker Hub.

(2) Login to your Docker-Hub account from CLI: `sudo docker login`
  - Enter your username and password

(3) Tag your container
  - We need to tag our container before we can upload it. Think of this step as giving our container a name.
  - Run `sudo docker images` and locate the image id for our keras-app container.

#### Format
`sudo docker tag <your image id> <your docker hub id>/<app name>`
#### My Exact Command - Make Sure To Use Your Inputs
`sudo docker tag c511f5e4eb83 dpac9525/dlonkube_web`

(4) Push your container to Docker-Hub

#### Format
`sudo docker push <your docker hub name>/<app-name>`
#### My exact command
`sudo docker push dpac9525/dlonkube_web`

Now if you navigate back to Docker Hub’s website, you should see your dlonkube_web repository. Well done! We’re ready for the final stretch.

(5) Create a Kubernetes Cluster

- From your GCP account, go to the Kubernetes Engine.

- Create a new cluster

- Click on the `connect` button and then click on `Run in Cloud Shell`, this will open up the cloud shell for the cluster

- Now we run our docker container in Kubernetes. Note that the image tag is just pointing to our hosted docker image on Docker Hub. In addition, we’ll specify with --port that we want to run our app on port 5000.
  `kubectl run keras-app --image=dpac9525/dlonkube_web --port 5000`
  (Here, `keras-app` is the name of the deployment app)

- In Kubernetes, containers all run inside of pods. We can verify that our pod is running by typing `kubectl get pods`

- Now that our pod is alive and running, we need to expose our pod on port 80 to the outside world. This means that anyone visiting the IP address of our deployment can access our API. It also means we don’t have to specify a pesky port number after our url like we did before (say goodbye to :5000).
  `kubectl expose deployment keras-app --type=LoadBalancer --port 80 --target-port 5000`

- We’re almost there! Now, we determine the status of our deployment (and the URL that we need to call our API) by running `kubectl get service`.

- Grab that External-IP for your keras application from the above command, because now is the moment of truth. Open your local terminal (or wherever you have dog photo) and run the following command to call the API
  `curl -X POST -F image=@images/dog.jpg 'http://<your service External IP>/predict'`

Feast your eyes on the results! The result is similar to what we got while building the deep learning model locally, except now that the whole world can use it :)


##  Wrapping up

In this tutorial we served a deep learning model as a REST API using Keras and Flask. We then put that application inside of a Docker container, uploaded the container to Docker Hub, and deployed it with Kubernetes.
