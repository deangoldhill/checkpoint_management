# Check Point Management for Home Assistant

A custom integration for Home Assistant that connects to the Check Point Management API. Monitor firewall objects, VPN communities, track license statuses, and toggle individual security rules natively via Home Assistant devices.

## Features
* **Device Grouping:** All entities automatically group underneath your Check Point server inside Home Assistant Devices.
* **Granular Object Counters:** Track Hosts, Networks, Groups, Dynamic Objects, Security Zones, VPN Communities (Meshed, Star, Remote Access), and more.
* **Dynamic Gateway Detection:** Automatically discovers gateway/server types on your network and builds sensors mapping their quantities.
* **Rule Switches with Rich Metadata:** Imports every rule inside your selected policy package as a toggleable switch entity. These switches track and display rich extra attributes including match hits, sources, destinations, and assigned actions.
* **Actionable Buttons:** Allows you to install the Access Policy or Database natively via Home Assistant.
* **Advanced Config:** Supports dynamic polling intervals directly via UI setup.

## Prerequisites: Check Point API Setup
1. Open Check Point SmartConsole.
2. Navigate to **Manage & Settings** > **Blades** > **Management API** > **Advanced Settings**.
3. Set **Require IP/Hostname matching** to "All IP addresses" or specify the IP address of your Home Assistant server.
4. Publish the changes.
5. Restart the API service via SSH (Expert mode) using the command: `api restart`
6. Create an API user with permissions to read objects and install policies.

## Installation via HACS
1. Navigate to **HACS** > **Integrations**.
2. Select **Custom repositories** via the top right menu.
3. Paste the URL of this repository, select **Integration**, and click **Add**.
4. Download "Check Point Management" in HACS and restart Home Assistant.

## Configuration
1. Go to **Settings** > **Devices & Services** and add the "Check Point Management" integration.
2. Enter the Host, Port, Username, and Password.
3. On the next screen, select the desired **Policy Package** from the dynamic dropdown and define your **Polling Interval** (default 60 seconds, minimum 5 seconds).
