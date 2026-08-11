# Geocaching Plus for Home Assistant

Geocaching Plus is a custom Home Assistant integration that adds additional Geocaching functionality on top of the official Home Assistant Geocaching integration.

It reuses the existing Geocaching authentication from Home Assistant, so no additional Geocaching OAuth credentials are required.

> **Status:** Early release (v0.1.0). Feedback and bug reports are very welcome.

## Features

### Recent Geocaching logs

Geocaching Plus retrieves your most recent Geocaching logs directly from the Geocaching API.

Available information includes:

- Cache name
- GC code
- Log date and time
- Log type, such as `Found It` or `Didn't find it`
- Whether a Favorite Point was awarded
- Geocaching log reference code

The number of recent logs to retrieve is configurable from **1 to 50**.

### Latest log

A separate sensor exposes your latest Geocaching log, including additional attributes with cache and log information.

### Membership level

Shows your Geocaching membership level, such as Basic, Charter or Premium.

## Requirements

Before installing Geocaching Plus, the official **Geocaching** integration in Home Assistant must already be configured and working.

Geocaching Plus uses the existing OAuth authentication from that integration.

## Installation with HACS

Geocaching Plus can currently be installed as a custom HACS repository.

1. Open HACS in Home Assistant.
2. Open the menu and select **Custom repositories**.
3. Add:

   `https://github.com/lampje25/ha-geocaching-plus`

4. Select **Integration** as the category.
5. Install **Geocaching Plus**.
6. Restart Home Assistant.
7. Go to **Settings → Devices & services → Add integration**.
8. Search for **Geocaching Plus**.

The official Geocaching integration must already be configured.

## Configuration

After installation, open:

**Settings → Devices & services → Geocaching Plus → Configure**

You can configure the number of recent Geocaching logs to retrieve.

Supported range: **1–50**
Default: **10**

## Entities

The initial release provides:

| Entity | Description |
| --- | --- |
| Membership level | Your Geocaching membership level |
| Latest log | Your most recent Geocaching log |
| Recent logs | Recent Geocaching logs stored as entity attributes |

The Recent logs entity can be used in dashboard templates to display a list of recent finds and DNFs.

## Example dashboard card

A standard Home Assistant Markdown card can display the recent logs:

```yaml
type: markdown
title: Recent Geocaching logs
content: |
  {% set logs = state_attr('sensor.recent_logs', 'logs') %}
  {% if logs %}
  {% for log in logs %}
  {% if log.log_type == 'Found It' %}✅{% elif log.log_type == "Didn't find it" %}❌{% else %}🔹{% endif %} **{{ log.geocache_name }}**
  `{{ log.geocache_code }}` · {{ as_timestamp(log.logged_date) | timestamp_custom('%d-%m-%Y') }} · {{ log.log_type }}

  {% endfor %}
  {% else %}
  No recent logs available.
  {% endif %}
```

Entity IDs may differ depending on your Home Assistant installation.

## Updates

Geocaching data is periodically refreshed through Home Assistant.

Changing the Geocaching Plus options automatically reloads the integration.

## Feedback and issues

This project is still in an early stage.

Testing, ideas and bug reports are welcome. Please use the GitHub Issues page:

`https://github.com/lampje25/ha-geocaching-plus/issues`

## Planned development

Possible future features include:

- Additional Geocaching statistics
- Better dashboard presentation
- More information about recent logs
- Cache-related functionality
- Trackables
- Additional configurable options

Development will be driven in part by feedback from users.

## Disclaimer

Geocaching Plus is an independent community project and is not affiliated with or endorsed by Geocaching HQ or Groundspeak.

Geocaching and related trademarks are the property of their respective owners.

## License

See [LICENSE](LICENSE).