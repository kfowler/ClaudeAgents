# StartupStack

**Ship SaaS MVPs in 2-4 hours. Not 2-4 weeks.**

StartupStack is a velocity-first AI agent platform for building and deploying production SaaS products same-day. SvelteKit + self-hosted PostgreSQL + OAuth. Zero vendor lock-in. $10-20/month hosting (not $110+).

---

## Why StartupStack?

### The Problem
Most development platforms optimize for enterprise complexity:
- 73+ specialized agents (choice paralysis)
- 8-12 hour MVP workflows (too slow)
- Vendor lock-in (Vercel $110+/month)
- Perfectionism embedded (multiple review agents, comprehensive testing)
- Over-engineered solutions (microservices for MVPs)

### The Solution
StartupStack optimizes for startup velocity:
- **12 focused agents** - Zero cognitive overload
- **2-4 hour MVPs** - Ship today, iterate tomorrow
- **Self-hosted** - $10-20/month VPS (Hetzner, DigitalOcean, Linode)
- **Good enough shipped** - 70% perfect and live beats 95% perfect and stuck
- **Monolith first** - Split when it hurts, not before

---

## Quick Start

### 1. Build Your First MVP (2 Hours)

```bash
# Use mvp-builder to ship a working SaaS product
@mvp-builder "Build a todo app with OAuth + Stripe subscriptions"

# 2 hours later: Deployed on Hetzner, users can sign up and pay
```

**What you get**:
- ✅ Landing page with pricing
- ✅ OAuth sign-in (Google + Apple)
- ✅ Core feature working (todo CRUD)
- ✅ Stripe checkout + webhooks
- ✅ PostgreSQL in Docker
- ✅ Deployed with HTTPS
- ✅ $15/month hosting cost

### 2. Fast-Track Commands

Ship complete features in hours, not days:

```bash
# Add payments to existing app (30 minutes)
/stripe-integration

# Launch checklist before going live (1 hour)
/launch-checklist

# Fix top performance issues (2 hours)
/perf-quick-win

# Deploy A/B test (90 minutes)
/growth-experiment
```

---

## The Stack (Non-Negotiable)

### Frontend
- **SvelteKit** - Fast, simple, productive
- **Tailwind CSS** - Utility-first styling
- **shadcn-svelte** - Beautiful components

### Backend
- **SvelteKit server routes** - Start simple
- **tRPC-sveltekit** - Add when type safety hurts
- **Drizzle ORM** - Type-safe SQL
- **PostgreSQL** - Self-hosted in Docker

### Auth
- **OAuth** - Apple, Google, Microsoft, LinkedIn
- **JWT sessions** - HTTP-only cookies
- **NO email/password** - Too much complexity

### Infrastructure
- **VPS** - Hetzner ($5), DigitalOcean ($6), Linode ($5)
- **Docker + Caddy** - Automatic HTTPS
- **Backblaze B2** - S3-compatible storage ($5/month)

### Cost: $10-20/month
*(vs $110+ with Vercel + Supabase + Clerk)*

---

## 12 Core Agents

### Tier 1: Product & Execution
1. **mvp-builder** - Ship MVPs in 2-4 hours (SvelteKit + PostgreSQL + OAuth)
2. **the-validator** - Market validation experiments (not product perfection)
3. **the-shipper** - Deploy now, fix later (SHIP bias)
4. **growth-hacker** - Metrics, experiments, viral loops

### Tier 2: Core Development
5. **svelte-architect** - SvelteKit apps (Server Actions, forms, routing)
6. **api-builder** - REST first, tRPC when needed
7. **postgres-pro** - Self-hosted PostgreSQL (migrations, optimization)
8. **ai-integrator** - OpenAI + RAG (ship AI in hours)

### Tier 3: Quality & Scale
9. **bug-destroyer** - Fix bugs fast, no ceremony
10. **auth-engineer** - OAuth flows (4 providers) + JWT sessions
11. **perf-optimizer** - Core Web Vitals only
12. **launch-reviewer** - 1-hour pre-launch checklist

---

## 8 Fast-Track Commands

### MVP Commands (2-4 hours)
- **/saas-mvp-2h** - OAuth → Landing → Feature → Deploy (2 hours)
- **/marketplace-mvp** - Two-sided marketplace (3 hours)
- **/ai-feature-mvp** - Add AI to existing app (2 hours)

### Growth Commands
- **/launch-checklist** - Pre-launch validation (1 hour)
- **/growth-experiment** - A/B test in 90 minutes
- **/metrics-dashboard** - Analytics setup (1 hour)

### Technical Debt
- **/perf-quick-win** - Fix top 3 bottlenecks (2 hours)
- **/bug-triage** - Sentry + prioritize bugs (90 minutes)

---

## Philosophy

### Ship Fast, Iterate Faster
- **70% perfect and live** > 95% perfect and stuck
- **Real users today** > Perfect features someday
- **Working code** > Comprehensive documentation

### Zero Vendor Lock-In
- **NO Vercel** - Expensive, lock-in
- **NO Supabase** - Self-hosted PostgreSQL is free
- **NO Clerk** - OAuth is straightforward
- **YES generic VPS** - Portable anywhere

### Ruthless Prioritization
- **ONE core feature** for launch
- **Defer everything else** to iteration
- **No admin dashboard** - Use database tool
- **No team features** - Single user first
- **No perfection** - Ship and iterate

---

## Example MVPs

### SaaS Todo App (2 hours)
- OAuth (Google + Apple)
- Todo CRUD + PostgreSQL
- Stripe $9/month subscription
- Deployed on Hetzner $5/month
- **Result: 50 users = $450 MRR - $5 hosting**

### Marketplace (3 hours)
- Two-sided (tutors + students)
- OAuth (Google + LinkedIn)
- Stripe Connect payments
- Simple matching algorithm
- **Result: 20 tutors @ $20/month = $400 MRR**

### AI Document Q&A (2.5 hours)
- OAuth (Microsoft + Google)
- OpenAI + pgvector
- Semantic search
- Stripe $29/month subscription
- **Result: 15 users = $435 MRR - $15 hosting**

---

## Cost Comparison

| Service | Vendor Stack | StartupStack | Savings |
|---------|--------------|--------------|---------|
| Database | Supabase $25+ | PostgreSQL $0 | $25/mo |
| Auth | Clerk $25+ | Custom OAuth $0 | $25/mo |
| Hosting | Vercel $20+ | Hetzner $5 | $15/mo |
| Storage | Vercel Blob $20+ | Backblaze $5 | $15/mo |
| Analytics | Vercel $20+ | Plausible (self-hosted) $0 | $20/mo |
| **Total** | **$110+/mo** | **$10-20/mo** | **$90/mo** |

**Year 1 savings: ~$1,100**

---

## What StartupStack Is NOT

### ❌ Not For Enterprise
- No SOC 2 compliance agents
- No comprehensive audit trails
- No enterprise deployment patterns
- No Windows/Active Directory specialists

### ❌ Not For Perfectionists
- No multi-tier code review
- No comprehensive testing suites
- No architectural debates
- No death certificates for deprecated features

### ❌ Not For Creative Projects
- No music composition agents
- No choreography agents
- No poetry agents
- No film production workflows

### ✅ Perfect For
- **0-to-1 SaaS products** - Ship your idea today
- **Side projects** - Evenings and weekends
- **Bootstrapped startups** - Control costs
- **Rapid prototyping** - Validate ideas fast

---

## Getting Started

### Installation
```bash
git clone https://github.com/yourusername/startup-stack
cd startup-stack
```

### Your First MVP
```bash
# Use the mvp-builder agent
@mvp-builder "Build a waitlist app with OAuth and email collection"

# 2 hours later: Working product deployed
```

### Learn More
- **CLAUDE.md** - Claude Code instructions and agent selection
- **agents/** - 12 core agent definitions
- **commands/** - 8 fast-track workflow commands
- **templates/** - SvelteKit starters (coming soon)
- **examples/** - 3 deployed MVPs (coming soon)

---

## Success Metrics

### vs Enterprise Platforms
- **Time to MVP**: 2-4 hours (vs 8-12 hours)
- **Monthly cost**: $10-20 (vs $110+)
- **Agent selection**: 30 seconds (vs 5 minutes with 73 agents)
- **Documentation**: 5 minutes (vs 2 hours reading 7.3MB docs)

### Startup KPIs
- ✅ 0-to-deployed MVP: <4 hours
- ✅ Add Stripe: <30 minutes
- ✅ Ship A/B test: <90 minutes
- ✅ Launch checklist: <1 hour
- ✅ Lighthouse score: >90
- ✅ Monthly hosting: <$20

---

## Contributing

StartupStack is opinionated by design. Contributions must:
- ✅ **Increase velocity** - Make shipping faster
- ✅ **Reduce cost** - Lower monthly expenses
- ✅ **Stay simple** - No enterprise bloat
- ✅ **Be pragmatic** - Good enough ships

Pull requests welcome for:
- New fast-track commands
- SvelteKit starter templates
- Cost optimization tips
- Deployed example MVPs

---

## Why SvelteKit?

**Simpler than React**:
- Less boilerplate, cleaner code
- No complex state management
- Native form actions (no libraries)

**Faster**:
- Smaller bundles
- Better runtime performance
- Faster builds

**Production-Ready**:
- Used by: Apple, Supabase dashboard, 1Password, Spotify
- Battle-tested at scale
- Excellent documentation

**Modern DX**:
- TypeScript native
- Vite for fast HMR
- Server routes built-in
- Form actions native

---

## License

MIT License - Build whatever you want

---

## Support

- **Issues**: For bugs and features
- **Discussions**: For questions and ideas
- **Twitter**: @startupsstack (coming soon)

---

**StartupStack: Ship it. Get feedback. Iterate. Repeat.**

*Built for founders who ship, not founders who plan.*
