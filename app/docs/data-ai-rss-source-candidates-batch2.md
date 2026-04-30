# Data AI RSS Source Candidates: Batch 2

Last verified:
- `2026-04-30 America/Chicago`

Purpose:
- Add 100+ more validated public, no-auth RSS/Atom/RDF feeds for Data AI.
- This batch is additional to `app/docs/data-ai-rss-source-candidates.md`.

Validation result:
- 115 additional working feeds validated.
- Validation required HTTP 200, parseable RSS/Atom/RDF XML, and non-empty item/entry count.

Guardrails:
- These are source candidates/backlog items, not implemented connectors.
- Media, blog, vendor, and NGO feeds are contextual awareness only.
- Official feeds still require source-specific caveats; do not infer impact, exploitation, or severity from titles alone.
- Do not scrape linked article pages without a separate approved no-auth machine-readable source.
- Use source-health, ETag/Last-Modified where available, backoff, and dedupe by GUID/link/hash.

## Validated Feeds

### Cybersecurity / Internet

| Source id | Feed URL | Verification result | Evidence basis | Caveats |
| --- | --- | --- | --- | --- |
| `dark-reading` | `https://www.darkreading.com/rss.xml` | HTTP 200, RSS, 50 items | media/contextual | Cyber news context; verify operational claims against primary sources. |
| `help-net-security` | `https://www.helpnetsecurity.com/feed/` | HTTP 200, RSS, 10 items | media/contextual | Cyber news context. |
| `security-affairs` | `https://securityaffairs.com/feed` | HTTP 200, RSS, 10 items | media/contextual | Cyber news context. |
| `cyberscoop` | `https://cyberscoop.com/feed/` | HTTP 200, RSS, 10 items | media/contextual | Cyber policy/news context. |
| `the-record` | `https://therecord.media/feed` | HTTP 200, RSS, 5 items | media/contextual | Cyber news context; low item count at verification time. |
| `checkpoint-research` | `https://research.checkpoint.com/feed/` | HTTP 200, RSS, 15 items | vendor/research | Threat research; vendor-source caveats apply. |
| `crowdstrike-blog` | `https://www.crowdstrike.com/en-us/blog/feed` | HTTP 200, RSS, 10 items | vendor/research | Final URL differs from candidate URL; use final URL. |
| `sentinelone-labs` | `https://www.sentinelone.com/labs/feed/` | HTTP 200, RSS, 10 items | vendor/research | Threat research; vendor-source caveats apply. |
| `qualys-blog` | `https://blog.qualys.com/feed` | HTTP 200, RSS, 10 items | vendor/contextual | Vendor vulnerability/cloud/security context. |
| `tenable-blog` | `https://www.tenable.com/blog/feed` | HTTP 200, RSS, 10 items | vendor/contextual | Vendor vulnerability-management context. |
| `proofpoint-blog` | `https://www.proofpoint.com/us/rss.xml` | HTTP 200, RSS, 10 items | vendor/research | Email/security research context. |
| `imperva-blog` | `https://www.imperva.com/blog/feed/` | HTTP 200, RSS, 10 items | vendor/contextual | Application/data security context. |
| `red-canary-blog` | `https://redcanary.com/blog/feed/` | HTTP 200, RSS, 10 items | vendor/research | Detection/security-operations context. |
| `huntress-blog` | `https://www.huntress.com/blog/rss.xml` | HTTP 200, RSS, 596 items | vendor/research | High item count; use pagination/backoff and dedupe carefully. |
| `jvn-en-new` | `https://jvn.jp/en/rss/jvn.rdf` | HTTP 200, RDF, 20 items | advisory | JVN vulnerability notes; preserve source language/region caveats. |
| `schneier-crypto-gram` | `https://www.schneier.com/crypto-gram/feed/` | HTTP 200, RSS, 10 items | analysis/contextual | Security commentary; not an incident feed. |
| `the-register-security` | `https://www.theregister.com/security/headlines.atom` | HTTP 200, Atom, 50 entries | media/contextual | Security news context. |
| `wired-security` | `https://www.wired.com/feed/category/security/latest/rss` | HTTP 200, RSS, 20 items | media/contextual | Security/news context; some articles may be analysis/features. |
| `ycombinator-hackernews` | `https://hnrss.org/frontpage` | HTTP 200, RSS, 20 items | community/contextual | Community ranking feed; not authoritative source truth. |
| `slashdot` | `http://rss.slashdot.org/Slashdot/slashdotMain` | HTTP 200, RDF, 15 items | community/media | Technology/news context; editorial/community caveats. |
| `ars-technica` | `https://feeds.arstechnica.com/arstechnica/index` | HTTP 200, RSS, 20 items | media/contextual | Technology/science/policy context. |
| `the-register` | `https://www.theregister.com/headlines.atom` | HTTP 200, Atom, 50 entries | media/contextual | Technology/news context. |
| `wired-business` | `https://www.wired.com/feed/category/business/latest/rss` | HTTP 200, RSS, 20 items | media/contextual | Business/technology context. |
| `techcrunch` | `https://techcrunch.com/feed/` | HTTP 200, RSS, 20 items | media/contextual | Technology/business context. |
| `the-verge` | `https://www.theverge.com/rss/index.xml` | HTTP 200, Atom, 10 entries | media/contextual | Technology/culture/business context. |
| `lacnic-news` | `https://blog.lacnic.net/en/feed/` | HTTP 200, RSS, 9 items | internet governance/contextual | Regional internet registry context; low item count at verification time. |

### Official / Event / Science

| Source id | Feed URL | Verification result | Evidence basis | Caveats |
| --- | --- | --- | --- | --- |
| `usgs-earthquakes-hour` | `https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.atom` | HTTP 200, Atom, 9 entries | observed/source-reported | Recent earthquake feed; event presence does not prove impact. |
| `usgs-significant-earthquakes` | `https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/significant_month.atom` | HTTP 200, Atom, 6 entries | observed/source-reported | Significant earthquake feed; magnitude/location do not prove damage. |
| `usgs-45-earthquakes` | `https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_day.atom` | HTTP 200, Atom, 6 entries | observed/source-reported | M4.5+ recent earthquake feed; not an impact feed. |
| `noaa-nhc-central-pacific` | `https://www.nhc.noaa.gov/index-cp.xml` | HTTP 200, RSS, 1 item | advisory | Central Pacific tropical advisory index; seasonal item count may be low. |
| `noaa-nhc-tropical-atlantic-outlook` | `https://www.nhc.noaa.gov/gtwo.xml` | HTTP 200, RSS, 3 items | advisory | Tropical weather outlook; advisory/contextual only. |
| `nasa-breaking-news` | `https://www.nasa.gov/news-release/feed/` | HTTP 200, RSS, 10 items | official/contextual | NASA news releases; not an emergency feed. |
| `nasa-image-of-day` | `https://www.nasa.gov/image-article/feed/` | HTTP 200, RSS, 10 items | contextual/science | Image/article context; not operational event truth. |
| `esa-news` | `https://www.esa.int/rssfeed/TopNews` | HTTP 200, RSS, 9 items | official/contextual | ESA top news; low item count at verification time. |
| `noaa-news` | `https://www.noaa.gov/rss.xml` | HTTP 200, RSS, 10 items | official/contextual | NOAA news context; not all items are live hazards. |
| `fda-news` | `https://www.fda.gov/about-fda/contact-fda/stay-informed/rss-feeds/press-releases/rss.xml` | HTTP 200, RSS, 20 items | official/contextual | FDA press releases; not all are emergencies. |
| `amnesty-news` | `https://www.amnesty.org/en/latest/news/feed/` | HTTP 200, RSS, 12 items | NGO/contextual | Human-rights reporting; contextual, not government confirmation. |
| `hrw-news` | `https://www.hrw.org/rss/news` | HTTP 200, RSS, 20 items | NGO/contextual | Human-rights reporting; contextual, not government confirmation. |
| `crisisgroup` | `https://www.crisisgroup.org/rss.xml` | HTTP 200, RSS, 10 items | analysis/contextual | Conflict analysis; not direct field-observation proof. |

### BBC

| Source id | Feed URL | Verification result | Evidence basis | Caveats |
| --- | --- | --- | --- | --- |
| `bbc-top-news` | `https://feeds.bbci.co.uk/news/rss.xml` | HTTP 200, RSS, 38 items | media/contextual | Broad news awareness. |
| `bbc-uk` | `https://feeds.bbci.co.uk/news/uk/rss.xml` | HTTP 200, RSS, 47 items | media/contextual | UK news context. |
| `bbc-us-canada` | `https://feeds.bbci.co.uk/news/world/us_and_canada/rss.xml` | HTTP 200, RSS, 25 items | media/contextual | U.S./Canada news context. |
| `bbc-europe` | `https://feeds.bbci.co.uk/news/world/europe/rss.xml` | HTTP 200, RSS, 26 items | media/contextual | Europe news context. |
| `bbc-middle-east` | `https://feeds.bbci.co.uk/news/world/middle_east/rss.xml` | HTTP 200, RSS, 33 items | media/contextual | Middle East news context. |
| `bbc-africa` | `https://feeds.bbci.co.uk/news/world/africa/rss.xml` | HTTP 200, RSS, 28 items | media/contextual | Africa news context. |
| `bbc-asia` | `https://feeds.bbci.co.uk/news/world/asia/rss.xml` | HTTP 200, RSS, 17 items | media/contextual | Asia news context. |
| `bbc-latin-america` | `https://feeds.bbci.co.uk/news/world/latin_america/rss.xml` | HTTP 200, RSS, 18 items | media/contextual | Latin America news context. |
| `bbc-business` | `https://feeds.bbci.co.uk/news/business/rss.xml` | HTTP 200, RSS, 54 items | media/contextual | Business/economy context. |
| `bbc-technology` | `https://feeds.bbci.co.uk/news/technology/rss.xml` | HTTP 200, RSS, 21 items | media/contextual | Technology context. |
| `bbc-science` | `https://feeds.bbci.co.uk/news/science_and_environment/rss.xml` | HTTP 200, RSS, 42 items | media/contextual | Science/environment context. |
| `bbc-health` | `https://feeds.bbci.co.uk/news/health/rss.xml` | HTTP 200, RSS, 52 items | media/contextual | Health news context; not official medical guidance. |

### Guardian

| Source id | Feed URL | Verification result | Evidence basis | Caveats |
| --- | --- | --- | --- | --- |
| `guardian-us` | `https://www.theguardian.com/us-news/rss` | HTTP 200, RSS, 33 items | media/contextual | U.S. news context. |
| `guardian-uk` | `https://www.theguardian.com/uk-news/rss` | HTTP 200, RSS, 45 items | media/contextual | UK news context. |
| `guardian-europe` | `https://www.theguardian.com/world/europe-news/rss` | HTTP 200, RSS, 20 items | media/contextual | Europe news context. |
| `guardian-middle-east` | `https://www.theguardian.com/world/middleeast/rss` | HTTP 200, RSS, 20 items | media/contextual | Middle East news context. |
| `guardian-africa` | `https://www.theguardian.com/world/africa/rss` | HTTP 200, RSS, 20 items | media/contextual | Africa news context. |
| `guardian-asia-pacific` | `https://www.theguardian.com/world/asia-pacific/rss` | HTTP 200, RSS, 20 items | media/contextual | Asia-Pacific news context. |
| `guardian-environment` | `https://www.theguardian.com/us/environment/rss` | HTTP 200, RSS, 34 items | media/contextual | Environment news context; final URL is U.S. edition path. |
| `guardian-technology` | `https://www.theguardian.com/us/technology/rss` | HTTP 200, RSS, 32 items | media/contextual | Technology news context; final URL is U.S. edition path. |
| `guardian-business` | `https://www.theguardian.com/us/business/rss` | HTTP 200, RSS, 20 items | media/contextual | Business news context; final URL is U.S. edition path. |
| `guardian-science` | `https://www.theguardian.com/science/rss` | HTTP 200, RSS, 28 items | media/contextual | Science news context. |

### NPR

| Source id | Feed URL | Verification result | Evidence basis | Caveats |
| --- | --- | --- | --- | --- |
| `npr-news` | `https://feeds.npr.org/1001/rss.xml` | HTTP 200, RSS, 10 items | media/contextual | Broad news context. |
| `npr-national` | `https://feeds.npr.org/1003/rss.xml` | HTTP 200, RSS, 10 items | media/contextual | U.S. national news context. |
| `npr-politics` | `https://feeds.npr.org/1014/rss.xml` | HTTP 200, RSS, 10 items | media/contextual | U.S. politics context. |
| `npr-business` | `https://feeds.npr.org/1006/rss.xml` | HTTP 200, RSS, 10 items | media/contextual | Business context. |
| `npr-science` | `https://feeds.npr.org/1007/rss.xml` | HTTP 200, RSS, 10 items | media/contextual | Science context. |
| `npr-health` | `https://feeds.npr.org/1128/rss.xml` | HTTP 200, RSS, 10 items | media/contextual | Health context; not official medical guidance. |
| `npr-technology` | `https://feeds.npr.org/1019/rss.xml` | HTTP 200, RSS, 10 items | media/contextual | Technology context. |

### New York Times

| Source id | Feed URL | Verification result | Evidence basis | Caveats |
| --- | --- | --- | --- | --- |
| `nytimes-world` | `https://rss.nytimes.com/services/xml/rss/nyt/World.xml` | HTTP 200, RSS, 57 items | media/contextual | Broad world news context. |
| `nytimes-us` | `https://rss.nytimes.com/services/xml/rss/nyt/US.xml` | HTTP 200, RSS, 42 items | media/contextual | U.S. news context. |
| `nytimes-politics` | `https://rss.nytimes.com/services/xml/rss/nyt/Politics.xml` | HTTP 200, RSS, 25 items | media/contextual | U.S. politics context. |
| `nytimes-business` | `https://rss.nytimes.com/services/xml/rss/nyt/Business.xml` | HTTP 200, RSS, 49 items | media/contextual | Business/economy context. |
| `nytimes-technology` | `https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml` | HTTP 200, RSS, 51 items | media/contextual | Technology context. |
| `nytimes-science` | `https://rss.nytimes.com/services/xml/rss/nyt/Science.xml` | HTTP 200, RSS, 27 items | media/contextual | Science context. |
| `nytimes-health` | `https://rss.nytimes.com/services/xml/rss/nyt/Health.xml` | HTTP 200, RSS, 20 items | media/contextual | Health news context; not official medical guidance. |
| `nytimes-climate` | `https://rss.nytimes.com/services/xml/rss/nyt/Climate.xml` | HTTP 200, RSS, 47 items | media/contextual | Climate news context. |
| `nytimes-asia` | `https://rss.nytimes.com/services/xml/rss/nyt/AsiaPacific.xml` | HTTP 200, RSS, 20 items | media/contextual | Asia-Pacific news context. |
| `nytimes-europe` | `https://rss.nytimes.com/services/xml/rss/nyt/Europe.xml` | HTTP 200, RSS, 20 items | media/contextual | Europe news context. |
| `nytimes-middle-east` | `https://rss.nytimes.com/services/xml/rss/nyt/MiddleEast.xml` | HTTP 200, RSS, 48 items | media/contextual | Middle East news context. |
| `nytimes-africa` | `https://rss.nytimes.com/services/xml/rss/nyt/Africa.xml` | HTTP 200, RSS, 20 items | media/contextual | Africa news context. |

### ABC / CBS / CBC / Sky News

| Source id | Feed URL | Verification result | Evidence basis | Caveats |
| --- | --- | --- | --- | --- |
| `abcnews-top` | `https://abcnews.com/abcnews/topstories` | HTTP 200, RSS, 25 items | media/contextual | Final URL changed from `abcnews.go.com` to `abcnews.com`. |
| `abcnews-international` | `https://abcnews.com/abcnews/internationalheadlines` | HTTP 200, RSS, 25 items | media/contextual | International news context. |
| `abcnews-us` | `https://abcnews.com/abcnews/usheadlines` | HTTP 200, RSS, 25 items | media/contextual | U.S. news context. |
| `abcnews-politics` | `https://abcnews.com/abcnews/politicsheadlines` | HTTP 200, RSS, 25 items | media/contextual | U.S. politics context. |
| `abcnews-technology` | `https://abcnews.com/abcnews/technologyheadlines` | HTTP 200, RSS, 25 items | media/contextual | Technology context. |
| `cbs-latest` | `https://www.cbsnews.com/latest/rss/main` | HTTP 200, RSS, 30 items | media/contextual | Broad news context. |
| `cbs-world` | `https://www.cbsnews.com/latest/rss/world` | HTTP 200, RSS, 30 items | media/contextual | World news context. |
| `cbs-us` | `https://www.cbsnews.com/latest/rss/us` | HTTP 200, RSS, 30 items | media/contextual | U.S. news context. |
| `cbs-politics` | `https://www.cbsnews.com/latest/rss/politics` | HTTP 200, RSS, 30 items | media/contextual | U.S. politics context. |
| `cbs-technology` | `https://www.cbsnews.com/latest/rss/technology` | HTTP 200, RSS, 30 items | media/contextual | Technology context. |
| `cbc-top` | `https://www.cbc.ca/webfeed/rss/rss-topstories` | HTTP 200, RSS, 20 items | media/contextual | Canadian/global top stories context. |
| `cbc-canada` | `https://www.cbc.ca/webfeed/rss/rss-canada` | HTTP 200, RSS, 20 items | media/contextual | Canada news context. |
| `cbc-politics` | `https://www.cbc.ca/webfeed/rss/rss-politics` | HTTP 200, RSS, 20 items | media/contextual | Canada politics context. |
| `cbc-business` | `https://www.cbc.ca/webfeed/rss/rss-business` | HTTP 200, RSS, 20 items | media/contextual | Business context. |
| `cbc-technology` | `https://www.cbc.ca/webfeed/rss/rss-technology` | HTTP 200, RSS, 20 items | media/contextual | Technology context. |
| `cbc-health` | `https://www.cbc.ca/webfeed/rss/rss-health` | HTTP 200, RSS, 20 items | media/contextual | Health news context; not official medical guidance. |
| `skynews-home` | `https://feeds.skynews.com/feeds/rss/home.xml` | HTTP 200, RSS, 10 items | media/contextual | Broad news context. |
| `skynews-uk` | `https://feeds.skynews.com/feeds/rss/uk.xml` | HTTP 200, RSS, 8 items | media/contextual | UK news context; low item count at verification time. |
| `skynews-us` | `https://feeds.skynews.com/feeds/rss/us.xml` | HTTP 200, RSS, 10 items | media/contextual | U.S. news context. |
| `skynews-business` | `https://feeds.skynews.com/feeds/rss/business.xml` | HTTP 200, RSS, 10 items | media/contextual | Business context. |
| `skynews-technology` | `https://feeds.skynews.com/feeds/rss/technology.xml` | HTTP 200, RSS, 10 items | media/contextual | Technology context. |

### RFI / Euronews / France 24 / The Conversation

| Source id | Feed URL | Verification result | Evidence basis | Caveats |
| --- | --- | --- | --- | --- |
| `rfi-africa` | `https://www.rfi.fr/en/africa/rss` | HTTP 200, RSS, 30 items | media/contextual | Africa news context. |
| `rfi-international` | `https://www.rfi.fr/en/international/rss` | HTTP 200, RSS, 30 items | media/contextual | International news context. |
| `rfi-france` | `https://www.rfi.fr/en/france/rss` | HTTP 200, RSS, 30 items | media/contextual | France news context. |
| `euronews-business` | `https://www.euronews.com/rss?level=theme&name=business` | HTTP 200, RSS, 50 items | media/contextual | Business/economy context. |
| `france24-africa` | `https://www.france24.com/en/africa/rss` | HTTP 200, RSS, 27 items | media/contextual | Africa news context. |
| `france24-europe` | `https://www.france24.com/en/europe/rss` | HTTP 200, RSS, 29 items | media/contextual | Europe news context. |
| `france24-middle-east` | `https://www.france24.com/en/middle-east/rss` | HTTP 200, RSS, 27 items | media/contextual | Middle East news context. |
| `france24-americas` | `https://www.france24.com/en/americas/rss` | HTTP 200, RSS, 30 items | media/contextual | Americas news context. |
| `france24-asia-pacific` | `https://www.france24.com/en/asia-pacific/rss` | HTTP 200, RSS, 29 items | media/contextual | Asia-Pacific news context. |
| `the-conversation-us` | `https://theconversation.com/us/articles.atom` | HTTP 200, Atom, 50 entries | analysis/contextual | Expert analysis/commentary; not breaking-event confirmation. |
| `the-conversation-tech` | `https://theconversation.com/us/technology/articles.atom` | HTTP 200, Atom, 25 entries | analysis/contextual | Technology analysis/commentary. |
| `the-conversation-environment` | `https://theconversation.com/us/environment/articles.atom` | HTTP 200, Atom, 25 entries | analysis/contextual | Environment analysis/commentary. |
| `the-conversation-politics` | `https://theconversation.com/us/politics/articles.atom` | HTTP 200, Atom, 25 entries | analysis/contextual | Politics analysis/commentary. |
| `the-conversation-health` | `https://theconversation.com/us/health/articles.atom` | HTTP 200, Atom, 25 entries | analysis/contextual | Health analysis/commentary; not official medical guidance. |
