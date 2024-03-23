# service-program
Service program to maintain mobile phone repair center

all of the required files are placed here.
how to install, the idea is to build docker container with all of the files in the repository, including Dockerfile required for building.
The application requiring interaction with mongodb which also can be provisioned with docker.



1. build docker container docker build -t service_program .
2. run docker container docker run --name service_program -p 5000:5000 service_program


Mongo
test> show dbs
admin    40.00 KiB
config   96.00 KiB
formDB  152.00 KiB
local    72.00 KiB

formDB> db.forms_collection.findOne()
{
  _id: ObjectId('65ed99c5031398aeb943f5b9'),
  model: 'xioami',
  phone: 'asd',
  device_type: 'Телефон',
  offered_price: '0',
  created_date: '10/03/24 11:18:23',
  info: 'asd',
  status: 'приключен ремонт',
  order_number: 33,
  accessories: {
    accessory_case: false,
    accessory_bag: false,
    accessory_charger: false,
    accessory_sim: false
