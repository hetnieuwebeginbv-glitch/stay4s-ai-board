"""agent_factory.py — genereert een gespecialiseerde agent op basis van een vraag.

Vraag -> eigen AI genereert agent-spec (JSON) -> factory bouwt agent.py + config
-> sandbox-test -> eval -> iterate.

Dit is het prototype: werkt met elk Ollama-model (LoRA nu, cyc7-sft straks).

Gebruik:
  python agent_factory.py "maak een agent die samenvattingen schrijft van .txt bestanden"
  python agent_factory.py "maak een agent die recepten opslaat" --model stay4s-lora
"""
import argparse
import json
import os
import re
import sys
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")

OLLAMA_URL = "http://127.0.0.1:11434"

AGENT_GENERATOR_SYSTEM = (
    "Je bent Stay4S Agent-Factory. Een gebruiker geeft een taak. "
    "Jij ontwerpt een gespecialiseerde AI-agent die die taak kan uitvoeren. "
    "Antwoord STRICT in JSON met dit schema:\n"
    "{\n"
    '  "agent_name": "korte-naam",\n'
    '  "description": "wat de agent doet",\n'
    '  "tools": ["read_file", "write_file", "list_dir", "type", "click", "screenshot", "call_ollama"],\n'
    '  "steps": ["stap1", "stap2"],\n'
    '  "output_format": "text|json|markdown",\n'
    '  "safety_level": "safe|medium"\n'
    "}\n"
    "Kies tools ALLEEN uit deze lijst: read_file, write_file, list_dir, type, click, "
    "screenshot, call_ollama. Geen uitleg, alleen de JSON."
)

AGENT_CODE_TEMPLATE = '''"""__AGENT_NAME__ — gegenereerd door Stay4S Agent-Factory."""
import json
import os


def run(input_data):
    """Voer de agent-taak uit."""
    result = {"agent": "__AGENT_NAME__", "status": "ok", "output": None}

    # STAPPEN: __STEPS__
    # (deze stub wordt ingevuld op basis van de gegenereerde spec)
    result["output"] = input_data
    return result


if __name__ == "__main__":
    print(json.dumps(run("test"), ensure_ascii=False))
'''

# Werkende tool-implementaties voor de gegenereerde agent
TOOL_IMPLEMENTATIONS = {
    "read_file": '''def _read_file(path):
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()''',
    "list_dir": '''def _list_dir(path):
    return sorted(os.listdir(path))''',
    "call_ollama": '''def _call_ollama(prompt, model="stay4s-lora:1"):
    import urllib.request
    body = json.dumps({"model": model, "messages": [{"role": "user", "content": prompt}],
                       "stream": False, "options": {"num_predict": 200}}).encode()
    req = urllib.request.Request("http://127.0.0.1:11434/api/chat", data=body,
                                 headers={"Content-Type": "application/json"})
    d = json.loads(urllib.request.urlopen(req, timeout=120).read().decode())
    return d.get("message", {}).get("content", "")''',
    "write_file": '''def _write_file(path, content):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)
    return f"geschreven: {path}"''',
}


def build_agent_code(spec):
    """Genereer werkende agent-code op basis van de spec."""
    tools = spec.get("tools", [])
    name = spec["agent_name"]

    impls = "\n\n".join(TOOL_IMPLEMENTATIONS.get(t, "") for t in tools if t in TOOL_IMPLEMENTATIONS)

    # build een werkende run()-functie
    steps_notes = "; ".join(spec.get("steps", []))
    has_ollama = "call_ollama" in tools
    has_read = "read_file" in tools

    body = f'    result = {{"agent": "{name}", "status": "ok", "output": None}}\n'
    body += f'    # Taak: {steps_notes}\n'
    if has_read:
        body += '    target = input_data if isinstance(input_data, str) else input_data.get("path", ".")\n'
        body += '    if os.path.isdir(target):\n'
        body += '        files = _list_dir(target)\n'
        body += '        texts = []\n'
        body += '        for f in files:\n'
        body += '            if f.endswith(".txt"):\n'
        body += '                try:\n'
        body += '                    texts.append(_read_file(os.path.join(target, f)))\n'
        body += '                except Exception:\n'
        body += '                    pass\n'
        body += '        content = "\\n\\n".join(texts)\n'
        body += '    else:\n'
        body += '        try:\n'
        body += '            content = _read_file(target)\n'
        body += '        except Exception:\n'
        body += '            content = target\n'
    else:
        body += '    content = input_data if isinstance(input_data, str) else str(input_data)\n'

    if has_ollama:
        body += '    result["output"] = _call_ollama("Vat de volgende tekst kort samen in het Nederlands:\\n\\n" + content)\n'
    else:
        body += '    result["output"] = content[:500]\n'
    body += '    return result\n'

    code = f'''"""{name} — gegenereerd door Stay4S Agent-Factory."""
import json
import os

{impls}


def run(input_data):
{body}

if __name__ == "__main__":
    print(json.dumps(run("test"), ensure_ascii=False))
'''
    return code


def call_model(model, prompt, system, num_predict=400, timeout=120):
    body = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "stream": False,
        "options": {"temperature": 0.3, "num_predict": num_predict},
    }).encode()
    req = urllib.request.Request(OLLAMA_URL + "/api/chat", data=body,
                                 headers={"Content-Type": "application/json"})
    d = json.loads(urllib.request.urlopen(req, timeout=timeout).read().decode())
    return d.get("message", {}).get("content", "")


def extract_json(text):
    start = text.find("{")
    end = text.rfind("}") + 1
    if start >= 0 and end > start:
        return json.loads(text[start:end])
    raise ValueError(f"geen JSON: {text[:200]}")


def validate_spec(spec):
    """Valideer de gegenereerde agent-spec."""
    allowed = {"read_file", "write_file", "list_dir", "type", "click",
               "screenshot", "call_ollama"}
    tools = spec.get("tools", [])
    if not tools:
        return False, "geen tools"
    bad = [t for t in tools if t not in allowed]
    if bad:
        return False, f"verboden tool: {bad}"
    if not spec.get("agent_name"):
        return False, "geen agent_name"
    return True, "ok"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("task", help="de taak waarvoor je een agent wil")
    ap.add_argument("--model", default="staylm2-lora4b:1")
    ap.add_argument("--outdir", default="/workspace/agents")
    args = ap.parse_args()

    print(f"[factory] Vraag: {args.task}")
    print(f"[factory] Model: {args.model}")

    # Stap 1: AI genereert agent-spec
    print("[factory] AI genereert agent-spec...")
    try:
        raw = call_model(args.model, args.task, AGENT_GENERATOR_SYSTEM)
        spec = extract_json(raw)
    except Exception as e:
        print(f"[factory] FOUT: kan geen agent-spec genereren: {e}")
        return 1

    ok, msg = validate_spec(spec)
    if not ok:
        print(f"[factory] SPEC ONGELDIG: {msg}")
        print(json.dumps(spec, ensure_ascii=False, indent=2))
        return 1

    print(f"[factory] Agent: {spec['agent_name']}")
    print(f"[factory] Tools: {spec['tools']}")
    print(f"[factory] Stappen: {spec['steps']}")
    print(f"[factory] Output: {spec.get('output_format')}")

    # Stap 2: bouw agent.py + config (met werkende implementatie)
    os.makedirs(args.outdir, exist_ok=True)
    agent_dir = os.path.join(args.outdir, spec["agent_name"])
    os.makedirs(agent_dir, exist_ok=True)

    code = build_agent_code(spec)
    with open(os.path.join(agent_dir, "agent.py"), "w", encoding="utf-8") as fh:
        fh.write(code)

    spec["generated_by"] = "agent_factory v0.1"
    with open(os.path.join(agent_dir, "config.json"), "w", encoding="utf-8") as fh:
        json.dump(spec, fh, indent=2, ensure_ascii=False)

    print(f"[factory] GEBOUWD: {agent_dir}")
    print("[factory] Bestanden: agent.py + config.json")

    # Stap 3: test (stub draaien)
    print("[factory] Sandbox-test...")
    import subprocess
    r = subprocess.run([sys.executable, os.path.join(agent_dir, "agent.py")],
                       capture_output=True, text=True, timeout=30)
    if r.returncode == 0:
        print(f"[factory] TEST OK: {r.stdout.strip()[:100]}")
    else:
        print(f"[factory] TEST FOUT: {r.stderr[:200]}")
        return 1

    print("[factory] KLAAR — agent is klaar voor verdere ontwikkeling.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
