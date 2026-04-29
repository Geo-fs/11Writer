from src.reference.ingest.parsers.airport_codes import parse_airport_codes_dataset
from src.reference.ingest.parsers.fixes import parse_fixes_dataset
from src.reference.ingest.parsers.ourairports import parse_ourairports_dataset
from src.reference.ingest.parsers.places import parse_places_dataset


PARSERS = {
    "airport-codes": parse_airport_codes_dataset,
    "ourairports": parse_ourairports_dataset,
    "places": parse_places_dataset,
    "fixes": parse_fixes_dataset,
}
