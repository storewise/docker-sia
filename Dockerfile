FROM debian:stable-slim

ENV APP sia
ENV BASEDIR /srv/apps/$APP
ENV APPDIR $BASEDIR/app
ENV SIADIR $BASEDIR/sia
ENV PATH $SIADIR:$PATH

# Create initial dirs
RUN mkdir -p $APPDIR $SIADIR
WORKDIR $APPDIR

# Install system dependencies
ENV RUNTIME_PACKAGES socat wget ca-certificates unzip
RUN apt-get update && \
    apt-get --no-install-recommends -y install $RUNTIME_PACKAGES && \
    rm -rf /var/lib/apt/lists/*

# Install Sia
ENV SIA_VERSION 1.3.2
ENV SIA_RELEASE https://github.com/NebulousLabs/Sia/releases/download/v${SIA_VERSION}/Sia-v${SIA_VERSION}-linux-amd64.zip
RUN wget --progress=bar:force:noscroll --show-progress -q $SIA_RELEASE -O $SIADIR/sia.zip && \
    unzip -q $SIADIR/sia.zip -d $SIADIR && \
    mv $SIADIR/Sia-v${SIA_VERSION}-linux-amd64/* $SIADIR && \
    rm -r $SIADIR/Sia-v${SIA_VERSION}-linux-amd64 && \
    rm $SIADIR/sia.zip

COPY entrypoint.sh $APPDIR

EXPOSE 8000
ENTRYPOINT ./entrypoint.sh
