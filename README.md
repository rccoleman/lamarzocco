# La Marzocco Home Assistant Integration

## Overview

This is a prototype integration for recent La Marzocco espresso machines that use Wifi to connect to the cloud and can be controlled via the La Marzocco mobile app.  This capability was rolled out in late 2019, and La Marzocco supposedly offers a retrofit kit to add it to earlier models.

Based on the investigation from Plonx on the Home Assistant forum [here](https://community.home-assistant.io/t/la-marzocco-gs-3-linea-mini-support/203581), I built an integration that makes configuration/machine status available to Home Assistant and allows the user to turn the machine to "on" or "standby".

Unfortunately, two very long and hard-to-access pieces of information (client_id and client_secret) are required to retrieve the initial token, and the only way that I've been able to get them is to sniff the web traffic from the mobile app.  This is complicated and you'll need to research how to do it (investigate `mitmproxy`).  I won't provide assistance for this.

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
2. Run this repo and move `lamarzocco` into `config/custom_components`.  Your directory tree should look like `config/custom_components/lamarzocco/...files...`

#### Restart Home Assistant

## Configuration

1. Navigate to Configuration->Integrations
2. Hit the "+ Add New Integration" button in the lower-right
3. Search for "La Marzocco" and select it
4. You'll be presented with a dialog box like this:

![Config Flow](https://github.com/rccoleman/lamarzocco/blob/master/Config%20Flow.png?raw=true)

5. Fill in the info (you'll find the serial number in the app starting with "LM" for a Linea Mini or "GS" for a GS/3)
6. Hit "Submit"
7. You should find a new entity in Dev->States initially called `switch.espresso_machine`

You should be able to turn your machine on and off by toggling the switch and a number of attributes should be populated with data from your machine.  Here's an example:

![Entity](https://github.com/rccoleman/lamarzocco/blob/master/States.png?raw=true)

If you have any questions or find any issues, please post to the thread on the Home Assistant forum [here](https://community.home-assistant.io/t/la-marzocco-gs-3-linea-mini-support/203581).
