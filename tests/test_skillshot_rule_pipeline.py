from data.abilities import AbilityDefinition, DEFAULT_ABILITY_BUILD, get_ability_catalog_definition
from data.skillshot_landing_rules import get_skillshot_landing_rules
from scripts.skillshot_rule_pipeline import (
    build_candidate_status_table,
    build_coverage,
    build_wiki_triage,
    build_work_packet,
    classify_ability,
    classify_wiki_entry,
    parse_wiki_hero_data,
)


WIKI_SAMPLE = """
{{hero data
| name = Example
| skills =
Example Shot;Q;File:Example.png;Shoots a bolt toward target area that deals damage to the first enemy it contacts.<!--
-->{{undoc-x|type=Spell Damage<!--
-->|affects=Enemies<!--
-->|target=Point target<!--
-->|props=[[Skillshot]]<!--
-->|hitbox=1.0 x 1.0<!--
-->|missile=20}};8;;;True

Example Burst;W;File:Example.png;Deals damage to nearby enemies.<!--
-->{{undoc-x|type=Spell Damage<!--
-->|affects=Enemies<!--
-->|target=No target<!--
-->|props=[[Area of Effect]]<!--
-->|radius=4.0}};10;;;True

Example Trap;E;File:Example.png;Spawn a mine that becomes active after a short time.<!--
-->{{undoc-x|type=Summon<!--
-->|target=Point target<!--
-->|range=70<!--
-->|prop1=Arming delay|val1=5 seconds}};10;;;False
| talents =
Passive Talent;1;1;Increase Example Shot damage by 10%.;File:Passive.png;
}}
"""


def test_skillshot_rule_pipeline_marks_existing_kelthuzad_rules_as_implemented():
    coverage = build_coverage(DEFAULT_ABILITY_BUILD)
    kelthuzad = next(hero for hero in coverage["heroes"] if hero["heroName"] == "Kel'Thuzad")
    alarak = next(hero for hero in coverage["heroes"] if hero["heroName"] == "Alarak")
    tyrande = next(hero for hero in coverage["heroes"] if hero["heroName"] == "Tyrande")
    abilities = {ability["abilityCatalogName"]: ability for ability in kelthuzad["abilities"]}
    alarak_abilities = {ability["abilityCatalogName"]: ability for ability in alarak["abilities"]}
    tyrande_abilities = {ability["abilityCatalogName"]: ability for ability in tyrande["abilities"]}

    assert coverage["heroCount"] == 90
    assert abilities["KelThuzadChains"]["decision"] == "implemented"
    assert abilities["KelThuzadChains"]["rule"]["detector"] == "same_user_followup"
    assert abilities["KelThuzadFrostNova"]["decision"] == "implemented"
    assert abilities["KelThuzadFrostNova"]["rule"]["detector"] == "area_position_overlap"
    assert alarak_abilities["AlarakDiscordStrike"]["decision"] == "implemented"
    assert alarak_abilities["AlarakDiscordStrike"]["rule"]["detector"] == "directional_position_overlap"
    assert tyrande_abilities["TyrandeLunarFlare"]["decision"] == "implemented"
    assert tyrande_abilities["TyrandeSentinelShot"]["decision"] == "implemented"


def test_skillshot_rule_pipeline_first_pass_classification_routes_likely_skillshots():
    hook = classify_ability("Stitches", "StitchesHook", "Hook", implemented_rule=None)
    cancel = classify_ability("Hogger", "HoggerCancelHoggWild", "Cancel Hogg Wild", implemented_rule=None)
    ambiguous = classify_ability("Example", "ExampleFriendlyAura", "Friendly Aura", implemented_rule=None)

    assert hook["decision"] == "needs_research"
    assert "hook" in hook["reason"]
    assert hook["researchQueries"]
    assert cancel["decision"] == "no_rule_likely"
    assert ambiguous["decision"] == "needs_triage"


def test_skillshot_rule_pipeline_builds_hero_work_packet():
    packet = build_work_packet("Kel'Thuzad", DEFAULT_ABILITY_BUILD)

    assert packet["hero"]["heroSlug"] == "kelthuzad"
    assert packet["branchName"] == "codex/skillshot-kelthuzad"
    assert packet["prTitle"] == "[skillshots] Add Kel'Thuzad landing rules"
    assert {ability["abilityCatalogName"] for ability in packet["implementedRules"]} >= {
        "KelThuzadChains",
        "KelThuzadFrostNova",
    }
    assert any(ability["abilityCatalogName"] == "KelThuzadShadowFissure" for ability in packet["researchBacklog"])
    assert "example-stats" in packet["exampleStatsCommand"]


def test_skillshot_rule_pipeline_classification_accepts_ability_definition_shape():
    definition = AbilityDefinition("AnaSleepDart", "Sleep Dart", "Ana", "Ana")

    classification = classify_ability(
        definition.hero_name,
        definition.catalog_name,
        definition.display_name,
        implemented_rule=None,
    )

    assert classification["decision"] == "needs_research"


def test_skillshot_rules_reference_existing_catalog_rows():
    missing = [
        rule.ability_catalog_name
        for rule in get_skillshot_landing_rules(DEFAULT_ABILITY_BUILD)
        if get_ability_catalog_definition(rule.ability_catalog_name, DEFAULT_ABILITY_BUILD) is None
    ]

    assert missing == []


def test_wiki_hero_data_parser_extracts_skill_and_talent_entries():
    parsed = parse_wiki_hero_data("Example", WIKI_SAMPLE)
    entries = {entry["name"]: entry for entry in parsed["entries"]}

    assert parsed["entryCount"] == 4
    assert entries["Example Shot"]["undoc"]["target"] == "Point target"
    assert entries["Example Shot"]["undoc"]["props"] == "Skillshot"
    assert entries["Passive Talent"]["section"] == "talents"


def test_wiki_entry_classifier_routes_common_targeting_shapes():
    parsed = parse_wiki_hero_data("Example", WIKI_SAMPLE)
    entries = {entry["name"]: entry for entry in parsed["entries"]}

    assert classify_wiki_entry(entries["Example Shot"]) == {
        "decision": "rule_candidate_existing_detector",
        "detectorFamily": "directional_position_overlap",
        "reason": "Wiki marks this as a point-target skillshot or projectile-style ability.",
    }
    assert classify_wiki_entry(entries["Example Burst"]) == {
        "decision": "blocked_new_detector",
        "detectorFamily": "source_centered_area",
        "reason": "Wiki marks this as a no-target area effect around the caster or hosted source.",
    }
    assert classify_wiki_entry(entries["Example Trap"])["detectorFamily"] == "trap_trigger"
    assert classify_wiki_entry(entries["Passive Talent"])["decision"] == "no_rule_likely"


def test_wiki_triage_reclassifies_original_needs_triage_rows():
    coverage = {
        "build": DEFAULT_ABILITY_BUILD,
        "heroCount": 1,
        "abilityCount": 3,
        "heroes": [
            {
                "heroCatalogName": "Example",
                "heroName": "Example",
                "heroSlug": "example",
                "abilities": [
                    {
                        "abilityCatalogName": "ExampleShot",
                        "abilityName": "Example Shot",
                        "decision": "needs_triage",
                    },
                    {
                        "abilityCatalogName": "ExampleBurst",
                        "abilityName": "Example Burst",
                        "decision": "needs_triage",
                    },
                    {
                        "abilityCatalogName": "ExamplePassiveTalent",
                        "abilityName": "Passive Talent",
                        "decision": "needs_triage",
                    },
                ],
            }
        ],
    }
    wiki_sources = {
        "schemaVersion": 1,
        "source": "test",
        "apiUrl": "test",
        "failures": [],
        "heroes": [parse_wiki_hero_data("Example", WIKI_SAMPLE)],
    }

    triage = build_wiki_triage(coverage, wiki_sources)

    assert triage["originalNeedsTriageDecisionCounts"] == {
        "blocked_new_detector": 1,
        "no_rule_likely": 1,
        "rule_candidate_existing_detector": 1,
    }


def test_candidate_status_table_includes_created_and_pending_candidates_only():
    triage = {
        "build": DEFAULT_ABILITY_BUILD,
        "source": "test",
        "heroes": [
            {
                "heroName": "Example",
                "abilities": [
                    {
                        "abilityCatalogName": "ExampleCreated",
                        "abilityName": "Created Skillshot",
                        "wikiDecision": "implemented",
                        "detectorFamily": "directional_position_overlap",
                        "originalDecision": "implemented",
                        "reason": "A versioned skillshot landing rule already exists.",
                    },
                    {
                        "abilityCatalogName": "ExampleCandidate",
                        "abilityName": "Candidate Skillshot",
                        "wikiDecision": "rule_candidate_existing_detector",
                        "detectorFamily": "area_position_overlap",
                        "originalDecision": "needs_triage",
                        "reason": "Wiki marks this as a point-target area ability.",
                        "wikiEntry": {
                            "name": "Candidate Skillshot",
                            "target": "Point target",
                            "type": "Spell Damage",
                            "props": "Area of Effect",
                            "sourceUrl": "https://example.test",
                        },
                    },
                    {
                        "abilityCatalogName": "ExampleIgnored",
                        "abilityName": "Ignored Skill",
                        "wikiDecision": "no_rule_likely",
                        "detectorFamily": "unit_target_guaranteed",
                        "originalDecision": "needs_triage",
                        "reason": "Unit target.",
                    },
                ],
            }
        ],
    }

    table = build_candidate_status_table(triage)

    assert table["totalCandidateSkills"] == 2
    assert table["created"] == 1
    assert table["candidateNotCreated"] == 1
    assert table["heroSummaries"] == [
        {
            "heroName": "Example",
            "totalCandidateSkills": 2,
            "created": 1,
            "candidateNotCreated": 1,
            "detectorFamilies": "area_position_overlap, directional_position_overlap",
        }
    ]
    assert [row["abilityCatalogName"] for row in table["rows"]] == [
        "ExampleCreated",
        "ExampleCandidate",
    ]
