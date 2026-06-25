from data.abilities import get_ability_definition
from data.ability_link_candidates_97039 import (
    ABILITY_LINK_CANDIDATE_SOURCE_97039,
    ABILITY_LINK_CANDIDATES_97039,
    HERO_ABILITY_CANDIDATES_97039,
    AbilityCandidate,
)


def test_ability_link_candidates_are_current_build_unconfirmed_rows():
    assert ABILITY_LINK_CANDIDATE_SOURCE_97039["build"] == 97039
    assert ABILITY_LINK_CANDIDATE_SOURCE_97039["candidate_rows"] == len(ABILITY_LINK_CANDIDATES_97039)
    assert ABILITY_LINK_CANDIDATE_SOURCE_97039["candidate_rows"] == 1212

    for row in ABILITY_LINK_CANDIDATES_97039:
        assert get_ability_definition(row.ability_link, row.ability_cmd_index, 97039) is None
        assert HERO_ABILITY_CANDIDATES_97039[row.hero_catalog_name]


def test_ability_link_candidates_include_catalog_options_for_review():
    nazeebo = next(
        row
        for row in ABILITY_LINK_CANDIDATES_97039
        if row.hero_name == "Nazeebo" and row.ability_link == 690 and row.ability_cmd_index == 0
    )

    assert nazeebo.ability_tag == 22080
    assert nazeebo.count == 4996
    assert nazeebo.target_types == {"TargetPoint": 4996}
    assert AbilityCandidate("WitchDoctorCorpseSpiders", "Corpse Spiders") in HERO_ABILITY_CANDIDATES_97039[
        nazeebo.hero_catalog_name
    ]
