import pytest

from app.repositories.career import CareerRepository


@pytest.mark.asyncio
async def test_get_careers_by_ids_returns_matches(database, sample_careers):
    repo = CareerRepository(database)
    target_ids = [sample_careers[0].id, sample_careers[1].id]

    careers = await repo.get_careers_by_ids(target_ids)
    assert careers
    assert {career.id for career in careers} == set(target_ids)

    empty = await repo.get_careers_by_ids([])
    assert empty == []


@pytest.mark.asyncio
async def test_list_careers_with_dimension_filters_results(database, sample_careers):
    repo = CareerRepository(database)

    careers = await repo.list_careers_with_dimension("R", limit=5)
    assert careers
    for career in careers:
        dimensions = career.holland_dimensions or []
        assert any(letter.upper() == "R" for letter in dimensions)
