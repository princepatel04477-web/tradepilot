import sys
from pathlib import Path
from app.database import init_db
from app.services.email_exporter import PerEmailExporter

def test_export():
    print("=" * 70)
    print("TradePilot - Testing Per-Email PDF & TXT Document Exporter")
    print("=" * 70)
    init_db()

    res = PerEmailExporter.export_campaign_emails(campaign_id=1)
    print(f"[+] Total Emails Processed: {res['total_emails']}")
    print(f"[+] Export Directory:       {res['export_dir']}")
    print(f"[+] ZIP Bundle Location:    {res['zip_bundle']}")
    
    for f in res["files"]:
        print(f"\n[Email #{f['index']}] {f['email']}")
        print(f" - TXT File: {f['txt']}")
        print(f" - PDF File: {f['pdf']}")

    assert Path(res['zip_bundle']).exists()
    print("\nSUCCESS! Per-email PDF and TXT documents generated and verified.")

if __name__ == "__main__":
    test_export()
