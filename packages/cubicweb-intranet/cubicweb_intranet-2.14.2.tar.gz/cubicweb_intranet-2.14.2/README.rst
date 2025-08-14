Intranet cube
=============

Developping with docker
=======================

Assuming you have a postgresql running on your machine where you can connect
with peer authentication, run "make dev" it will spawn an interactive shell
inside a docker container with the code mounted in develop mode. It mean you
can edit the code locally and run it in the container.

Some useful commands::

* ``cubicweb-ctl db-create -a intranet`` will create and initialize the
  database

* ``cubicweb-ctl pyramid -D -l info intranet`` will start the instance on
  http://localhost:8080

Deploying on kubernetes
=======================

To create the initial database from an existing empty database::

   kubectl run -it intranet-dbcreate \
      --env CW_DB_HOST=db \
      --env CW_DB_USER=user \
      --env CW_DB_PASSWORD=pass \
      --env CW_DB_NAME=intranet \
      --image=hub.extranet.logilab.fr/logilab/intranet --command -- \
      cubicweb-ctl db-create --automatic --create-db=n intranet
   kubectl delete deployment intranet-dbcreate


Then generate a secret named "intranet" from where environment variables are set::

   kubectl create secret generic intranet-env \
      --from-literal CW_DB_HOST=db
      --from-literal CW_DB_USER=user \
      --from-literal CW_DB_PASSWORD=pass \
      --from-literal CW_DB_NAME=intranet \
      --from-literal CW_BASE_URL=https://intranet.example.com


Then deploy intranet with::

   kubectl apply -f deployment.yaml
