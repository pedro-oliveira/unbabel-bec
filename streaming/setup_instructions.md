# Setup Instructions


## Requirements

- have a GCP account
- enable the relevant APIs
- create a service account
- gcloud and kubectl are installed

## Configure GCP Defaults

- project
- compute zones

## Create a Cluster in GKE

The first step is the creation of a Kubernetes cluster using the following command.

```bash
$ gcloud beta container clusters create <cluster_name>
```

## Create a Secret with the Service Account Credentials

```bash
$ kubectl create secret generic gcp-svc-key --from-file=/Users/<username>/Downloads/keys.json
```

```bash
$ kubectl create secret generic gcp-project --from-literal=project=<project_name>
```

## Create Deployments

 ```bash
 $ kubectl apply -f streaming/k8s
 ```
