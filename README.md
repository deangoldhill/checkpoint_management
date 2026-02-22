# Check Point Management for Home Assistant

A custom integration for Home Assistant that connects to the Check Point Management API. It allows you to monitor the number of objects, rules, and zones in your environment, and provides a button to install your selected policy package directly from Home Assistant.

## Features

* **Dynamic Object Sensors:** Tracks the total count of Hosts, Networks, Groups, Dynamic Objects, Security Zones, Data Centers, Updatable Objects, Access Layers, Access Rules, and NAT Rules.
* **Policy Installation Button:** Easily push/install your selected policy package via a Home Assistant dashboard button.
* **UI Configuration:** Fully configurable via the Home Assistant UI, including dynamic fetching of available policy packages during setup.

## Prerequisites: Check Point API Setup

Before installing this integration, you must ensure the Check Point Management API is enabled and accessible to your Home Assistant instance.

1. Open **Check Point SmartConsole**.
2. Navigate to **Manage & Settings** > **Blades** > **Management API** > **Advanced Settings**.
3. Ensure **Automatic start** is checked.
4. Set **Require IP/Hostname matching** to "All IP addresses" or specify the IP address of your Home Assistant server.
5. Publish the changes.
6. Restart the API service via SSH (Expert mode) on your management server using the command: `api restart`
7. Create a dedicated API user in SmartConsole with the necessary permissions (Read-only for sensors, but requires "Install Policy" permissions if you intend to use the install button).
8. Publish the creation of the new user.

## Installation via HACS

1. Open Home Assistant and navigate to **HACS**.
2. Click the three dots in the top right corner and select **Custom repositories**.
3. Paste the URL of this repository into the repository field.
4. Select **Integration** as the category and click **Add**.
5. Close the custom repositories window.
6. Search for "Check Point Management" in HACS and click **Download**.
7. Restart Home Assistant.

## Configuration

1. In Home Assistant, go to **Settings** > **Devices & Services**.
2. Click **Add Integration** in the bottom right corner.
3. Search for **Check Point Management** and select it.
4. Enter your Check Point Management IP/Hostname, Port (usually 443), Username, and Password.
5. Choose whether to verify the SSL certificate (leave unchecked if using a self-signed certificate).
6. Click **Submit**.
7. On the next screen, select the **Policy Package** you want to monitor and install, then click **Submit**.
