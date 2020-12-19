# La Marzocco Home Assistant Integration

## Overview

This is a prototype integration for recent La Marzocco espresso machines that use Wifi to connect to the cloud and can be controlled via the La Marzocco mobile app.  This capability was rolled out in late 2019, and La Marzocco supposedly offers a retrofit kit to add it to earlier models.

Based on the investigation from Plonx on the Home Assistant forum [here](https://community.home-assistant.io/t/la-marzocco-gs-3-linea-mini-support/203581), I built an integration that makes configuration/machine status available to Home Assistant and allows the user to turn the machine to "on" or "standby".

Unfortunately, two very long and hard-to-access pieces of information (client_id and client_secret) are required to retrieve the initial token and encryption key for the local API.  I wrote a Python script to use with `mitmproxy` to get this information and you can find instructions [here](https://github.com/rccoleman/lmdirect/blob/master/Credentials.md).

## Installation

### HACS

If you've installed [HACS](https://hacs.xyz), you can simply add this repo as a Custom Repository and install that way.

1. Launch the HACS panel from the left sidebar
2. Click "Integrations`
3. Click the three dots in the upper-right corner
4. Select "Custom Repositories"
5. Select "Integration" from the dropdown box
6. Paste `https://github.com/rccoleman/lamarzocco` into the textbox to the left
7. Click "Add"
8. Click "Install" on card that appears

### Manual

If you don't have HACS installed or would prefer to install manually.

1. Create a `config/custom_comoponents` directory if it doesn't already exist
2. Clone this repo and move `lamarzocco` into `config/custom_components`.  Your directory tree should look like `config/custom_components/lamarzocco/...files...`

#### Restart Home Assistant

## Configuration

### Discovery

Home Assistant should automatically discover your machine on your local network via Zeroconf.  You'll get a notification in Lovelace that it has discovered a device, and you should see a "Discovered" box in Configuration->Integrations like this:

![](https://github.com/rccoleman/lamarzocco/blob/master/images/Discovered_Integration.png)

Clicking "Configure" brings you to this:

![](https://github.com/rccoleman/lamarzocco/blob/master/images/Config_Flow_Discovered.png)

Fill in the `client_id`, `client_secret`, `username`, and `password` as requested and hit "submit.  The integration will attempt to connect to the cloud server and your local machine to ensure that everything is correct and let you correct it if not.

### Manual

You can also add the integration manually.

1. Navigate to Configuration->Integrations
2. Hit the "+ Add New Integration" button in the lower-right
3. Search for "La Marzocco" and select it
4. You'll be presented with a dialog box like this:

![](https://github.com/rccoleman/lamarzocco/blob/master/images/Config_Flow_Manual.png)

5. Fill in the info
6. Hit "Submit"

#### Configured Integration

Regardless of how you configured the integration, you should see this in Configuration->Integrations:

![](https://github.com/rccoleman/lamarzocco/blob/master/images/Configured_Integration.png)

In Dev->States, you should see something like this, initially called `switch.espresso_machine`:

![](https://github.com/rccoleman/lamarzocco/blob/master/images/States.png)

You should be able to turn your machine on and off by toggling the switch and the switch should reflect the current state.

If you have any questions or find any issues, either file them here or post to the thread on the Home Assistant forum [here](https://community.home-assistant.io/t/la-marzocco-gs-3-linea-mini-support/203581).
