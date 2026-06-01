# doc2plugin

🤖 **AI Agent Powered Infrastructure-as-Code (IaC) Tool**

Automatically convert deployment documentation into executable scripts.

## ✨ Features

* 🧠 **Intelligent Understanding**: Document analysis powered by Large Language Models (LLMs).
* 🔧 **Automated Generation**: One-click transformation from documentation to scripts.
* 📖 **Documentation-Driven**: Supports multiple output formats including Shell and oeDeploy.
* 🔄 **Flexible Adaptation**: Supports both document-driven and document-free scenarios.
* 📋 **Precise Constraints**: Ensures multi-file project consistency through file manifests and detailed implementation plans.
* 🎯 **Structured Prompting**: Unified message construction that prioritizes deployment documentation in the `SystemMessage`.
* 🔒 **Strict JSON Formatting**: Enforces JSON formatting for all LLM outputs to improve parsing reliability.
* 🔀 **Isolated Operations**: Complete separation of `compose`, `test`, and `modify` workflows, each loading its own context-specific documents and prompts.

## 🚀 Quick Start

### Installation

```bash
git clone <repository-url>
cd doc2plugin
pip install -r requirements.txt
pip install -e .
doc2plugin --version

```

### Workflow

**1. Initialize Project**

```bash
doc2plugin init

```

**2. Prepare Documentation (Optional)**

Place your deployment documentation in the `doc/` directory. If no documentation is provided, the system will generate scripts based on the task description.

```bash
cp your-docs/* doc/

```

**3. Configure Task**

Edit `work.yaml` to configure the LLM and task specifications:

```yaml
llm_info:
  base_url: 'https://api.deepseek.com/v1'
  api_key: 'your-api-key'
  model_name: 'deepseek-chat'
  temperature: 0.1

task:
  target: 'Generate Nginx deployment script based on documentation'
  prompt: 'Target environment is openEuler with sudo privileges'
  mode: 'shell'  # shell or oedp

```

**4. Generate Scripts**

```bash
doc2plugin compose

```

Generated scripts will be located in the `plugin/` directory.

**5. Test Scripts (Optional)**

```bash
doc2plugin test

```

This automatically generates a test script at `cache/test.sh` and executes it, routing test logs to `cache/test.log`. If both files already exist, the generation step is skipped to allow iterative testing and modification.

**6. Modify Code (Optional)**

```bash
doc2plugin modify

```

If the tests fail, run this command to automatically modify the code or test scripts based on the test results.

## 🔧 Commands

| Command | Description |
| --- | --- |
| `doc2plugin init` | Initialize project directories and configuration files. |
| `doc2plugin compose` | Analyze documentation and generate scripts. |
| `doc2plugin test` | Test the generated code. (Skips test script generation if both `test.sh` and `test.log` exist, to support an iterative test/optimize cycle.) |
| `doc2plugin modify` | Modify code based on test execution results. |
| `doc2plugin status` | Check current project status. |
| `doc2plugin clean [-f]` | Clean up generated files (`-f` to skip confirmation). |

## ⚙️ Configuration

### LLM Configuration (`llm_info`)

| Parameter | Description | Default |
| --- | --- | --- |
| `base_url` | API service endpoint | - |
| `api_key` | API authorization key | - |
| `model_name` | Model identifier | - |
| `timeout` | Request timeout (seconds) | 600 |
| `temperature` | Sampling temperature (0.0-2.0) | 0.1 |
| `max_tokens` | Maximum token limit | null |

Supports OpenAI API, Azure OpenAI, SiliconFlow, Zhipu AI, and other compatible services.

### Task Configuration (`task`)

| Parameter | Description | Example |
| --- | --- | --- |
| `target` | Task goal/objective | `Generate Nginx deployment script based on documentation` |
| `prompt` | Environmental constraints and requirements | `openEuler system, sudo privileges` |
| `mode` | Output target format | `shell` or `oedp` |

## 📖 Examples

### Example 1: Document-Driven Shell Script Generation

Place the Nginx deployment documentation into the `doc/` directory, then configure:

```yaml
task:
  target: 'Generate Nginx deployment script supporting install and uninstall actions'
  prompt: 'openEuler system, sudo privileges'
  mode: 'shell'

```

Output: `plugin/deploy.sh`, `plugin/readme.md`

### Example 2: Document-Free Script Generation

When the `doc/` directory is empty, provide detailed requirements directly in the task description:

```yaml
task:
  target: 'Write an Nginx installation script supporting install, start, and uninstall actions'
  prompt: 'openEuler system, yum package manager, sudo privileges, port 80'
  mode: 'shell'

```

### Example 3: oeDeploy Plugin Generation

```yaml
task:
  target: 'Create an oeDeploy plugin for Nginx'
  prompt: 'openEuler system, single-node deployment'
  mode: 'oedp'

```

Output: Full plugin directory structure (`main.yaml`, `config.yaml`, playbooks, etc.).

### Example 4: Testing Generated Code

```bash
# First, generate the code
doc2plugin compose

# Next, run tests
doc2plugin test

```

The system automatically generates and executes a test script to validate functionality. If `test.sh` and `test.log` both exist, script generation is skipped to support seamless, iterative testing and modification.

### Example 5: Code Modification

```bash
# If tests fail, run the modification workflow
doc2plugin modify

# Re-test after modifications
doc2plugin test

```

The system analyzes the test logs, automatically rectifies issues in the code or test scripts, and allows you to re-test immediately.

## 🏗️ Extending with New Modes

Add new generation modes in 3 steps without modifying the core codebase:

1. **Add Documentation**: Create `doc/YourMode.md` and `doc/YourModeTest.md`.
2. **Configure Mode**: Edit `config/modes.yaml`.
3. **Apply Mode**: Set `mode: 'your_mode'` inside `work.yaml`.

## 🐛 Troubleshooting

### Diagnostics

**Check Project Status**

```bash
doc2plugin status  # Checks project status and configurations

```

**View Logs**

```bash
cat cache/agent.log  # System execution logs, terminal outputs, and token stats
cat cache/llm.log    # Full LLM interaction history (untruncated inputs/outputs, detailed token metrics)

```

Token consumption per LLM call is automatically logged to simplify cost tracking and optimization.

### FAQ

| Issue | Resolution |
| --- | --- |
| Configuration Error | Verify that the API key and service endpoint in `work.yaml` are correct. |
| Incomplete Generation | Provide more detailed requirement descriptions in the `target` and `prompt` fields. |
| Missing Document Warning | The system supports document-free operations. Elaborate your requirements thoroughly in the task configuration. |
| LLM Call Failed | Check network connectivity, API quota/balances, and model name accuracy. |
| Invalid Project Structure | Run `doc2plugin status`. Any missing directories will be generated automatically. |
