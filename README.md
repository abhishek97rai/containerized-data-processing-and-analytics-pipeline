# arai31-project-2
Please ensure to "pip install neo4j" from the location where you will be running interface.py (i.e. tester.py)

To build the docker image, go to the location where Dockerfile is present, and run:
docker build -t cse511-project2-phase1-abhishek-rai .

To run the container for the above image, run:
docker run -p 7474:7474 -p 7687:7687 -it cse511-project2-phase1-abhishek-rai

Note: We need to expose the ports using -p option so that docker ports are exposed to the host machine.
