# NAO_pickandplace
This is a pick and place application for the NAO Robot by Softbank

The application was meant to run a main file which would get data from another program. The provider program would plan the actions and send command through .txt file. My program (receiver) would open the command file, execute the command and return the events that happened with the robot. actions.py is the program that has all the possible commands for this pick and place domain.

The Pick and Place domain is a simple domain where the robot would grab a box in one place and place it at a specific place. Boxes and Places are marks with NAOmarks to make tracking easier.
The results of this project can be seen in this video:
