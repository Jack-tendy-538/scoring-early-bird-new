# score_early_bird

> Translated from: [README.md](README.md) by Baidu Translate


This is a desktop habit tracking and check-in incentive tool specifically designed for **individuals or small teams**. Through automated point rewards and scheduled reminders, it transforms tedious repetitive behaviors into an engaging growth game, helping you effortlessly establish and maintain good habits.
-----
### **What pain points does it address?**

1. **Lack of Motivation, Hard to Stay Consistent**: Relying solely on willpower for habit tracking often leads to giving up halfway. This project introduces a **gamified points system**, offering visible rewards for continuous check-ins and providing sustained positive feedback.
2. **Prone to forgetting, lacks reminders**: You often forget to clock in when busy. The tool features **smart scheduled reminders**, popping up windows at preset times to ensure you never miss a record.
3. **Disjointed Records, Inconvenient for Review**: Manual entries are scattered across various locations, making it difficult to summarize. The program can automatically generate **clear and aesthetically pleasing Markdown-formatted weekly/monthly reports**, allowing you to effortlessly review your progress.
4. **Tool Bloat and Complex Settings**: Many habit-tracking apps offer numerous features that are rarely used. This tool is **extremely lightweight and highly configurable**, allowing users to customize all rules with just a simple YAML configuration file—no complex operations required

-----
### **Technology Stack Used**

```Core Development Language: `Python 3` - Ensures excellent cross-platform compatibility and robust library support.```.
* **Graphical User Interface (GUI)**: `Tkinter` + `ttkbootstrap` - Utilizing Python's standard GUI library paired with modern themes to create a clean desktop interface resembling Windows 11 style, capable of running without a browser.
* **Configuration Management**: `YAML` - Uses a human-readable configuration file format, allowing easy modification of all rules (such as points, reminder times, and display settings) without altering the code.

### **Core Supported Features**

1. **Configurable Points System**:
    * Support setting reward points for different continuous check-in cycles (e.g., 3 days, 7 days) to encourage long-term persistence.
2. **Smart Timed Reminders**:
    *   It can be freely turned on/off, with precise settings for morning and afternoon reminders to prevent forgetting.
3. **Personalized Name List**:
    * Allow users to customize fun "nicknames" for check-in items, enhancing the enjoyment and sense of belonging in the check-in process.
4. **Data Visualization Output**:
    * Automatically generates punch-in data into beautifully formatted Markdown table documents for easy sharing, printing, or archiving.
5. **One-stop Configuration Management**
    * Provides a graphical configuration window for centralized management of points rules, reminder times, interface fonts, output formats, and more.


---

### **Typical Applicable Scenarios**

* **Student Self-Management**: Used to record daily morning routines, vocabulary memorization, and exercise check-ins, motivating oneself through point rewards.
* **Team Goal Co-Creation**: Within small teams or study groups, used to synchronize and track project progress, daily learning check-ins, and automatically generate weekly team check-in reports.
**Habit Formation**: Whether you aim to cultivate daily reading, drinking water, or handwriting practice habits, or seek to break certain unhealthy habits, this tool enables visual self-monitoring.
* **Lightweight Data Logging**: Replaces paper or basic Excel spreadsheets for scenarios requiring regular, repetitive data recording and the desire for automated statistical views.

In summary, `score_early_bird` functions like a quiet and reliable digital companion. Lacking complex social features, it focuses on addressing two core issues—"consistent tracking" and "motivation"—and through high customization, becomes a lightweight management tool that truly aligns with your personal habits.

---

## On AI-Generated Content and Copyright

Most of the content in this project was generated with the assistance of AI tools (such as GitHub Copilot and DeepSeek).

Current laws have yet to establish a definitive conclusion on the copyright ownership of AI-generated content. This project is licensed under the MIT License, based on the creative efforts of the project maintainers in areas such as prompt engineering, content curation, code integration, and modification.

### Requirements for Contributors

When submitting contributions to this project, you must ensure:
1. Your contribution is your own original work, or;
2. You have clearly disclosed the source of the AI-generated portion and confirmed its license compatibility with this project.

3. You agree that your contributions will also be licensed under the MIT License.
