# La Marzocco Home Assistant Integration

![Validation And Formatting](https://github.com/rccoleman/lamarzocco/workflows/Validation%20And%20Formatting/badge.svg)
![Validation And Formatting](https://github.com/rccoleman/lamarzocco/workflows/Validation%20And%20Formatting/badge.svg?branch=dev)
[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs)

## Overview

This is an integration for recent La Marzocco espresso machines that use Wifi to connect to the cloud and can be controlled via the La Marzocco mobile app. This capability was rolled out in late 2019, and La Marzocco supposedly offers a retrofit kit to add it to earlier models.

Based on the investigation from Plonx on the Home Assistant forum [here](https://community.home-assistant.io/t/la-marzocco-gs-3-linea-mini-support/203581), this integration presents a comprehensive machine status through 6 different entities and allows the user to change the machine configuration from Home Assistant.

Unfortunately, two very long and hard-to-access pieces of information (client_id and client_secret) are required to retrieve the initial token and encryption key for the local API. I wrote a Python script to use with `mitmproxy` to get this information and you can find instructions [here](https://github.com/rccoleman/lmdirect/blob/master/Credentials.md).

After digging around in the Android La Marzocco Home app, I found the same client_id and client_secret embedded in the app that several users (including me) discovered "the hard way".  You're welcome to try these first before going through the annoying effort of using mitmproxy:

```
CLIENT_ID: 4_2d2impykbv0g44oc88kogw000s8wgwwgws80ccowkcg0wk8o8w
CLIENT_SECRET: 1m52x65srmysk4owk0ww4ok84sw484ww0gsoo0kc0gs4gcwkko
```

Please report to the thread above if these values work or don't work for you, and if you discover some other values.  I'm trying to figure out what kind of variety is out there and whether it matters.

This integration currently only supports a single espresso machine. It's possible to support multiple machines, but I only have one and I suspect that'll be the case for most folks. If anyone has a fleet of espresso machines and is willing to provide data and feedback, I'm happy to entertain adding support for more than one machine.

A companion Lovelace card that uses this integration to retrieve data and control the machine can be found [here](https://github.com/rccoleman/lovelace-lamarzocco-config-card).

## Installation

### HACS

If you've installed [HACS](https://hacs.xyz), this integration is in the default list and you can simply search for "La Marzocco" and install it that way.

1. Launch the HACS panel from the left sidebar
2. Click "Integrations`
3. Search for "La Marzocco" and select it
4. Click "Install" on card that appears

### Manual

If you don't have HACS installed or would prefer to install manually.

1. Create a `config/custom_comoponents` directory if it doesn't already exist
2. Clone this repo and move `lamarzocco` into `config/custom_components`. Your directory tree should look like `config/custom_components/lamarzocco/...files...`

#### Restart Home Assistant

## Configuration

### Discovery

Home Assistant should automatically discover your machine on your local network via Zeroconf. You'll get a notification in Lovelace that it has discovered a device, and you should see a "Discovered" box in Configuration->Integrations like this:

![](https://github.com/rccoleman/lamarzocco/blob/master/images/Discovered_Integration.png)

Clicking "Configure" brings you to this:

![](https://github.com/rccoleman/lamarzocco/blob/master/images/Config_Flow_Discovered.png)

Fill in the `client_id`, `client_secret`, `username`, and `password` as requested and hit "submit. The integration will attempt to connect to the cloud server and your local machine to ensure that everything is correct and let you correct it if not.  You can try the `client_id` and `client_secret` above first to see if they work before sniffing your network traffic, if you want.

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

## Usage

In Dev->States, you should see 6 new entities:

- 3 sensors
  - `water_heater.<machine_name>_coffee`
  - `water_heater.<machine_name>_steam`
  - `sensor.<machine_name>_total_drinks`
- 3 switches
  - `switch.<machine_name>_main`
  - `switch.<machine_name>_auto_on_off`
  - `switch.<machine_name>_prebrew`

Thw switches control their respective functions globally, i.e., enable/disable auto on/off for the whole machine, enable/disable prebrewing for all front-panel keys.

## Services

The `water_heater` and `switch` entities support the standard services for those domains, described [here](https://www.home-assistant.io/integrations/water_heater/) and [here](https://www.home-assistant.io/integrations/switch/), respectively.

The following domain-specific services are also available:

#### Service `lamarzocco.set_auto_on_off_enable`

Enable or disable auto on/off for a specific day of the week.

| Service data attribute | Optional | Description                                                                           |
| ---------------------- | -------- | ------------------------------------------------------------------------------------- |
| `day_of_week`          | no       | The day of the week to enable (sun, mon, tue, wed, thu, fri, sat)                     |
| `enable`               | no       | Boolean value indicating whether to enable or disable auto on/off, e.g. "on" or "off" |

#### Service `lamarzocco.set_auto_on_off_times`

Set the auto on and off times for each day of the week.

| Service data attribute | Optional | Description                                                       |
| ---------------------- | -------- | ----------------------------------------------------------------- |
| `day_of_week`          | no       | The day of the week to enable (sun, mon, tue, wed, thu, fri, sat) |
| `hour_on`              | no       | The hour to turn the machine on (0..23)                           |
| `minute_on`            | yes      | The minute to turn the machine on (0..59)                         |
| `hour_off`             | no       | The hour to turn the machine off (0..23)                          |
| `minute_off`           | yes      | The minute to turn the machine off (0..59)                        |

#### Service `lamarzocco.set_dose`

Sets the dose for a specific key.

| Service data attribute | Optional | Description                                             |
| ---------------------- | -------- | ------------------------------------------------------- |
| `key`                  | no       | The key to program (1-5)                                |
| `pulses`               | no       | The dose in pulses (roughly ~0.5ml per pulse), e.g. 120 |

#### Service `lamarzocco.set_dose_hot_water`

Sets the dose for hot water.

| Service data attribute | Optional | Description                                        |
| ---------------------- | -------- | -------------------------------------------------- |
| `seconds`              | no       | The number of seconds to stream hot water, e.g. 8  |

#### Service `lamarzocco.set_prebrew_times`

Set the prebrewing "on" and "off" times for a specific key.

| Service data attribute | Optional | Description                                                         |
| ---------------------- | -------- | ------------------------------------------------------------------- |
| `key`                  | no       | The key to program (1-4)                                            |
| `seconds_on`           | no       | The time in seconds for the pump to run during prebrewing (0-5.9s)  |
| `seconds_off`          | no       | The time in seconds for the pump to stop during prebrewing (0-5.9s) |

> **_NOTE:_** The machine won't allow more than one device to connect at once, so you may need to wait to allow the mobile app to connect while the integration is running. The integration only maintains the connection while it's sending or receiving information and polls every 30s, so you should still be able to use the mobile app.

If you have any questions or find any issues, either file them here or post to the thread on the Home Assistant forum [here](https://community.home-assistant.io/t/la-marzocco-gs-3-linea-mini-support/203581).
