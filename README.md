# service-program
Service program to maintain mobile phone repair center

all of the required files are placed here.
how to install, the idea is to build docker container with all of the files in the repository, including Dockerfile required for building.
The application requiring interaction with mongodb which also can be provisioned with docker.



1. build docker container docker build -t service_program .
2. run docker container docker run --name service_program -p 5000:5000 service_program
3. Install mongodb from official repo.

2. Create a Docker Network

Docker on Windows supports networking just like on Linux, and containers on the same network can communicate via container names. Open a Command Prompt or PowerShell window and run the following command to create a custom network:

docker network create app-network

This creates a new network (app-network) that will allow the containers to talk to each other using their container names.
3. Run MongoDB Container

To run MongoDB in a container and ensure it uses the custom network, run the following command in the Command Prompt or PowerShell window:

docker run --name mongodb --network app-network -d mongo:latest

This command will:

    Download the latest MongoDB image (mongo:latest).
    Create a container named mongo.
    Run the MongoDB container in the background and connect it to the app-network network.

4. Run Your Application Container

Next, you need to run your app container. Assuming you have already built your app image (e.g., using the Dockerfile you mentioned earlier), you can run the app container and connect it to the same network:

docker run --name service_program --network app-network -p 5000:5000 -d your-app-image

How to restore mongodb

4. Backup the Data (Optional)

If you are worried about losing data or just want to ensure you have a backup, you can create a backup of your MongoDB database before running the new container. Here's a simple way to do that using mongodump:

docker exec mongodb mongodump --out /tmp/mongo-backup

This will dump the database to /tmp/mongo-backup inside the container. You can then copy the backup out of the container:

docker cp mongodb:/tmp/mongo-backup /path/to/host/backup

This will copy the backup from the container to your host machine.

docker cp /path/to/backup mongodb:/tmp/mongo-backup

This will copy the backup directory to /tmp/mongo-backup in the MongoDB container.
Step 3: Use mongorestore to Restore the Backup

Now, you can restore the backup using the mongorestore command. Run the following command inside the MongoDB container:

docker exec mongodb mongorestore --dir=/tmp/mongo-backup

This command will restore the data from the /tmp/mongo-backup directory to the MongoDB instance running inside the container.

If your backup is stored in a specific database, you can specify that database like this:

docker exec mongodb mongorestore --dir=/tmp/mongo-backup --db your_database_name

You can replace your_database_name with the actual name of the database you want to restore.
Step 4: Clean Up the Backup Files

Once the restore is complete, you can clean up the backup files inside the container:

docker exec mongodb rm -r /tmp/mongo-backup


Bug report: 22/03//24
1. If status=="готов за получаване" not updating the additional text field details "part_price","repair_details" and "warranty"


Bug fixes 23/03/24

1.  If status=="готов за получаване" not updating the additional text field details "part_price","repair_details" and "warranty".
2.  Login form enabled for all pages.
