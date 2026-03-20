# Project State

> Last updated: 2026-03-20

## Todo

### Phase 1: Foundation
- [ ] Add hailo-apps-infra as git submodule
- [ ] Fix `.gitignore` merge conflicts + add new patterns
- [ ] Simplify `config.yaml` (local submodule path, remove legacy fields)
- [ ] Rewrite `install.sh` (submodule init → delegate to hailo-apps-infra → community setup)
- [ ] Rewrite `setup_env.sh` (venv_hailo_apps, PYTHONPATH, .env loading)
- [ ] Remove `basic_pipelines/`
- [ ] Remove `download_resources.sh`
- [ ] Remove `hailo_python_installation.sh`
- [ ] Verify: pip install + imports work

### Phase 3: Port Community Apps & Gesture Detection
- [ ] Copy `community/apps/pipeline_apps/` (16 apps)
- [ ] Copy `community/apps/standalone_apps/` (5 apps)
- [ ] Copy `community/apps/gen_ai_apps/` (2 apps)
- [ ] Copy `community/contributions/`
- [ ] Copy untracked data files + add to `.gitignore`
- [ ] Create gesture_detection_example wrapper
- [ ] Verify: community apps compile, existing community_projects/ still works

### Phase 5: Testing & Documentation
- [ ] Test clean install flow
- [ ] Test imports
- [ ] Test skill path resolution
- [ ] Run test suite
- [ ] Run at least one community app end-to-end
- [ ] Update README.md
- [ ] Update tests/ for new structure

## In Progress
- (none)

## Done
- [x] Explored both repos (structure, install flows, configs)
- [x] Made architectural decisions (submodule, no backward compat, remove basic_pipelines, align venv name)
- [x] Created GSD project plan (roadmap.md, requirements.md, state.md)
- [x] **Agentic Infrastructure Merge (replaces Phase 2 + Phase 4):**
  - [x] Created `.hailo/` as canonical shared knowledge directory
  - [x] Migrated instructions (7 files) from System B → `.hailo/instructions/`
  - [x] Migrated toolsets (5 files) from System B → `.hailo/toolsets/`
  - [x] Migrated knowledge bases (8 files) from System A → `.hailo/knowledge/`
  - [x] Merged knowledge_base.yaml from both systems
  - [x] Merged memory (9 files) from both systems → `.hailo/memory/`
  - [x] Migrated templates (4 files) → `.hailo/templates/`
  - [x] Migrated examples (11 files) → `.hailo/examples/`
  - [x] Created 13 unified skill docs in `.hailo/skills/` (hl- prefix)
  - [x] Created `.hailo/README.md` master index
  - [x] Created 7 thin Claude Code SKILL.md wrappers in `.claude/skills/hl-*/`
  - [x] Moved scripts to new skill dirs (hl-build-app, hl-profile)
  - [x] Rewrote `CLAUDE.md` as thin pointer to `.hailo/`
  - [x] Created `.cursor/rules` as thin pointer to `.hailo/`
  - [x] Rewrote `.github/copilot-instructions.md` as thin pointer to `.hailo/`
  - [x] Created 6 hl-prefixed Copilot prompts in `.github/prompts/`
  - [x] Set `.claude/memory/MEMORY.md` as redirect to `.hailo/memory/`
  - [x] Removed old `.claude/skills/{app-builder,profile-pipeline,contribute-insights}/`
  - [x] Removed `.github/.github/` entirely (all content migrated)

## Blocked
- [ ] sudo install.sh testing — no sudo access in current session

## Notes
- No backward compatibility required — clean restructure
- `basic_pipelines/` removed; official apps accessed via hailo-apps-infra entry points
- Venv renamed from `venv_hailo_rpi_examples` to `venv_hailo_apps`
- Legacy install scripts removed (download_resources.sh, hailo_python_installation.sh)
- Agentic infrastructure is now cross-platform: Claude Code + Copilot + Cursor
- All skills use `hl-` prefix for consistency
- Shared knowledge lives in `.hailo/` (platform-neutral); platform-specific entry points are thin wrappers
