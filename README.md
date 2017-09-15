# Estate (Terraform UX)

<img src="https://i.imgur.com/eJq5XVW.png" width="800" />

**Latin:** Status **Old French:** estat **English:** Esate

> a piece of landed property or status of an owner, with respect to property, especially one of large extent with an elaborate house on it

Estate is essentially at Terraform UI/UX experience that makes Terraform easier for everyone to use.

It is designed around these key principles:

* Self-service infrastructure as code for everyone
* Reduce the learning curve of Terraform
* Make the right way the easy thing to do
* Standardize usage of Terraform across an organization
* Get out of the way of a power user limiting impact on their productivity
* Make management of Terraform easier

This project has been presented at [HashiConf 2017 in Austin](https://www.hashiconf.com/talks/underarmour-terraform.html) and the presentation deck is available [here](http://slides.com/rocktavious/estate#/)

## Getting Started & Bootstrapping

**For AWS Users**

Terraform files in the bootstrap folder of the repository will provision the necessary AWS resources to run Estate in a production environment.

**For non-AWS users**

For those who rely on other cloud providers or your own deployment tooling, Estate can be run in docker containers.

```
docker pull underarmourconnectedfitness/estate:master

docker run --privileged \
 -p 9200:9200 \
 -e SECRET_KEY=super_secret \
 -e DATABASE_URL=postgres://username:password@postgres.example.com:5432/estate \
 -v /var/run/docker.sock:/var/run/docker.sock \
 underarmourconnectedfitness/estate:master
```

The requirements to run Estate in production are:
* `DATABASE_URL` which leverages the [Django Database URL plugin](https://github.com/kennethreitz/dj-database-url) style configuration, so if you'd like to use MySQL you can easily
* [SECRET_KEY](https://docs.djangoproject.com/en/1.11/ref/settings/#std:setting-SECRET_KEY): Django secret key variable
* The docker socket is needed because Estate runs terraform in context of another docker container that it spins up on demand - the docker socket requires the container to run in privileged mode.

Configuration
-------------

Estate is a Django application, this means it can have complex configuration, many plugins added to it which add additional features and configuration.  As such we've tried to keep the core configuration needed down to just environment variables.  That being said we want to make it's configuration as flexible and pluggable as possible so we've exposed a way to plugin a normal django configuration file as well.

The main environment variables that Estate will pickup are as follows:

* **TERRAFORM_DOCKER_IMAGE**: Specify the docker container to use as a context to run terraform in (Default: `underarmourconnectedfitness/estate:master`)
* **TERRAFORM_EXTRA_ARGS**: Extra commandline arguments that will be applied to every terraform command, except for experiment functionality (Default: `-input=false`)
* **TERRAFORM_INIT_EXTRA_ARGS**: Extra commandline arguments that will be applied only the `terraform init` command (Default ``)
* **TERRAFORM_PLAN_EXTRA_ARGS**: Extra commandline arguments that will be applied only to the `terraform plan` command (Default: `-detailed-exitcode -out=plan`)
* **TERRAFORM_APPLY_EXTRA_ARGS**: Extra commandline arguments that will be applied only to the `terraform apply` command (Default: ``)
* **TERRAFORM_ELASTICACHE_URL**: If using a clustered setup and AWS Elasticache then you can configure the elasticache url

The following can only be applied as environment variables

* **GUNICORN_BIND_ADDRESS**: The network interface to bind to (Default: `0.0.0.0`)
* **GUNICORN_BIND_PORT**: The network port to bind to (Default: `8000`)
* **GUNICORN_WORKER_COUNT**: The amount of gunicorn workers to run (Default: `<cpu_count> * 10 + 1`)
* **GUNICORN_WORKER_CLASS**: See the gunicorn documentation on worker classes for more information (Default: "gevent")
* **GUNICORN_LOG_LEVEL**: See the gunicorn documenation on log levels for more information (Default: "info")


As well you can configure a django settings file, which is just pure python, and mount it into the container

contents of custom.py
```
from . import INSTALLED_APPS, MIDDLEWARE

# Add other django apps - IE Sentry
INSTALLED_APPS += [
    'raven.contrib.django.raven_compat',
]

MIDDLEWARE = (
    'raven.contrib.django.raven_compat.middleware.Sentry404CatchMiddleware',
) + MIDDLEWARE

# Configure estate settings as well
TERRAFORM_INIT_EXTRA_ARGS = "-input=false -backend-config 'access_token=6ae45dff-1272-4v75-8gd7-ad52bd756e66' -backend-config 'scheme=https' -backend-config 'address=consul.example.com' -backend-config 'path=estate/remote_state/{NAMESPACE}'"
```

Then mount this file into the container at the path `/usr/local/service/estate/settings/custom.py`
```
docker run -v ./custom.py:/usr/local/service/estate/settings/custom.py underarmourconnectedfitness/estate:master
```

Running as a Cluster
--------------------

Estate by default is setup to only run as a single standalone service, but as your team grows you'll likely need to scale it horizontally.  This is quite easy with estate it just requries 1 thing - a cache database

Estate uses a cache database to store the output of the different terraform commands run, by default it stores them on disk inside the container, but when you start to cluster Estate this won't work, so you will need to set up something like redis or memcached and configure the Django [cache framework](https://docs.djangoproject.com/en/1.11/topics/cache/) to store the cache data in the database.

## Sentry Integration

Sentry is a first class citizen with Estate and the integration requires configuring just one variable to connect to your sentry cluster

* `SENTRY_DSN`: [Data Source Name](https://docs.sentry.io/quickstart/#configure-the-dsn) is a variable consisting of configuration for sentry cluster. Example: 'https://key:secret@sentry.io/project'

## Built With

* [Docker](url) - description
* [Django](https://www.djangoproject.com/) application with
* [Django Rest Framework](http://www.django-rest-framework.org/) to design it REST API functionality.
* [Gunicorn](http://gunicorn.org/) workers.  The backend leverages
* [Webpack](https://webpack.github.io/) using a standard single page app design that leverages
* [React](https://facebook.github.io/react/)
* [Redux](http://redux.js.org/)

## Developing locally

* Clone this repo with [Git](https://git-scm.com/): `git clone https://github.com/underarmour/estate.git`
* Build the container images from root of the repo: `docker-compose build`
* Run the containers: `docker-compose up`

Every change to `Dockerfile` will require `docker-compose build` to be run. Changes to the codebase will be detected and Estate will be hot-reloaded.

## Contributing

* Fork the master branch ( https://github.com/underarmour/estate/fork )
* Create your branch (git checkout -b my-branch)
* Commit your changes (git commit -am 'added fixes for something')
* Push to the branch (git push origin my-branch)
* Create a new Pull Request (Travis CI will test your changes)
* And you're done!

Features, bug fixes, bug reports and documentation update are all welcome!
See the Github issues page for outstanding things that could be worked on.
