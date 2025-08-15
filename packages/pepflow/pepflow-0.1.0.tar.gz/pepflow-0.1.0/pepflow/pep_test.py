import pytest

from pepflow import pep
from pepflow import pep_context as pc


class TestPEPBuilder:
    def test_make_context(self) -> None:
        builder = pep.PEPBuilder()
        assert pc.get_current_context() is None

        with builder.make_context("test") as ctx:
            assert ctx is pc.get_current_context()

        assert pc.get_current_context() is None

    def test_get_context(self) -> None:
        builder = pep.PEPBuilder()
        with builder.make_context("test") as ctx:
            prev_ctx = ctx

        builder.get_context("test") is prev_ctx

    def test_clear_context(self) -> None:
        builder = pep.PEPBuilder()
        with builder.make_context("test"):
            pass

        assert "test" in builder.pep_context_dict.keys()
        builder.clear_context("test")
        assert "test" not in builder.pep_context_dict.keys()

    def test_clear_all_context(self) -> None:
        builder = pep.PEPBuilder()
        with builder.make_context("test"):
            pass
        with builder.make_context("test2"):
            pass

        assert len(builder.pep_context_dict) == 2
        builder.clear_all_context()
        assert len(builder.pep_context_dict) == 0

    def test_make_context_twice(self) -> None:
        builder = pep.PEPBuilder()
        with builder.make_context("test"):
            pass

        assert "test" in builder.pep_context_dict.keys()

        with pytest.raises(
            KeyError, match="There is already a context test in the builder"
        ):
            with builder.make_context("test"):
                pass

        with builder.make_context("test", override=True):
            pass
