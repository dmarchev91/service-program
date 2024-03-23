# service-program
Service program to maintain mobile phone repair center

all of the required files are placed here.
how to install, the idea is to build docker container with all of the files in the repository, including Dockerfile required for building.
The application requiring interaction with mongodb which also can be provisioned with docker.



1. build docker container docker build -t service_program .
2. run docker container docker run --name service_program -p 5000:5000 service_program
3. Install mongodb from official repo.


Bug report: 22/03//24
1. If status=="готов за получаване" not updating the additional text field details "part_price","repair_details" and "warranty"


Bug fixes 23/03/24

1.  If status=="готов за получаване" not updating the additional text field details "part_price","repair_details" and "warranty".
2.  Login form enabled for all pages.
