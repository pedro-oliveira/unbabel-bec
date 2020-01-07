# Backend Engineering Challenge 2.0

[![pipeline status](https://gitlab.com/psoliveira/unbabel-bec/badges/master/pipeline.svg)](https://gitlab.com/psoliveira/unbabel-bec/commits/master)

This project contains a solution to the Unbabel's [Backend Engineering Challenge](https://github.com/Unbabel/backend-engineering-challenge/blob/master/README.md) 
reformulated to a more realistic context, in which the translation events arrive in real time.  

## Idea

The goal of this project is to solve the original challenge, but assuming the translation events occur in real time. In this reformulated challenge, we also assume that we care about the metrics by client. 

For solving this problem the Apache Beam framework was chosen given that it is able to solve this problem in both a batch and streaming ways. We can also leverage on the GCP's Dataflow runner to run a fully scalable and managed pipeline.

In summary, we have in each folder:

- **batch** the solution to the batch problem, where we process an input json file and write to an output json file.
- **streaming** the solution to streaming problem, where we have: multiple publishers (`publisher.py`), simulating the clients translation events (Unbabel's translation API); the streaming pipeline (`streaming_pipeline.py`) performing the pipeline processing; and a subscriber (`subscriber.py`) that reads the output from the pipeline and prints the information. 

**Note:** For the messaging in the streaming problem, the Cloud Pub/Sub is used.

More details will be provided here in the following days.

## To Do List

- [x] Formulate problem to solve, choose technologies to use and define 
architecture.
- [x] Solution to batch pipeline problem (`batch_pipeline.py`).
- [x] Solution to streaming pipeline problem (`streaming_pipeline.py`).
- [x] Containerize project code ([psoliveira/unbabel-batch](https://hub.docker.com/repository/docker/psoliveira/unbabel-batch/) and [psoliveira/unbabel-streaming](https://hub.docker.com/repository/docker/psoliveira/unbabel-streaming/)).
- [x] Setup CI using GitLab CI ([Pipelines](https://gitlab.com/psoliveira/unbabel-bec/pipelines)).
- [ ] Write **README.md**.
- [ ] Add Tests.
- [ ] Add test stage to CI pipeline.
- [x] Added `.yaml` files (`streaming/k8s`) for deploying architecture in a Kubernetes cluster.
- [ ] Finalize **README.md**.