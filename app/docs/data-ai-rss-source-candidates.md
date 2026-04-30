# Data AI RSS Source Candidates

Last verified:
- `2026-04-30 America/Chicago`

Purpose:
- Seed the new Data AI lane with public, no-auth RSS/Atom feeds for cybersecurity, internet infrastructure, world news, and world events.
- These are source candidates/backlog items. They are not implemented, validated workflows, or production-ready connectors.

Validation method:
- Normal backend-style HTTP request with a clear `User-Agent`
- HTTP 200 response
- XML parsed as RSS, Atom, or RDF
- Feed item/entry count greater than zero at verification time

Additional validated feed batch:
- `app/docs/data-ai-rss-source-candidates-batch2.md`
- 115 more working RSS/Atom/RDF feeds validated on `2026-04-30 America/Chicago`
- Data AI now has 167 validated feed candidates across the first list and Batch 2.

General ingestion rules:
- Preserve feed URL, final URL after redirects, source name, source category, published timestamp, fetched timestamp, GUID/link, title, summary, source health, and caveats.
- Treat official advisory/event feeds as advisory or observed-by-source, depending on source semantics.
- Treat media, vendor, and blog feeds as contextual awareness only, not ground truth.
- Do not scrape pages linked from feed items unless a separate no-auth machine-readable source is approved.
- Use conservative polling, ETag/Last-Modified where available, and backoff on errors.
- Deduplicate by GUID first, canonical link second, content hash third.

## Recommended First 20

| Priority | Source id | Feed | Category | Why first |
| ---: | --- | --- | --- | --- |
| 1 | `cisa-cybersecurity-advisories` | `https://www.cisa.gov/cybersecurity-advisories/all.xml` | cyber official | High-authority U.S. cybersecurity advisory stream. |
| 2 | `cisa-ics-advisories` | `https://www.cisa.gov/cybersecurity-advisories/ics-advisories.xml` | cyber official | High-value industrial-control-system advisory stream. |
| 3 | `ncsc-uk-all` | `https://www.ncsc.gov.uk/api/1/services/v1/all-rss-feed.xml` | cyber official | UK official cybersecurity guidance/advisory feed. |
| 4 | `cert-fr-alerts` | `https://www.cert.ssi.gouv.fr/alerte/feed/` | cyber official | French national CERT alert feed. |
| 5 | `cert-fr-advisories` | `https://www.cert.ssi.gouv.fr/avis/feed/` | cyber official | French national CERT advisory feed. |
| 6 | `sans-isc-diary` | `https://isc.sans.edu/rssfeed.xml` | cyber community | Strong operational security diary and threat context. |
| 7 | `bleepingcomputer` | `https://www.bleepingcomputer.com/feed/` | cyber news | Broad ransomware, breach, vulnerability, and cybercrime awareness. |
| 8 | `krebs-on-security` | `https://krebsonsecurity.com/feed/` | cyber news | High-signal investigative cybercrime reporting. |
| 9 | `google-security-blog` | `https://security.googleblog.com/feeds/posts/default` | cyber vendor | Major platform security announcements and research. |
| 10 | `microsoft-security-blog` | `https://www.microsoft.com/en-us/security/blog/feed/` | cyber vendor | Major platform security guidance and incident context. |
| 11 | `cisco-talos-blog` | `https://blog.talosintelligence.com/rss/` | cyber vendor | Threat research and malware/vulnerability context. |
| 12 | `cloudflare-status` | `https://www.cloudflarestatus.com/history.rss` | internet status | Operational infrastructure status events. |
| 13 | `cloudflare-radar` | `https://blog.cloudflare.com/tag/cloudflare-radar/rss/` | internet events | Internet traffic/outage/security analysis context. |
| 14 | `netblocks` | `https://netblocks.org/feed` | internet events | Internet disruption and connectivity incident context. |
| 15 | `apnic-blog` | `https://blog.apnic.net/feed/` | internet infrastructure | Internet routing, measurement, and network operations context. |
| 16 | `gdacs-alerts` | `https://www.gdacs.org/xml/rss.xml` | world events | Global disaster alert context. |
| 17 | `usgs-earthquakes-atom` | `https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.atom` | world events | Atom event feed for recent earthquakes. |
| 18 | `who-news` | `https://www.who.int/rss-feeds/news-english.xml` | world health | Official global health news and emergency context. |
| 19 | `bbc-world` | `https://feeds.bbci.co.uk/news/world/rss.xml` | world news | Broad global-news awareness. |
| 20 | `aljazeera-all` | `https://www.aljazeera.com/xml/rss/all.xml` | world news | Broad international-news awareness with different regional emphasis. |

## Validated Feed Backlog

### Cybersecurity Official / Advisory

| Source id | Feed URL | Verification result | Evidence basis | Caveats |
| --- | --- | --- | --- | --- |
| `cisa-cybersecurity-advisories` | `https://www.cisa.gov/cybersecurity-advisories/all.xml` | HTTP 200, RSS, 30 items | advisory | Official CISA advisory stream; advisory context, not incident proof. |
| `cisa-news` | `https://www.cisa.gov/news.xml` | HTTP 200, RSS, 10 items | contextual | Official CISA news; mix of announcements and advisories. |
| `cisa-ics-advisories` | `https://www.cisa.gov/cybersecurity-advisories/ics-advisories.xml` | HTTP 200, RSS, 30 items | advisory | ICS advisory context only; do not infer exploitation without source text. |
| `ncsc-uk-all` | `https://www.ncsc.gov.uk/api/1/services/v1/all-rss-feed.xml` | HTTP 200, RSS, 20 items | advisory/contextual | UK official feed; mix of guidance, news, advisories. |
| `cert-fr-alerts` | `https://www.cert.ssi.gouv.fr/alerte/feed/` | HTTP 200, RSS, 40 items | advisory | French official alert feed; preserve language/source context. |
| `cert-fr-advisories` | `https://www.cert.ssi.gouv.fr/avis/feed/` | HTTP 200, RSS, 40 items | advisory | French official advisory feed; preserve language/source context. |
| `sans-isc-diary` | `https://isc.sans.edu/rssfeed.xml` | HTTP 200, RSS, 10 items | contextual/advisory | Community/analyst context; not official government truth. |

### Cybersecurity News / Analysis / Vendor Research

| Source id | Feed URL | Verification result | Evidence basis | Caveats |
| --- | --- | --- | --- | --- |
| `the-hacker-news` | `https://feeds.feedburner.com/TheHackersNews` | HTTP 200, RSS, 50 items | media/contextual | Cyber news; verify claims against primary sources before escalation. |
| `krebs-on-security` | `https://krebsonsecurity.com/feed/` | HTTP 200, RSS, 10 items | media/contextual | Investigative cyber reporting; contextual, not direct official confirmation. |
| `bleepingcomputer` | `https://www.bleepingcomputer.com/feed/` | HTTP 200, RSS, 15 items | media/contextual | Cyber news; do not treat article titles as confirmed incident facts. |
| `securityweek` | `https://www.securityweek.com/feed/` | HTTP 200, RSS, 10 items | media/contextual | Cyber industry news; contextual awareness only. |
| `schneier-on-security` | `https://www.schneier.com/feed/atom/` | HTTP 200, Atom, 10 entries | analysis/contextual | Expert commentary and analysis; not an incident feed. |
| `google-security-blog` | `https://security.googleblog.com/feeds/posts/default` | HTTP 200, Atom, 25 entries | vendor/contextual | Vendor security updates; relevant to Google ecosystem and broader research. |
| `microsoft-security-blog` | `https://www.microsoft.com/en-us/security/blog/feed/` | HTTP 200, RSS, 10 items | vendor/contextual | Vendor blog; not the same as MSRC vulnerability database. |
| `cisco-talos-blog` | `https://blog.talosintelligence.com/rss/` | HTTP 200, RSS, 15 items | vendor/research | Threat research; preserve vendor attribution and confidence limits. |
| `palo-alto-unit42` | `https://unit42.paloaltonetworks.com/feed/` | HTTP 200, RSS, 15 items | vendor/research | Threat research; not official incident confirmation. |
| `rapid7-blog` | `https://www.rapid7.com/rss.xml` | HTTP 200, RSS, 20 items | vendor/contextual | Final URL redirects from `/blog/rss/`; use final feed URL. |
| `welivesecurity` | `https://www.welivesecurity.com/en/rss/feed/` | HTTP 200, RSS, 100 items | vendor/research | Final URL redirects from `/en/rss/`; vendor research/news. |
| `github-security-blog` | `https://github.blog/security/feed/` | HTTP 200, RSS, 10 items | vendor/contextual | GitHub platform security news and research. |
| `mozilla-security-blog` | `https://blog.mozilla.org/security/feed/` | HTTP 200, RSS, 10 items | vendor/contextual | Mozilla security engineering/research context. |
| `securelist` | `https://securelist.com/feed/` | HTTP 200, RSS, 10 items | vendor/research | Kaspersky research; geopolitical/vendor-source caveats may apply. |
| `malwarebytes-labs` | `https://www.malwarebytes.com/blog/feed/index.xml` | HTTP 200, RSS, 20 items | vendor/research | Malware and cybercrime context. |
| `recorded-future` | `https://www.recordedfuture.com/feed` | HTTP 200, RSS, 50 items | vendor/research | Threat intelligence vendor context; not public incident proof. |
| `greynoise-blog` | `https://www.greynoise.io/blog/rss.xml` | HTTP 200, RSS, 100 items | vendor/research | Internet scanning/noise research context. |

### Internet Infrastructure / Governance / Status

| Source id | Feed URL | Verification result | Evidence basis | Caveats |
| --- | --- | --- | --- | --- |
| `cloudflare-blog` | `https://blog.cloudflare.com/rss/` | HTTP 200, RSS, 20 items | vendor/contextual | Cloudflare platform and internet analysis; not neutral global measurement. |
| `cloudflare-radar` | `https://blog.cloudflare.com/tag/cloudflare-radar/rss/` | HTTP 200, RSS, 20 items | vendor/contextual | Useful internet event analysis; preserve methodology caveats. |
| `cloudflare-status` | `https://www.cloudflarestatus.com/history.rss` | HTTP 200, RSS, 25 items | operational status | Cloudflare service status only; not whole-internet status. |
| `netblocks` | `https://netblocks.org/feed` | HTTP 200, RSS, 10 items | contextual/measurement | Internet disruption reporting; preserve methodology and confidence caveats. |
| `apnic-blog` | `https://blog.apnic.net/feed/` | HTTP 200, RSS, 30 items | contextual | Internet infrastructure, routing, measurement, and policy context. |
| `ripe-labs` | `https://labs.ripe.net/feed.xml` | HTTP 200, RSS, 15 items | contextual | Final URL redirects from `/rss/`; internet measurement/policy research. |
| `internet-society` | `https://www.internetsociety.org/feed/` | HTTP 200, RSS, 20 items | contextual | Internet governance and resilience context. |

### World Events / Disasters / Health / Science

| Source id | Feed URL | Verification result | Evidence basis | Caveats |
| --- | --- | --- | --- | --- |
| `gdacs-alerts` | `https://www.gdacs.org/xml/rss.xml` | HTTP 200, RSS, 78 items | advisory/event | Global disaster alert context; preserve alert level and source caveats. |
| `usgs-earthquakes-atom` | `https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.atom` | HTTP 200, Atom, 270 entries | observed/source-reported | Event feed, but magnitude/location do not prove impact. |
| `noaa-nhc-atlantic` | `https://www.nhc.noaa.gov/index-at.xml` | HTTP 200, RSS, 1 item | advisory | Atlantic tropical cyclone advisory index; seasonal item count may be low. |
| `noaa-nhc-eastern-pacific` | `https://www.nhc.noaa.gov/index-ep.xml` | HTTP 200, RSS, 1 item | advisory | Eastern Pacific tropical cyclone advisory index; seasonal item count may be low. |
| `nasa-earth-observatory` | `https://science.nasa.gov/feed/?science_org=19791%2C22453` | HTTP 200, RSS, 10 items | contextual/science | Final URL from NASA Earth Observatory feed; science/context, not emergency alert. |
| `who-news` | `https://www.who.int/rss-feeds/news-english.xml` | HTTP 200, RSS, 25 items | official/contextual | Official health news; not all posts are emergencies or outbreaks. |
| `nature-news` | `https://www.nature.com/nature.rss` | HTTP 200, RDF, 75 items | science/contextual | Science news/research context; not operational event truth. |
| `undrr-news` | `https://www.undrr.org/rss.xml` | HTTP 200, RSS, 40 items | contextual/official | Disaster risk reduction news; not a live disaster alert feed. |

### World News / Global Awareness

| Source id | Feed URL | Verification result | Evidence basis | Caveats |
| --- | --- | --- | --- | --- |
| `bbc-world` | `https://feeds.bbci.co.uk/news/world/rss.xml` | HTTP 200, RSS, 31 items | media/contextual | Broad news awareness; verify critical claims against primary sources. |
| `guardian-world` | `https://www.theguardian.com/world/rss` | HTTP 200, RSS, 45 items | media/contextual | Broad news awareness; article framing may be editorial. |
| `aljazeera-all` | `https://www.aljazeera.com/xml/rss/all.xml` | HTTP 200, RSS, 25 items | media/contextual | Broad international awareness; preserve source attribution. |
| `npr-world` | `https://feeds.npr.org/1004/rss.xml` | HTTP 200, RSS, 10 items | media/contextual | World news context; not primary event confirmation. |
| `dw-all` | `https://rss.dw.com/rdf/rss-en-all` | HTTP 200, RDF, 126 items | media/contextual | Broad DW English feed; may include more than world events. |
| `france24-en` | `https://www.france24.com/en/rss` | HTTP 200, RSS, 23 items | media/contextual | Broad France 24 English feed; not primary event confirmation. |
| `japan-times-news` | `https://www.japantimes.co.jp/feed/` | HTTP 200, RSS, 30 items | media/contextual | Japan/regional/global news context. |
| `euronews-world` | `https://www.euronews.com/rss?level=theme&name=news` | HTTP 200, RSS, 50 items | media/contextual | Broad news feed; not primary event confirmation. |
| `cbc-world` | `https://www.cbc.ca/webfeed/rss/rss-world` | HTTP 200, RSS, 20 items | media/contextual | Canadian public broadcaster world-news context. |
| `skynews-world` | `https://feeds.skynews.com/feeds/rss/world.xml` | HTTP 200, RSS, 10 items | media/contextual | World-news context; verify critical claims. |
| `rfi-en` | `https://www.rfi.fr/en/rss` | HTTP 200, RSS, 22 items | media/contextual | Broad international news with French/international emphasis. |
| `globalnews-world` | `https://globalnews.ca/world/feed/` | HTTP 200, RSS, 10 items | media/contextual | Canadian commercial world-news context. |
| `the-conversation-world` | `https://theconversation.com/us/world/articles.atom` | HTTP 200, Atom, 25 entries | analysis/contextual | Expert analysis/commentary; not breaking-event confirmation. |

## Held Or Excluded After Validation Attempt

| Candidate | Result | Reason |
| --- | --- | --- |
| `cisa-ics-alerts` | hold | Old `/uscert/ics/alerts/alerts.xml` route failed; use `cisa-ics-advisories` first. |
| `google-cloud-security-blog` | hold | Candidate feed URL failed validation in this pass. |
| `microsoft-msrc-blog` | hold | Candidate feed URL failed validation in this pass; use Microsoft Security Blog feed first. |
| `sophos-news` | hold | Candidate feed URL failed validation in this pass. |
| `trendmicro-research` | hold | Candidate feed URL failed validation in this pass. |
| `cert-eu-news` | hold | Candidate feed URL failed validation in this pass. |
| `arin-blog` | hold | Candidate feed URL failed validation in this pass. |
| `ietf-blog` | hold | Candidate feed URL failed validation in this pass. |
| `icann-announcements` | hold | Candidate feed URL failed validation in this pass. |
| `reliefweb-updates-rss` | hold | Candidate RSS URL failed validation; ReliefWeb API remains separately approved elsewhere. |
| `un-news-all-rss` | hold | Candidate RSS URL failed validation in this pass. |
| `voa-news` | hold | Candidate feed URL failed validation in this pass. |
| `enisa-news-rss` | rejected/hold | ENISA says RSS feeds were discontinued after its new website launch. |
| `jpcert-en-rss` | hold | English candidate failed; Japanese/JVN feed routes need a separate pinning pass. |
| `cve-news-rss` | hold | Candidate response was not well-formed XML in this pass. |
| `elastic-security-labs` | hold | Candidate redirected with HTTP 308 and was not accepted by the simple validator. |
| `akamai-security` | hold | Candidate returned HTTP 403 to normal backend request. |
| `datadog-security-labs` | hold | Candidate feed URL returned HTTP 404. |
| `abc-au-world` | hold | Candidate feed URL returned HTTP 404. |
| `ilo-news` | hold | Candidate feed URL returned HTTP 404. |
| `un-ocha-stories` | hold | Candidate returned an empty/non-XML response. |
| `wfp-stories` | hold | Candidate feed URL returned HTTP 404. |

## First Data AI Implementation Slice

Recommended first implementation:

- Add a generic RSS/Atom/RDF feed adapter with fixture-first parsing.
- Use 5 feeds only for the first code slice:
  - `cisa-cybersecurity-advisories`
  - `cisa-ics-advisories`
  - `sans-isc-diary`
  - `cloudflare-status`
  - `gdacs-alerts`
- Normalize into one `DataFeedItem` contract:
  - `sourceId`
  - `sourceName`
  - `sourceCategory`
  - `feedUrl`
  - `finalUrl`
  - `guid`
  - `link`
  - `title`
  - `summary`
  - `publishedAt`
  - `fetchedAt`
  - `evidenceBasis`
  - `sourceMode`
  - `sourceHealth`
  - `caveats`
  - `tags`

Do not:
- start with all 52 feeds in runtime polling
- use article body scraping
- infer severity from title keywords alone
- treat media reports as confirmed official events
- mix cybersecurity and world-news scoring into one severity scale
