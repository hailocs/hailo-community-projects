# How to Contribute

This guide covers all the ways to contribute to Hailo Community Projects — from building new apps to sharing optimization insights.

---

## Building New Apps

### Option 1: AI-Assisted (Recommended)

Use the agentic development tools to build apps through guided conversation:

**Claude Code:**
```
/hl-build-app                    # Interactive 7-phase workflow
/hl-build-app parking monitor    # Start with a use case description
/hl-build-app from detection     # Start from an existing template
```

**VS Code Copilot:**
Use the prompt templates in `.github/prompts/`:
- `hl-build-vlm-app.prompt.md` — VLM application
- `hl-build-pipeline-app.prompt.md` — GStreamer pipeline app
- `hl-build-agent-app.prompt.md` — Agent with tool calling
- `hl-orchestrated-build.prompt.md` — Universal orchestrated build

**Any AI Agent:**
Read the skill docs in `.hailo/skills/` directly. Start with `hl-build-app.md`.

New apps are scaffolded automatically in `community/apps/<type>_apps/<your_app>/`.

### Option 2: Manual

1. **Set up your environment:**
   ```bash
   source setup_env.sh
   ```

2. **Choose a template app** from `hailo-apps-infra/hailo_apps/python/pipeline_apps/` (or `standalone_apps/` or `gen_ai_apps/`)

3. **Create your app directory:**
   ```bash
   mkdir -p community/apps/pipeline_apps/<your_app>
   ```

4. **Create the required files:**
   - `__init__.py`
   - `<your_app>.py` — Callback + main entry point
   - `<your_app>_pipeline.py` — GStreamerApp subclass (for pipeline apps)
   - `README.md` — Documentation

5. **Follow the framework conventions:**
   - Use absolute imports: `from hailo_apps.python.core...`
   - Use `resolve_hef_path()` for model paths
   - Use `get_pipeline_parser()` / `get_standalone_parser()` for CLI
   - Keep callbacks non-blocking

See the [Development Guide](basic-pipelines.md) for more details.

---

## Sharing Optimization Insights

If you discover something useful while building or profiling an app — a configuration tweak, a bottleneck fix, a non-obvious pattern — share it with the community.

### AI-Assisted
```
/hl-contribute                   # Interactive contribution workflow
```
The agent formats your finding, scrubs sensitive data, and creates a PR with your name as contributor.

### Manual
1. Create a `.md` file following the [contribution format](../community/contributions/README.md)
2. Place it in `community/contributions/<category>/`
3. Submit a PR targeting `dev`

---

## Contributing Legacy Community Projects

For standalone projects that don't fit the `community/apps/` structure (games, robots, creative demos):

1. Create a directory under `community_projects/<your_project>/`
2. Include a `README.md` with description, requirements, and setup instructions
3. Keep all code within your project directory

**Important:**
- PRs modifying core framework code will be rejected — keep changes in your directory
- Do not add binary files (images, HEFs, videos) to the repo — host them externally and provide a download script
- Use a `download_resources.sh` script to fetch external resources

---

## Adding New Networks and Post-Processes

1. Save your HEF file on a file-sharing service (Google Drive, etc.)
2. Provide a `download_resources.sh` script to automate the download
3. For custom post-processing:
   - Add the code and a compilation script
   - See [hailo-apps-infra](https://github.com/hailo-ai/hailo-apps-infra) for guidance on creating and compiling post-processes

---

## Pull Requests

1. Submit PRs to the **`dev` branch**
2. Keep your code within your project directory (`community/apps/` or `community_projects/`)
3. PRs that modify core framework code will be rejected — suggest improvements via issues instead

Suggestions for improving the core framework are welcome. However, they must be generic, well-tested, and adaptable to multiple platforms. If you identify missing functionality, implement it in your directory first — exceptional features may be integrated into the core.

---

## Code of Conduct

We are committed to fostering a welcoming and inclusive community:
- Use clean and non-offensive language
- Be respectful and considerate of others
- Avoid any form of harassment or discrimination
