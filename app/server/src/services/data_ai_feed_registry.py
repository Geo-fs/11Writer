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
)


DATA_AI_MULTI_FEED_SOURCE_IDS: tuple[str, ...] = tuple(definition.source_id for definition in DATA_AI_MULTI_FEED_DEFINITIONS)
