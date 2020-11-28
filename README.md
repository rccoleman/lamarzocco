# La Marzocco Home Assistant Integration

## Overview

This is a prototype integration for recent La Marzocco espresso machines that use Wifi to connect to the cloud and can be controlled via the La Marzocco mobile app.  This capability was rolled out in late 2019, and La Marzocco supposedly offers a retrofit kit to add it to earlier models.

Based on the investigation from Plonx on the Home Assistant forum [here](https://community.home-assistant.io/t/la-marzocco-gs-3-linea-mini-support/203581), I built an integration that requests and automatically updates tokens and delivers configuration and machine status info from the cloud gateway to Home Assistant.

Unfortunately, two very long and hard-to-access pieces of information (client_id and client_secret) are required to retrieve the initial token, and the only way that I've been able to get them is to sniff the web traffic from the mobile app.  This is complicated and you'll need to research how to do it (investigate mitmproxy).  I won't provide assistance for this.

## Installation

Installation is a manual process for now.

1. Create a `config/custom_comoponents` directory if it doesn't already exist
2. Clone the contents of this repo into that directory.  Your directory tree should look like `config/custom_components/lamarzocco/...files...`
3. Restart Home Assistant
4. Navigate to Configuration->Integrations
5. Hit the "+ Add New Integration" button in the lower-right
6. Search for "La Marzocco" and select it
7. You'll be presented with a dialog box like this:

![Config Flow](https://github.com/rccoleman/lamarzocco/blob/master/Config%20Flow.png?raw=true)

8. Fill in the info (you'll find the serial number in the app starting with "LM" for a Linea Mini or "GS" for a GS/3)
9. Hit "Submit"
10. You should find a new entity in Dev->States initially called `switch.la_marzocco`

You should be able to turn your machine on and off by toggling the switch and a number of attributes should be populated with data from your machine.  Here's an example:

![Config Flow](https://github.com/rccoleman/lamarzocco/blob/master/States.png?raw=true)

If you have any questions or find any issues, please post to the thread on the Home Assistant forum [here](https://community.home-assistant.io/t/la-marzocco-gs-3-linea-mini-support/203581).
