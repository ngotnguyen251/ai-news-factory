"""Audit OpenMontage capabilities; fail visibly if integration cannot be verified."""
import json, subprocess, sys
from pathlib import Path
root=Path("OpenMontage")
if not (root/"tools/tool_registry.py").exists():
    raise SystemExit("OpenMontage tool registry missing")
sys.path.insert(0,str(root.resolve()))
code="from tools.tool_registry import registry; import json; registry.discover(); print(json.dumps({'envelope':registry.support_envelope(),'providers':registry.provider_menu()},default=str))"
r=subprocess.run([sys.executable,"-c",code],cwd=str(root),capture_output=True,text=True,timeout=120)
Path("output").mkdir(exist_ok=True)
Path("output/openmontage_probe.json").write_text(json.dumps({"returncode":r.returncode,"stdout":r.stdout[-25000:],"stderr":r.stderr[-10000:]},indent=2),encoding="utf-8")
if r.returncode:raise SystemExit("OpenMontage capability probe failed; inspect artifact")
print("OpenMontage registry discovered. This is an integration audit, not a rendered video.")
