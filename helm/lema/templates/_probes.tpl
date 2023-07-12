{{- define "probe.postgres" -}}
exec:
  command:
    - psql
    - -U
    - {{ .username }}
    - --list
{{- end }}
{{- define "probe.keycloak" -}}
httpGet:
  port: 8080
  path: /{{ .Values.auth.service.path }}/health
{{- end }}
{{- define "probe.seaweedfs" -}}
httpGet:
  port: 8333
  path: /status
{{- end }}
{{- define "probe.api" -}}
httpGet:
  port: 8080
  path: /meta/health/basic
{{- end }}
{{- define "probe.lema" -}}
httpGet:
  port: 80
  path: /assets/config.json
{{- end }}
{{- define "probe.nifi" -}}
httpGet:
  port: 8090
  path: /nifi
{{- end }}
