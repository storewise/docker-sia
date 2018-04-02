FROM golang:1.10-alpine

ENV APP=sia
ENV BASEDIR=/srv/apps/$APP
ENV APPDIR=$BASEDIR/app

# Create initial dirs
RUN mkdir -p $APPDIR
WORKDIR $APPDIR

# Install system dependencies
ENV BUILD_PACKAGES git build-base

# Install Sia
RUN apk --no-cache add $BUILD_PACKAGES && \
    go get -u github.com/NebulousLabs/Sia/... && \
    apk del $BUILD_PACKAGES

EXPOSE 9980
ENTRYPOINT ['sh']
CMD ['siad', '-d', '$APPDIR', '--api-addr', '0.0.0.0:9980']
