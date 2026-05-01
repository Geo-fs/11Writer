# Data AI RSS Source Candidates: Batch 3

Last verified:
- `2026-04-30 America/Chicago`

Purpose:
- Add 100+ more validated public, no-auth RSS/Atom/RDF feeds for Data AI.
- This batch emphasizes global coverage beyond ordinary news: OSINT investigations, digital rights, fact-checking, disinformation tracking, conflict/security analysis, humanitarian context, environment/climate/science, travel/security advisories, regional coverage, economics, energy, open data, and geodata.

Validation result:
- 110 additional working feeds validated.
- Validation required HTTP 200, parseable RSS/Atom/RDF XML, and non-empty item/entry count.

Guardrails:
- These are source candidates/backlog items, not implemented connectors.
- Investigation, fact-checking, NGO, think-tank, media, vendor, and blog feeds are contextual awareness unless the source is authoritative for the specific record.
- Do not infer incident severity, conflict status, exploitation, casualty counts, policy conclusions, or humanitarian impact from titles alone.
- Do not scrape linked article pages without a separate approved no-auth machine-readable source.
- Use source-health, ETag/Last-Modified where available, backoff, and dedupe by GUID/link/hash.

## Validated Feeds

### OSINT / Investigations / Rights / Fact-Checking

| Source id | Feed URL | Category | Verification |
| --- | --- | --- | --- |
| `bellingcat` | `https://www.bellingcat.com/feed/` | osint-investigations | HTTP 200, RSS, 10 items |
| `citizen-lab` | `https://citizenlab.ca/feed/` | digital-rights | HTTP 200, RSS, 10 items |
| `eff-deeplinks` | `https://www.eff.org/rss/updates.xml` | digital-rights | HTTP 200, RSS, 50 items |
| `access-now` | `https://www.accessnow.org/feed/` | digital-rights | HTTP 200, RSS, 15 items |
| `privacy-international` | `https://privacyinternational.org/rss.xml` | digital-rights | HTTP 200, RSS, 10 items |
| `freedom-house` | `https://freedomhouse.org/rss.xml` | democracy-rights | HTTP 200, RSS, 10 items |
| `global-voices` | `https://globalvoices.org/feed/` | global-civic | HTTP 200, RSS, 15 items |
| `first-draft` | `https://firstdraftnews.org/feed/` | disinformation | HTTP 200, RSS, 11 items |
| `dfrlab` | `https://dfrlab.org/feed/` | disinformation | HTTP 200, RSS, 10 items |
| `full-fact` | `https://fullfact.org/feed/` | fact-checking | HTTP 200, RSS, 10 items |
| `snopes` | `https://www.snopes.com/feed/` | fact-checking | HTTP 200, RSS, 20 items |
| `politifact` | `https://www.politifact.com/rss/all/` | fact-checking | HTTP 200, RSS, 20 items |
| `factcheck-org` | `https://www.factcheck.org/feed/` | fact-checking | HTTP 200, RSS, 10 items |
| `euvsdisinfo` | `https://euvsdisinfo.eu/feed/` | disinformation | HTTP 200, RSS, 10 items |
| `occrp` | `https://www.occrp.org/en/feed` | investigations | HTTP 200, RSS, 60 items |
| `icij` | `https://www.icij.org/feed/` | investigations | HTTP 200, RSS, 11 items |
| `propublica` | `https://www.propublica.org/feeds/propublica/main` | investigations | HTTP 200, RSS, 20 items |
| `lighthouse-reports` | `https://www.lighthousereports.com/feed/` | investigations | HTTP 200, RSS, 10 items |
| `witness` | `https://www.witness.org/feed/` | human-rights-media | HTTP 200, RSS, 10 items |
| `article19` | `https://www.article19.org/feed/` | digital-rights | HTTP 200, RSS, 9 items |
| `cpj` | `https://cpj.org/feed/` | press-freedom | HTTP 200, RSS, 10 items |

### Conflict / Security / Policy Analysis

| Source id | Feed URL | Category | Verification |
| --- | --- | --- | --- |
| `atlantic-council` | `https://www.atlanticcouncil.org/feed/` | policy-thinktank | HTTP 200, RSS, 100 items |
| `ecfr` | `https://ecfr.eu/feed/` | policy-thinktank | HTTP 200, RSS, 25 items |
| `fdd` | `https://www.fdd.org/feed/` | security-thinktank | HTTP 200, RSS, 50 items |
| `war-on-the-rocks` | `https://warontherocks.com/feed/` | security-analysis | HTTP 200, RSS, 100 items |
| `modern-war-institute` | `https://mwi.westpoint.edu/feed/` | security-analysis | HTTP 200, RSS, 5 items |
| `irregular-warfare` | `https://irregularwarfare.org/feed/` | security-analysis | HTTP 200, RSS, 10 items |
| `defense-one` | `https://www.defenseone.com/rss/all/` | security-news | HTTP 200, RSS, 24 items |
| `breaking-defense` | `https://breakingdefense.com/feed/` | security-news | HTTP 200, RSS, 15 items |

### Humanitarian / Development / Environment / Science

| Source id | Feed URL | Category | Verification |
| --- | --- | --- | --- |
| `oxfam-press` | `https://www.oxfam.org/en/rss.xml` | humanitarian | HTTP 200, RSS, 10 items |
| `our-world-in-data` | `https://ourworldindata.org/atom.xml` | data-research | HTTP 200, Atom, 10 entries |
| `carbon-brief` | `https://www.carbonbrief.org/feed/` | environment | HTTP 200, RSS, 10 items |
| `climate-home-news` | `https://www.climatechangenews.com/feed/` | environment | HTTP 200, RSS, 40 items |
| `inside-climate-news` | `https://insideclimatenews.org/feed/` | environment | HTTP 200, RSS, 10 items |
| `mongabay` | `https://news.mongabay.com/feed/` | environment | HTTP 200, RSS, 32 items |
| `earth-observer-nasa` | `https://science.nasa.gov/feed/?science_org=19791%2C22453` | environment | HTTP 200, RSS, 10 items |
| `eumetsat-news` | `https://www.eumetsat.int/rss.xml` | weather-space | HTTP 200, RSS, 10 items |
| `smithsonian-volcano-news` | `https://volcano.si.edu/news/WeeklyVolcanoRSS.xml` | science-events | HTTP 200, RSS, 27 items |
| `ipcc-news` | `https://www.ipcc.ch/feed/` | environment | HTTP 200, RSS, 10 items |
| `eos-news` | `https://eos.org/feed` | science-events | HTTP 200, RSS, 15 items |
| `phys-org-earth` | `https://phys.org/rss-feed/earth-news/` | science-events | HTTP 200, RSS, 30 items |
| `phys-org-space` | `https://phys.org/rss-feed/space-news/` | science-events | HTTP 200, RSS, 30 items |
| `sciencedaily-top` | `https://www.sciencedaily.com/rss/top.xml` | science-events | HTTP 200, RSS, 60 items |
| `sciencedaily-earth` | `https://www.sciencedaily.com/rss/earth_climate.xml` | science-events | HTTP 200, RSS, 60 items |
| `sciencedaily-health` | `https://www.sciencedaily.com/rss/health_medicine.xml` | world-health | HTTP 200, RSS, 60 items |
| `sciencedaily-tech` | `https://www.sciencedaily.com/rss/computers_math.xml` | science-tech | HTTP 200, RSS, 60 items |

### Cyber / Internet Infrastructure / Web Standards

| Source id | Feed URL | Category | Verification |
| --- | --- | --- | --- |
| `trailofbits-blog` | `https://blog.trailofbits.com/index.xml` | cyber-research | HTTP 200, RSS, 20 items |
| `letsencrypt` | `https://letsencrypt.org/feed.xml` | internet-infra | HTTP 200, RSS, 119 items |
| `mozilla-hacks` | `https://hacks.mozilla.org/feed/` | internet-tech | HTTP 200, RSS, 20 items |
| `chromium-blog` | `https://blog.chromium.org/feeds/posts/default` | internet-tech | HTTP 200, Atom, 25 entries |
| `webdev-google` | `https://web.dev/static/blog/feed.xml` | internet-tech | HTTP 200, RSS, 10 items |
| `w3c-news` | `https://www.w3.org/news/feed/` | internet-standards | HTTP 200, RSS, 25 items |
| `seclists-fulldisclosure` | `https://seclists.org/rss/fulldisclosure.rss` | cyber-security | HTTP 200, RSS, 15 items |
| `debian-security` | `https://www.debian.org/security/dsa` | cyber-official | HTTP 200, RDF, 30 items |
| `gitlab-releases` | `https://about.gitlab.com/releases.xml` | cyber-vendor | HTTP 200, Atom, 110 entries |
| `github-changelog` | `https://github.blog/changelog/feed/` | internet-tech | HTTP 200, RSS, 10 items |

### Official / Travel / International Organizations

| Source id | Feed URL | Category | Verification |
| --- | --- | --- | --- |
| `state-travel-advisories` | `https://travel.state.gov/_res/rss/TAsTWs.xml` | travel-security | HTTP 200, RSS, 214 items |
| `eu-commission-press` | `https://ec.europa.eu/commission/presscorner/api/rss` | policy-official | HTTP 200, RSS, 10 items |
| `un-press-releases` | `https://press.un.org/en/rss.xml` | world-events | HTTP 200, RSS, 10 items |
| `unaids-news` | `https://www.unaids.org/en/rss.xml` | world-health | HTTP 200, RSS, 10 items |

### Regional / Global Coverage

| Source id | Feed URL | Category | Verification |
| --- | --- | --- | --- |
| `rferl` | `https://www.rferl.org/api/` | regional-news | HTTP 200, RSS, 20 items |
| `kyiv-independent` | `https://kyivindependent.com/news-archive/rss/` | regional-news | HTTP 200, RSS, 15 items |
| `meduza-en` | `https://meduza.io/rss/en/all` | regional-news | HTTP 200, RSS, 30 items |
| `moscow-times` | `https://www.themoscowtimes.com/rss/news` | regional-news | HTTP 200, RSS, 50 items |
| `balkan-insight` | `https://balkaninsight.com/feed/` | regional-news | HTTP 200, RSS, 90 items |
| `politico-eu` | `https://www.politico.eu/feed/` | regional-news | HTTP 200, RSS, 10 items |
| `euractiv` | `https://www.euractiv.com/feed/` | regional-news | HTTP 200, RSS, 100 items |
| `times-of-israel` | `https://www.timesofisrael.com/feed/` | regional-news | HTTP 200, RSS, 15 items |
| `jerusalem-post` | `https://www.jpost.com/rss/rssfeedsheadlines.aspx` | regional-news | HTTP 200, RSS, 30 items |
| `anadolu-world` | `https://www.aa.com.tr/en/rss/default?cat=world` | regional-news | HTTP 200, RSS, 30 items |
| `anadolu-middle-east` | `https://www.aa.com.tr/en/rss/default?cat=middle-east` | regional-news | HTTP 200, RSS, 28 items |
| `diplomat` | `https://thediplomat.com/feed/` | regional-analysis | HTTP 200, RSS, 96 items |
| `scmp-world` | `https://www.scmp.com/rss/91/feed` | regional-news | HTTP 200, RSS, 50 items |
| `scmp-china` | `https://www.scmp.com/rss/4/feed` | regional-news | HTTP 200, RSS, 50 items |
| `hong-kong-free-press` | `https://hongkongfp.com/feed/` | regional-news | HTTP 200, RSS, 30 items |
| `taipei-times` | `https://www.taipeitimes.com/xml/index.rss` | regional-news | HTTP 200, RDF, 50 items |
| `straits-times-asia` | `https://www.straitstimes.com/news/asia/rss.xml` | regional-news | HTTP 200, RSS, 50 items |
| `the-hindu-international` | `https://www.thehindu.com/news/international/feeder/default.rss` | regional-news | HTTP 200, RSS, 60 items |
| `indian-express-world` | `https://indianexpress.com/section/world/feed/` | regional-news | HTTP 200, RSS, 200 items |
| `dawn-world` | `https://www.dawn.com/feeds/world` | regional-news | HTTP 200, RSS, 30 items |
| `africanews` | `https://www.africanews.com/feed/rss` | regional-news | HTTP 200, RSS, 50 items |
| `allafrica` | `https://allafrica.com/tools/headlines/rdf/latest/headlines.rdf` | regional-news | HTTP 200, RSS, 30 items |
| `daily-maverick` | `https://www.dailymaverick.co.za/dmrss/` | regional-news | HTTP 200, RSS, 46 items |
| `premium-times-ng` | `https://www.premiumtimesng.com/feed` | regional-news | HTTP 200, RSS, 15 items |
| `buenos-aires-times` | `https://www.batimes.com.ar/feed` | regional-news | HTTP 200, RSS, 100 items |
| `rio-times` | `https://www.riotimesonline.com/feed/` | regional-news | HTTP 200, RSS, 10 items |
| `laprensalatina` | `https://laprensalatina.com/feed/` | regional-news | HTTP 200, RSS, 10 items |
| `mexico-news-daily` | `https://mexiconewsdaily.com/feed/` | regional-news | HTTP 200, RSS, 10 items |
| `dw-world` | `https://rss.dw.com/rdf/rss-en-world` | regional-news | HTTP 200, RDF, 12 items |
| `dw-europe` | `https://rss.dw.com/rdf/rss-en-eu` | regional-news | HTTP 200, RDF, 20 items |
| `dw-germany` | `https://rss.dw.com/rdf/rss-en-ger` | regional-news | HTTP 200, RDF, 12 items |
| `dw-business` | `https://rss.dw.com/rdf/rss-en-bus` | economic-news | HTTP 200, RDF, 20 items |
| `dw-top-stories` | `https://rss.dw.com/xml/rss-en-top` | regional-news | HTTP 200, RSS, 21 items |
| `upi-top` | `https://rss.upi.com/news/top_news.rss` | world-news | HTTP 200, RSS, 25 items |
| `upi-world` | `https://rss.upi.com/news/news.rss` | world-news | HTTP 200, RSS, 25 items |
| `upi-security` | `https://rss.upi.com/news/security_news.rss` | security-news | HTTP 200, RSS, 25 items |
| `upi-science` | `https://rss.upi.com/news/science_news.rss` | science-events | HTTP 200, RSS, 25 items |
| `upi-health` | `https://rss.upi.com/news/health_news.rss` | world-health | HTTP 200, RSS, 25 items |
| `sbs-world` | `https://www.sbs.com.au/news/topic/world/feed` | regional-news | HTTP 200, RSS, 25 items |
| `tehran-times` | `https://www.tehrantimes.com/rss` | regional-news | HTTP 200, RSS, 30 items |
| `egyptian-streets` | `https://egyptianstreets.com/feed/` | regional-news | HTTP 200, RSS, 9 items |
| `morocco-world-news` | `https://www.moroccoworldnews.com/feed/` | regional-news | HTTP 200, RSS, 10 items |

### Economics / Energy

| Source id | Feed URL | Category | Verification |
| --- | --- | --- | --- |
| `ft-world` | `https://www.ft.com/world?format=rss` | economic-news | HTTP 200, RSS, 25 items |
| `economist-latest` | `https://www.economist.com/latest/rss.xml` | economic-news | HTTP 200, RSS, 300 items |
| `marketwatch-top` | `https://feeds.content.dowjones.io/public/rss/mw_topstories` | economic-news | HTTP 200, RSS, 10 items |
| `investing-com-news` | `https://www.investing.com/rss/news.rss` | economic-news | HTTP 200, RSS, 10 items |
| `oilprice` | `https://oilprice.com/rss/main` | energy-news | HTTP 200, RSS, 15 items |

### Open Data / Geodata / Visualization

| Source id | Feed URL | Category | Verification |
| --- | --- | --- | --- |
| `openstreetmap-blog` | `https://blog.openstreetmap.org/feed/` | geodata-civic | HTTP 200, RSS, 10 items |
| `flowingdata` | `https://flowingdata.com/feed/` | data-visualization | HTTP 200, RSS, 10 items |
| `open-knowledge` | `https://blog.okfn.org/feed/` | open-data | HTTP 200, RSS, 10 items |

## Held Or Excluded After Validation Attempt

These were tested in Batch 3 but failed the validation bar or require a separate endpoint-pinning pass. Do not assign them from this batch.

| Candidate | Reason |
| --- | --- |
| `graphika` | Candidate feed returned HTTP 404. |
| `africacheck` | Candidate feed returned HTTP 403 to normal backend request. |
| `understanding-war` | Candidate feed returned HTTP 403 to normal backend request. |
| `rusi-commentary` | Candidate feed returned HTTP 404. |
| `csis-analysis` | Candidate feed returned HTTP 404. |
| `brookings` | Candidate feed XML had undefined entities under the strict parser. |
| `rand-blog` | Candidate feed returned HTTP 403 to normal backend request. |
| `world-bank-news` | Candidate feed was not well-formed XML under the strict parser. |
| `imf-news` | Candidate feed returned HTTP 403 to normal backend request. |
| `weforum-agenda` | Candidate feed returned HTTP 403 to normal backend request. |
| `msf-news` | Candidate feed returned HTTP 403 to normal backend request. |
| `unicef-press` | Candidate feed returned HTTP 404. |
| `reliefweb-disasters` | Candidate returned empty/non-XML response. |
| `apnews-*` | Candidate host failed DNS resolution in this environment. |
| `reuters-top-news` | Candidate feed returned HTTP 404. |
| `aljazeera-section-feeds` | Candidate section feed URLs returned HTTP 404; use existing `aljazeera-all`. |
| `project-zero` | Candidate feed had an unclosed CDATA section under the strict parser. |
| `seclists-bugtraq` | Candidate returned HTTP 200 but no items under the strict parser. |
| `uk-fcdo-travel` | Candidate Atom feed had undefined entities under the strict parser. |
| `promedmail` | Candidate returned HTTP 308 and was not accepted by the validator. |
