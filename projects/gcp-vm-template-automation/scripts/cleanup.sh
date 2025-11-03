#!/usr/bin/env bash
set -euo pipefail

ZONE="${ZONE:-europe-west1-b}"
GROUP_NAME="${GROUP_NAME:-web-mig}"
TEMPLATE_NAME="${TEMPLATE_NAME:-web-template}"
FIREWALL_RULE="${FIREWALL_RULE:-allow-http}"

echo "Deleting MIG ${GROUP_NAME} (and its instances) in ${ZONE} ..."
gcloud compute instance-groups managed delete "${GROUP_NAME}" --zone "${ZONE}" -q || true

echo "Deleting instance template ${TEMPLATE_NAME} ..."
gcloud compute instance-templates delete "${TEMPLATE_NAME}" -q || true

echo "Deleting firewall rule ${FIREWALL_RULE} ..."
gcloud compute firewall-rules delete "${FIREWALL_RULE}" -q || true

echo "Cleanup completed."
