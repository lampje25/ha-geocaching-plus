# Geocaching Plus for Home Assistant

Geocaching Plus is a custom Home Assistant integration that adds additional Geocaching functionality on top of the official Home Assistant Geocaching integration.

It reuses the existing Geocaching authentication from Home Assistant, so no additional Geocaching OAuth credentials are required.

> **Status:** Early release (v0.2.0). Feedback and bug reports are very welcome.

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

### Owned geocaches

Geocaching Plus automatically retrieves geocaches owned by the authenticated Geocaching account.

Each owned geocache is represented as a separate Home Assistant device with:

- Current cache status
- Find count
- Favorite Point count
- Last visited date
- Latest log type
- Logger username
- Log date and complete log text
- Number of attached images
- Whether a Favorite Point was awarded
- A direct link to the log

### Maintenance monitoring

Each owned geocache has a **Maintenance required** binary sensor.

The sensor turns on after a `Needs Maintenance` log and returns to normal after a newer `Owner Maintenance` log.

### New-log events

### Example notification automation

The following automation creates a Home Assistant notification for every new log. Maintenance logs receive a different title.

```yaml
alias: Geocaching Plus - new owned-cache log
description: Notify when an owned geocache receives a new log
triggers:
  - trigger: event
    event_type: geocaching_plus_new_owned_cache_log

actions:
  - action: persistent_notification.create
    data:
      title: >-
        {% if trigger.event.data.maintenance_required %}
          Maintenance required: {{ trigger.event.data.cache_name }}
        {% else %}
          New log: {{ trigger.event.data.cache_name }}
        {% endif %}
      message: >-
        {{ trigger.event.data.logger }} posted a
        {{ trigger.event.data.log_type }} log.

        {{ trigger.event.data.text }}

        {{ trigger.event.data.url }}

mode: queued
max: 20
```

Replace `persistent_notification.create` with a mobile-app notification action if notifications should be sent to a phone.

When a new log is detected on an owned geocache, Geocaching Plus fires:

```text
geocaching_plus_new_owned_cache_log

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

Geocaching Plus provides account-wide entities and three entities for every owned geocache:

| Entity | Scope | Description |
| --- | --- | --- |
| Membership level | Account | Geocaching membership level |
| Latest log | Account | Most recent log placed by the authenticated user |
| Recent logs | Account | Recent user logs stored as entity attributes |
| Status | Owned cache | Current status and cache statistics |
| Latest log | Owned cache | Newest log with logger, text, date and URL |
| Maintenance required | Owned cache | Problem sensor for unresolved maintenance |

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
- Additional owned-cache information and configurable notifications
- Trackables
- Additional configurable options

Development will be driven in part by feedback from users.

## Disclaimer

Geocaching Plus is an independent community project and is not affiliated with or endorsed by Geocaching HQ or Groundspeak.

Geocaching and related trademarks are the property of their respective owners.

## License

See [LICENSE](LICENSE).