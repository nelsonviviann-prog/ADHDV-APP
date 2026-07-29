# Images

Drop image files here. They are **optional** - the app renders fine without
them and picks them up automatically on the next rerun. No code change needed.

Filenames must match **exactly** (extension can be `.png`, `.jpg`, `.jpeg`, or
`.webp`):

| Filename           | Where it appears              | Recommended size |
|--------------------|-------------------------------|------------------|
| `hero_children`    | Home page, under the banner   | 1600 × 600 (wide) |
| `role_parent`      | Home page, Parent role card   | 800 × 500 |
| `role_teacher`     | Home page, Teacher role card  | 800 × 500 |
| `role_clinician`   | Home page, Clinician role card| 800 × 500 |

## Rules

- **Keep files under ~300 KB.** They are inlined as base64 into the page, so a
  large file directly slows the app down for every visitor - and the app is
  meant to work on low-bandwidth connections.
- **Use AI-generated or properly licensed images only.** Do not use photographs
  of real, identifiable children. Beyond the licensing problem, a screening tool
  for a stigmatised condition must never imply that a real, named child was
  screened for ADHD.
- Images are cropped with `object-fit: cover`, so keep the subject centred - 
  the edges will be trimmed.
