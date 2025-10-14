# CLAUDE.md

Instructions for Claude Code (claude.ai/code) when working with StartupStack.

---

## Project Overview

**StartupStack** is a velocity-first AI agent platform for shipping production SaaS MVPs in 2-4 hours. Optimized for startup speed with:
- **12 focused agents** (not 73)
- **8 fast-track commands** (not 68)
- **SvelteKit + self-hosted stack** (no vendor lock-in)
- **$10-20/month hosting** (not $110+)

---

## Core Philosophy

### Ship Fast, Iterate Faster
- **70% perfect and live** > 95% perfect and stuck
- **Working MVPs today** > Perfect products someday
- **Real features** > Comprehensive documentation

### Zero Vendor Lock-In
- Self-hosted PostgreSQL (not Supabase)
- Generic VPS (not Vercel)
- Custom OAuth (not Clerk)
- Backblaze B2 (not Vercel Blob)

### Ruthless Prioritization
- **ONE core feature** for launch
- Defer admin dashboards, settings, team features
- Ship at 70%, iterate to 95%

---

## Agent Selection (12 Agents)

### When User Says: "Build an MVP" or "Ship a SaaS product"
**Use**: `mvp-builder`
- Ships complete MVPs in 2-4 hours
- SvelteKit + PostgreSQL + OAuth + Stripe
- Deployed on VPS with HTTPS
- The cornerstone agent

### When User Says: "Validate my idea" or "Test market demand"
**Use**: `the-validator`
- Market validation experiments
- A/B testing strategy
- Not product perfection

### When User Says: "Deploy" or "Go live" or "Ship now"
**Use**: `the-shipper`
- Deploy-first mentality
- Fix bugs post-launch
- SHIP bias embedded

### When User Says: "Growth" or "Metrics" or "Experiments"
**Use**: `growth-hacker`
- Analytics setup
- A/B testing
- Viral loops
- NOT 6 separate SEO agents

### When User Says: "SvelteKit" or "Frontend" or "UI"
**Use**: `svelte-architect`
- SvelteKit specialist
- Server Actions
- Form actions
- NOT React/Next.js

### When User Says: "API" or "Backend" or "Endpoints"
**Use**: `api-builder`
- Start with SvelteKit server routes
- Add tRPC-sveltekit when type safety hurts
- NOT tRPC from day 1

### When User Says: "Database" or "PostgreSQL" or "Schema"
**Use**: `postgres-pro`
- Self-hosted PostgreSQL
- Drizzle ORM
- Migrations
- NOT Supabase

### When User Says: "AI" or "OpenAI" or "RAG" or "Vector database"
**Use**: `ai-integrator`
- OpenAI integration
- pgvector for semantic search
- Ship AI features in hours

### When User Says: "Bug" or "Debug" or "Fix" or "Error"
**Use**: `bug-destroyer`
- Fast debugging
- No ceremony
- Ship fixes quickly

### When User Says: "Auth" or "OAuth" or "Login" or "Sign in"
**Use**: `auth-engineer`
- OAuth (Apple, Google, Microsoft, LinkedIn)
- JWT sessions
- NO email/password (too complex)

### When User Says: "Performance" or "Slow" or "Optimize"
**Use**: `perf-optimizer`
- Core Web Vitals only
- Fix top 3 bottlenecks
- Ship fast, optimize later

### When User Says: "Launch" or "Production" or "Ready" or "Checklist"
**Use**: `launch-reviewer`
- 1-hour pre-launch checklist
- NOT 3-agent comprehensive review

---

## Command Selection (8 Commands)

### MVP Commands (2-4 hours)
- `/saas-mvp-2h` - Complete MVP: OAuth → Landing → Feature → Deploy
- `/marketplace-mvp` - Two-sided marketplace in 3 hours
- `/ai-feature-mvp` - Add AI to existing app in 2 hours

### Growth Commands
- `/launch-checklist` - Pre-launch validation (1 hour)
- `/growth-experiment` - A/B test in 90 minutes
- `/metrics-dashboard` - Analytics in 1 hour

### Technical Debt
- `/perf-quick-win` - Fix top 3 bottlenecks (2 hours)
- `/bug-triage` - Sentry + prioritize (90 minutes)

---

## Tech Stack (Non-Negotiable)

### Frontend
- **Framework**: SvelteKit (ONLY SvelteKit, not React/Next.js)
- **Styling**: Tailwind CSS + shadcn-svelte
- **State**: Svelte stores + page data
- **Forms**: SvelteKit form actions (native)

### Backend
- **API**: SvelteKit server routes (start here)
- **Type Safety**: Add tRPC-sveltekit when REST hurts
- **Database**: Self-hosted PostgreSQL in Docker
- **ORM**: Drizzle ORM (type-safe, SQL-first)

### Auth
- **OAuth**: Apple, Google, Microsoft, LinkedIn
- **Sessions**: JWT + HTTP-only cookies
- **NO email/password** - Skip this complexity

### Infrastructure
- **Hosting**: Hetzner ($5), DigitalOcean ($6), Linode ($5)
- **Containers**: Docker + Docker Compose
- **Proxy**: Caddy (automatic HTTPS)
- **Database**: PostgreSQL 16 in Docker
- **Storage**: Backblaze B2 or Wasabi ($5/month)
- **Email**: SendGrid/Mailgun/Postmark (pay-as-you-go)
- **Payments**: Stripe (webhooks + subscriptions)
- **Analytics**: Plausible (self-hosted) or PostHog
- **Errors**: Sentry (free tier) or GlitchTip
- **Monitoring**: Uptime Kuma (self-hosted)

### Monthly Cost: $10-20
*(vs $110+ with Vercel + Supabase + Clerk)*

---

## What to NEVER Recommend

### ❌ Vendor Lock-In Services
- **NO Vercel** - Expensive, lock-in
- **NO Supabase** - Self-hosted PostgreSQL is free
- **NO Clerk** - OAuth is straightforward
- **NO Auth0** - Enterprise pricing
- **NO PlanetScale** - MySQL when we need PostgreSQL
- **NO Firebase** - Google lock-in

### ❌ Premature Optimization
- **NO microservices** - Monolith first
- **NO Redis** - PostgreSQL is fast enough for MVP
- **NO CDN** - VPS bandwidth is enough
- **NO load balancing** - One server handles thousands
- **NO message queues** - Background jobs can wait

### ❌ Enterprise Patterns
- **NO comprehensive testing** - Manual testing for MVP
- **NO multi-tier review** - Ship and iterate
- **NO SOC 2 compliance** - Not for MVP
- **NO audit trails** - Add post-launch if needed

### ❌ Feature Bloat
- **NO admin dashboard** - Use database tool
- **NO user settings page** - Add when users ask
- **NO team features** - Single user first
- **NO webhooks** (except Stripe - required)
- **NO API for third-parties** - Build when needed
- **NO dark mode** - Nice to have, not required

---

## MVP Success Criteria

### Must Work
1. **User can sign up** - OAuth flow completes
2. **User can pay** - Stripe checkout works
3. **User can use core feature** - Product works
4. **User can see their data** - Dashboard shows stuff
5. **Webhooks process** - Subscription updates work
6. **Emails send** - Welcome and receipts arrive
7. **HTTPS works** - No browser warnings
8. **Errors track** - Sentry catches exceptions

### Can Be Rough
- Ugly UI (functional > beautiful)
- Missing edge cases (fix when reported)
- Basic mobile (works, not optimized)
- Minimal docs (just enough)
- No comprehensive tests (manual is enough)

---

## Time Estimates

All estimates assume StartupStack agents, not enterprise approach:

### MVPs (2-4 hours)
- Simple SaaS: 2 hours
- Marketplace: 3 hours
- AI-powered: 2.5 hours

### Features (30 minutes - 2 hours)
- Stripe integration: 30 minutes
- OAuth provider: 20 minutes
- Landing page: 20 minutes
- Dashboard: 20 minutes
- Core feature (simple): 20-40 minutes

### Quality (1-2 hours)
- Launch checklist: 1 hour
- Performance fixes: 2 hours
- Bug triage: 90 minutes
- A/B test: 90 minutes

---

## Common User Requests

### "Build me a SaaS product"
→ Use `mvp-builder` with `/saas-mvp-2h` command
→ 2-4 hours total
→ Deployed on VPS with HTTPS

### "Add payments to my app"
→ Use `mvp-builder` (Stripe is built-in)
→ 30 minutes
→ Webhooks working

### "I need authentication"
→ Use `auth-engineer`
→ OAuth (pick 2 providers)
→ 30-40 minutes
→ NO email/password

### "My app is slow"
→ Use `perf-optimizer`
→ Fix top 3 bottlenecks
→ 2 hours
→ NOT comprehensive optimization

### "Ready to launch?"
→ Use `launch-reviewer` with `/launch-checklist`
→ 1 hour checklist
→ NOT 3-agent review

### "Add AI features"
→ Use `ai-integrator` with `/ai-feature-mvp`
→ OpenAI + pgvector
→ 2 hours

### "A/B test an idea"
→ Use `growth-hacker` with `/growth-experiment`
→ 90 minutes
→ PostHog or Plausible

---

## Directory Structure

```
startup-stack/
├── README.md                    # Project overview
├── CLAUDE.md                    # This file
├── agents/                      # 12 core agents
│   ├── mvp-builder.md           # Cornerstone agent
│   ├── the-validator.md
│   ├── the-shipper.md
│   ├── growth-hacker.md
│   ├── svelte-architect.md
│   ├── api-builder.md
│   ├── postgres-pro.md
│   ├── ai-integrator.md
│   ├── bug-destroyer.md
│   ├── auth-engineer.md
│   ├── perf-optimizer.md
│   └── launch-reviewer.md
├── commands/                    # 8 fast-track commands
│   ├── saas-mvp-2h.md
│   ├── marketplace-mvp.md
│   ├── ai-feature-mvp.md
│   ├── launch-checklist.md
│   ├── growth-experiment.md
│   ├── metrics-dashboard.md
│   ├── perf-quick-win.md
│   └── bug-triage.md
├── templates/                   # SvelteKit starters
│   └── sveltekit-starter/       # Full template with OAuth + Stripe
└── examples/                    # 3 deployed MVPs
    ├── todo-saas/               # Real deployment
    ├── marketplace-tutors/      # Real deployment
    └── ai-doc-qa/               # Real deployment
```

---

## Key Differences from Enterprise Platforms

| Aspect | Enterprise | StartupStack |
|--------|-----------|--------------|
| **Agents** | 73 agents | 12 agents |
| **Commands** | 68 commands | 8 commands |
| **Documentation** | 7.3MB, 52 files | 1 README, 5 min read |
| **MVP Time** | 8-12 hours | 2-4 hours |
| **Tech Stack** | Multiple options | Opinionated (SvelteKit) |
| **Hosting** | Vercel $110+/mo | VPS $10-20/mo |
| **Auth** | Clerk $25+/mo | Custom OAuth $0 |
| **Database** | Supabase $25+/mo | PostgreSQL $0 |
| **Code Review** | 3 agents, 4 phases | 1 agent, 1 phase |
| **Philosophy** | Perfect | Good enough shipped |

---

## Agent Coordination

### Single Agent Tasks
- Most tasks use ONE agent
- NO multi-agent orchestration for MVPs
- Keep it simple

### When to Use Multiple Agents
- `mvp-builder` → `svelte-architect` (complex UI)
- `mvp-builder` → `auth-engineer` (4+ OAuth providers)
- `mvp-builder` → `ai-integrator` (AI features)
- `perf-optimizer` → `postgres-pro` (database bottlenecks)

### When NOT to Use Multiple Agents
- ❌ Don't chain review agents (no the-critic, the-realist, the-pragmatist)
- ❌ Don't use project-orchestrator (too heavy for MVPs)
- ❌ Don't use multiple quality agents (one is enough)

---

## Git Workflow

```bash
# Main branch
master

# Feature branches
claude/feature-name

# Commit style
Ship working MVP with OAuth + Stripe + PostgreSQL

Deployed on Hetzner $5/month VPS with Caddy HTTPS.
Users can sign up (Google OAuth), pay (Stripe), and use core feature.

Total time: 2 hours
Monthly cost: $15
```

---

## Success Metrics

### Velocity
- ✅ MVP deployed: <4 hours
- ✅ Add Stripe: <30 minutes
- ✅ Add OAuth: <20 minutes
- ✅ Fix bug: <15 minutes
- ✅ Ship A/B test: <90 minutes

### Cost
- ✅ Monthly hosting: <$20
- ✅ Year 1 savings: ~$1,100 (vs vendor stack)
- ✅ No usage surprises (fixed costs)

### Quality
- ✅ Lighthouse score: >90
- ✅ Core feature works: 100%
- ✅ Can be rough: UI, edge cases, mobile

---

## Remember

**StartupStack is for founders who ship, not founders who plan.**

- **Ship at 70%** - Perfect is the enemy of done
- **Iterate fast** - User feedback > Internal debates
- **Control costs** - $10-20/month, not $110+
- **Stay simple** - Monolith > Microservices
- **Own your stack** - VPS > Vendor lock-in

**When in doubt, ship it.**
