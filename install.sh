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
chmod +x "$HOME/.local/bin"/omarchy* "$HOME/.local/bin"/codex-query "$HOME/.local/bin"/impeccable "$HOME/.local/bin"/uipro-search "$HOME/.local/bin"/taste-skill "$HOME/.local/bin"/inspiration-scout "$HOME/.local/bin"/herdr-swarm "$HOME/.local/bin"/stageshow

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
mkdir -p "$HOME/.gemini/config" "$HOME/.agents/rules" "$HOME/Work" 2>/dev/null || true
if [[ -w "$HOME/.gemini/config" || -w "$HOME/.gemini/config/AGENTS.md" ]]; then
  cat "$SCRIPT_DIR/config/gemini/AGENTS.md" > "$HOME/.gemini/config/AGENTS.md" 2>/dev/null || true
fi
if [[ -w "$HOME/.gemini" || -w "$HOME/.gemini/GEMINI.md" ]]; then
  cat "$SCRIPT_DIR/config/gemini/AGENTS.md" > "$HOME/.gemini/GEMINI.md" 2>/dev/null || true
fi
cat "$SCRIPT_DIR/config/gemini/AGENTS.md" > "$HOME/.agents/rules/orchestration.md"
cat "$SCRIPT_DIR/config/gemini/AGENTS.md" > "$HOME/Work/AGENTS.md"

# Propagate AGENTS.md to all sub-repositories in ~/Work
for d in "$HOME/Work"/*/; do
  if [[ -d "$d/.git" ]]; then
    cat "$SCRIPT_DIR/config/gemini/AGENTS.md" > "$d/AGENTS.md"
  fi
done

# 5. Configure Antigravity MCP Servers (Figma, etc.)
echo -e "${BLUE}==>${NC} Configuring Antigravity MCP servers..."
MCP_CONFIG="$HOME/.gemini/config/mcp_config.json"
if [[ -f "$SCRIPT_DIR/config/gemini/mcp_config.json" && ( -w "$MCP_CONFIG" || -w "$(dirname "$MCP_CONFIG")" ) ]]; then
  if [[ ! -f "$MCP_CONFIG" || ! -s "$MCP_CONFIG" ]]; then
    cp -f "$SCRIPT_DIR/config/gemini/mcp_config.json" "$MCP_CONFIG"
  elif command -v jq >/dev/null 2>&1; then
    tmp=$(mktemp)
    jq -s '.[0] * .[1]' "$MCP_CONFIG" "$SCRIPT_DIR/config/gemini/mcp_config.json" > "$tmp" && mv "$tmp" "$MCP_CONFIG"
  fi
fi

# 6. Install Custom Orchestration Skills (codex-query, inspiration-scout, design-architect)
echo -e "${BLUE}==>${NC} Installing orchestration & frontend architect skills..."
mkdir -p "$HOME/.agents/skills/codex-query" "$HOME/.local/share/agent-skills/custom/inspiration-scout" "$HOME/.local/share/agent-skills/custom/design-architect"
cp -f "$SCRIPT_DIR/config/skills/codex-query/SKILL.md" "$HOME/.agents/skills/codex-query/"
cp -f "$SCRIPT_DIR/config/skills/inspiration-scout/SKILL.md" "$HOME/.local/share/agent-skills/custom/inspiration-scout/"
cp -f "$SCRIPT_DIR/config/skills/design-architect/SKILL.md" "$HOME/.local/share/agent-skills/custom/design-architect/"

# 6b. Ensure TasteSkill (Leonxlnx/taste-skill) & UI/UX Pro Max (nextlevelbuilder/ui-ux-pro-max-skill) are installed
AGENT_SKILLS_DIR="$HOME/.local/share/agent-skills"
if [[ ! -d "$AGENT_SKILLS_DIR/taste-skill" ]]; then
  echo -e "${BLUE}==>${NC} Cloning TasteSkill (Leonxlnx/taste-skill)..."
  git clone --depth 1 https://github.com/Leonxlnx/taste-skill "$AGENT_SKILLS_DIR/taste-skill" >/dev/null 2>&1 || true
fi
if [[ ! -d "$AGENT_SKILLS_DIR/ui-ux-pro-max-skill" ]]; then
  echo -e "${BLUE}==>${NC} Cloning UI/UX Pro Max (nextlevelbuilder/ui-ux-pro-max-skill)..."
  git clone --depth 1 https://github.com/nextlevelbuilder/ui-ux-pro-max-skill "$AGENT_SKILLS_DIR/ui-ux-pro-max-skill" >/dev/null 2>&1 || true
  sed -i 's|python "\${CLAUDE_PLUGIN_ROOT}/\.claude/skills/ui-ux-pro-max/scripts/search\.py"|uipro-search|g' "$AGENT_SKILLS_DIR/ui-ux-pro-max-skill/.claude/skills/ui-ux-pro-max/SKILL.md" 2>/dev/null || true
fi

for root in "$HOME/.gemini/skills" "$HOME/.agents/skills" "$HOME/.claude/skills"; do
  mkdir -p "$root"
  ln -sfn "$AGENT_SKILLS_DIR/custom/inspiration-scout" "$root/inspiration-scout"
  ln -sfn "$AGENT_SKILLS_DIR/custom/design-architect" "$root/design-architect"
  [[ -d "$AGENT_SKILLS_DIR/taste-skill/skills/taste-skill" ]] && ln -sfn "$AGENT_SKILLS_DIR/taste-skill/skills/taste-skill" "$root/design-taste-frontend"
  [[ -d "$AGENT_SKILLS_DIR/ui-ux-pro-max-skill/.claude/skills/ui-ux-pro-max" ]] && ln -sfn "$AGENT_SKILLS_DIR/ui-ux-pro-max-skill/.claude/skills/ui-ux-pro-max" "$root/ui-ux-pro-max"
  for sub in ui-styling design-system brand banner-design slides; do
    [[ -d "$AGENT_SKILLS_DIR/ui-ux-pro-max-skill/.claude/skills/$sub" ]] && ln -sfn "$AGENT_SKILLS_DIR/ui-ux-pro-max-skill/.claude/skills/$sub" "$root/$sub"
  done
done

# Propagate all unified skills to all agent runtimes (Omp, Pi, Hermes, Claude)
echo -e "${BLUE}==>${NC} Propagating unified skills across agent runtimes..."
for skill_path in "$HOME/.agents/skills"/*; do
  [[ -e "$skill_path" ]] || continue
  skill_name="$(basename "$skill_path")"
  for target_root in "$HOME/.omp/agent/skills" "$HOME/.pi/agent/skills" "$HOME/.hermes/skills" "$HOME/.claude/skills"; do
    mkdir -p "$target_root"
    ln -sfn "$skill_path" "$target_root/$skill_name"
  done
done

# 7. Pin Impeccable Design & Frontend Skills
if [[ -x "$HOME/.local/bin/impeccable" ]]; then
  echo -e "${BLUE}==>${NC} Pinning Impeccable design skills & slash commands..."
  for cmd in init extract document shape critique audit polish bolder quieter distill harden onboard live animate colorize typeset layout delight overdrive clarify adapt optimize generate; do
    "$HOME/.local/bin/impeccable" pin pin "$cmd" >/dev/null 2>&1 || true
  done
fi

# 8. Apply Hyprland bindings (Super+A)
BINDINGS_LUA="$HOME/.config/hypr/bindings.lua"
if [[ -f "$BINDINGS_LUA" ]]; then
  if ! grep -q "SUPER + A" "$BINDINGS_LUA"; then
    echo -e "${BLUE}==>${NC} Adding Super+A binding to $BINDINGS_LUA..."
    echo -e "\n-- Launch the default AI Agent (Antigravity)\no.bind(\"SUPER + A\", \"AI Agent\", \"omarchy-agent\")" >> "$BINDINGS_LUA"
  fi
fi

# 9. Apply Hyprland window rules (Floating HUD)
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

# 10. Reload Hyprland and Omarchy Shell
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
