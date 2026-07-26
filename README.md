# 🎡 Eventis - Local Event Radar for Home Assistant

A custom Home Assistant integration that fetches local events, wine festivals, folk fairs (Kirchweih), and concerts within your specified radius and displays them on your dashboard.

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?repository=https%3A%2F%2Fgithub.com%2FDealwirth%2Feventis&category=integration)


## Features
- 📍 **Radius-based filtering**: Set your city/location and search radius in kilometers.
- 🍷 **Category selection**: Filter for Wine Festivals, Kirchweih, Concerts, Markets, etc.
- 📅 **Native HA Calendar**: View events in your HA calendar view.
- 🎨 **Pre-made UI Dashboard Card**: Out-of-the-box Lovelace dashboard card without writing YAML code!

## Installation

### Method 1: Direct Link (Recommended)
Click the **"Open Link"** badge above. It will automatically open your Home Assistant instance and prompt you to add this repository directly in HACS.

---

### Method 2: Manual HACS Installation
1. Open **HACS** in your Home Assistant.
2. Click the 3 dots in the top right corner and select **Custom repositories**.
3. Paste the URL: `https://github.com/Dealwirth/eventis`
4. Select Category: **Integration**.
5. Click **Add / Install**.
6. Restart Home Assistant.
7. Go to **Settings -> Devices & Services -> Add Integration** and search for **Eventis**.

## API Key Setup
Get a free API token from [BayernCloud Tourismus](https://bayerncloud.digital/).
