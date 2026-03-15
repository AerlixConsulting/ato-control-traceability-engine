# Assets

<!-- SPDX-License-Identifier: Apache-2.0 -->

This directory contains visual assets used in documentation.

## Contents

| Asset | Description |
|---|---|
| _(diagrams are generated as Mermaid in `architecture/`)_ | Architecture diagrams are Mermaid-native in Markdown |

## Generating PNG/SVG Exports

To export Mermaid diagrams to image files for formal documentation packages,
install the [Mermaid CLI](https://github.com/mermaid-js/mermaid-cli):

```bash
npm install -g @mermaid-js/mermaid-cli

# Export system context diagram
mmdc -i architecture/system-context.md -o assets/system-context.png

# Export data flow diagram
mmdc -i architecture/data-flow.md -o assets/data-flow.png

# Export traceability graph
mmdc -i examples/traceability_graph.mmd -o assets/traceability-graph.png
```
