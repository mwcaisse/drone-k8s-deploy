OWNER=mwcaisse
GIT_REPO=drone-images
IMAGE_NAME=drone-k8s-deploy
VERSION=latest
TAG=registry.gitlab.com/$(OWNER)/$(GIT_REPO)/$(IMAGE_NAME):$(VERSION)

all: push

build:
	docker build -t $(TAG) .

push: build
	docker push $(TAG)