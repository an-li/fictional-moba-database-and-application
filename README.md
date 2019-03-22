# Fictional MOBA Database management system
Database management system and application program for a fictional MOBA similar to League of Legends by Riot Games

## Requirements
* PostgreSQL 11
* Python 3.7.x
* Required packages are indicated at the top of app.py file.

## Setup instructions
1. Create an empty database in a local or remote PostgreSQL server with your preferred PostgreSQL management tool, either command-line or GUI
2. Run schema.sql in your preferred PostgreSQL management tool
3. (Optional) Import starter data into the database using your preferred method

## Program description (app.py)
When the program is launched, the user is presented with five options. Users may add a new user, create a new squad of five provided users, simulate a gameplay with a map, a game mode and players, buy an item from the store or simulate a tournament between three or more squads. Users start by entering the number corresponding the option they want, then they enter the required information for each option to encode in the database. The random library in Python is extensively used to, for instance, randomly generate stats for users, champions and items and the outcome of each simulated game instance and each simulated tournament.  
Note: Please edit the connection info on line 17 of the Python script to match your database name and its connection settings.