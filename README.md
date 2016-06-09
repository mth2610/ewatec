# EWATEC
This is a web-based platform buit on top ODM (observational data model) for sharing environmental data.

## Features

## Setup database 

## Setup virtual environment
`virtualenv env`
### Install GDAL in virtualenv
* GDAL library must have been installed.

`sudo apt-get install libgdal-dev`.

* Now install Python binding for GDAL.
```
export CPLUS_INCLUDE_PATH=/usr/include/gdal
export C_INCLUDE_PATH=/usr/include/gdal
pip install GDAL
```
### Install requirements
`pip install -r requirements.txt`

## Setup gunicorn

## Setup nginx
