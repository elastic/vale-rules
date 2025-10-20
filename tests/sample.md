When configuring an {{elastic-defend}} integration policy, access the [**Advanced settings** section](/solutions/security/configure-elastic-defend/configure-an-integration-policy-for-elastic-defend.md#adv-policy-settings) to fine-tune how the integration behaves in your environment. Use these settings to customize detection, performance, and security options based on your specific requirements.

:::{important}
Advanced settings are not recommended for most users. Use them only if you have specific configuration or security requirements. If configured incorrectly, these settings can cause unpredictable behavior.
:::

`[linux,mac,windows].advanced.agent.connection_delay`
:   Added in 7.9.0.

    *How long to wait for agent connectivity before sending first policy reply, in seconds. Default: `60`.*

    {{elastic-endpoint}} applies a cached configuration from disk immediately on start up. However, before generating a policy response document, {{elastic-endpoint}} waits to first establish a connection to {{elastic-agent}} to see if there are configuration updates. Use this setting to specify how long that delay should be. Regardless of this setting, {{elastic-endpoint}} will periodically attempt to (re)connect to {{elastic-agent}} if it isn't connected.


`[mac,windows].advanced.alerts.cloud_lookup`

:  Added in 7.12.0.

   *Check a cloud service for known false positives before generating malware alerts. Default: `true`.* Whitelist

   Before blocking or alerting on malware files, {{elastic-endpoint}} reaches out to an Elastic cloud service ([https://cloud.security.elastic.co](https://cloud.security.elastic.co)) to see if the alert is a known false positive. Use this setting to disable this feature.

   ::::{note}
   Disabling cloud lookup for alerts may result in higher false positive rates.
   ::::


`[linux,mac,windows].advanced.alerts.hash.md5`
:   Added in 8.16.0.

    *Include MD5 hashes in alerts. Even if set to false, MD5 hashes will still be included if alert exceptions, trusted apps, or blocklisting require them. Default: <=8.17: true, >=8.18: false.*

    {{elastic-endpoint}} doesn't generate MD5 hashes in alerts unless alert exceptions, trusted apps, or blocklisting requires them, in which case this setting is ignored. This setting was added in 8.16 to allow users to opt out of MD5 hashing; starting with 8.18, users are opted out by default. Prior to 8.16, MD5 hashes were always included.


`[linux,mac,windows].advanced.alerts.hash.sha1`
:   Added in 8.16.0.

    *Include SHA-1 hashes in alerts. Even if set to `false`, SHA-1 hashes will still be included if alert exceptions, trusted apps, or blocklisting require them. Default: <=8.17: true, >=8.18: `false`.*

    {{elastic-endpoint}} doesn't generate SHA-1 hashes in alerts unless alert exceptions, trusted apps, or blocklisting requires them, in which case this setting is ignored. This setting was added in 8.16 to allow users to opt out of SHA-1 hashing; starting with 8.18, users are opted out by default. Prior to 8.16, SHA-1 hashes were always included.


`windows.advanced.alerts.rollback.self_healing.enabled`
:   Added in 8.4.0.

    *Enable self-healing by erasing attack artifacts when prevention alerts are triggered. Warning: data loss can occur. Default: `false`.*

    When a prevention alert is generated, {{elastic-endpoint}} can [roll back](/solutions/security/configure-elastic-defend/configure-self-healing-rollback-for-windows-endpoints.md) recent filesystem changes likely associated with the attack. Use this setting to enable the self-healing rollback feature.
    
    ::::{warning}
    This feature can cause permanent data loss.
    ::::
