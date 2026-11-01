#!/usr/bin/env bash
# ==============================================================================
# Omarchy AI Orchestration — Installer Script
# Integrates Antigravity (Gemini 3.8 Flash / 4 Argon) + Codex into Omarchy
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}==>${NC} Installing Omarchy AI Orchestration setup..."

# 1. Install CLI binaries to ~/.local/bin
echo -e "${BLUE}==>${NC} Installing binaries to ~/.local/bin/..."
mkdir -p "$HOME/.local/bin"
cp -f "$SCRIPT_DIR"/bin/* "$HOME/.local/bin/"
chmod +x "$HOME/.local/bin"/omarchy* "$HOME/.local/bin"/codex-query

# 2. Configure Omarchy defaults & menu
echo -e "${BLUE}==>${NC} Configuring Omarchy defaults & menu..."
mkdir -p "$HOME/.config/omarchy/defaults" "$HOME/.config/omarchy/extensions"
cp -f "$SCRIPT_DIR/config/omarchy/defaults/agent" "$HOME/.config/omarchy/defaults/"
cp -f "$SCRIPT_DIR/config/omarchy/extensions/omarchy-menu.jsonc" "$HOME/.config/omarchy/extensions/"

# 3. Enable Antigravity and Codex in Omarchy bar widget (shell.json)
SHELL_JSON="$HOME/.config/omarchy/shell.json"
if [[ -f "$SHELL_JSON" ]] && command -v jq >/dev/null 2>&1; then
  echo -e "${BLUE}==>${NC} Enabling providers in $SHELL_JSON..."
  tmp=$(mktemp)
  jq '
    walk(
      if type == "object" and .id == "omarchy.agents" then
        .providers.antigravity.enabled = true |
        .providers.codex.enabled = true
      else . end
    )
  ' "$SHELL_JSON" > "$tmp" && mv "$tmp" "$SHELL_JSON"
fi

# 4. Install Universal Multi-Agent Orchestration Guidelines (AGENTS.md)
echo -e "${BLUE}==>${NC} Installing AGENTS.md rules..."
mkdir -p "$HOME/.gemini/config" "$HOME/.agents/rules" "$HOME/Work"
cp -f "$SCRIPT_DIR/config/gemini/AGENTS.md" "$HOME/.gemini/config/AGENTS.md"
cp -f "$SCRIPT_DIR/config/gemini/AGENTS.md" "$HOME/.agents/rules/orchestration.md"
[[ ! -f "$HOME/Work/AGENTS.md" ]] && cp -f "$SCRIPT_DIR/config/gemini/AGENTS.md" "$HOME/Work/AGENTS.md"

# 5. Configure Antigravity MCP Servers (Figma, etc.)
echo -e "${BLUE}==>${NC} Configuring Antigravity MCP servers..."
MCP_CONFIG="$HOME/.gemini/config/mcp_config.json"
if [[ -f "$SCRIPT_DIR/config/gemini/mcp_config.json" ]]; then
  if [[ ! -f "$MCP_CONFIG" || ! -s "$MCP_CONFIG" ]]; then
    cp -f "$SCRIPT_DIR/config/gemini/mcp_config.json" "$MCP_CONFIG"
  elif command -v jq >/dev/null 2>&1; then
    tmp=$(mktemp)
    jq -s '.[0] * .[1]' "$MCP_CONFIG" "$SCRIPT_DIR/config/gemini/mcp_config.json" > "$tmp" && mv "$tmp" "$MCP_CONFIG"
  fi
fi

# 6. Install Codex Query Skill
echo -e "${BLUE}==>${NC} Installing Codex Query skill..."
mkdir -p "$HOME/.agents/skills/codex-query"
cp -f "$SCRIPT_DIR/config/skills/codex-query/SKILL.md" "$HOME/.agents/skills/codex-query/"

# 7. Apply Hyprland bindings (Super+A)
BINDINGS_LUA="$HOME/.config/hypr/bindings.lua"
if [[ -f "$BINDINGS_LUA" ]]; then
  if ! grep -q "SUPER + A" "$BINDINGS_LUA"; then
    echo -e "${BLUE}==>${NC} Adding Super+A binding to $BINDINGS_LUA..."
    echo -e "\n-- Launch the default AI Agent (Antigravity)\no.bind(\"SUPER + A\", \"AI Agent\", \"omarchy-agent\")" >> "$BINDINGS_LUA"
  fi
fi

# 8. Apply Hyprland window rules (Floating HUD)
HYPRLAND_LUA="$HOME/.config/hypr/hyprland.lua"
if [[ -f "$HYPRLAND_LUA" ]]; then
  if ! grep -q "org.omarchy.agent" "$HYPRLAND_LUA"; then
    echo -e "${BLUE}==>${NC} Adding floating HUD window rule to $HYPRLAND_LUA..."
    cat << 'EOF' >> "$HYPRLAND_LUA"

-- Antigravity / AI Agent floating HUD window
o.window("org.omarchy.agent", {
  float = true,
  center = true,
  size = { 1100, 750 },
})
EOF
  fi
fi

# 9. Reload Hyprland and Omarchy Shell
echo -e "${BLUE}==>${NC} Refreshing Omarchy bar and reloading Hyprland..."
if command -v hyprctl >/dev/null 2>&1; then
  hyprctl reload >/dev/null 2>&1 || true
fi
if command -v omarchy-agent-usage-update >/dev/null 2>&1; then
  omarchy-agent-usage-update --force >/dev/null 2>&1 || true
fi
if command -v omarchy-shell >/dev/null 2>&1; then
  omarchy-shell omarchy.agents refresh >/dev/null 2>&1 || true
fi

echo -e "${GREEN}==> Setup installed successfully!${NC}"
echo -e "You can now launch Antigravity using ${YELLOW}Super + A${NC} or right-clicking the bar icon."
