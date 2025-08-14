# engineering-memory-bank

**AI-Powered Engineering Decision Documentation System**

An intelligent system for automatically capturing, organizing, and analyzing engineering design decisions with git integration. Transforms scattered documentation into structured knowledge that improves with every project.

## 🚀 Key Features

- **🧠 Automatic Decision Capture**: Git hooks automatically document design decisions
- **🤖 AI-Powered Analysis**: Claude integration for decision insights and recommendations
- **📊 Cross-Project Learning**: Knowledge sharing between projects and teams
- **⏰ Timeline Reconstruction**: Automatic timeline of design decisions
- **🔍 Decision Search**: Find relevant decisions across project history
- **📋 Template System**: Structured documentation templates
- **🔗 Git Integration**: Seamless integration with existing development workflows

## 🆚 vs. Existing Solutions

| Feature | engineering-memory-bank | Traditional Docs | Engineering Notebooks |
|---------|-------------|------------------|----------------------|
| **Automatic Capture** | ✅ Git hooks | ❌ Manual | ❌ Manual |
| **AI Analysis** | ✅ Claude integration | ❌ None | ❌ Limited |
| **Cross-Project** | ✅ Knowledge sharing | ❌ Isolated | ❌ Isolated |
| **Timeline Tracking** | ✅ Automatic | ❌ Manual | ⚠️ Basic |
| **Decision Search** | ✅ Intelligent | ⚠️ Text search | ⚠️ Basic |
| **Version Control** | ✅ Native git | ⚠️ External | ❌ Poor |

## 📦 Installation

```bash
# Install from PyPI (coming soon)
pip install engineering-memory-bank

# Or install from source
git clone https://github.com/circuit-synth/engineering-memory-bank.git
cd engineering-memory-bank
pip install -e .
```

## 🎯 Quick Start

### Initialize in Project

```bash
# Initialize memory-bank in your project
cd my_engineering_project
memory-bank init

# Configure git hooks (automatic)
memory-bank setup-hooks
```

### Automatic Decision Capture

```bash
# Make changes and commit - decisions automatically captured
git add power_supply.py
git commit -m "Switch to buck converter for 90% efficiency vs 60% with linear reg"

# Memory bank automatically captures:
# - What changed (component selection)
# - Why it changed (efficiency improvement)
# - Context (power supply design)
# - Alternatives considered (linear regulator)
```

### Manual Decision Logging

```python
import engineering_memory_bank as emb

# Log design decisions programmatically
bank = emb.MemoryBank.current_project()

bank.log_decision(
    category='component_selection',
    decision='Selected STM32F407 over STM32F405',
    rationale='Need USB OTG and Ethernet for full feature set',
    alternatives=['STM32F405', 'STM32H7 series'],
    impact='high',
    tags=['mcu', 'connectivity', 'performance']
)

# Log test results
bank.log_test_result(
    test='power_consumption',
    result={'idle': '50mA', 'active': '120mA'},
    meets_spec=True,
    notes='Under 150mA budget with margin'
)
```

### AI-Powered Analysis

```python
# Get AI insights on decisions
insights = bank.analyze_decisions()
print(f"Decision confidence: {insights.confidence_score}")
print(f"Potential issues: {insights.risk_factors}")

# Get recommendations for current project
recommendations = bank.get_ai_recommendations()
for rec in recommendations:
    print(f"Recommendation: {rec.suggestion}")
    print(f"Based on: {rec.similar_projects}")

# Cross-project learning
similar = bank.find_similar_decisions(
    'microcontroller selection',
    across_projects=True
)
```

### Decision Management

```python
# Search decision history
power_decisions = bank.search_decisions('power supply')
recent_decisions = bank.get_recent_decisions(days=30)

# Timeline analysis
timeline = bank.get_decision_timeline()
milestones = bank.get_project_milestones()

# Export and reporting
report = bank.generate_decision_report()
bank.export_decisions('project_decisions.json')
```

## 🏗️ Architecture

```
memory-bank/
├── python/                          # Core Python library
│   ├── memory_bank/
│   │   ├── core/                   # Core decision engine
│   │   ├── ai/                     # AI integration (Claude, etc.)
│   │   ├── git/                    # Git hooks and integration
│   │   ├── templates/              # Documentation templates
│   │   ├── analysis/               # Decision analysis
│   │   └── utils/                  # Utilities
│   └── tests/                      # Test suite
├── templates/                      # Project templates
└── examples/                       # Usage examples
```

## 🧪 Use Cases

### **Electronics Design**
- Component selection rationale
- Power supply design decisions  
- Layout and routing choices
- Test results and validation

### **Software Development**
- Architecture decisions
- Library/framework choices
- Performance optimization decisions
- Security design choices

### **Mechanical Engineering**
- Material selection rationale
- Manufacturing process decisions
- Design constraint trade-offs
- Testing and validation results

### **Research Projects**
- Experimental design decisions
- Parameter selection rationale
- Result interpretation
- Future work planning

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

**Built with ❤️ by the Circuit-Synth team**