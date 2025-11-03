# GCP VM Template & Automated Deployment (8 Web Servers)

This repo provides a **minimal, reproducible** workflow to:
- Create an **instance template** with a startup script that enables an auto-start service (Nginx).
- Deploy **8 identical web servers** either via a **Managed Instance Group (MIG)** or as **standalone instances**.
- Open HTTP traffic with a firewall rule and expose a simple landing page.

> Target audience: IT admins and learners who want a fast, documented baseline to clone and run.

---

## Architecture (quick)
- **Instance template**: Debian 12 base + startup script (`startup-web.sh`) that installs and enables **Nginx**.
- **Auto-enabled service**: `systemd` manages Nginx; service is enabled on boot.
- **Deployment options**:
  - **Managed Instance Group (recommended)**: 8 instances created and managed as a group.
  - **Standalone instances**: create 8 instances directly from the template.
- **Firewall**: Rule `allow-http` permits TCP/80 from the internet; instances tagged `http-server`.

---

## Prerequisites
- A Google Cloud project with **billing enabled**.
- **Google Cloud CLI** (`gcloud`) authenticated and pointing to your project:
  ```bash
  gcloud auth login
  gcloud auth application-default login   # optional for some workflows
  gcloud config set project <YOUR_PROJECT_ID>
  ```
- Pick a region/zone (defaults in scripts use `europe-west1` / `europe-west1-b`).

---

## Quickstart (Managed Instance Group, 8 VMs)

> This creates: firewall rule, instance template, and a MIG of 8 instances.

```bash
# 1) Clone and enter
git clone https://github.com/your-user/gcp-vm-template-automation.git
cd gcp-vm-template-automation

# 2) Configure your project and optional defaults
export PROJECT_ID=<YOUR_PROJECT_ID>
gcloud config set project "$PROJECT_ID"

# Optional overrides (defaults are fine)
export REGION=europe-west1
export ZONE=europe-west1-b
export TEMPLATE_NAME=web-template
export GROUP_NAME=web-mig
export SIZE=8
export MACHINE_TYPE=e2-micro     # eligible for Free Tier in some regions; adjust as needed

# 3) Make scripts executable
chmod +x scripts/*.sh

# 4) Deploy a MIG of 8 instances
./scripts/deploy-mig.sh
```

**Check instances & IPs**
```bash
gcloud compute instance-groups managed list-instances "$GROUP_NAME" --zone "$ZONE"   --format="table(instance, status)"
gcloud compute instances list --filter="name~'^web-'"   --format="table(name, zone.basename(), EXTERNAL_IP)"
```

Open a browser to any instance’s external IP; you should see the default page with the instance hostname.

**Cleanup**
```bash
./scripts/cleanup.sh
```

---

## Alternative: Standalone Instances (8 VMs, no MIG)

```bash
# After creating the template (deploy-mig.sh also creates it; or run the template block from that script):
export TEMPLATE_NAME=web-template
export ZONE=europe-west1-b

chmod +x scripts/*.sh
./scripts/deploy-from-template.sh
```

List and open IPs as above. To delete, remove the instances and then the template:
```bash
gcloud compute instances delete $(gcloud compute instances list --filter="name~'^web-'" --format="value(name)")   --zone "$ZONE" -q
gcloud compute instance-templates delete "$TEMPLATE_NAME" -q
gcloud compute firewall-rules delete allow-http -q
```

---

## What the startup script does
`scripts/startup-web.sh`:
- Updates packages, installs **Nginx**.
- Creates a simple `index.html` including the VM hostname.
- Enables and restarts Nginx (auto-start on boot).

This satisfies the “auto-enabled service” requirement with `systemd` + Nginx.

---

## Notes
- Default machine type is `e2-micro`. Adjust for your quotas, region availability, and cost.
- The firewall rule is created once (`allow-http`) and targets the `http-server` tag used by the template.
- For production parity, prefer a **custom image** instead of heavy startup scripts; keep this repo as a fast baseline.
- If you prefer to **follow the Console-first flow** (create 1 VM via UI, configure it, then create a template from it), use:
  ```bash
  gcloud compute instance-templates create web-template     --source-instance=<YOUR_INSTANCE_NAME>     --source-instance-zone=<YOUR_INSTANCE_ZONE>
  ```

---

## Repository Structure
```
gcp-vm-template-automation/
├─ README.md
└─ scripts/
   ├─ startup-web.sh
   ├─ deploy-mig.sh
   ├─ deploy-from-template.sh
   └─ cleanup.sh
```

---

## License
MIT
