# 8. CV Approach

When the enricher surfaces a job you like, you want to apply fast. This is how to use Hermes to produce a tailored, ATS-optimized CV in minutes.

## The core principle: one base, many tailored versions

Keep one base CV that reflects everything you've done. For each application, generate a tailored version that emphasizes the skills and experience most relevant to that specific role.

**The workflow:**
1. You (or Hermes) reads the job description
2. Hermes identifies which parts of your background are most relevant
3. It writes a tailored CV that leads with those points
4. Output: a single-page PDF with a filename like `yourname-companyname.pdf`

## CV format that works

A clean single-page HTML/CSS CV converts well to PDF and is fully ATS-readable:

- **A4 format, single page** - never go over one page for tech roles
- **Dark header** with name, role title, contact info
- **Two-column layout** - sidebar (skills, tools, education) + main (experience, projects)
- **No icons, no graphics, no tables** - ATS scanners choke on these
- **Bullet points** - each bullet = one accomplishment, one metric if possible

To generate yours, tell Hermes:

```
Create a tailored CV for me for this job posting: [paste job description]
My base experience is: [paste your background or LinkedIn URL]
Format: single page, A4, HTML/CSS, dark header, 2-col sidebar.
Filename: yourname-companyname.pdf
```

## What to tell Hermes about your experience (once, in memory)

Set this up once so Hermes always knows your background:

```
Save to memory:
My experience (for CV generation):
- [Role] at [Company] (YYYY-YYYY): [key achievements, stack used]
- [Role] at [Company] (YYYY-YYYY): [key achievements, stack used]
Education: [degree if relevant]
Notable: [any standout projects, open source, etc.]
Stack: [your primary languages and tools]
```

## Naming convention

Use a consistent naming format so you can track applications:

```
yourname-companyname.pdf
yourname-companyname-rolename.pdf  (if applying to multiple roles at same company)
```

## Per-company tailoring tips

Tell Hermes to:
- **Match keywords from the job description** - ATS scanners filter on exact terms
- **Reorder bullet points** - most relevant experience first
- **Adjust the summary/title** - use their exact role title, not yours
- **Trim irrelevant experience** - if the role is pure backend, cut the frontend work down

## The "external RAM" trick

For roles where you'll need to discuss architecture in a technical interview, ask Hermes to also generate a **one-page visual cheat sheet** - a high-level diagram of relevant systems you've built, with clear zones and callouts. Print it or keep it on a second screen. It reduces anxiety about blanking on details under pressure.

```
Generate a technical cheat sheet for my interview at [Company]:
- Diagram of [most relevant system I built]
- Key architectural decisions and why
- Hardest problems and how I solved them
Format: HTML, clean, printable, fits one A4 page.
```

---

→ [Next: Troubleshooting](09-troubleshooting.md)
