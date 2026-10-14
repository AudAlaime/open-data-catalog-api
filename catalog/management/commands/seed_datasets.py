from django.core.management.base import BaseCommand

from catalog.models import Dataset

DATASETS = [
    {
        "title": "Diagnostics de performance énergétique des logements",
        "description": "Diagnostics énergétiques réalisés sur les logements existants.",
        "producer": "ADEME",
        "theme": "energy",
        "tags": ["energy", "housing", "DPE"],
        "source_url": "https://data.ademe.fr/datasets/dpe-v2-logements-existants",
        "license": "Licence Ouverte 2.0",
    },
    {
        "title": "Bornes de recharge pour véhicules électriques",
        "description": "Implantation des infrastructures de recharge électrique.",
        "producer": "ADEME",
        "theme": "energy",
        "tags": ["energy", "transport", "electric vehicles"],
        "source_url": "https://data.ademe.fr/datasets/bornes-de-recharge",
        "license": "Licence Ouverte 2.0",
    },
    {
        "title": "Horaires des transports collectifs",
        "description": "Horaires théoriques des réseaux de transport public français.",
        "producer": "data.gouv.fr",
        "theme": "transport",
        "tags": ["transport", "bus", "train"],
        "source_url": "https://transport.data.gouv.fr/datasets/horaires-theoriques",
        "license": "Licence Ouverte 2.0",
    },
    {
        "title": "Logements par commune",
        "description": "Nombre et caractéristiques des logements dans chaque commune.",
        "producer": "INSEE",
        "theme": "housing",
        "tags": ["housing", "population", "municipalities"],
        "source_url": "https://www.insee.fr/fr/statistiques/6456056",
        "license": "Licence Ouverte 2.0",
    },
    {
        "title": "Mesures de la qualité de l'air",
        "description": "Mesures territoriales des principaux polluants atmosphériques.",
        "producer": "Métropole de Lyon",
        "theme": "environment",
        "tags": ["environment", "air quality", "pollution"],
        "source_url": "https://data.grandlyon.com/portail/fr/jeux-de-donnees/qualite-air",
        "license": "Licence Ouverte 2.0",
    },
    {
        "title": "Contours administratifs français",
        "description": "Contours géographiques des régions, départements et communes.",
        "producer": "Etalab",
        "theme": "geography",
        "tags": ["geography", "boundaries", "municipalities"],
        "source_url": "https://www.data.gouv.fr/fr/datasets/contours-administratifs/",
        "license": "Licence Ouverte 2.0",
    },
    {
        "title": "Réseau cyclable parisien",
        "description": "Aménagements et itinéraires cyclables de la Ville de Paris.",
        "producer": "Ville de Paris",
        "theme": "transport",
        "tags": ["transport", "cycling", "Paris"],
        "source_url": "https://opendata.paris.fr/explore/dataset/reseau-cyclable/",
        "license": "Open Database License",
    },
]


class Command(BaseCommand):
    help = "Create example public datasets for local development."

    def handle(self, *args: object, **options: object) -> None:
        created_count = 0

        for values in DATASETS:
            source_url = values["source_url"]
            defaults = {
                key: value for key, value in values.items() if key != "source_url"
            }
            _, created = Dataset.objects.get_or_create(
                source_url=source_url,
                defaults=defaults,
            )
            created_count += int(created)

        existing_count = len(DATASETS) - created_count
        self.stdout.write(
            self.style.SUCCESS(
                f"Seed complete: {created_count} created, "
                f"{existing_count} already existed."
            )
        )
