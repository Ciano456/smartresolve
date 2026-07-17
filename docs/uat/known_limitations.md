# Known Limitations And Future Work

## Current Limitations

- Railway persistent volumes restrict the application to one replica and can cause
  brief deployment downtime.
- Attachment validation checks allowlists and basic signatures but is not antivirus
  or sandbox scanning.
- Microsoft Graph delivery depends on external tenant configuration and availability.
- Audit records are visible in the application but there is no automated alerting or
  dedicated security dashboard.
- Formal load/performance targets have not yet been measured on production-sized data.
- Backups and restoration require Railway operational procedures and live validation.
- Self-service registration is not supported; administrators create accounts.

## Future Enhancements

- object storage and malware scanning for attachments
- multiple web replicas after media is moved off the local volume
- central monitoring and security alerts
- SLA timers and escalation rules
- AI-assisted categorisation and response suggestions using synthetic training data
- Teams integration and knowledge-base suggestions
- formal accessibility and load-testing programmes
