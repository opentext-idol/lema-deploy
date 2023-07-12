{{- define "image" -}}
image: {{ .Values.docker.registry }}{{ .Values.docker.nameSeparator }}{{ .imageName }}{{ .Values.docker.versionSeparator }}{{ .version }}
{{- end -}}