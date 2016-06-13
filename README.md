# EWATEC
This is a web-based platform buit on top ODM (observational data model) for sharing environmental data.

## Features

## Setup database 
### Install postgresql
```
$ sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt/ `lsb_release -cs`-pgdg main" >> /etc/apt/sources.list.d/pgdg.list'
$ wget -q https://www.postgresql.org/media/keys/ACCC4CF8.asc -O - | sudo apt-key add -
$ sudo apt-get update
$ sudo apt-get install postgresql postgresql-contrib
```
### Install postgis
```
sudo apt-add-repository ppa:ubuntugis/ubuntugis-unstable
sudo apt-get update
sudo apt-get install postgis
```
### Connect to PostgreSQL
```
$ sudo su - postgres
$ psql
```
## Setup virtual environment
`$ virtualenv env`
### Install GDAL in virtualenv
* GDAL library must have been installed.

`sudo apt-get install libgdal-dev`.

* Now install Python binding for GDAL.
```
$ export CPLUS_INCLUDE_PATH=/usr/include/gdal
$ export C_INCLUDE_PATH=/usr/include/gdal
$ (env) pip install GDAL==1.11.2
```
### Install ibfreetype6-dev libxft-dev (for matplotlib)
`$ sudo apt-get install libfreetype6-dev libxft-dev`

### Install gfortran libblas-dev liblapack-dev libatlas-base-dev  (for scipy numpy)
`$ sudo apt-get install gfortran libblas-dev liblapack-dev libatlas-base-dev`

### Install requirements
`$ (env) pip install -r requirements.txt`

## Setup gunicorn

## Setup nginx
