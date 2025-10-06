# Python Web Scraping with Playwright & Chrome

Advanced web scraping and automation using Playwright with Chrome/Chromium:

**Playwright Setup & Configuration:**
- Install and configure Playwright with Chrome/Chromium browsers
- Set up browser contexts with custom user agents and headers
- Configure viewport sizes, timezone, and locale settings
- Handle browser downloads and persistent context storage

**Advanced Browser Automation:**
- Navigate pages with proper wait strategies (networkidle, domcontentloaded)
- Handle dynamic content loading and JavaScript rendering
- Interact with complex UI elements (dropdowns, modals, forms)
- Manage cookies, sessions, and authentication flows

**Data Extraction Strategies:**
- Use CSS selectors and XPath for precise element targeting
- Extract structured data from tables, lists, and cards
- Handle pagination and infinite scroll scenarios
- Parse and clean extracted text, numbers, and URLs

**Anti-Detection & Stealth:**
- Rotate user agents and browser fingerprints
- Implement random delays and human-like interaction patterns
- Handle CAPTCHAs and bot detection mechanisms
- Use residential proxies and IP rotation

**Performance & Scaling:**
- Run multiple browser instances with asyncio concurrency
- Implement connection pooling and resource management
- Handle memory usage and browser cleanup
- Create distributed scraping with multiple containers

**Error Handling & Resilience:**
- Implement retry logic for failed requests and timeouts
- Handle network errors and connection issues gracefully
- Create fallback strategies for blocked or changed websites
- Log errors and monitor scraping success rates

**Data Processing & Storage:**
- Structure scraped data with Pydantic models for validation
- Store data in PostgreSQL with proper indexing
- Handle duplicate detection and data deduplication
- Create data pipelines for ETL processing

**Advanced Techniques:**
- Screenshot capture for visual validation
- PDF generation from web pages
- File download automation and management
- Form submission and multi-step workflows

**Chrome DevTools Integration:**
- Use browser DevTools for debugging and inspection
- Monitor network requests and response interception
- Analyze page performance and loading times
- Debug JavaScript execution and console errors

**Legal & Ethical Considerations:**
- Respect robots.txt and rate limiting
- Implement polite crawling with appropriate delays
- Handle terms of service and legal compliance
- Monitor server load and avoid overloading targets

**Integration with Your Stack:**
- Run scraping jobs in OrbStack containers for isolation
- Deploy scrapers to pi server with scheduling via cron/systemd
- Store scraped data in PostgreSQL database
- Create FastAPI endpoints for scraping job management

**Monitoring & Alerting:**
- Track scraping success rates and performance metrics
- Set up alerts for failed scraping jobs
- Monitor data quality and freshness
- Create dashboards for scraping pipeline health

**Testing & Development:**
- Create test suites for scraping logic validation
- Mock websites for development and testing
- Validate data extraction accuracy
- Test across different browser versions and environments

**Deployment & Scaling:**
- Containerize scrapers with proper Chrome/Chromium setup
- Handle headless browser requirements in production
- Scale scraping with worker queues and job scheduling
- Manage browser resource limits and cleanup

Target Website/Scraping Task: $ARGUMENTS

