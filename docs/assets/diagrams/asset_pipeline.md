# Asset production pipeline

```mermaid
flowchart LR
  A[Spec + sources] --> B[Technical blockout]
  B --> C[LOW]
  C --> D[MID]
  D --> E[HIGH where justified]
  E --> F[UV + Bake]
  F --> G[Master materials]
  G --> H[Runtime materials]
  H --> I[LOD0/1/2]
  I --> J[GLB + collision]
  J --> K[Blender/runtime QA]
  K --> L[Visual approval]
```
