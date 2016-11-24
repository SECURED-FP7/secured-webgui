SECURED Policy GUI
=================

This is a web interface for non-tech savvy users to define high-level security policies 
using an English-like syntax. For the lifetime of the SECURED project this has been 
known as the "Grandmother GUI" since it should be relatively intuitive to use. This project
is dependent on these two projects:

* the [User Profile repository (UPR)](https://github.com/SECURED-FP7/secured-upr), which is
  the central database for storing user policies and other attributes
* the [Security Policy Module (SPM)](https://github.com/SECURED-FP7/secured-spm), which is the backend
  service that analyses and translates policies

Ideally you should have these installed before continuing. 

**Installation**

Dependencies for Ubuntu (and Debian):

```bash
$ sudo apt-get install libudev-dev libjson0 libjson0-dev libncurses5-dev \
  python-dev libxml2-dev libxslt1-dev gcc python-virtualenv zlib1g-dev
```

You can install the GUI with the following commands:

    virtualenv .env  
    source .env/bin/activate  
    pip install django djangorestframework django-sslserver requests lxml \
    json2xml dicttoxml termcolor python-keystoneclient
    
    python manage.py makemigrations webContent  
    python manage.py migrate

**Configuration**

Configurations to the required external services (the UPR and the SPM)
are set in the file **constants.py** (webContent/constants.py)

**Use HTTPS**

To use HTTPS is needed to use the OpenSSL package. Generate the new certificate:

    mkdir certificate
    cd certificate/
    openssl genrsa -des3 -passout pass:x -out server.pass.key 2048
    openssl rsa -passin pass:x -in server.pass.key -out server.key
    openssl req -new -key server.key -out server.csr
    openssl x509 -req -days 365 -in server.csr -signkey server.key -out server.crt
    cd ..

**Start**

To run the grandmother gui launch the following command:

    python manage.py runserver 0.0.0.0:8080 &
    
To use HTTPS the command is the following:

    python manage.py runsslserver --certificate certificate/server.crt \
    --key certificate/server.key --addrport 0.0.0.0:8080 &

**Live demo**

As today (feb 25 2016), a live demo is available here:

    
     https://securedproject.ipv6.polito.it:9091/
     
     User/password: father/father

This GGUI are connected to the UPR at 130.192.225.110:8081 and at the PSAR 130.192.225.110:8080

