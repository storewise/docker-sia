# docker-sia
[![CircleCI branch](https://img.shields.io/circleci/project/github/GooBox/docker-sia/master.svg)](https://circleci.com/gh/GooBox/docker-sia)
[![GPLv3](https://img.shields.io/badge/license-GPLv3-blue.svg)](https://www.gnu.org/copyleft/gpl.html)

Docker image for Sia project.

## Getting started
To run _Sia_ you need previously to install the requirements and you can either use public docker image or build it 
from sources.

### Requirements
1. *Docker:* Install it following [official docs](https://docs.docker.com/engine/installation/).

### Use public image
You can use public docker image to run the Sia service:

    docker run -p 8000:8000 goobox/docker-sia:latest start
    
To keep node your node data you can mount data volume as:

    docker run -p 8000:8000 -v data:/srv/apps/sia/data goobox/docker-sia:latest start

## License

[GNU GPL v3](https://github.com/GooBox/docker-sia/blob/master/LICENSE)
