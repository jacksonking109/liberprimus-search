"""Phase 2 generators: round trips, invertibility, the zero-step sources, and the plaintext handling (synthetic)."""
import numpy as np
import pytest

from lpswarm import research_generators as G

N = 29


def _plain(rng, n=1500, symbols=N):
    w = np.arange(symbols, 0, -1) ** 2.0
    return rng.choice(symbols, size=n, p=w / w.sum())


@pytest.mark.parametrize("m", [G.TableWalk("cyclic Latin", "row (0,j)", "wrap"), G.TableWalk("keyed Latin", "row (0,j)", "wrap"),
                               G.PermAlphabet("slot", 0), G.PermAlphabet("slot", 28), G.PermAlphabet("swap", 7), G.PermAlphabet("slot2", 14),
                               G.PermAlphabet("chao"), G.NonZeroStep("lcg"), G.NonZeroStep("lagfib"), G.NonZeroStep("matrix"), G.NonZeroStep("autokey")])
def test_every_invertible_machine_round_trips(m):
    p = _plain(np.random.default_rng(1), symbols=m.symbols)
    c = G.encipher(m, p, seed=4)
    assert np.array_equal(G.decipher(m, c, seed=4), p)
    assert G.invertible_share(m) == 1.0


def test_a_rook_walk_on_a_keyed_table_cannot_carry_every_message():
    assert G.invertible_share(G.TableWalk("keyed Latin", "rook", "wrap")) < 1.0
    assert G.invertible_share(G.TableWalk("page-05 grid 5x5", "near list", "wrap")) < 1.0     # 13 distinct values for 29 symbols


def test_moving_the_emitted_rune_to_the_last_slot_repeats_exactly_on_the_last_plaintext_rune():
    """slot 28: the rune just emitted sits last, so the next output repeats it iff the plaintext rune is 28 (EA): a plaintext trigger."""
    rng = np.random.default_rng(2)
    p = _plain(rng, 4000)
    c = G.encipher(G.PermAlphabet("slot", 28), p, seed=1)
    zero = np.nonzero(c[1:] == c[:-1])[0] + 1
    assert len(zero) > 0 and set(p[zero].tolist()) == {28}
    assert np.sum(p[1:] == 28) == len(zero)


def test_the_non_zero_step_machines_never_repeat_a_rune():
    rng = np.random.default_rng(3)
    for gen in ("lcg", "lagfib", "matrix", "autokey"):
        m = G.NonZeroStep(gen)
        c = G.encipher(m, _plain(rng, 3000, 28), seed=2)
        assert not np.any(c[1:] == c[:-1])


def test_fold_plaintext_gives_28_symbols_and_keeps_the_original_index():
    plain = np.array([0, 5, 28, 3, 28, 14, 1])
    p, idx = G.fold_plaintext(plain, "skip", 28)
    assert p.tolist() == [0, 5, 3, 14, 1] and idx.tolist() == [0, 1, 3, 5, 6]
    p, idx = G.fold_plaintext(plain, "fold", 14)
    assert p.tolist() == [0, 5, 27, 3, 27, 14, 1] and idx.tolist() == list(range(7))      # 14 folds into 15, then runes above 14 shift down
    p, _ = G.fold_plaintext(np.array([28, 0, 28]), "fold", 28)
    assert p.tolist() == [0, 0, 0]                                     # 28 folds into 0 (the next rune, wrapping)


def test_word_categories_and_the_variant_screen_run_end_to_end():
    from lpswarm import research_signature as S
    from lpswarm.alphabet import get_alphabet
    from lpswarm.research_packets import ALPHABET, load_sections
    cats = G.word_categories(8, [0, 3, 4])
    assert cats.tolist() == ["initial", "internal", "final", "single", "initial", "internal", "internal", "final"]
    alpha = get_alphabet(ALPHABET)
    ref = S.reference(load_sections(indexes=list(S.SECTIONS)))
    windows = S.english_windows(alpha, 2, 2000, 5)
    r = G.run_variant(G.NonZeroStep("lcg"), windows, ref, 28, "skip")
    assert r["zeros"] == 0 and r["lag1"] == 0.0 and r["verdict"].startswith("near miss") and r["invertible"] == 1.0
    r2 = G.run_variant(G.PermAlphabet("slot", 28), windows, ref)
    assert r2["source"].startswith("plaintext rune 28") and r2["verdict"] != "full match"
