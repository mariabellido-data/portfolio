#!/usr/bin/env bash
set -euo pipefail

ZONE="${ZONE:-europe-west1-b}"
TEMPLATE_NAME="${TEMPLATE_NAME:-web-template}"

# Create 8 standalone instances from an existing template
for i in $(seq -w 1 8); do
  NAME="web-${i}"
  echo "Creating ${NAME} from template ${TEMPLATE_NAME} in ${ZONE} ..."
  gcloud compute instances create "${NAME}" \
    --zone "${ZONE}" \
    --source-instance-template "${TEMPLATE_NAME}" \
    -q
done

echo "Done. Listing instances and external IPs:"
gcloud compute instances list --filter="name~'^web-'" \
  --format="table(name, zone.basename(), EXTERNAL_IP)"
