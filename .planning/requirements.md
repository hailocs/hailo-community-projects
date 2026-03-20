# Technical Requirements

## Overview

Restructure hailo-community-projects as a cross-platform agentic-development-enabled community hub built on top of hailo-apps-infra (git submodule). No backward compatibility with the current repo structure is required. The `basic_pipelines/` directory and legacy install scripts are removed.

---

## Architectural Decisions

### 1. Sub-repo Strategy: Git Submodule
- hailo-apps-infra at `hailo-apps-infra/` in repo root
- Pinned to branch `test/app-builder-20-apps` (will move to release tag later)
- Installed in editable mode: `pip install -e hailo-apps-infra`

### 2. Venv Naming: Align to `venv_hailo_apps`
- Matches hailo-apps-infra convention
- No backward compatibility needed

### 3. Installation: Rewrite, Delegate to hailo-apps-infra
- Rewrite `install.sh` to:
  1. Init submodule
  2. Delegate to hailo-apps-infra's install flow (or call `hailo-post-install` after pip install)
  3. Install community-projects specific requirements
- Remove legacy scripts: `download_resources.sh`, `hailo_python_installation.sh`

### 4. Remove `basic_pipelines/`
- All official apps (detection, pose, segmentation, depth) live in hailo-apps-infra
- Accessible via `hailo-detect`, `hailo-pose`, etc. entry points after install
- No need for duplicate code in this repo

### 5. Community Directory Structure
- `community/apps/` — AI-agent-generated apps (ported from hailo-apps-infra): pipeline/standalone/genai
- `community_projects/` — Existing human-contributed projects (fruit_ninja, TAILO, etc.) — kept intact
- `community/contributions/` — Knowledge contributions from contribute-insights agent

### 6. Gesture Detection: Thin Wrapper
- Core code stays in hailo-apps-infra
- Community example demonstrates customization on top of the pipeline

### 7. Cross-Platform Agentic Infrastructure
- `.hailo/` as canonical shared knowledge directory (platform-neutral)
- All skills use `hl-` prefix for consistency
- Platform-specific entry points are thin wrappers:
  - `.claude/skills/hl-*/SKILL.md` → reads `.hailo/skills/hl-*.md`
  - `.github/copilot-instructions.md` → points to `.hailo/`
  - `.cursor/rules` → points to `.hailo/`
  - `CLAUDE.md` → thin entry, points to `.hailo/README.md`
- 13 unified skills, 7 as Claude Code slash commands, 6 as reference docs
- Supports Claude Code, VS Code Copilot, and Cursor

---

## Functional Requirements

### Installation
1. `install.sh` inits submodule automatically
2. hailo-apps-infra installed in editable mode
3. `hailo-post-install` called for resources + C++ compilation
4. `setup_env.sh` adds both repos to PYTHONPATH, loads `.env`
5. Venv name: `venv_hailo_apps`

### Agentic Tools (Cross-Platform)
1. All shared knowledge lives in `.hailo/` (instructions, skills, toolsets, knowledge, memory, templates, examples)
2. Skills use `hl-` prefix: `hl-build-app`, `hl-build-vlm-app`, `hl-build-standalone-app`, `hl-build-agent-app`, `hl-add-voice`, `hl-profile`, `hl-contribute`, `hl-monitoring`, `hl-event-detection`, `hl-camera`, `hl-model-management`, `hl-plan-and-execute`, `hl-validate`
3. Skills read framework code from `hailo-apps-infra/`, write new apps to `community/apps/`
4. Generated code uses `from hailo_apps.*` (pip imports, no path prefix)
5. Platform-specific wrappers point to `.hailo/`; never duplicate content
6. Memory lives in `.hailo/memory/`, old `.claude/memory/` redirects there
7. Scripts remain in `.claude/skills/hl-*/scripts/` (Claude Code-specific operational tools)

### Community Apps
1. All 20+ community apps ported with working imports
2. Untracked/incomplete files copied but `.gitignore`-d
3. Existing `community_projects/` apps continue to work
4. Gesture detection example imports from `hailo_apps.python.pipeline_apps.gesture_detection`

---

## Files to Remove
| File/Dir | Reason |
|----------|--------|
| `basic_pipelines/` | Official apps live in hailo-apps-infra |
| `download_resources.sh` | Handled by `hailo-download-resources` from hailo-apps-infra |
| `hailo_python_installation.sh` | Handled by hailo-apps-infra installer |
| `.github/.github/` | All content migrated to `.hailo/` ✅ |
| `.claude/skills/app-builder/` | Replaced by `.claude/skills/hl-build-app/` ✅ |
| `.claude/skills/profile-pipeline/` | Replaced by `.claude/skills/hl-profile/` ✅ |
| `.claude/skills/contribute-insights/` | Replaced by `.claude/skills/hl-contribute/` ✅ |

## Files Created (Agentic Infrastructure) ✅
| File/Dir | Purpose |
|----------|---------|
| `.hailo/README.md` | Master index of shared knowledge |
| `.hailo/instructions/*` (7) | Architecture & standards |
| `.hailo/toolsets/*` (5) | API references |
| `.hailo/skills/*` (13) | Platform-neutral skill docs |
| `.hailo/knowledge/*` (8) | YAML knowledge bases |
| `.hailo/memory/*` (9) | Persistent cross-session knowledge |
| `.hailo/templates/*` (4) | Scaffold templates |
| `.hailo/examples/**` (11) | Runnable examples |
| `.claude/skills/hl-*/SKILL.md` (7) | Thin Claude Code wrappers |
| `.github/prompts/hl-*.prompt.md` (6) | Copilot prompt files |
| `.cursor/rules` | Cursor entry point |

## Files to Rewrite
| File | Changes |
|------|---------|
| `install.sh` | Rewrite — submodule init, delegate to hailo-apps-infra, community layer setup |
| `setup_env.sh` | Rewrite — align venv, PYTHONPATH, .env loading |
| `config.yaml` | Simplify — local submodule path, remove legacy fields |
| `.gitignore` | Fix conflicts, new patterns |
| `CLAUDE.md` | Rewritten as thin pointer to `.hailo/` ✅ |
| `.github/copilot-instructions.md` | Rewritten as thin pointer to `.hailo/` ✅ |

## Files to Keep As-Is
| File/Dir | Reason |
|----------|--------|
| `community_projects/` | Existing human-contributed projects, still functional |
| `tests/` | Adapted for new structure, but existing test patterns kept |
| `doc/` | Documentation updated but not removed |

---

## Dependencies
- hailo-apps-infra at `/home/giladn/tappas_apps/repos/hailo-apps-infra` (branch: `test/app-builder-20-apps`)
- HailoRT + TAPPAS system packages
- Python 3.x with venv support
- git with submodule support

## Constraints
- Cannot run `sudo` in current dev session
- hailo-apps-infra branch is dev (not yet released)
- Some community app files are untracked in source repo
