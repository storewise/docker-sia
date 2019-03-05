# Docker Sia

![Generic badge](https://img.shields.io/badge/Project-Goobox-blue.svg)
![Generic badge](https://img.shields.io/badge/Author-José%20Antonio%20Perdiguero%20López-blue.svg)
![Generic badge](https://img.shields.io/badge/Status-Production-blue.svg)
[![GPLv3](https://img.shields.io/badge/license-GPLv3-blue.svg)](https://www.gnu.org/copyleft/gpl.html)
[![CircleCI branch](https://img.shields.io/circleci/project/github/GooBox/docker-sia/master.svg)](https://circleci.com/gh/GooBox/docker-sia)

* **Project:** Goobox
* **Author:** José Antonio Perdiguero López
* **Status:** Production

Docker image for Sia node with a useful wrapper to provide multiple features such as automatic wallet unlocking, 
consensus database bootstrapping...

## Getting started
To run _Sia_ you need previously to install the requirements and you can either use public docker image or build it 
from sources.

## Requirements
1. *Docker:* Install it following [official docs](https://docs.docker.com/engine/installation/).

## Usage
You can use public docker image to run the Sia service:

```commandline
docker run -p 8000:8000 goobox/docker-sia:latest start
```
    
To keep node your node data you can mount data volume as:

```commandline
docker run -p 8000:8000 -v data:/srv/apps/sia/data goobox/docker-sia:latest start
```
    
### Automatic wallet unlocking
Wallet unlocking will be done after node finishes starting. It is necessary to define the wallet primary seed under 
`UNLOCK_WALLET` environment variable and to use `--unlock` flag.

```commandline
docker run -p 8000:8000 -e UNLOCK_WALLET="<primary seed>" goobox/docker-sia:latest start --unlock
```

### Consensus database bootstrapping
At start you will be asked for bootstrapping consensus database but it could be declared using `--(no-)bootstrap` flags 
to avoid manual interactions.

```commandline
docker run -p 8000:8000 goobox/docker-sia:latest --bootstrap
```

```commandline
docker run -p 8000:8000 goobox/docker-sia:latest --no-bootstrap
```

## License

[GNU GPL v3](https://github.com/GooBox/docker-sia/blob/master/LICENSE)
