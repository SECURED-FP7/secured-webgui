GRANDMOTHER GUI
=================

**Installation**

Dependencies for Ubuntu (and possibly Debian):

```bash
$ sudo apt-get install libudev-dev libjson0 libjson0-dev libncurses5-dev python-dev
```

You can insatll the Gmother GUI with the following commands:

    virtualenv .env  
    source .env/bin/activate  
    pip install django  
    pip install djangorestframework 
    pip install django-sslserver
    pip install requests  
    pip install lxml
    pip install json2xml dicttoxml termcolor
    python manage.py makemigrations webContent  
    python manage.py migrate

**Configuration**

Configurations to external services are in file constants.py (webContent/constants.py)

**Use HTTPS**

To use HTTPS is needed to download openssl:

Debian:

    sudo apt-get install openssl

RedHat:

    sudo yum install openssl
    
Generate the new certificate:

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

    python manage.py runsslserver --certificate certificate/server.crt --key certificate/server.key --addrport 0.0.0.0:8080 &

**Live demo**

As today (feb 25 2016), a live demo is available here:

    
     https://securedproject.ipv6.polito.it:9091/
     
     User/password: father/father

This GGUI are connected to the UPR at 130.192.225.110:8081 and at the PSAR 130.192.225.110:8080

