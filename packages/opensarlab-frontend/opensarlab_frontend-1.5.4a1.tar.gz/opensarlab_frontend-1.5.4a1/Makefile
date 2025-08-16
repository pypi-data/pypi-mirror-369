.PHONY := docker-shell
docker-shell:
	echo "Starting Docker Shell..."
	echo ""
	docker run \
		-v "$$(pwd):/code" \
		-it \
		--rm \
		--pull always \
	ghcr.io/asfopensarlab/osl-utils:main \
		bash