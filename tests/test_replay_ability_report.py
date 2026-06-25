from pathlib import Path

from scripts.replay_ability_report import _build_report, _hero_catalog_name, _replay_files


REPLAY_DIR = Path(__file__).parent / "fixtures" / "replays"


def test_replay_ability_report_groups_casts_by_build_hero_and_link():
    files = _replay_files(REPLAY_DIR, recursive=True, limit=None)

    report = _build_report(files, progress_every=None, max_examples=1, include_candidates=True)

    assert report["total"] == 2
    assert report["passed"] == 2
    assert report["failed"] == 0
    assert report["builds"] == {"97039": 2}
    assert report["unmappedObservations"] == 0
    assert report["heroes"]["97039:Hogger"] == 9

    hogger_dynamite = next(
        row
        for row in report["observations"]
        if row["heroName"] == "Hogger" and row["abilityLink"] == 1318 and row["abilityCmdIndex"] == 0
    )
    assert hogger_dynamite["abilityCatalogName"] == "HoggerEzThroDynamite"
    assert hogger_dynamite["abilityName"] == "Ez-Thro Dynamite"
    assert hogger_dynamite["targetTypes"] == {"TargetPoint": 96}
    assert len(hogger_dynamite["examples"]) == 1


def test_hero_catalog_name_resolves_display_names():
    assert _hero_catalog_name("Kael'thas", 97039) == "Kaelthas"
    assert _hero_catalog_name("Li Li", 97039) == "LiLi"
    assert _hero_catalog_name("Nazeebo", 97039) == "WitchDoctor"
