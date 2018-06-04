FROM debian:stable-slim

ENV LC_ALL C.UTF-8
ENV PYTHONIOENCODING utf-8
ENV APP sia
ENV BASEDIR /srv/apps/$APP
ENV APPDIR $BASEDIR/app
ENV SIADIR $BASEDIR/sia
ENV PATH $SIADIR:$PATH

# Create initial dirs
RUN mkdir -p $APPDIR $SIADIR
WORKDIR $APPDIR

# Install system dependencies
ENV RUNTIME_PACKAGES socat wget ca-certificates unzip python3-minimal
ENV BUILD_PACKAGES python3-pip
RUN apt-get update && \
    apt-get --no-install-recommends -y install $RUNTIME_PACKAGES && \
    rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY Pipfile Pipfile.lock $APPDIR/
RUN apt-get update && \
    apt-get --no-install-recommends -y install $BUILD_PACKAGES && \
    python3 -m pip install --no-cache-dir --upgrade pip pipenv && \
    pipenv install --system --deploy --ignore-pipfile && \
    apt-get purge -y $BUILD_PACKAGES && \
    apt-get autoclean && \
    rm -rf \
        /var/lib/apt/lists/* \
        $HOME/.cache/pip

# Install Sia
ENV SIA_VERSION 1.3.3-rc3
# ENV SIA_RELEASE https://github.com/NebulousLabs/Sia/releases/download/v${SIA_VERSION}/Sia-v${SIA_VERSION}-linux-amd64.zip
ENV SIA_RELEASE https://pixeldra.in/api/getfile/yWzgvH
RUN wget --progress=bar:force:noscroll --show-progress -q $SIA_RELEASE -O $SIADIR/sia.zip && \
    unzip -q $SIADIR/sia.zip -d $SIADIR && \
    mv $SIADIR/Sia-v${SIA_VERSION}-linux-amd64/* $SIADIR && \
    rm -r $SIADIR/Sia-v${SIA_VERSION}-linux-amd64 && \
    rm $SIADIR/sia.zip

COPY run $APPDIR/

EXPOSE 8000
ENTRYPOINT ["python3", "run"]
