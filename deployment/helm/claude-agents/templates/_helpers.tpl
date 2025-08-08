{{/*
Expand the name of the chart.
*/}}
{{- define "claude-agents.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "claude-agents.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "claude-agents.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "claude-agents.labels" -}}
helm.sh/chart: {{ include "claude-agents.chart" . }}
{{ include "claude-agents.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- with .Values.commonLabels }}
{{ toYaml . }}
{{- end }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "claude-agents.selectorLabels" -}}
app.kubernetes.io/name: {{ include "claude-agents.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "claude-agents.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "claude-agents.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Create the namespace name
*/}}
{{- define "claude-agents.namespace" -}}
{{- if .Values.namespace.create }}
{{- default .Values.namespace.name .Release.Namespace }}
{{- else }}
{{- .Release.Namespace }}
{{- end }}
{{- end }}

{{/*
Create PostgreSQL connection string
*/}}
{{- define "claude-agents.postgresql.connectionString" -}}
{{- if .Values.postgresql.enabled }}
{{- printf "postgresql://%s:%s@%s-postgresql:5432/%s" .Values.postgresql.auth.username .Values.postgresql.auth.password (include "claude-agents.fullname" .) .Values.postgresql.auth.database }}
{{- else }}
{{- .Values.externalDatabase.url }}
{{- end }}
{{- end }}

{{/*
Create Redis connection string
*/}}
{{- define "claude-agents.redis.connectionString" -}}
{{- if .Values.redis.enabled }}
{{- if .Values.redis.auth.enabled }}
{{- printf "redis://:%s@%s-redis:6379" .Values.redis.auth.password (include "claude-agents.fullname" .) }}
{{- else }}
{{- printf "redis://%s-redis:6379" (include "claude-agents.fullname" .) }}
{{- end }}
{{- else }}
{{- .Values.externalRedis.url }}
{{- end }}
{{- end }}

{{/*
Create Redis service name
*/}}
{{- define "claude-agents.redis.fullname" -}}
{{- if .Values.redis.enabled }}
{{- printf "%s-redis" (include "claude-agents.fullname" .) }}
{{- else }}
{{- .Values.externalRedis.host }}
{{- end }}
{{- end }}

{{/*
Create Qdrant connection string
*/}}
{{- define "claude-agents.qdrant.connectionString" -}}
{{- if .Values.qdrant.enabled }}
{{- printf "http://%s-qdrant:6333" (include "claude-agents.fullname" .) }}
{{- else }}
{{- .Values.externalQdrant.url }}
{{- end }}
{{- end }}

{{/*
Generate certificates
*/}}
{{- define "claude-agents.gen-certs" -}}
{{- $ca := genCA "claude-agents-ca" 365 }}
{{- $cert := genSignedCert (include "claude-agents.fullname" .) nil (list (printf "%s.%s" (include "claude-agents.fullname" .) .Release.Namespace) (printf "%s.%s.svc" (include "claude-agents.fullname" .) .Release.Namespace)) 365 $ca }}
tls.crt: {{ $cert.Cert | b64enc }}
tls.key: {{ $cert.Key | b64enc }}
ca.crt: {{ $ca.Cert | b64enc }}
{{- end }}

{{/*
Common deployment strategy
*/}}
{{- define "claude-agents.deploymentStrategy" -}}
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxUnavailable: 25%
    maxSurge: 25%
{{- end }}

{{/*
Common security context
*/}}
{{- define "claude-agents.securityContext" -}}
securityContext:
  allowPrivilegeEscalation: false
  capabilities:
    drop:
      - ALL
  readOnlyRootFilesystem: true
  runAsNonRoot: true
  runAsUser: 1000
{{- end }}

{{/*
Common pod security context
*/}}
{{- define "claude-agents.podSecurityContext" -}}
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  fsGroup: 1000
{{- end }}

{{/*
Common resource limits
*/}}
{{- define "claude-agents.resources" -}}
{{- if .resources }}
resources:
  {{- toYaml .resources | nindent 2 }}
{{- else }}
resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 100m
    memory: 128Mi
{{- end }}
{{- end }}

{{/*
Common environment variables
*/}}
{{- define "claude-agents.commonEnv" -}}
- name: KUBERNETES_NAMESPACE
  valueFrom:
    fieldRef:
      fieldPath: metadata.namespace
- name: POD_NAME
  valueFrom:
    fieldRef:
      fieldPath: metadata.name
- name: POD_IP
  valueFrom:
    fieldRef:
      fieldPath: status.podIP
- name: NODE_NAME
  valueFrom:
    fieldRef:
      fieldPath: spec.nodeName
{{- end }}

{{/*
Common volume mounts
*/}}
{{- define "claude-agents.commonVolumeMounts" -}}
- name: tmp
  mountPath: /tmp
- name: var-cache
  mountPath: /var/cache
{{- end }}

{{/*
Common volumes
*/}}
{{- define "claude-agents.commonVolumes" -}}
- name: tmp
  emptyDir: {}
- name: var-cache
  emptyDir: {}
{{- end }}

{{/*
Generate monitoring labels
*/}}
{{- define "claude-agents.monitoringLabels" -}}
{{- if .Values.monitoring.enabled }}
monitoring: "true"
prometheus.io/scrape: "true"
{{- end }}
{{- end }}

{{/*
Generate service monitor selector
*/}}
{{- define "claude-agents.serviceMonitorSelector" -}}
matchLabels:
  {{- include "claude-agents.selectorLabels" . | nindent 2 }}
  monitoring: "true"
{{- end }}