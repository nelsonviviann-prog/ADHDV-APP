"""
Nigerian teaching hospital + Federal Neuro-Psychiatric Hospital directory,
covering all 36 states + FCT. Used to auto-route a screening referral to
the closest tertiary child & adolescent mental health unit.

Sources: Federal Ministry of Health hospital register; Medical and Dental
Council of Nigeria (MDCN) accredited teaching hospital list. Phone numbers
are intentionally omitted because they change frequently and incorrect
clinical contact info is dangerous; users should call the hospital's main
switchboard or visit the hospital website.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Hospital:
    name: str
    abbreviation: str
    city: str
    state: str
    zone: str
    kind: str  # 'federal_teaching' | 'state_teaching' | 'federal_neuro_psychiatric' | 'specialist'
    has_child_psych_unit: bool = True


HOSPITALS: list[Hospital] = [
    # ---- South-West ----
    Hospital("Lagos University Teaching Hospital", "LUTH", "Idi-Araba, Lagos", "Lagos", "South-West", "federal_teaching"),
    Hospital("Federal Neuro-Psychiatric Hospital, Yaba", "FNPHY", "Yaba, Lagos", "Lagos", "South-West", "federal_neuro_psychiatric"),
    Hospital("Lagos State University Teaching Hospital", "LASUTH", "Ikeja, Lagos", "Lagos", "South-West", "state_teaching"),
    Hospital("University College Hospital, Ibadan", "UCH", "Ibadan", "Oyo", "South-West", "federal_teaching"),
    Hospital("Obafemi Awolowo University Teaching Hospitals Complex", "OAUTHC", "Ile-Ife", "Osun", "South-West", "federal_teaching"),
    Hospital("Federal Neuro-Psychiatric Hospital, Aro", "FNPHA", "Abeokuta", "Ogun", "South-West", "federal_neuro_psychiatric"),
    Hospital("Federal Teaching Hospital, Ido-Ekiti", "FETHI", "Ido-Ekiti", "Ekiti", "South-West", "federal_teaching"),
    Hospital("Federal Medical Centre, Owo", "FMC Owo", "Owo", "Ondo", "South-West", "federal_teaching"),

    # ---- South-East ----
    Hospital("University of Nigeria Teaching Hospital", "UNTH", "Ituku-Ozalla, Enugu", "Enugu", "South-East", "federal_teaching"),
    Hospital("Federal Neuro-Psychiatric Hospital, Enugu", "FNPHE", "Enugu", "Enugu", "South-East", "federal_neuro_psychiatric"),
    Hospital("Nnamdi Azikiwe University Teaching Hospital", "NAUTH", "Nnewi", "Anambra", "South-East", "federal_teaching"),
    Hospital("Federal Teaching Hospital, Abakaliki", "FETHA", "Abakaliki", "Ebonyi", "South-East", "federal_teaching"),
    Hospital("Federal Medical Centre, Owerri", "FMC Owerri", "Owerri", "Imo", "South-East", "federal_teaching"),
    Hospital("Abia State University Teaching Hospital", "ABSUTH", "Aba", "Abia", "South-East", "state_teaching"),

    # ---- South-South ----
    Hospital("University of Port Harcourt Teaching Hospital", "UPTH", "Port Harcourt", "Rivers", "South-South", "federal_teaching"),
    Hospital("University of Benin Teaching Hospital", "UBTH", "Benin City", "Edo", "South-South", "federal_teaching"),
    Hospital("University of Calabar Teaching Hospital", "UCTH", "Calabar", "Cross River", "South-South", "federal_teaching"),
    Hospital("Federal Neuro-Psychiatric Hospital, Calabar", "FNPHC", "Calabar", "Cross River", "South-South", "federal_neuro_psychiatric"),
    Hospital("University of Uyo Teaching Hospital", "UUTH", "Uyo", "Akwa Ibom", "South-South", "federal_teaching"),
    Hospital("Niger Delta University Teaching Hospital", "NDUTH", "Okolobiri", "Bayelsa", "South-South", "state_teaching"),
    Hospital("Delta State University Teaching Hospital", "DELSUTH", "Oghara", "Delta", "South-South", "state_teaching"),

    # ---- North-Central ----
    Hospital("Jos University Teaching Hospital", "JUTH", "Jos", "Plateau", "North-Central", "federal_teaching"),
    Hospital("University of Abuja Teaching Hospital", "UATH", "Gwagwalada, FCT", "FCT", "North-Central", "federal_teaching"),
    Hospital("National Hospital Abuja", "NHA", "Abuja", "FCT", "North-Central", "specialist"),
    Hospital("University of Ilorin Teaching Hospital", "UITH", "Ilorin", "Kwara", "North-Central", "federal_teaching"),
    Hospital("Benue State University Teaching Hospital", "BSUTH", "Makurdi", "Benue", "North-Central", "state_teaching"),
    Hospital("Federal Medical Centre, Bida", "FMC Bida", "Bida", "Niger", "North-Central", "federal_teaching"),
    Hospital("Dalhatu Araf Specialist Hospital", "DASH", "Lafia", "Nasarawa", "North-Central", "specialist"),
    Hospital("Federal Medical Centre, Lokoja", "FMC Lokoja", "Lokoja", "Kogi", "North-Central", "federal_teaching"),

    # ---- North-West ----
    Hospital("Aminu Kano Teaching Hospital", "AKTH", "Kano", "Kano", "North-West", "federal_teaching"),
    Hospital("Murtala Mohammed Specialist Hospital", "MMSH", "Kano", "Kano", "North-West", "specialist"),
    Hospital("Ahmadu Bello University Teaching Hospital", "ABUTH", "Zaria", "Kaduna", "North-West", "federal_teaching"),
    Hospital("Barau Dikko Teaching Hospital", "BDTH", "Kaduna", "Kaduna", "North-West", "state_teaching"),
    Hospital("Usmanu Danfodiyo University Teaching Hospital", "UDUTH", "Sokoto", "Sokoto", "North-West", "federal_teaching"),
    Hospital("Federal Neuro-Psychiatric Hospital, Kware", "FNPHK", "Kware", "Sokoto", "North-West", "federal_neuro_psychiatric"),
    Hospital("Federal Medical Centre, Birnin Kebbi", "FMC Kebbi", "Birnin Kebbi", "Kebbi", "North-West", "federal_teaching"),
    Hospital("Federal Medical Centre, Gusau", "FMC Gusau", "Gusau", "Zamfara", "North-West", "federal_teaching"),
    Hospital("Federal Medical Centre, Katsina", "FMC Katsina", "Katsina", "Katsina", "North-West", "federal_teaching"),
    Hospital("Federal Medical Centre, Jigawa", "FMC Jigawa", "Birnin Kudu", "Jigawa", "North-West", "federal_teaching"),

    # ---- North-East ----
    Hospital("University of Maiduguri Teaching Hospital", "UMTH", "Maiduguri", "Borno", "North-East", "federal_teaching"),
    Hospital("Abubakar Tafawa Balewa University Teaching Hospital", "ATBUTH", "Bauchi", "Bauchi", "North-East", "federal_teaching"),
    Hospital("Federal Teaching Hospital, Gombe", "FTHG", "Gombe", "Gombe", "North-East", "federal_teaching"),
    Hospital("Federal Medical Centre, Yola", "FMC Yola", "Yola", "Adamawa", "North-East", "federal_teaching"),
    Hospital("Federal Medical Centre, Jalingo", "FMC Jalingo", "Jalingo", "Taraba", "North-East", "federal_teaching"),
    Hospital("Federal Medical Centre, Nguru", "FMC Nguru", "Nguru", "Yobe", "North-East", "federal_teaching"),
]


def all_states() -> list[str]:
    return sorted({h.state for h in HOSPITALS})


def hospitals_by_state(state: str) -> list[Hospital]:
    return [h for h in HOSPITALS if h.state.lower() == state.lower()]


def hospitals_by_zone(zone: str) -> list[Hospital]:
    return [h for h in HOSPITALS if h.zone == zone]


def referral_recommendations(state: str, max_results: int = 5) -> list[Hospital]:
    """
    Pick the most appropriate tertiary facilities for a child living in `state`.

    Priority order:
      1. Federal Neuro-Psychiatric Hospital in the same state (best-fit clinically).
      2. Federal teaching hospital in the same state.
      3. Other tertiary hospitals in the same state.
      4. Fall back to nearest hospital in the same geopolitical zone.
    """
    in_state = hospitals_by_state(state)
    same_state_neuro = [h for h in in_state if h.kind == "federal_neuro_psychiatric"]
    same_state_fed = [h for h in in_state if h.kind == "federal_teaching"]
    same_state_other = [h for h in in_state if h not in same_state_neuro + same_state_fed]

    ordered = same_state_neuro + same_state_fed + same_state_other

    if len(ordered) < max_results:
        zone = next((h.zone for h in in_state), None)
        if zone:
            zonal = [h for h in hospitals_by_zone(zone) if h not in ordered]
            zonal.sort(key=lambda h: (h.kind != "federal_neuro_psychiatric", h.kind != "federal_teaching"))
            ordered.extend(zonal)

    return ordered[:max_results]


NIGERIAN_STATES_AND_FCT: list[str] = [
    "Abia", "Adamawa", "Akwa Ibom", "Anambra", "Bauchi", "Bayelsa", "Benue", "Borno",
    "Cross River", "Delta", "Ebonyi", "Edo", "Ekiti", "Enugu", "FCT", "Gombe", "Imo",
    "Jigawa", "Kaduna", "Kano", "Katsina", "Kebbi", "Kogi", "Kwara", "Lagos",
    "Nasarawa", "Niger", "Ogun", "Ondo", "Osun", "Oyo", "Plateau", "Rivers",
    "Sokoto", "Taraba", "Yobe", "Zamfara",
]
