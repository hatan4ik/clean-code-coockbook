#!/usr/bin/env bash
set -euo pipefail

echo "=== Gemini 3 VS Code Setup ==="

# 1. Ask for API key and model
if [[ -z "${GEMINI_API_KEY:-}" ]]; then
  read -r -p "Enter your Gemini API key: " GEMINI_API_KEY
fi

read -r -p "Enter Gemini model name [default: gemini-3.0-pro]: " GEMINI_MODEL_INPUT
GEMINI_MODEL=${GEMINI_MODEL_INPUT:-gemini-3.0-pro}

echo "Using model: $GEMINI_MODEL"

# 2. Create .env file
if [[ -f .env ]]; then
  echo "Existing .env found, creating backup as .env.bak"
  cp .env .env.bak
fi

cat > .env <<EOF
GEMINI_API_KEY=$GEMINI_API_KEY
GEMINI_MODEL=$GEMINI_MODEL
EOF

echo "✔ .env created/updated"

# 3. Create Python virtual environment and install deps
if ! command -v python3 >/dev/null 2>&1; then
  echo "ERROR: python3 not found. Install Python 3 first."
  exit 1
fi

if [[ ! -d .venv ]]; then
  echo "Creating Python venv in .venv ..."
  python3 -m venv .venv
else
  echo "Python venv .venv already exists, reusing it."
fi

# shellcheck disable=SC1091
source .venv/bin/activate

echo "Installing python deps (google-generativeai, python-dotenv) ..."
pip install --upgrade pip >/dev/null
pip install google-generativeai python-dotenv >/dev/null

echo "✔ Python deps installed"

# 4. Create gemini3_cli.py
cat > gemini3_cli.py <<'EOF'
#!/usr/bin/env python
import os
import sys

from dotenv import load_dotenv
import google.generativeai as genai


def main():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    model_name = os.getenv("GEMINI_MODEL", "gemini-3.0-pro")

    if not api_key:
        print("ERROR: GEMINI_API_KEY not set in environment or .env", file=sys.stderr)
        sys.exit(1)

    genai.configure(api_key=api_key)

    # Prompt from args or stdin
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
    else:
        prompt = sys.stdin.read()

    if not prompt.strip():
        print("ERROR: No prompt provided (args or stdin).", file=sys.stderr)
        sys.exit(1)

    model = genai.GenerativeModel(model_name)
    resp = model.generate_content(prompt)

    if hasattr(resp, "text"):
        print(resp.text)
    else:
        for c in resp.candidates:
            for part in c.content.parts:
                text = getattr(part, "text", "")
                if text:
                    print(text)


if __name__ == "__main__":
    main()
EOF

chmod +x gemini3_cli.py
echo "✔ gemini3_cli.py created"

# 5. Create VS Code HTTP file for REST Client
mkdir -p .vscode/gemini

cat > .vscode/gemini/gemini3.http <<EOF
### Simple prompt to Gemini 3 Pro
POST https://generativelanguage.googleapis.com/v1beta/models/$GEMINI_MODEL:generateContent?key=$GEMINI_API_KEY
Content-Type: application/json

{
  "contents": [
    {
      "parts": [
        { "text": "You are an expert software engineer. Write an idiomatic Go function that calculates the nth Fibonacci number iteratively." }
      ]
    }
  ]
}

###

# Code-assist style: send code and ask for refactor
POST https://generativelanguage.googleapis.com/v1beta/models/$GEMINI_MODEL:generateContent?key=$GEMINI_API_KEY
Content-Type: application/json

{
  "contents": [
    {
      "parts": [
        {
          "text": "Refactor this code for clarity and performance. Keep public API unchanged:\\n\\n```\\n{{code}}\\n```"
        }
      ]
    }
  ]
}
EOF

echo "✔ .vscode/gemini/gemini3.http created"

# 6. Install REST Client extension (if VS Code CLI available)
if command -v code >/dev/null 2>&1; then
  echo "Installing VS Code REST Client extension (humao.rest-client) if not present ..."
  code --install-extension humao.rest-client >/dev/null || true
  echo "✔ VS Code REST Client ensured"
else
  echo "WARN: 'code' CLI not found. Enable 'Shell Command: Install \"code\" command in PATH' from VS Code Command Palette."
fi

# 7. VS Code tasks snippet
mkdir -p .vscode

if [[ ! -f .vscode/tasks.json ]]; then
  cat > .vscode/tasks.json <<'EOF'
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Gemini 3: Explain current file",
      "type": "shell",
      "command": "source .venv/bin/activate && cat ${file} | ./gemini3_cli.py \"Explain this file, then propose improvements.\"",
      "options": {
        "cwd": "${workspaceFolder}"
      },
      "problemMatcher": []
    }
  ]
}
EOF
  echo "✔ .vscode/tasks.json created with Gemini 3 task"
else
  cat > .vscode/tasks.gemini3.json <<'EOF'
{
  "label": "Gemini 3: Explain current file",
  "type": "shell",
  "command": "source .venv/bin/activate && cat ${file} | ./gemini3_cli.py \"Explain this file, then propose improvements.\"",
  "options": {
    "cwd": "${workspaceFolder}"
  },
  "problemMatcher": []
}
EOF
  echo "✔ Existing .vscode/tasks.json detected."
  echo "  → Gemini task snippet written to .vscode/tasks.gemini3.json."
  echo "  → Please merge that object into the \"tasks\" array in tasks.json."
fi

echo
echo "=== DONE ==="
echo "Now you can:"
echo "  1) Open .vscode/gemini/gemini3.http and click 'Send Request' for quick Gemini 3 calls."
echo "  2) Run the VS Code task 'Gemini 3: Explain current file' (⇧⌘P → Run Task)."
echo "  3) Use ./gemini3_cli.py from the terminal for scripted Gemini 3 usage."
