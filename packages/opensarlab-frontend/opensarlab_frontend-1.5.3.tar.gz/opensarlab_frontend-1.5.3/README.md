# v4

All opensarlab extensions have been updated for JupyterLab 4. They have also been combined into one superextension for ease of installation and updating. Ordering and visibility can be controlled via the `overrrides.json` file. This file is often applied during the OSL image build. Extensions included:

### Control Button

OpenScienceLab has a unique URI structure. To make it easier for OSL users to find the server stop page, a button is placed in the top right corner of JupyterLab.

### Documentation Link

A hyperlink to opensarlab-docs.asf.alaska.edu is placed in the top right corner of JupyterLab.

### Profile Label

The name of the server profile selected by user is placed in the top right corner of JupyterLab. This is intended to make debugging of problems easier.

### Notifications

A toast is shown on page load from two sources:

1. Google Calendar notifications.

   The Google Calendar notifications are handled via the OpenScienceLab `/user/notifications/{lab_shortname}?profile={profiile_name}` endpoint.

1. Percent storage usage.

   The percent storage used of the home directory is shown. If the percentage is greater than 99%, the toast banner will be red and across the whole screen. This is only on page load and not in real-time.

### GIF Capture

A button that links to `gifcap.dev`. Users can screen capture and then save as a GIF. The recording is purely client-side in the browser.

### Disk Space

Display percent of remaining disk space. The values update every 5 seconds. Depending on settings, the display performs differently based on percent usage:

0 - 70%: Text on transparent background
70 - 85%: Text on yellow background
85 - 90%: Text on red background
91 - 99%: Blinking text on red background

Settings can be changed in the JupyterLab Advance Settings under _opensarlab-frontend_.

---

## <br>

---

**To ease local development, do the following...**

# Template mamba enviroment

Create an extension for JupyterLab 4

Use `copier` to create an extension. This requires a certain mamba environment.

```
mamba create -n opensarlab-extensions-template --override-channels --strict-channel-priority -c conda-forge -c nodefaults jupyterlab=4 nodejs=18 git copier=8 jinja2-time

mamba activate opensarlab-extensions-template
```

# Build Individual Extensions

Each extension should be built in it's own mamba enironment to makes sure there is no false dependency conflicts, etc.

```
NAME_OF_EXTENSION=opensarlab-extension-name-of-extension

mamba deactivate
mamba create -n $NAME_OF_EXTENSION --override-channels --strict-channel-priority -c conda-forge jupyterlab=4 nodejs=18
mamba activate $NAME_OF_EXTENSION
```

If there is a `dev-build.sh` file included, use that to build. Update the dependencies at the top of the file. Run by `bash dev-build.sh`.

---

## <br>

---

**Original extention documentation...**

# opensarlab_frontend

[![Github Actions Status](https://github.com/ASFOpenSARlab/opensarlab-extensions/actions/workflows/build.yml/badge.svg)](https://github.com/ASFOpenSARlab/opensarlab-extensions/actions/workflows/build.yml)
A JupyterLab extension.

This extension is composed of a Python package named `opensarlab_frontend`
for the server extension and a NPM package named `opensarlab_frontend`
for the frontend extension.

## Requirements

- JupyterLab >= 4.0.0

## Install

To install the extension, execute:

```bash
pip install opensarlab_frontend
```

## Uninstall

To remove the extension, execute:

```bash
pip uninstall opensarlab_frontend
```

## Troubleshoot

If you are seeing the frontend extension, but it is not working, check
that the server extension is enabled:

```bash
jupyter server extension list
```

If the server extension is installed and enabled, but you are not seeing
the frontend extension, check the frontend extension is installed:

```bash
jupyter labextension list
```

## Contributing

### Development install

Note: You will need NodeJS to build the extension package.

The `jlpm` command is JupyterLab's pinned version of
[yarn](https://yarnpkg.com/) that is installed with JupyterLab. You may use
`yarn` or `npm` in lieu of `jlpm` below.

```bash
# Clone the repo to your local environment
# Change directory to the opensarlab_frontend directory
# Install package in development mode
pip install -e "."
# Link your development version of the extension with JupyterLab
jupyter labextension develop . --overwrite
# Server extension must be manually installed in develop mode
jupyter server extension enable opensarlab_frontend
# Rebuild extension Typescript source after making changes
jlpm build
```

You can watch the source directory and run JupyterLab at the same time in different terminals to watch for changes in the extension's source and automatically rebuild the extension.

```bash
# Watch the source directory in one terminal, automatically rebuilding when needed
jlpm watch
# Run JupyterLab in another terminal
jupyter lab
```

With the watch command running, every saved change will immediately be built locally and available in your running JupyterLab. Refresh JupyterLab to load the change in your browser (you may need to wait several seconds for the extension to be rebuilt).

By default, the `jlpm build` command generates the source maps for this extension to make it easier to debug using the browser dev tools. To also generate source maps for the JupyterLab core extensions, you can run the following command:

```bash
jupyter lab build --minimize=False
```

### Development uninstall

```bash
# Server extension must be manually disabled in develop mode
jupyter server extension disable opensarlab_frontend
pip uninstall opensarlab_frontend
```

In development mode, you will also need to remove the symlink created by `jupyter labextension develop`
command. To find its location, you can run `jupyter labextension list` to figure out where the `labextensions`
folder is located. Then you can remove the symlink named `opensarlab_frontend` within that folder.

### Packaging the extension

See [RELEASE](RELEASE.md)
