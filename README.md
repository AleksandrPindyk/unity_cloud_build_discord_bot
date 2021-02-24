# README #

Discord bot for run and share build created in Unity Cloud Build service

### How to use ###

Fill .env file with: 
* **DISCORD_TOKEN** - Discord bot token
* **DISCORD_GUILD** - Discord guild ID
* **DISCORD_BOT_NAME** - Discord bot name
* **UNITY_API_KEY** - Unity organization API key
* **UNITY_ORGANIZATION_ID** - Unity organization ID
* **PROJECT_ID** - Target project ID
* **PROJECT_NAME** - Target project name

#### Local ####

* Install Python 3.9.2
* Install python from requirements.txt 
* Run command: **python3 discord_bot.py**

#### Cloud ####

* Create VM with installed docker
* Build and start docker image with command: **make up**
* To stop docker image run command: **make down**

Detailed instruction on how to create and use this bot can be found [here]()

### Available commands ###

To send command go to channel **ci** mention bot and send one of this command:
* **help** - print all available commands
* **supported_builds** - print all supported build targets names
* **build_target_info [build target name]** - print additional information about **[build target name]** 
* **build [build target name]** - run build for **[build target name]**

### Contacts ###

* Author: Aleksandr Pindyk <apindyk@gmail.com> © 2021
* Feel free contact for any ideas, bug or improvements
