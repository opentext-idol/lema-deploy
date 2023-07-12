## LEMA Helm charts

_Helm_ is a package manager for Kubernetes, a system for automating deployment, scaling, and management of containerized applications.

A Helm _Chart_ defines and aids installation of a Kubernetes application.

This directory contains tools to deploy IDOL LEMA on Kubernetes, using Helm:
* The _charts_ directory contains a Helm Chart to deploy the `basic-idol` container set-up.

## Prerequisites

You will need to install:
* [The `kubectl` command-line tool](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
* [The `helm` command-line tool](https://helm.sh/)

## Configuration

Helm creates Kubernetes objects by substituting values into templates.
It reads the values from YAML files. Before deploying you must edit at least the follow values in `values.user.yaml`:
*  The IP of an IDOL License Server that will provide licensing for the system
*  The external hostname of the server running Kubernetes   
*  Authentication to pull the IDOL container images from dockerhub.
   Instructions for doing this are in the file comments.

## Deployment

`helm install --values lema/values.user.yaml lema ./lema/`

