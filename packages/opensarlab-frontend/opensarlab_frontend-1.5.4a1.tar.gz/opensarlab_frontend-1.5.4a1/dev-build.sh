#! /bin/bash

set -ex

## 1.
## THIS var needs to be updated to the extension name
EXTENSION_NAME="opensarlab_frontend"

## 2.
JLPM_DEPENDS=(
	## THIS array holds extra jlpm node packages to be install
	@jupyterlab/apputils
	@jupyterlab/application-extension
	toastr
	@lumino/widgets
)

## 3.
JLPM_DEV_DEPENDS=(
	## THIS array holds extra dev jlpm node packages to be install
	@types/toastr
)

## 4.
ENV_VARS=(
	## THIS array holds environment vars injected into JupyterLab at startup
	# Escape single quotes ( ' => \' )
	OPENSARLAB_PROFILE_NAME=\'SAR 1\'
	OPENSCIENCELAB_LAB_SHORT_NAME=\'opensarlab-test\'
	OPENSCIENCELAB_PORTAL_DOMAIN=\'https://opensciencelab-test.asf.alaska.edu\'
)

## 5.
## If there is a server "backend" to the extension, say "true"
USE_SERVER_EXTENSION=true

## 6.
# shellcheck disable=SC2034
MAMBA_DEPENDS=(
	## THIS array holds extra mamba packages to be installed in the environment. This should be used sparingly
)

## 7.
## ANY possible additional python packages will need to be added to the "project.dependencies" section of pyproject.toml

##############################################################################
##############################################################################
#
# DON'T UPDATE ANY OF THE FOLLOWING
#
##############################################################################
##############################################################################

MAMBA_ENV_NAME="opensarlab-extension-$EXTENSION_NAME"
printf "Extension name: %s" "$EXTENSION_NAME"

# Create environment
if ! { mamba env list | grep -w "$MAMBA_ENV_NAME"; }; then
	mamba create -n $MAMBA_ENV_NAME -y --override-channels --strict-channel-priority -c conda-forge "jupyterlab>=4" "nodejs>=18"
else
	echo "******** Environment $MAMBA_ENV_NAME already exists....updating"
	mamba update -n $MAMBA_ENV_NAME -y --override-channels --strict-channel-priority -c conda-forge "jupyterlab>=4" "nodejs>=18"
fi

mamba env list

# shellcheck disable=SC2116
cat >steps.sh <<EOF

    set -ex

    printf "\n\n"
    # Install npm package dependencies
    jlpm
    
    
    jlpm clean:all


    printf "\n\n"
    # Add javascript libs
    if [ ${#JLPM_DEPENDS[@]} != 0 ]; then
        jlpm add ${JLPM_DEPENDS[@]}
    else
        echo "No jlpm dependencies to add"
    fi

    printf "\n\n"
    # Add javascript dev libs
    if [ ${#JLPM_DEV_DEPENDS[@]} != 0 ]; then
        jlpm add --dev ${JLPM_DEV_DEPENDS[@]}
    else
        echo "No jlpm dependencies to add"
    fi

    printf "\n\n"
    jlpm build


    printf "\n\n"
    # Link your development version of the extension with JupyterLab
    jupyter labextension develop . --overwrite


    printf "\n\n"
    # Clone the repo to your local environment
    # Change directory to the proper directory
    # Install package in development mode
    # (!! This breaks on build !!)
    ##python -m pip install -v -e .


    printf "\n\n"
    # Server extension must be manually installed in develop mode
    if [ $USE_SERVER_EXTENSION == true ]; 
    then
        jupyter server extension list
        jupyter server extension enable "$EXTENSION_NAME"

    else
        echo "No server extensions..."
    fi


    printf "\n\n"
    jupyter labextension enable "$EXTENSION_NAME"


    printf "\n\n"
    jlpm run build


    printf "\n\n"
    mamba env list

    printf "\n\n"
    ( $(echo "${ENV_VARS[@]}") jupyter lab -y )

EOF

mamba run --live-stream -n $MAMBA_ENV_NAME bash steps.sh
