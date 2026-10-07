# Semantic Versioning & Migration Policy — Project Intelligence

## 1. Scope of Versioning
The Project Intelligence framework versioning applies to:
- Core Schemas (`core/schemas/*.schema.json`)
- Contracts (`contracts/**/*.json`)
- Memory Structures (`memory/schemas/*.json`)
- Lifecycle Gates & Transitions (`core/lifecycle/*.json`)
- Skill Definitions (`skills/**/SKILL.md`)
- Platform Adapters (`adapters/**/*`)

## 2. Version Number Format
All entities follow strict Semantic Versioning 2.0.0 (`MAJOR.MINOR.PATCH`):
- **MAJOR (`X.0.0`)**: Incompatible API or contract changes, breaking field removals, mandatory new fields without defaults, or altered lifecycle gate sequences.
- **MINOR (`0.Y.0`)**: Backwards-compatible additions (e.g. optional fields in contracts, new non-breaking quality profile attributes, new optional skills).
- **PATCH (`0.0.Z`)**: Backwards-compatible bug fixes, documentation clarifications, and test fixture updates.

## 3. Contract Schema Evolution Rules
1. **Never Remove Required Fields in Minor Releases**: A field marked `required` in version `1.0.0` must remain recognized in all `1.x.x` releases.
2. **Deprecation Window**: Deprecated fields must be annotated with `"deprecated": true` for at least one minor release cycle before removal in a major version bump.
3. **Migration Transformers**: Any major schema transition must provide an automated migration transform script in `core/versioning/` to migrate existing contracts and memory states.
