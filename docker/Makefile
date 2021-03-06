CENTOS_RELEASE  := 7
DOCKER          := docker

INAME = $(@:%-image=%)
CNAME = $(@:%-container=%)

.PHONY: images
images: docker-image-latest \
        docker-image-7.6 \
        docker-image-cortx

.PHONY: docker-image-latest docker-image-7
docker-image-latest docker-image-7: sspl-devel-image

.PHONY: docker-image-7.6
docker-image-7.6: CENTOS_RELEASE := 7.6
docker-image-7.6: sspl-devel-image

.PHONY: docker-image-cortx
docker-image-cortx: CENTOS_RELEASE := cortx
docker-image-cortx: sspl-devel-image


.PHONY: sspl-devel-image
sspl-devel-image:
	cd $(INAME) \
	&& tar -ch . \
	   | $(DOCKER) build \
			--build-arg CENTOS_RELEASE=$(CENTOS_RELEASE) \
			-t $(NAMESPACE)/$(INAME):$(CENTOS_RELEASE) \
			-t $(NAMESPACE)/cortx/sspl:$(CENTOS_RELEASE) \
			$(DOCKER_OPTS) -

.PHONY: push
name := sspl*
tag  := *
push:
	@for img in $$(docker images --filter=reference='$(NAMESPACE)/$(name):$(tag)' \
				    --format '{{.Repository}}:{{.Tag}}' | grep -v none) \
		    $$(docker images --filter=reference='$(NAMESPACE)/cortx/$(name):$(tag)' \
				    --format '{{.Repository}}:{{.Tag}}' | grep -v none) ; \
	do \
		echo "---> $$img" ; \
		$(DOCKER) push $$img ; \
	done

.PHONY: clean
clean:
	@for img in $$(docker images --filter=reference='$(NAMESPACE)/$(name):$(tag)' \
				    --format '{{.Repository}}:{{.Tag}}') \
		    $$(docker images --filter=reference='$(NAMESPACE)/cortx/$(name):$(tag)' \
				    --format '{{.Repository}}:{{.Tag}}') ; \
	do \
		echo "---> $$img" ; \
		$(DOCKER) rmi $$img ; \
	done

.PHONY: help
help:
	@echo 'Build targets:'
	@echo '  images          - create docker images for CI environment'
	@echo ''
	@echo 'Publish targets:'
	@echo "  push            - upload local $(NAMESPACE)/* images to docker hub repository"
	@echo ''
	@echo 'Clean targets:'
	@echo "  clean           - remove local $(NAMESPACE)/* images"
