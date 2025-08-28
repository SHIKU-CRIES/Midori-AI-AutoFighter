from autofighter.party import Party
from autofighter.relics import apply_relics
from autofighter.relics import award_relic
from plugins.players._base import PlayerBase


def test_award_relics_stack():
    party = Party()
    member = PlayerBase()
    member.atk = 100
    party.members.append(member)
    assert award_relic(party, "bent_dagger") is not None
    assert award_relic(party, "bent_dagger") is not None
    apply_relics(party)
    assert party.relics == ["bent_dagger", "bent_dagger"]
    assert party.members[0].atk == int(100 * 1.03 * 1.03)
