# Law Enforcement Media Application (LEMA)

The following installation steps complement the full LEMA Administration Guide, available from the [IDOL documentation site](https://www.microfocus.com/documentation/idol/), under "IDOL Government Solutions".

## Basic deployment

This directory contains tools to deploy IDOL LEMA on Kubernetes, using Helm.  The _lema_ directory contains a Helm Chart
for this purpose.

_Kubernetes_ is a system for automating deployment, scaling, and management of containerized applications.

_Helm_ is a package manager for Kubernetes.

A Helm _Chart_ defines and aids installation of a Kubernetes application.

## Prerequisites

You will need to install:
* [The `kubectl` command-line tool](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
* [The `helm` command-line tool](https://helm.sh/)

## Configuration

You can configure LEMA by modifying the YAML file `values.yaml`.  It is recommended to review all settings before
deploying, especially passwords and maximum volume sizes.  Read below to learn about the required values that you must
fill in.

### Docker Hub login

The `secret.base64dockerconfigjson` setting is a base64-encoded JSON Docker configuration file including credentials.

> To obtain your password (API key) contact OpenText support.

If you have the `docker` command-line tool installed, you can run:

```
docker login -u microfocusidolreadonly
kubectl create secret docker-registry docker-secret --dry-run=client -o yaml \
    --from-file=.dockerconfigjson=/path/to/.docker/config.json
```

Otherwise, run:

```
kubectl create secret docker-registry docker-secret --dry-run=client -o yaml \
    --docker-username=microfocusidolreadonly --docker-password=<token>
```

Copy the `.dockerconfigjson` value from the output into the `secret.base64dockerconfig.json` setting.

### License Server

Fill in the `license.ip` setting to point to an IDOL License Server.  Grant the `admin` role in your License Server
configuration to the hosts that will run Kubernetes components.

## Deployment

Install the application with your updated configuration using Helm:

```
helm install --values lema/values.user.yaml lema ./lema/
```

After the system has started:
* Add a user with the `admin` role (refer to the LEMA Administration Guide for details).
* With the default configuration, access the LEMA UI at `http://your-kubernetes-server/lema/`.
* Log in with the user you created. The LEMA UI will then perform a one-off initialization.

## Entities database schema

The entities database can be customized by modifying the file `lema/entity-schema.yaml`.  The schema can only be
customized once, before deploying the system.  Customizations are saved permanently in the `entity-data` volume.

## System information

By default, the following HTTP paths serve requests on port 80:

| **Path** | **Purpose**                                       |
|----------|---------------------------------------------------|
| /auth/   | Keycloak authentication server (API and admin UI) |
| /api/    | System HTTP API                                   |
| /lema/   | LEMA UI                                           |

The following persisent volumes claims are created:

| **Name**               | **Default size** | **Purpose**                         |
|------------------------|------------------|-------------------------------------|
| auth-db-data           | 1GiB             | Authentication server configuration |
| entity-storage-db-data | 5GiB             | Application data                    |
| entity-index-db-data   | 5GiB             | Search index for application data   |
| filestore-data         | 1TiB             | Uploaded and generated files        |
| audit-db-data          | 1GiB             | Audit logs                          |
| api-entity-data        | 100MiB           | Schema for application data         |
