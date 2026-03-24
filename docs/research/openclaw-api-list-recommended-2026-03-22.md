# OpenClaw Curated API List — 92 Recommended APIs
**Source**: https://github.com/Kevjade/openclaw-api-list/blob/main/OPENCLAW_RECOMMENDED.md
**Ingested**: 2026-03-22
**Purpose**: PAI (Personal AI Infrastructure) — API catalog for Jake/Hermes skill and MCP integration

---

**92 APIs** hand-picked for OpenClaw operators. Every entry is something people in the community actually use. Focused on: outreach, social media scraping, SEO, marketing, and knowledge base building.

## Integration Patterns
1. **MCP** = add server URL to OpenClaw's MCP config, restart. No skill folder needed.
2. **Skill** = create `~/.openclaw/workspace/skills/<name>/SKILL.md`. Set API key in `skills.entries.<name>.apiKey` in `openclaw.json`.
3. **Webhook** = point outbound webhook at OpenClaw's webhook handler or cron endpoint.
4. **Browser** = OpenClaw uses built-in Chromium. No config needed.

---

## 1. Scraping & Data Extraction

| API | Pattern | Description + Use Case | Setup Hint |
|-----|---------|------------------------|------------|
| [Firecrawl MCP Server](https://apify.com/agentify/firecrawl-mcp-server) | MCP | Scrapes any URL → clean structured content for AI. Build knowledge bases from competitor sites. | Add MCP URL, set `FIRECRAWL_API_KEY` |
| [Website Content Crawler Pro](https://apify.com/datascoutapi/website-content-crawler-pro) | Skill | Crawls entire sites → Markdown/JSON/text. Bulk scrape 200-page docs for RAG pipeline. | Apify API token |
| [Doc To Markdown MCP Server](https://apify.com/abotapi/doc-to-markdown-mcp) | MCP | Converts PDFs, Word, Excel → clean Markdown. Drop a contract PDF → agent converts + summarizes. | No API key needed |
| [Markitdown MCP Server](https://apify.com/rector_labs/markitdown-mcp-server) | MCP | Converts 29+ formats (PDF, DOCX, PPTX, images, audio) → Markdown. Go-to for RAG ingestion pipelines. | No API key needed |
| [URL to Article Summarizer](https://apify.com/easyapi/any-website-url-to-article-summarizer) | Skill | Extracts + summarizes any article → key points. Drop a URL → 3-bullet summary. | Apify API token |
| [Browserbase MCP Server](https://apify.com/agentify/browserbase-mcp-server) | MCP | Cloud browser for sites that block bots. Breaks through Cloudflare, handles dynamic pages. | `BROWSERBASE_API_KEY` |
| [Playwright MCP Server](https://apify.com/jiri.spilka/playwright-mcp-server) | MCP | Full browser automation: click, type, screenshot, navigate. Agent screenshots dashboard metrics → posts to Slack. | No API key needed |
| [RSS Feed Parser](https://apify.com/dtrungtin/rss-feed-parser) | Skill | Parses RSS/Atom → structured articles. Monitor 20 industry blogs + build daily digest. | Apify API token |
| [Sitemap Scraper](https://apify.com/datascoutapi/sitemap-scraper) | Skill | Extracts all URLs from a site's sitemap. First step building any knowledge base from a site. | Apify API token |

---

## 2. Lead Generation & Outreach

| API | Pattern | Description + Use Case | Setup Hint |
|-----|---------|------------------------|------------|
| [Google Maps Email Extractor](https://apify.com/lukaskrivka/google-maps-with-contact-details) | Skill | Emails, phones, websites, social links from Google Maps businesses. | Apify API token |
| [Leads Scraper (Apollo Alternative)](https://apify.com/code_crafter/leads-finder) | Skill | B2B leads: emails, phones, LinkedIn, company details. $1.5/1k leads, 90M+ database. | Apify API token |
| [Email & Contact Extractor](https://apify.com/logical_scrapers/extract-email-from-any-website) | Skill | Emails + social links from any website list. | Apify API token |
| [Smart Email Finder & Verifier](https://apify.com/clearpath/email-finder-api) | Skill | Find verified emails by name + domain. Tests 10 patterns, stops on verified match. Bulk CSV. | Apify API token |
| [Company Research Intelligence](https://apify.com/easyapi/company-research-intelligence-tool) | Skill | Deep company profiles: tech stack, funding, team size, social. Pre-call research automation. | Apify API token |
| [LinkedIn Profile Scraper (No Cookies)](https://apify.com/vulnv/linkedin-profile-scraper) | Skill | Public LinkedIn data: work history, education, skills. No login required. | Apify API token |
| [LinkedIn Posts Scraper (No Login)](https://apify.com/vulnv/linkedin-posts-scraper) | Skill | Content, author info, engagement from public LinkedIn posts. Monitor what prospects are posting. | Apify API token |
| [LinkedIn Employee Scraper (No Login)](https://apify.com/jayed/linkedin-employee-scraper) | Skill | Employee profiles from a company page with keyword filtering. Find VPs and Directors. | Apify API token |
| [LinkedIn Search Posts Scraper](https://apify.com/scary_good_apis/linkedin-search-posts) | Skill | Search LinkedIn posts by keyword without risking your account. Find active voices in your market. | Apify API token |
| [Y Combinator Scraper](https://apify.com/damilo/y-combinator-scraper-apify) | Skill | YC startup directory: founders, team size, funding, job postings. Target funded startups. | Apify API token |
| [BuiltWith Tech Stack Scraper](https://apify.com/scrapegoats/builtwith-scraper) | Skill | Tech stack from any website list. Find companies on Shopify, WordPress, HubSpot. | Apify API token |
| [WhatsApp Number Validator](https://apify.com/thinkerpro/whatsapp-number-validator) | Skill | Validates phone numbers for WhatsApp registration. Essential for WA outreach campaigns. | Apify API token |
| [LeadLocator Pro (Google Maps)](https://apify.com/mea/leadlocator-pro) | Skill | Local business data worldwide: phone, email, address. Build targeted lead lists by location+industry. | Apify API token |

---

## 3. Social Media Scraping & Monitoring

| API | Pattern | Description + Use Case | Setup Hint |
|-----|---------|------------------------|------------|
| [Instagram Scraper](https://apify.com/apidojo/instagram-scraper) | Skill | Profiles, posts, hashtags, locations. $0.50/1k posts. Monitor competitor Instagram weekly. | Apify API token |
| [Tweet Scraper V2 (X/Twitter)](https://apify.com/apidojo/tweet-scraper) | Skill | Tweets by search, URL, list, or profile. $0.40/1k. Daily brand mention tracking. | Apify API token |
| [X/Twitter Scraper (Auto-Detect)](https://apify.com/mikolabs/x-scraper) | Skill | Auto-detects: tweets, profiles, users, lists, or media. Drop a URL, it figures out what you want. | Apify API token |
| [TikTok Scraper](https://apify.com/apidojo/tiktok-scraper) | Skill | Profiles, videos, hashtags, comments. 600 posts/sec. Find trending content in your niche. | Apify API token |
| [TikTok Comments Scraper](https://apify.com/apidojo/tiktok-comments-scraper) | Skill | Comments at 100-200/sec. Mine for pain points, questions, content ideas. | Apify API token |
| [MCP Reddit](https://apify.com/barudob/mcp-reddit) | MCP | Search posts, read threads, analyze sentiment by subreddit. Monitor for buying signals. | Reddit API credentials |
| [YouTube Transcript Scraper](https://apify.com/supreme_coder/youtube-transcript-scraper) | Skill | Bulk transcript extraction from multiple videos. Build content briefs from competitor channels. | Apify API token |
| [YouTube Channel Comment Collector](https://apify.com/n.nobar/youtube-channel-comment-collector) | Skill | Comments + likes from latest videos on any channel. Mine for audience sentiment + FAQs. | Apify API token |
| [Video to Social Post](https://apify.com/agentx/video-to-social-post) | Skill | Transforms video → social content + 6 styled images across 12+ platforms. Record once, post everywhere. | Apify API token |
| [Social Media Trend Scraper 6-in-1](https://apify.com/manju4k/social-media-trend-scraper-6-in-1-ai-analysis) | Skill | Trends from TikTok, Instagram, YouTube, Reddit, X, Pinterest with AI analysis. Weekly trend report. | Apify API token |
| [Video Transcript (Multi-Platform)](https://apify.com/agentx/video-transcript) | Skill | Transcripts from YouTube, TikTok, Instagram, 1000+ platforms. 100+ language translations. | Apify API token |
| [Find My Influencers](https://apify.com/easyapi/find-my-influencers) | Skill | Discovers influencers by niche from URL or topic. No manual scrolling required. | Apify API token |

---

## 4. SEO & Marketing

| API | Pattern | Description + Use Case | Setup Hint |
|-----|---------|------------------------|------------|
| [FetchSERP MCP Server](https://apify.com/agentify/fetchserp-mcp-server) | MCP | SERP analysis, keyword data, rank tracking. Daily keyword ranking → posts to Discord/Slack. | `FETCHSERP_API_KEY` |
| [Google Keyword Planner MCP](https://apify.com/smacient/google-keyword-planner-mcp) | MCP | Keyword research, search volume, location-based targeting. Official Google data. | Google Ads credentials |
| [GSC MCP (Google Search Console)](https://apify.com/smacient/gsc-mcp-worker) | MCP | Queries, clicks, impressions, position data from GSC. Alert on ranking drops. | Google Search Console auth |
| [GA4 MCP (Google Analytics)](https://apify.com/smacient/ga4-mcp-worker) | MCP | GA4 reports, metrics, dimensions. Weekly traffic summary → Slack every Monday. | Google Analytics auth |
| [Ahrefs Scraper](https://apify.com/radeance/ahrefs-scraper) | Skill | Keyword rankings, backlink profiles, organic traffic, competitor analysis. 180+ countries. | Apify API token |
| [AI Rank Tracker](https://apify.com/salman_bareesh/ai-rank-tracker) | Skill | Monitors rankings across ChatGPT, Gemini, Perplexity, Claude for specific keywords. | Apify API token |
| [Backlink Opportunity Finder](https://apify.com/easyapi/backlink-opportunity-finder) | Skill | Discovers high-quality backlink opportunities with DA and relevance data. | Apify API token |
| [Google Search Results Scraper](https://apify.com/damilo/google-search-apify) | Skill | Geo-targeted SERP data with query, language, country, date, pagination controls. | Apify API token |
| [Google Autocomplete Scraper](https://apify.com/damilo/google-autocomplete-apify) | Skill | Live Google Autocomplete suggestions across 250+ countries, 100+ languages. | Apify API token |
| [All-in-One Autocomplete Keywords Tool](https://apify.com/easyapi/all-in-one-autocomplete-keywords-tool) | Skill | Autocomplete from Google, Pinterest, Instagram, TikTok, Amazon, more in one call. | Apify API token |
| [Keyword Density Checker](https://apify.com/easyapi/keyword-density-checker) | Skill | Analyzes keyword density on any webpage. Audit your pages or spy on competitors. | Apify API token |
| [Long-Tail Keyword Discovery](https://apify.com/powerai/long-tail-keyword-discovery) | Skill | AI-powered long-tail keywords with volume, competition, ranking difficulty. | Apify API token |

---

## 5. Knowledge Base & Content Pipeline

| API | Pattern | Description + Use Case | Setup Hint |
|-----|---------|------------------------|------------|
| [Tavily MCP Server](https://apify.com/agentify/tavily-mcp-server) | MCP | Web search optimized for AI agents with built-in content extraction. Default search tool. | `TAVILY_API_KEY` |
| [Exa MCP Server](https://apify.com/agentify/exa-mcp-server) | MCP | Semantic search by meaning, not keywords. Find companies doing X when keyword search fails. | `EXA_API_KEY` |
| [Google Search MCP Server](https://apify.com/datascoutapi/google-search-mcp-server) | MCP | Real-time Google SERP results with snippets and links. | Google API credentials |
| [Brave Search MCP Server](https://apify.com/agentify/brave-search-mcp-server) | MCP | Privacy-focused web search. Alternative when you want results without Google. | `BRAVE_API_KEY` |
| [Google Images Scraper](https://apify.com/damilo/google-images-scraper) | Skill | Image URLs, alt-text, titles by keyword. Build image libraries for content creation. | Apify API token |
| [Email Campaign Creator](https://apify.com/easyapi/email-campaign-creator) | Skill | Product info → structured email campaigns: subject lines, body, CTAs. 5-email nurture sequences. | Apify API token |
| [Transcript to LinkedIn Posts](https://apify.com/powerai/transcript-to-linkedin-posts-converter) | Skill | Transforms transcripts → 10 LinkedIn posts using hook-contrarian frameworks. | Apify API token |
| [Lead Nurturing Emails Creator](https://apify.com/powerai/lead-nurturing-emails-creator) | Skill | Full email nurture sequences with personalized content, subject lines, CTAs. | Apify API token |

---

## 6. Ecommerce & Competitive Intelligence

| API | Pattern | Description + Use Case | Setup Hint |
|-----|---------|------------------------|------------|
| [Amazon Product Scraper](https://apify.com/datascoutapi/amazon-product-scraper) | Skill | ASINs, pricing, reviews, specs from all Amazon marketplaces real-time. | Apify API token |
| [Google Shopping Scraper](https://apify.com/damilo/google-shopping-apify) | Skill | Live product listings from Google Shopping: prices, ratings, sellers, availability. | Apify API token |
| [eBay Scraper](https://apify.com/3x1t/ebay-scraper-ppr) | Skill | Product listings from eBay: prices, seller info, item condition. Track sold prices. | Apify API token |
| [Trustpilot Reviews Scraper](https://apify.com/thewolves/trustpilot-reviews-scraper) | Skill | Reviews at $0.50/1k. Monitor reviews daily, flag negatives, weekly sentiment report. | Apify API token |
| [AI Product Matcher](https://apify.com/equidem/ai-product-matcher) | Skill | Matches products across ecommerce sites using AI. Dynamic pricing against competitors. | Apify API token |

---

## 7. Productivity & Workspace

| API | Pattern | Description + Use Case | Setup Hint |
|-----|---------|------------------------|------------|
| [Google Sheet MCP Server](https://apify.com/bhansalisoft/google-sheet-mcp-server) | MCP | Read, write, update Google Sheets programmatically. Auto-log leads from WhatsApp conversations. | Google OAuth |
| [Google Calendar Create Event](https://apify.com/sambehnke/google-calendar-create-event) | MCP | Creates Calendar events with title, time, attendees, description. "Schedule a call with Sarah next Tuesday" → booked. | Google OAuth |
| [Slack MCP](https://apify.com/parseforge/slack-mcp) | MCP | Read channels, send messages, manage threads. Read support channel → draft replies → post for review. | Slack Bot OAuth token |
| [Discord MCP Server](https://apify.com/bhansalisoft/discord-mcp-server) | MCP | Send messages, read channels, manage Discord server. Auto-respond to FAQ questions. | Discord bot token |
| [WhatsApp Cloud API MCP](https://apify.com/mdbm/whatsapp-cloud-api-mcp) | MCP | Send/receive WhatsApp messages via Business Cloud API. Appointment confirmations, follow-ups. | WhatsApp Business API creds |
| [WordPress MCP Server](https://apify.com/extremescrapes/wordpress-mcp-server) | MCP | Create, update, publish WordPress posts via REST API. Draft blog post → publish as draft for review. | WordPress URL + app password |
| [HubSpot MCP Server](https://apify.com/anchor/hubspot-apify-mcp-server) | MCP | Read/write HubSpot contacts, deals, company records. Auto-create contact when lead fills intake form. | HubSpot private app token |
| [Notion MCP Server](https://apify.com/agentify/notion-mcp-server) | MCP | Read, create, update Notion pages, databases, blocks. Dump research findings into Notion workspace. | Notion integration token |
| [Gmail MCP Server](https://apify.com/agentify/gmail-mcp-server) | MCP | Read, send, search Gmail. Send follow-ups to leads, check replies, log to CRM. | Google OAuth |

---

## 8. Automation & Orchestration

| API | Pattern | Description + Use Case | Setup Hint |
|-----|---------|------------------------|------------|
| [Nova MCP Server](https://apify.com/sambehnke/nova-integrations-mcp-server) | MCP | Dynamically loads any Apify actor as MCP tool at runtime. The Swiss army knife — no individual server setup. | Apify API token |
| [OpenAPI to MCP Converter](https://apify.com/theguide/openapi-to-mcp-converter) | MCP | Converts any OpenAPI/Swagger spec → MCP server. Turn any REST API with a spec into native MCP tools. | Provide OpenAPI spec URL |
| [n8n Documentation MCP Server](https://apify.com/agentify/n8n-mcp-server) | MCP | Searchable n8n node docs. Agent references n8n docs when building/debugging workflows from chat. | No API key needed |
| [Natural Language Dataset Query](https://apify.com/apify/natural-language-dataset-query) | MCP | Query Apify datasets in plain English. "Show me all leads from last week with email addresses." | Apify API token |
| [Google Maps MCP](https://apify.com/crawlerbros/google-maps-mcp) | MCP | Business search, reviews, contact info, directions. Look up locals, pull ratings + contacts → stage as leads. | Google Maps API key |

---

## Category Index (Full Catalog)
- **Lead Generation** (3,452): LEAD-GENERATION-APIS
- **Social Media** (3,268): SOCIAL-MEDIA-APIS
- **Automation** (4,825): AUTOMATION-APIS
- **Ecommerce** (2,440): ECOMMERCE-APIS
- **Developer Tools** (2,652): DEVELOPER-TOOLS-APIS
- **AI** (1,208): AI-APIS
- **Videos** (979): VIDEOS-APIS
- **Open Source** (768): OPEN-SOURCE-APIS
- **SEO Tools** (710): SEO-TOOLS-APIS
- **Jobs** (848): JOBS-APIS
- **News** (590): NEWS-APIS
- **Real Estate** (851): REAL-ESTATE-APIS
- **Travel** (397): TRAVEL-APIS
- **MCP Servers** (131): MCP-SERVERS-APIS
- **Agents** (697): AGENTS-APIS

**Total: 10,000+ APIs**

---

## PAI Priority Mapping (Jake/Hermes)

### Tier 1 — Wire immediately (already have keys or trivial setup)
- Firecrawl MCP ← already have FIRECRAWL_API_KEY
- Tavily MCP ← already have TAVILY_API_KEY
- Brave Search MCP ← already have BRAVE_API_KEY
- Playwright MCP ← no key needed
- Markitdown MCP ← no key needed, handles PDF/DOCX/PPTX for Oracle Health docs
- Notion MCP ← already have Notion token
- Gmail MCP ← already have Google OAuth
- Google Calendar MCP ← already have Google OAuth

### Tier 2 — High value, need API key
- Exa MCP ← semantic search complement to Tavily
- Nova MCP ← dynamic Apify actor loading (requires Apify token)
- Reddit MCP ← Reddit API credentials needed
- Company Research Intelligence ← Apify token, pre-call research for Oracle Health

### Tier 3 — Situational / TransformFit / Alex Recruiting
- LinkedIn scrapers ← recruiting research
- Social media scrapers ← TransformFit content monitoring
- SEO tools ← TransformFit growth
- Lead generation ← Alex Recruiting outreach
