from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


EvidenceBasis = Literal["advisory", "contextual", "source-reported"]


@dataclass(frozen=True)
class DataAiFeedSourceDefinition:
    source_id: str
    source_name: str
    source_category: str
    feed_url: str
    fixture_file_name: str
    evidence_basis: EvidenceBasis
    caveat: str


@dataclass(frozen=True)
class DataAiFeedFamilyDefinition:
    family_id: str
    family_label: str
    source_ids: tuple[str, ...]
    tags: tuple[str, ...]
    caveat: str


DATA_AI_MULTI_FEED_DEFINITIONS: tuple[DataAiFeedSourceDefinition, ...] = (
    DataAiFeedSourceDefinition(
        source_id="cisa-cybersecurity-advisories",
        source_name="CISA Cybersecurity Advisories",
        source_category="cyber-official",
        feed_url="https://www.cisa.gov/cybersecurity-advisories/all.xml",
        fixture_file_name="cisa_cybersecurity_advisories.xml",
        evidence_basis="advisory",
        caveat=(
            "Official CISA advisory context only; do not infer exploitation, compromise, incident confirmation, attribution, impact, or required action from feed text alone."
        ),
    ),
    DataAiFeedSourceDefinition(
        source_id="cisa-ics-advisories",
        source_name="CISA ICS Advisories",
        source_category="cyber-official",
        feed_url="https://www.cisa.gov/cybersecurity-advisories/ics-advisories.xml",
        fixture_file_name="cisa_ics_advisories.xml",
        evidence_basis="advisory",
        caveat=(
            "Official ICS advisory context only; do not infer exploitation, operational consequence, or realized industrial impact unless the source explicitly supports it."
        ),
    ),
    DataAiFeedSourceDefinition(
        source_id="ncsc-uk-all",
        source_name="NCSC UK All RSS Feed",
        source_category="cyber-official",
        feed_url="https://www.ncsc.gov.uk/api/1/services/v1/all-rss-feed.xml",
        fixture_file_name="ncsc_uk_all.xml",
        evidence_basis="contextual",
        caveat=(
            "Official NCSC UK feed items mix guidance, advisories, and news context; do not infer exploitation, victimization, incident confirmation, attribution, impact, or required action from feed text alone."
        ),
    ),
    DataAiFeedSourceDefinition(
        source_id="cert-fr-alerts",
        source_name="CERT-FR Alertes de securite",
        source_category="cyber-official",
        feed_url="https://www.cert.ssi.gouv.fr/alerte/feed/",
        fixture_file_name="cert_fr_alerts.xml",
        evidence_basis="advisory",
        caveat=(
            "Official CERT-FR alert context in French only; preserve source wording and do not infer exploitation, compromise, victim impact, attribution, or required action beyond what the source explicitly supports."
        ),
    ),
    DataAiFeedSourceDefinition(
        source_id="cert-fr-advisories",
        source_name="CERT-FR Avis de securite",
        source_category="cyber-official",
        feed_url="https://www.cert.ssi.gouv.fr/avis/feed/",
        fixture_file_name="cert_fr_advisories.xml",
        evidence_basis="advisory",
        caveat=(
            "Official CERT-FR advisory context in French only; preserve advisory wording without inventing urgency, incident certainty, or a cross-source severity claim."
        ),
    ),
    DataAiFeedSourceDefinition(
        source_id="cisa-news",
        source_name="CISA News",
        source_category="cyber-official",
        feed_url="https://www.cisa.gov/news.xml",
        fixture_file_name="cisa_news.xml",
        evidence_basis="contextual",
        caveat=(
            "CISA news items are official institutional and cybersecurity announcement context only; they are not by themselves exploit proof, compromise proof, incident confirmation, or required-action guidance."
        ),
    ),
    DataAiFeedSourceDefinition(
        source_id="jvn-en-new",
        source_name="JVN Vulnerability Notes",
        source_category="cyber-official",
        feed_url="https://jvn.jp/en/rss/jvn.rdf",
        fixture_file_name="jvn_en_new.xml",
        evidence_basis="advisory",
        caveat=(
            "JVN vulnerability notes are official advisory context for the Japanese vulnerability-information ecosystem; they are not exploit proof, compromise proof, or universal remediation priority."
        ),
    ),
    DataAiFeedSourceDefinition(
        source_id="debian-security",
        source_name="Debian Security Advisories",
        source_category="cyber-official",
        feed_url="https://www.debian.org/security/dsa",
        fixture_file_name="debian_security.xml",
        evidence_basis="advisory",
        caveat=(
            "Debian security items are distribution advisory context only; they are not exploit proof, incident confirmation, or universal urgency guidance beyond the source wording."
        ),
    ),
    DataAiFeedSourceDefinition(
        source_id="microsoft-security-blog",
        source_name="Microsoft Security Blog",
        source_category="cyber-vendor",
        feed_url="https://www.microsoft.com/en-us/security/blog/feed/",
        fixture_file_name="microsoft_security_blog.xml",
        evidence_basis="contextual",
        caveat=(
            "Microsoft Security Blog items are vendor security and incident-response context only; they are not neutral global incident proof, exploitation proof, or required-action guidance."
        ),
    ),
    DataAiFeedSourceDefinition(
        source_id="cisco-talos-blog",
        source_name="Cisco Talos Blog",
        source_category="cyber-research",
        feed_url="https://blog.talosintelligence.com/rss/",
        fixture_file_name="cisco_talos_blog.xml",
        evidence_basis="contextual",
        caveat=(
            "Cisco Talos items are vendor threat-research context only; they are not independent incident confirmation, attribution proof, or required-action guidance."
        ),
    ),
    DataAiFeedSourceDefinition(
        source_id="mozilla-security-blog",
        source_name="Mozilla Security Blog",
        source_category="cyber-vendor",
        feed_url="https://blog.mozilla.org/security/feed/",
        fixture_file_name="mozilla_security_blog.xml",
        evidence_basis="contextual",
        caveat=(
            "Mozilla Security Blog items are vendor security engineering context only; they are not universal exploitation proof, compromise proof, or required-action guidance."
        ),
    ),
    DataAiFeedSourceDefinition(
        source_id="github-security-blog",
        source_name="GitHub Security Blog",
        source_category="cyber-vendor",
        feed_url="https://github.blog/security/feed/",
        fixture_file_name="github_security_blog.xml",
        evidence_basis="contextual",
        caveat=(
            "GitHub Security Blog items are platform security context only; they are not independent incident confirmation, exploitation proof, or required-action guidance."
        ),
    ),
    DataAiFeedSourceDefinition(
        source_id="trailofbits-blog",
        source_name="Trail of Bits Blog",
        source_category="cyber-research",
        feed_url="https://blog.trailofbits.com/index.xml",
        fixture_file_name="trailofbits_blog.xml",
        evidence_basis="contextual",
        caveat=(
            "Trail of Bits blog items are security-research and audit context only; they are not universal exploit proof, compromise proof, incident confirmation, or required-action guidance."
        ),
    ),
    DataAiFeedSourceDefinition(
        source_id="mozilla-hacks",
        source_name="Mozilla Hacks",
        source_category="internet-tech",
        feed_url="https://hacks.mozilla.org/feed/",
        fixture_file_name="mozilla_hacks.xml",
        evidence_basis="contextual",
        caveat=(
            "Mozilla Hacks items are browser, web, and engineering context only; they are not universal standards compliance proof, incident confirmation, or required-action guidance."
        ),
    ),
    DataAiFeedSourceDefinition(
        source_id="chromium-blog",
        source_name="Chromium Blog",
        source_category="internet-tech",
        feed_url="https://blog.chromium.org/feeds/posts/default",
        fixture_file_name="chromium_blog.xml",
        evidence_basis="contextual",
        caveat=(
            "Chromium Blog items are browser-platform release and engineering context only; they are not universal platform truth, incident confirmation, or required-action guidance."
        ),
    ),
    DataAiFeedSourceDefinition(
        source_id="webdev-google",
        source_name="web.dev Blog",
        source_category="internet-tech",
        feed_url="https://web.dev/static/blog/feed.xml",
        fixture_file_name="webdev_google.xml",
        evidence_basis="contextual",
        caveat=(
            "web.dev items are web-platform guidance and engineering context only; they are not standards compliance proof, incident confirmation, or required-action guidance."
        ),
    ),
    DataAiFeedSourceDefinition(
        source_id="gitlab-releases",
        source_name="GitLab Releases",
        source_category="cyber-vendor",
        feed_url="https://about.gitlab.com/releases.xml",
        fixture_file_name="gitlab_releases.xml",
        evidence_basis="contextual",
        caveat=(
            "GitLab release items are platform release and product-update context only; they are not compromise proof, incident confirmation, or universal remediation priority."
        ),
    ),
    DataAiFeedSourceDefinition(
        source_id="github-changelog",
        source_name="GitHub Changelog",
        source_category="internet-tech",
        feed_url="https://github.blog/changelog/feed/",
        fixture_file_name="github_changelog.xml",
        evidence_basis="contextual",
        caveat=(
            "GitHub Changelog items are platform feature and release context only; they are not platform-wide incident proof, security truth, or required-action guidance."
        ),
    ),
    DataAiFeedSourceDefinition(
        source_id="bbc-world",
        source_name="BBC World",
        source_category="media-world",
        feed_url="https://feeds.bbci.co.uk/news/world/rss.xml",
        fixture_file_name="bbc_world.xml",
        evidence_basis="contextual",
        caveat=(
            "BBC World items are broad media-awareness context only; preserve attribution and do not infer primary event truth, impact certainty, attribution proof, legal status, or required action from headline text alone."
        ),
    ),
    DataAiFeedSourceDefinition(
        source_id="guardian-world",
        source_name="The Guardian World",
        source_category="media-world",
        feed_url="https://www.theguardian.com/world/rss",
        fixture_file_name="guardian_world.xml",
        evidence_basis="contextual",
        caveat=(
            "Guardian World items are broad media-awareness and editorially framed context only; they are not primary event confirmation, intent proof, legal status, or required-action guidance."
        ),
    ),
    DataAiFeedSourceDefinition(
        source_id="aljazeera-all",
        source_name="Al Jazeera All News",
        source_category="media-world",
        feed_url="https://www.aljazeera.com/xml/rss/all.xml",
        fixture_file_name="aljazeera_all.xml",
        evidence_basis="contextual",
        caveat=(
            "Al Jazeera items are broad international media-awareness context only; preserve source attribution and do not infer primary field truth, impact certainty, attribution proof, or required action from feed text alone."
        ),
    ),
    DataAiFeedSourceDefinition(
        source_id="dw-all",
        source_name="DW English All News",
        source_category="media-world",
        feed_url="https://rss.dw.com/rdf/rss-en-all",
        fixture_file_name="dw_all.xml",
        evidence_basis="contextual",
        caveat=(
            "DW all-news items are broad media-awareness context only; they are not primary event confirmation, whole-situation truth, legal status, or required-action guidance."
        ),
    ),
    DataAiFeedSourceDefinition(
        source_id="france24-en",
        source_name="France 24 English",
        source_category="media-world",
        feed_url="https://www.france24.com/en/rss",
        fixture_file_name="france24_en.xml",
        evidence_basis="contextual",
        caveat=(
            "France 24 English items are broad media-awareness context only; they are not primary event truth, field confirmation, legal status, or required-action guidance."
        ),
    ),
    DataAiFeedSourceDefinition(
        source_id="npr-world",
        source_name="NPR World",
        source_category="media-world",
        feed_url="https://feeds.npr.org/1004/rss.xml",
        fixture_file_name="npr_world.xml",
        evidence_basis="contextual",
        caveat=(
            "NPR World items are broad world-news context only; they are not primary event confirmation, impact proof, attribution proof, or required-action guidance."
        ),
    ),
    DataAiFeedSourceDefinition(
        source_id="sans-isc-diary",
        source_name="SANS Internet Storm Center Diary",
        source_category="cyber-community",
        feed_url="https://isc.sans.edu/rssfeed.xml",
        fixture_file_name="sans_isc_diary.xml",
        evidence_basis="contextual",
        caveat=(
            "SANS ISC diary items are community/analyst context, not official government truth or incident confirmation."
        ),
    ),
    DataAiFeedSourceDefinition(
        source_id="cloudflare-status",
        source_name="Cloudflare Status History",
        source_category="internet-status",
        feed_url="https://www.cloudflarestatus.com/history.rss",
        fixture_file_name="cloudflare_status.xml",
        evidence_basis="source-reported",
        caveat=(
            "Cloudflare Status describes Cloudflare service status only; it is not whole-internet status, general outage proof, or global routing truth."
        ),
    ),
    DataAiFeedSourceDefinition(
        source_id="cloudflare-radar",
        source_name="Cloudflare Radar Blog",
        source_category="internet-analysis",
        feed_url="https://blog.cloudflare.com/tag/cloudflare-radar/rss/",
        fixture_file_name="cloudflare_radar.xml",
        evidence_basis="contextual",
        caveat=(
            "Cloudflare Radar items are provider-specific internet-analysis context with methodology caveats; they are not neutral whole-internet truth, outage proof, or incident confirmation."
        ),
    ),
    DataAiFeedSourceDefinition(
        source_id="netblocks",
        source_name="NetBlocks Feed",
        source_category="internet-measurement",
        feed_url="https://netblocks.org/feed",
        fixture_file_name="netblocks.xml",
        evidence_basis="contextual",
        caveat=(
            "NetBlocks items are methodology-dependent internet disruption context, not operator-confirmed outage proof, sovereign ground truth, or universal internet status."
        ),
    ),
    DataAiFeedSourceDefinition(
        source_id="apnic-blog",
        source_name="APNIC Blog",
        source_category="internet-infrastructure",
        feed_url="https://blog.apnic.net/feed/",
        fixture_file_name="apnic_blog.xml",
        evidence_basis="contextual",
        caveat=(
            "APNIC blog items are routing, measurement, policy, and infrastructure context only; they are not live incident proof, outage confirmation, or neutral whole-internet truth."
        ),
    ),
    DataAiFeedSourceDefinition(
        source_id="ripe-labs",
        source_name="RIPE Labs",
        source_category="internet-governance",
        feed_url="https://labs.ripe.net/feed.xml",
        fixture_file_name="ripe_labs.xml",
        evidence_basis="contextual",
        caveat=(
            "RIPE Labs items are internet-measurement, policy, and operations research context only; they are not whole-internet truth, outage proof, or required-action guidance."
        ),
    ),
    DataAiFeedSourceDefinition(
        source_id="internet-society",
        source_name="Internet Society",
        source_category="internet-governance",
        feed_url="https://www.internetsociety.org/feed/",
        fixture_file_name="internet_society.xml",
        evidence_basis="contextual",
        caveat=(
            "Internet Society items are internet-governance and resilience context only; they are not policy truth, standards compliance proof, or required-action guidance."
        ),
    ),
    DataAiFeedSourceDefinition(
        source_id="lacnic-news",
        source_name="LACNIC News",
        source_category="internet-registry",
        feed_url="https://blog.lacnic.net/en/feed/",
        fixture_file_name="lacnic_news.xml",
        evidence_basis="contextual",
        caveat=(
            "LACNIC news items are regional internet-registry policy and operations context only; they are not outage proof, standards compliance proof, or required-action guidance."
        ),
    ),
    DataAiFeedSourceDefinition(
        source_id="w3c-news",
        source_name="W3C News",
        source_category="internet-standards",
        feed_url="https://www.w3.org/news/feed/",
        fixture_file_name="w3c_news.xml",
        evidence_basis="contextual",
        caveat=(
            "W3C news items are web-standards and governance context only; they are not universal standards compliance proof, policy truth, or required-action guidance."
        ),
    ),
    DataAiFeedSourceDefinition(
        source_id="letsencrypt",
        source_name="Let's Encrypt",
        source_category="internet-operations",
        feed_url="https://letsencrypt.org/feed.xml",
        fixture_file_name="letsencrypt.xml",
        evidence_basis="contextual",
        caveat=(
            "Let's Encrypt items are certificate and internet-operations context only; they are not universal internet-health proof, standards compliance proof, or required-action guidance."
        ),
    ),
    DataAiFeedSourceDefinition(
        source_id="bellingcat",
        source_name="Bellingcat",
        source_category="osint-investigations",
        feed_url="https://www.bellingcat.com/feed/",
        fixture_file_name="bellingcat.xml",
        evidence_basis="contextual",
        caveat=(
            "Bellingcat items are investigative/OSINT context, not official incident truth, legal conclusion, attribution proof, or required action."
        ),
    ),
    DataAiFeedSourceDefinition(
        source_id="citizen-lab",
        source_name="Citizen Lab",
        source_category="digital-rights",
        feed_url="https://citizenlab.ca/feed/",
        fixture_file_name="citizen_lab.xml",
        evidence_basis="contextual",
        caveat=(
            "Citizen Lab items are research and digital-rights context, not official incident confirmation, legal judgment, or universal attribution proof."
        ),
    ),
    DataAiFeedSourceDefinition(
        source_id="occrp",
        source_name="OCCRP",
        source_category="investigations",
        feed_url="https://www.occrp.org/en/feed",
        fixture_file_name="occrp.xml",
        evidence_basis="contextual",
        caveat=(
            "OCCRP items are investigative-reporting context, not official source truth, legal conclusion, or standalone proof of culpability."
        ),
    ),
    DataAiFeedSourceDefinition(
        source_id="icij",
        source_name="ICIJ",
        source_category="investigations",
        feed_url="https://www.icij.org/feed/",
        fixture_file_name="icij.xml",
        evidence_basis="contextual",
        caveat=(
            "ICIJ items are investigative/public-interest context, not official incident confirmation, legal conclusion, or required-action guidance."
        ),
    ),
    DataAiFeedSourceDefinition(
        source_id="propublica",
        source_name="ProPublica",
        source_category="investigations",
        feed_url="https://www.propublica.org/feeds/propublica/main",
        fixture_file_name="propublica.xml",
        evidence_basis="contextual",
        caveat=(
            "ProPublica items are investigative and civic-accountability reporting context, not official event confirmation, wrongdoing proof, intent proof, legal conclusion, or required-action guidance."
        ),
    ),
    DataAiFeedSourceDefinition(
        source_id="global-voices",
        source_name="Global Voices",
        source_category="civic-media",
        feed_url="https://globalvoices.org/feed/",
        fixture_file_name="global_voices.xml",
        evidence_basis="contextual",
        caveat=(
            "Global Voices items are civic, translation, and advocacy-adjacent reporting context, not official event truth, impact proof, legal conclusion, or required-action guidance."
        ),
    ),
    DataAiFeedSourceDefinition(
        source_id="eff-updates",
        source_name="EFF Updates",
        source_category="digital-rights",
        feed_url="https://www.eff.org/rss/updates.xml",
        fixture_file_name="eff_updates.xml",
        evidence_basis="contextual",
        caveat=(
            "EFF updates are civic and digital-rights context, not official incident truth, legal conclusion, attribution proof, or required-action guidance."
        ),
    ),
    DataAiFeedSourceDefinition(
        source_id="access-now",
        source_name="Access Now",
        source_category="digital-rights",
        feed_url="https://www.accessnow.org/feed/",
        fixture_file_name="access_now.xml",
        evidence_basis="contextual",
        caveat=(
            "Access Now items are advocacy and digital-rights context, not official source truth, incident confirmation, legal conclusion, or required-action guidance."
        ),
    ),
    DataAiFeedSourceDefinition(
        source_id="privacy-international",
        source_name="Privacy International",
        source_category="digital-rights",
        feed_url="https://privacyinternational.org/rss.xml",
        fixture_file_name="privacy_international.xml",
        evidence_basis="contextual",
        caveat=(
            "Privacy International items are civic and privacy-rights context, not official incident truth, attribution proof, legal conclusion, or required-action guidance."
        ),
    ),
    DataAiFeedSourceDefinition(
        source_id="freedom-house",
        source_name="Freedom House",
        source_category="democracy-rights",
        feed_url="https://freedomhouse.org/rss.xml",
        fixture_file_name="freedom_house.xml",
        evidence_basis="contextual",
        caveat=(
            "Freedom House items are rights and democracy context, not official incident truth, legal conclusion, attribution proof, or required-action guidance."
        ),
    ),
    DataAiFeedSourceDefinition(
        source_id="full-fact",
        source_name="Full Fact",
        source_category="fact-checking",
        feed_url="https://fullfact.org/feed/",
        fixture_file_name="full_fact.xml",
        evidence_basis="contextual",
        caveat=(
            "Full Fact items are fact-checking context about claims and public statements, not universal ground truth, legal conclusion, or required-action guidance."
        ),
    ),
    DataAiFeedSourceDefinition(
        source_id="snopes",
        source_name="Snopes",
        source_category="fact-checking",
        feed_url="https://www.snopes.com/feed/",
        fixture_file_name="snopes.xml",
        evidence_basis="contextual",
        caveat=(
            "Snopes items are fact-checking and misinformation-review context, not universal truth adjudication, legal proof, or required-action guidance."
        ),
    ),
    DataAiFeedSourceDefinition(
        source_id="politifact",
        source_name="PolitiFact",
        source_category="fact-checking",
        feed_url="https://www.politifact.com/rss/all/",
        fixture_file_name="politifact.xml",
        evidence_basis="contextual",
        caveat=(
            "PolitiFact items are claim-rating and political fact-checking context, not universal truth adjudication, legal conclusion, or required-action guidance."
        ),
    ),
    DataAiFeedSourceDefinition(
        source_id="factcheck-org",
        source_name="FactCheck.org",
        source_category="fact-checking",
        feed_url="https://www.factcheck.org/feed/",
        fixture_file_name="factcheck_org.xml",
        evidence_basis="contextual",
        caveat=(
            "FactCheck.org items are fact-checking context about claims and narratives, not universal ground truth, legal conclusion, or required-action guidance."
        ),
    ),
    DataAiFeedSourceDefinition(
        source_id="euvsdisinfo",
        source_name="EUvsDisinfo",
        source_category="disinformation",
        feed_url="https://euvsdisinfo.eu/feed/",
        fixture_file_name="euvsdisinfo.xml",
        evidence_basis="contextual",
        caveat=(
            "EUvsDisinfo items are disinformation-monitoring context, not universal truth adjudication, attribution proof, legal conclusion, or required-action guidance."
        ),
    ),
    DataAiFeedSourceDefinition(
        source_id="gdacs-alerts",
        source_name="GDACS Alerts",
        source_category="world-events",
        feed_url="https://www.gdacs.org/xml/rss.xml",
        fixture_file_name="gdacs_alerts.xml",
        evidence_basis="advisory",
        caveat=(
            "GDACS alerts are disaster alert context, not proof of realized impact, damage, casualties, or public-safety consequence."
        ),
    ),
    DataAiFeedSourceDefinition(
        source_id="state-travel-advisories",
        source_name="U.S. State Department Travel Advisories",
        source_category="travel-security",
        feed_url="https://travel.state.gov/_res/rss/TAsTWs.xml",
        fixture_file_name="state_travel_advisories.xml",
        evidence_basis="advisory",
        caveat=(
            "U.S. State travel advisories are official advisory/guidance context only; they do not by themselves prove on-the-ground conditions, incident realization, or required action for every traveler."
        ),
    ),
    DataAiFeedSourceDefinition(
        source_id="eu-commission-press",
        source_name="European Commission Press Corner",
        source_category="policy-official",
        feed_url="https://ec.europa.eu/commission/presscorner/api/rss",
        fixture_file_name="eu_commission_press.xml",
        evidence_basis="contextual",
        caveat=(
            "European Commission press items are official institutional context and source-reported policy or announcement text, not field confirmation, legal conclusion, or required action."
        ),
    ),
    DataAiFeedSourceDefinition(
        source_id="un-press-releases",
        source_name="United Nations Press Releases",
        source_category="world-events",
        feed_url="https://press.un.org/en/rss.xml",
        fixture_file_name="un_press_releases.xml",
        evidence_basis="contextual",
        caveat=(
            "UN press releases are official institutional statements and contextual reporting, not independent field confirmation, legal conclusion, or attribution proof."
        ),
    ),
    DataAiFeedSourceDefinition(
        source_id="unaids-news",
        source_name="UNAIDS News",
        source_category="world-health",
        feed_url="https://www.unaids.org/en/rss.xml",
        fixture_file_name="unaids_news.xml",
        evidence_basis="contextual",
        caveat=(
            "UNAIDS news items are official public-health and program context, not medical diagnosis, field confirmation, or required-action guidance."
        ),
    ),
    DataAiFeedSourceDefinition(
        source_id="who-news",
        source_name="World Health Organization News",
        source_category="world-health",
        feed_url="https://www.who.int/rss-feeds/news-english.xml",
        fixture_file_name="who_news.xml",
        evidence_basis="contextual",
        caveat=(
            "WHO news items are official public-health and institutional context only; they are not outbreak proof, field confirmation, medical diagnosis, or required-action guidance."
        ),
    ),
    DataAiFeedSourceDefinition(
        source_id="undrr-news",
        source_name="UNDRR News",
        source_category="disaster-risk",
        feed_url="https://www.undrr.org/rss.xml",
        fixture_file_name="undrr_news.xml",
        evidence_basis="contextual",
        caveat=(
            "UNDRR news items are disaster-risk reduction and resilience context only; they are not disaster impact proof, casualty confirmation, or required-action guidance."
        ),
    ),
    DataAiFeedSourceDefinition(
        source_id="nasa-breaking-news",
        source_name="NASA News Releases",
        source_category="space-agency",
        feed_url="https://www.nasa.gov/news-release/feed/",
        fixture_file_name="nasa_breaking_news.xml",
        evidence_basis="contextual",
        caveat=(
            "NASA news-release items are official mission, science, and public institutional context only; they are not live hazard confirmation, public-safety proof, or required-action guidance."
        ),
    ),
    DataAiFeedSourceDefinition(
        source_id="noaa-news",
        source_name="NOAA News",
        source_category="weather-climate",
        feed_url="https://www.noaa.gov/rss.xml",
        fixture_file_name="noaa_news.xml",
        evidence_basis="contextual",
        caveat=(
            "NOAA news items are official weather, climate, ocean, and institutional context only; they are not local hazard confirmation, forecast guarantee, or required-action guidance."
        ),
    ),
    DataAiFeedSourceDefinition(
        source_id="esa-news",
        source_name="ESA Top News",
        source_category="space-agency",
        feed_url="https://www.esa.int/rssfeed/TopNews",
        fixture_file_name="esa_news.xml",
        evidence_basis="contextual",
        caveat=(
            "ESA news items are official space, Earth-observation, and institutional context only; they are not live event confirmation, operational directive, or required-action guidance."
        ),
    ),
    DataAiFeedSourceDefinition(
        source_id="fda-news",
        source_name="FDA Press Releases",
        source_category="public-health-regulator",
        feed_url="https://www.fda.gov/about-fda/contact-fda/stay-informed/rss-feeds/press-releases/rss.xml",
        fixture_file_name="fda_news.xml",
        evidence_basis="contextual",
        caveat=(
            "FDA press-release items are official regulatory and public-health announcement context only; they are not personal medical advice, product harm proof, or required-action guidance."
        ),
    ),
    DataAiFeedSourceDefinition(
        source_id="our-world-in-data",
        source_name="Our World in Data",
        source_category="data-research",
        feed_url="https://ourworldindata.org/atom.xml",
        fixture_file_name="our_world_in_data.xml",
        evidence_basis="contextual",
        caveat=(
            "Our World in Data items are research and explanatory context, not primary event truth, field confirmation, or required-action guidance."
        ),
    ),
    DataAiFeedSourceDefinition(
        source_id="carbon-brief",
        source_name="Carbon Brief",
        source_category="environment",
        feed_url="https://www.carbonbrief.org/feed/",
        fixture_file_name="carbon_brief.xml",
        evidence_basis="contextual",
        caveat=(
            "Carbon Brief items are climate and environmental reporting context, not primary hazard confirmation, scientific certainty proof, or required-action guidance."
        ),
    ),
    DataAiFeedSourceDefinition(
        source_id="eumetsat-news",
        source_name="EUMETSAT News",
        source_category="weather-space",
        feed_url="https://www.eumetsat.int/rss.xml",
        fixture_file_name="eumetsat_news.xml",
        evidence_basis="contextual",
        caveat=(
            "EUMETSAT news items are weather, climate, and Earth-observation context, not live hazard confirmation, operational forecast truth, or required-action guidance."
        ),
    ),
    DataAiFeedSourceDefinition(
        source_id="smithsonian-volcano-news",
        source_name="Smithsonian Volcano News",
        source_category="science-events",
        feed_url="https://volcano.si.edu/news/WeeklyVolcanoRSS.xml",
        fixture_file_name="smithsonian_volcano_news.xml",
        evidence_basis="contextual",
        caveat=(
            "Smithsonian Volcano News items are volcano and science-news context, not live eruption confirmation, geospatial event truth, or required-action guidance."
        ),
    ),
    DataAiFeedSourceDefinition(
        source_id="eos-news",
        source_name="Eos News",
        source_category="science-events",
        feed_url="https://eos.org/feed",
        fixture_file_name="eos_news.xml",
        evidence_basis="contextual",
        caveat=(
            "Eos News items are Earth and space science reporting context, not primary event confirmation, scientific certainty proof, or required-action guidance."
        ),
    ),
    DataAiFeedSourceDefinition(
        source_id="atlantic-council",
        source_name="Atlantic Council",
        source_category="policy-thinktank",
        feed_url="https://www.atlanticcouncil.org/feed/",
        fixture_file_name="atlantic_council.xml",
        evidence_basis="contextual",
        caveat=(
            "Atlantic Council items are policy and strategy commentary context, not event confirmation, field truth, intent proof, or required-action guidance."
        ),
    ),
    DataAiFeedSourceDefinition(
        source_id="ecfr",
        source_name="European Council on Foreign Relations",
        source_category="policy-thinktank",
        feed_url="https://ecfr.eu/feed/",
        fixture_file_name="ecfr.xml",
        evidence_basis="contextual",
        caveat=(
            "ECFR items are policy-analysis context, not event confirmation, geopolitical truth, escalation prediction, or required-action guidance."
        ),
    ),
    DataAiFeedSourceDefinition(
        source_id="war-on-the-rocks",
        source_name="War on the Rocks",
        source_category="security-analysis",
        feed_url="https://warontherocks.com/feed/",
        fixture_file_name="war_on_the_rocks.xml",
        evidence_basis="contextual",
        caveat=(
            "War on the Rocks items are strategy and security commentary context, not event confirmation, field truth, threat rating, or operational recommendation."
        ),
    ),
    DataAiFeedSourceDefinition(
        source_id="modern-war-institute",
        source_name="Modern War Institute",
        source_category="security-analysis",
        feed_url="https://mwi.westpoint.edu/feed/",
        fixture_file_name="modern_war_institute.xml",
        evidence_basis="contextual",
        caveat=(
            "Modern War Institute items are military-analysis and commentary context, not event confirmation, operational truth, targeting support, or required-action guidance."
        ),
    ),
    DataAiFeedSourceDefinition(
        source_id="irregular-warfare",
        source_name="Irregular Warfare Initiative",
        source_category="security-analysis",
        feed_url="https://irregularwarfare.org/feed/",
        fixture_file_name="irregular_warfare.xml",
        evidence_basis="contextual",
        caveat=(
            "Irregular Warfare Initiative items are analysis and commentary context, not event confirmation, attribution proof, threat rating, or operational recommendation."
        ),
    ),
    DataAiFeedSourceDefinition(
        source_id="google-security-blog",
        source_name="Google Security Blog",
        source_category="cyber-vendor",
        feed_url="https://security.googleblog.com/feeds/posts/default",
        fixture_file_name="google_security_blog.xml",
        evidence_basis="contextual",
        caveat=(
            "Google Security Blog items are vendor security updates and research context, not independent incident confirmation, exploitation proof, or required-action guidance."
        ),
    ),
    DataAiFeedSourceDefinition(
        source_id="bleepingcomputer",
        source_name="BleepingComputer",
        source_category="cyber-media",
        feed_url="https://www.bleepingcomputer.com/feed/",
        fixture_file_name="bleepingcomputer.xml",
        evidence_basis="contextual",
        caveat=(
            "BleepingComputer items are cyber-news context, not direct incident confirmation, compromise proof, or required-action guidance."
        ),
    ),
    DataAiFeedSourceDefinition(
        source_id="krebs-on-security",
        source_name="Krebs on Security",
        source_category="cyber-media",
        feed_url="https://krebsonsecurity.com/feed/",
        fixture_file_name="krebs_on_security.xml",
        evidence_basis="contextual",
        caveat=(
            "Krebs on Security items are investigative cyber-reporting context, not direct incident confirmation, attribution proof, or required-action guidance."
        ),
    ),
    DataAiFeedSourceDefinition(
        source_id="securityweek",
        source_name="SecurityWeek",
        source_category="cyber-media",
        feed_url="https://www.securityweek.com/feed/",
        fixture_file_name="securityweek.xml",
        evidence_basis="contextual",
        caveat=(
            "SecurityWeek items are cyber-industry news context, not incident confirmation, exploitation proof, or required-action guidance."
        ),
    ),
    DataAiFeedSourceDefinition(
        source_id="dfrlab",
        source_name="DFRLab",
        source_category="disinformation",
        feed_url="https://dfrlab.org/feed/",
        fixture_file_name="dfrlab.xml",
        evidence_basis="contextual",
        caveat=(
            "DFRLab items are research and disinformation-monitoring context, not direct incident confirmation, attribution proof, or required-action guidance."
        ),
    ),
)


DATA_AI_MULTI_FEED_SOURCE_IDS: tuple[str, ...] = tuple(definition.source_id for definition in DATA_AI_MULTI_FEED_DEFINITIONS)


DATA_AI_FEED_FAMILY_DEFINITIONS: tuple[DataAiFeedFamilyDefinition, ...] = (
    DataAiFeedFamilyDefinition(
        family_id="official-advisories",
        family_label="Official Advisories",
        source_ids=(
            "cisa-cybersecurity-advisories",
            "cisa-ics-advisories",
            "ncsc-uk-all",
            "cert-fr-alerts",
            "cert-fr-advisories",
        ),
        tags=("official", "advisory", "cyber"),
        caveat=(
            "Official-advisory family rows summarize source availability and advisory/context posture only; they do not prove exploitation, compromise, incident confirmation, realized impact, or required action."
        ),
    ),
    DataAiFeedFamilyDefinition(
        family_id="cyber-institutional-watch-context",
        family_label="Cyber Institutional Watch Context",
        source_ids=(
            "cisa-news",
            "jvn-en-new",
            "debian-security",
            "microsoft-security-blog",
            "cisco-talos-blog",
            "mozilla-security-blog",
            "github-security-blog",
        ),
        tags=("cyber", "institutional", "watch", "contextual"),
        caveat=(
            "Cyber institutional watch rows summarize official cyber announcements, advisory ecosystems, distribution security notices, and vendor/platform security watch context only; they do not create exploitation proof, compromise proof, incident confirmation, attribution proof, remediation priority, or required-action guidance."
        ),
    ),
    DataAiFeedFamilyDefinition(
        family_id="official-public-advisories",
        family_label="Official and Public Advisories",
        source_ids=(
            "state-travel-advisories",
            "eu-commission-press",
            "un-press-releases",
            "unaids-news",
        ),
        tags=("official", "public", "advisory", "press"),
        caveat=(
            "Official/public advisory rows summarize source-claimed guidance, announcements, and institutional context only; they do not create field confirmation, legal conclusions, impact proof, or required-action guidance."
        ),
    ),
    DataAiFeedFamilyDefinition(
        family_id="public-institution-world-context",
        family_label="Public Institution and World Context",
        source_ids=(
            "who-news",
            "undrr-news",
            "nasa-breaking-news",
            "noaa-news",
            "esa-news",
            "fda-news",
        ),
        tags=("public", "institutional", "world-context", "contextual"),
        caveat=(
            "Public institution/world-context rows summarize official institutional, health, disaster-risk, space, weather, and regulatory context only; they do not create field confirmation, impact proof, legal conclusions, personal medical advice, or required-action guidance."
        ),
    ),
    DataAiFeedFamilyDefinition(
        family_id="scientific-environmental-context",
        family_label="Scientific and Environmental Context",
        source_ids=(
            "our-world-in-data",
            "carbon-brief",
            "eumetsat-news",
            "smithsonian-volcano-news",
            "eos-news",
        ),
        tags=("science", "environmental", "research", "contextual"),
        caveat=(
            "Scientific/environmental rows summarize research, reporting, and science-communication context only; they do not create primary event truth, scientific certainty proof, health-risk conclusions, or required-action guidance."
        ),
    ),
    DataAiFeedFamilyDefinition(
        family_id="policy-thinktank-commentary",
        family_label="Policy and Think-Tank Commentary",
        source_ids=(
            "atlantic-council",
            "ecfr",
            "war-on-the-rocks",
            "modern-war-institute",
            "irregular-warfare",
        ),
        tags=("policy", "think-tank", "analysis", "contextual"),
        caveat=(
            "Policy/think-tank rows summarize commentary, analysis, and scenario framing only; they do not create event confirmation, intent proof, escalation prediction, threat ratings, or required-action guidance."
        ),
    ),
    DataAiFeedFamilyDefinition(
        family_id="cyber-vendor-community-follow-on",
        family_label="Cyber Vendor and Community Follow-On",
        source_ids=(
            "google-security-blog",
            "bleepingcomputer",
            "krebs-on-security",
            "securityweek",
            "dfrlab",
        ),
        tags=("cyber", "vendor", "media", "research", "contextual"),
        caveat=(
            "Cyber vendor/community rows summarize vendor updates, cyber media, and research context only; they do not create incident confirmation, exploitation proof, compromise proof, attribution proof, or required-action guidance."
        ),
    ),
    DataAiFeedFamilyDefinition(
        family_id="cyber-internet-platform-watch",
        family_label="Cyber and Internet Platform Watch",
        source_ids=(
            "trailofbits-blog",
            "mozilla-hacks",
            "chromium-blog",
            "webdev-google",
            "gitlab-releases",
            "github-changelog",
        ),
        tags=("cyber", "internet", "platform", "release", "contextual"),
        caveat=(
            "Cyber/internet platform-watch rows summarize security research, browser engineering, web-platform guidance, and release/changelog context only; they do not create incident confirmation, exploit proof, standards compliance truth, or required-action guidance."
        ),
    ),
    DataAiFeedFamilyDefinition(
        family_id="cyber-community-context",
        family_label="Cyber Community Context",
        source_ids=("sans-isc-diary",),
        tags=("cyber", "community", "contextual"),
        caveat=(
            "Cyber community rows summarize analyst/community context only; they do not convert commentary into official truth, incident proof, or validated action guidance."
        ),
    ),
    DataAiFeedFamilyDefinition(
        family_id="world-news-awareness",
        family_label="World News Awareness",
        source_ids=(
            "bbc-world",
            "guardian-world",
            "aljazeera-all",
            "dw-all",
            "france24-en",
            "npr-world",
        ),
        tags=("media", "world-news", "awareness", "contextual"),
        caveat=(
            "World-news-awareness rows summarize broad media context only; they do not create primary event truth, field confirmation, impact certainty, intent proof, legal status, attribution proof, or required-action guidance."
        ),
    ),
    DataAiFeedFamilyDefinition(
        family_id="infrastructure-status",
        family_label="Infrastructure and Status",
        source_ids=(
            "cloudflare-status",
            "cloudflare-radar",
            "netblocks",
            "apnic-blog",
        ),
        tags=("internet", "status", "measurement", "infrastructure"),
        caveat=(
            "Infrastructure/status family rows summarize provider, measurement, and infrastructure context only; they do not create whole-internet truth, outage proof, or causation proof."
        ),
    ),
    DataAiFeedFamilyDefinition(
        family_id="internet-governance-standards-context",
        family_label="Internet Governance and Standards Context",
        source_ids=(
            "ripe-labs",
            "internet-society",
            "lacnic-news",
            "w3c-news",
            "letsencrypt",
        ),
        tags=("internet", "governance", "standards", "operations", "contextual"),
        caveat=(
            "Internet governance/standards rows summarize policy, standards, registry, and network-operations context only; they do not create whole-internet truth, outage proof, standards compliance conclusions, or required-action guidance."
        ),
    ),
    DataAiFeedFamilyDefinition(
        family_id="osint-investigations",
        family_label="OSINT and Investigations",
        source_ids=(
            "bellingcat",
            "citizen-lab",
            "occrp",
            "icij",
        ),
        tags=("osint", "investigations", "research", "contextual"),
        caveat=(
            "OSINT/investigations family rows summarize investigative and research context only; they do not create official incident truth, legal conclusions, or standalone attribution proof."
        ),
    ),
    DataAiFeedFamilyDefinition(
        family_id="investigative-civic-context",
        family_label="Investigative and Civic Context",
        source_ids=(
            "propublica",
            "global-voices",
        ),
        tags=("investigations", "civic", "public-interest", "contextual"),
        caveat=(
            "Investigative/civic rows summarize investigative, translation, public-interest, and civic-accountability context only; they do not create official event truth, wrongdoing proof, intent proof, legal conclusions, or required-action guidance."
        ),
    ),
    DataAiFeedFamilyDefinition(
        family_id="rights-civic-digital-policy",
        family_label="Rights, Civic, and Digital Policy",
        source_ids=(
            "eff-updates",
            "access-now",
            "privacy-international",
            "freedom-house",
        ),
        tags=("rights", "civic", "policy", "contextual"),
        caveat=(
            "Rights/civic family rows summarize advocacy, policy, and rights context only; they do not create official incident truth, legal conclusions, or required-action guidance."
        ),
    ),
    DataAiFeedFamilyDefinition(
        family_id="fact-checking-disinformation",
        family_label="Fact-Checking and Disinformation",
        source_ids=(
            "full-fact",
            "snopes",
            "politifact",
            "factcheck-org",
            "euvsdisinfo",
        ),
        tags=("fact-checking", "disinformation", "claims", "contextual"),
        caveat=(
            "Fact-checking/disinformation family rows summarize claim-review and monitoring context only; they do not create universal truth adjudication, attribution proof, legal conclusions, or required-action guidance."
        ),
    ),
    DataAiFeedFamilyDefinition(
        family_id="world-events-disaster-alerts",
        family_label="World Events and Disaster Alerts",
        source_ids=("gdacs-alerts",),
        tags=("world-events", "disaster-alerts", "advisory"),
        caveat=(
            "World-events/disaster rows summarize alert context only; they do not prove realized damage, casualties, public-safety consequence, or operational impact."
        ),
    ),
)


DATA_AI_FEED_FAMILY_IDS: tuple[str, ...] = tuple(definition.family_id for definition in DATA_AI_FEED_FAMILY_DEFINITIONS)

DATA_AI_FEED_FAMILY_DEFINITION_BY_ID: dict[str, DataAiFeedFamilyDefinition] = {
    definition.family_id: definition for definition in DATA_AI_FEED_FAMILY_DEFINITIONS
}

DATA_AI_FEED_SOURCE_ID_TO_FAMILY_ID: dict[str, str] = {
    source_id: definition.family_id
    for definition in DATA_AI_FEED_FAMILY_DEFINITIONS
    for source_id in definition.source_ids
}
