#!/usr/bin/python
# -*- coding: utf-8 -*-
from data import HeroTranslator, MapTranslator


def test_HeroTranslator_with_english_characters():
    assert HeroTranslator.get_base_hero_name('Falstad') == 'Falstad'
    assert HeroTranslator.get_base_hero_name('Zuljin') == "Zul'jin"
    assert HeroTranslator.get_base_hero_name('Tinker') == "Gazlowe"
    assert HeroTranslator.get_base_hero_name(u"Gazleu /// Gazlowe") == "Gazlowe"
    assert HeroTranslator.get_base_hero_name("Gazleu /// Gazlowe") == "Gazlowe"
    assert HeroTranslator.get_base_hero_name(u"Thrall /// Thrall") == "Thrall"
    assert HeroTranslator.get_base_hero_name("Thrall /// Thrall") == "Thrall"


def test_HeroTranslator_with_unicode_characters():
    assert HeroTranslator.get_base_hero_name(u"\u7f1d\u5408\u602a /// Stitches") == 'Stitches'
    assert HeroTranslator.get_base_hero_name('失落的維京人') == 'The Lost Vikings'


def test_MapTranslator_with_english_characters():
    assert MapTranslator().get_base_map_name("Geisterminen") == 'Haunted Mines'
    assert MapTranslator().get_base_map_name("Garden of Terror") == 'Garden of Terror'


def test_MapTranslator_with_unicode_characters():
    assert MapTranslator().get_base_map_name("죽음의 광산") == 'Haunted Mines'
    assert MapTranslator().get_base_map_name('Jardín del Terror') == 'Garden of Terror'
