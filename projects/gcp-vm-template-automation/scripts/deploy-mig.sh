#!/usr/bin/env bash
set -euo pipefail

# Defaults (override via environment variables before calling the script)
PROJECT_ID="${PROJECT_ID:-$(gcloud config get-value project 2>/dev/null)}"
REGION="${REGION:-europe-west1}"
ZONE="${ZONE:-europe-west1-b}"
TEMPLATE_NAME="${TEMPLATE_NAME:-web-template}"
GROUP_NAME="${GROUP_NAME:-web-mig}"
SIZE="${SIZE:-8}"
MACHINE_TYPE="${MACHINE_TYPE:-e2-micro}"
IMAGE_FAMILY="${IMAGE_FAMILY:-debian-12}"
IMAGE_PROJECT="${IMAGE_PROJECT:-debian-cloud}"
NETWORK="${NETWORK:-default}"
FIREWALL_RULE="${FIREWALL_RULE:-allow-http}"

if [[ -z "${PROJECT_ID}" || "${PROJECT_ID}" == "(unset)" ]]; then
  echo "ERROR: PROJECT_ID is not set. Run: gcloud config set project <YOUR_PROJECT_ID>"
  exit 1
fi

echo "Project: ${PROJECT_ID}"
echo "Region/Zone: ${REGION} / ${ZONE}"
echo "Template: ${TEMPLATE_NAME}"
echo "MIG: ${GROUP_NAME} (size=${SIZE})"

# 1) Create or ensure firewall rule for HTTP (tcp/80); target tag 'http-server'
if ! gcloud compute firewall-rules describe "${FIREWALL_RULE}" >/dev/null 2>&1; then
  echo "Creating firewall rule ${FIREWALL_RULE} (tcp:80) ..."
  gcloud compute firewall-rules create "${FIREWALL_RULE}" \
    --allow=tcp:80 \
    --direction=INGRESS \
    --source-ranges=0.0.0.0/0 \
    --target-tags=http-server \
    --network="${NETWORK}" \
    -q
else
  echo "Firewall rule ${FIREWALL_RULE} already exists; skipping."
fi

# 2) Create instance template with startup script and tag `http-server`
if ! gcloud compute instance-templates describe "${TEMPLATE_NAME}" >/dev/null 2>&1; then
  echo "Creating instance template ${TEMPLATE_NAME} ..."
  gcloud compute instance-templates create "${TEMPLATE_NAME}" \
    --machine-type="${MACHINE_TYPE}" \
    --image-family="${IMAGE_FAMILY}" \
    --image-project="${IMAGE_PROJECT}" \
    --tags=http-server \
    --metadata-from-file=startup-script=scripts/startup-web.sh \
    -q
else
  echo "Instance template ${TEMPLATE_NAME} already exists; skipping."
fi

# 3) Create a Managed Instance Group of SIZE instances
if ! gcloud compute instance-groups managed describe "${GROUP_NAME}" --zone "${ZONE}" >/dev/null 2>&1; then
  echo "Creating MIG ${GROUP_NAME} (size=${SIZE}) ..."
  gcloud compute instance-groups managed create "${GROUP_NAME}" \
    --template="${TEMPLATE_NAME}" \
    --size="${SIZE}" \
    --zone="${ZONE}" \
    --base-instance-name="web" \
    -q
else
  echo "MIG ${GROUP_NAME} already exists; scaling to ${SIZE} ..."
  gcloud compute instance-groups managed resize "${GROUP_NAME}" --size="${SIZE}" --zone "${ZONE}" -q
fi

echo "Done. Listing instances and external IPs (it may take a minute to populate):"
gcloud compute instance-groups managed list-instances "${GROUP_NAME}" --zone "${ZONE}" \
  --format="table(instance, status)"
gcloud compute instances list \
  --filter="name~'^web-'" \
  --format="table(name, zone.basename(), EXTERNAL_IP)"
