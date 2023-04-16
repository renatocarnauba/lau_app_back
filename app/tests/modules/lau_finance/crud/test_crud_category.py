import pytest
from odmantic import AIOEngine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio.session import async_sessionmaker

from app.config.integration import crud
from app.modules.lau_finance.models.nosql.category import CategoryCreate, CategoryOrm, CategoryUpdate
from app.tests.modules.lau_finance.faker.fakeCategory import create_fake_category, fake_category_data
from app.tests.utils.fakeUser import create_fake_user


@pytest.mark.asyncio
async def test_create_category(asyncSection: async_sessionmaker[AsyncSession], asyncSectionMongo: AIOEngine) -> None:
    category_in = CategoryCreate(**fake_category_data())
    user = await create_fake_user(asyncSection)
    category = await crud.category.create_with_owner(
        asyncSectionMongo=asyncSectionMongo, obj_in=category_in, owner_id=int(user.id)
    )
    assert category.name == category_in.name
    assert category.owner_id == user.id


@pytest.mark.asyncio
async def test_get_category(asyncSection: async_sessionmaker[AsyncSession], asyncSectionMongo: AIOEngine) -> None:
    category = await create_fake_category(asyncSection=asyncSection,asyncSectionMongo=asyncSectionMongo)
    stored_category = await crud.category.get(asyncSectionMongo=asyncSectionMongo, id=category.id)
    assert stored_category
    assert category.id == stored_category.id
    assert category.name == stored_category.name
    assert category.owner_id == stored_category.owner_id


@pytest.mark.asyncio
async def test_update_category(asyncSection: async_sessionmaker[AsyncSession], asyncSectionMongo: AIOEngine) -> None:
    category = await create_fake_category(asyncSection=asyncSection,asyncSectionMongo=asyncSectionMongo)
    category_update = CategoryUpdate(**fake_category_data(), id=category.id)
    category2 = await crud.category.update(asyncSectionMongo=asyncSectionMongo, db_obj=category, obj_in=category_update)
    assert category.id == category2.id
    assert category.name == category2.name
    assert category2.name == category_update.name
    assert category.owner_id == category2.owner_id


@pytest.mark.asyncio
async def test_delete_category(asyncSection: async_sessionmaker[AsyncSession], asyncSectionMongo: AIOEngine) -> None:
    category_in_manter = CategoryCreate(**fake_category_data())
    category_in_excluir = CategoryCreate(**fake_category_data())
    user = await create_fake_user(asyncSection)
    categoryExcluir = await crud.category.create_with_owner(
        asyncSectionMongo=asyncSectionMongo, obj_in=category_in_excluir, owner_id=int(user.id)
    )
    categoryManter = await crud.category.create_with_owner(
        asyncSectionMongo=asyncSectionMongo, obj_in=category_in_manter, owner_id=int(user.id)
    )
    categoryExcluida = await crud.category.remove(asyncSectionMongo=asyncSectionMongo, id=categoryExcluir.id)
    categoryExcluidaAposConsulta = await crud.category.get(asyncSectionMongo=asyncSectionMongo, id=categoryExcluir.id)
    categoryMantidaAposConsulta = await crud.category.get(asyncSectionMongo=asyncSectionMongo, id=categoryManter.id)
    assert categoryExcluidaAposConsulta is None
    assert categoryExcluida is not None
    categoryExcluidaX: CategoryOrm = categoryExcluida
    assert categoryExcluidaX.id == categoryExcluir.id
    assert categoryExcluidaX.name == category_in_excluir.name
    assert categoryExcluidaX.owner_id == user.id
    assert categoryMantidaAposConsulta is not None
    categoryMantidaAposConsultaX: CategoryOrm = categoryMantidaAposConsulta
    assert categoryMantidaAposConsultaX.id == categoryManter.id
    assert categoryMantidaAposConsultaX.name == category_in_manter.name
    assert categoryMantidaAposConsultaX.owner_id == user.id


@pytest.mark.asyncio
async def test_create_category_parent(asyncSection: async_sessionmaker[AsyncSession], asyncSectionMongo: AIOEngine) -> None:
    category_in_parent = CategoryCreate(**fake_category_data())

    user = await create_fake_user(asyncSection)
    categoryParent = await crud.category.create_with_owner(
        asyncSectionMongo=asyncSectionMongo, obj_in=category_in_parent, owner_id=int(user.id)
    )

    category_in = CategoryCreate(**fake_category_data())
    category_in.parent_id = categoryParent.id
    category = await crud.category.create_with_owner(
        asyncSectionMongo=asyncSectionMongo, obj_in=category_in, owner_id=int(user.id)
    )
    assert category.name == category_in.name
    assert category.owner_id == user.id
    assert category.parent_id == categoryParent.id


@pytest.mark.asyncio
async def test_update_category_parent(asyncSection: async_sessionmaker[AsyncSession], asyncSectionMongo: AIOEngine) -> None:
    # Cria pais
    categoryParentFrom = await create_fake_category(asyncSection=asyncSection,asyncSectionMongo=asyncSectionMongo)
    categoryParentTo = await create_fake_category(asyncSection=asyncSection,asyncSectionMongo=asyncSectionMongo)

    # #Cria filho embaixo de From

    category_in = CategoryCreate(**fake_category_data())
    category_in.parent_id = categoryParentFrom.id
    category = await crud.category.create_with_owner(
        asyncSectionMongo=asyncSectionMongo, obj_in=category_in, owner_id=int(categoryParentFrom.owner_id)
    )
    assert category.name == category_in.name
    assert category.owner_id == categoryParentFrom.owner_id
    assert category.parent_id == categoryParentFrom.id

    # atualiza parent do Filho
    category_update = CategoryUpdate(parent_id=categoryParentTo.id, id=categoryParentFrom.id)
    categoryChild = await crud.category.update(
        asyncSectionMongo=asyncSectionMongo, db_obj=categoryParentFrom, obj_in=category_update
    )
    assert categoryChild.parent_id == categoryParentTo.id


@pytest.mark.asyncio
async def test_delete_category_parent(asyncSection: async_sessionmaker[AsyncSession], asyncSectionMongo: AIOEngine) -> None:
    category_in_parent = CategoryCreate(**fake_category_data())
    user = await create_fake_user(asyncSection)
    categoryParent = await crud.category.create_with_owner(
        asyncSectionMongo=asyncSectionMongo, obj_in=category_in_parent, owner_id=int(user.id)
    )

    category_in = CategoryCreate(**fake_category_data())
    category_in.parent_id = categoryParent.id
    categoryChild = await crud.category.create_with_owner(
        asyncSectionMongo=asyncSectionMongo, obj_in=category_in, owner_id=int(user.id)
    )
    assert categoryChild.name == category_in.name
    assert categoryChild.owner_id == user.id
    assert categoryChild.parent_id == categoryParent.id

    categoryExcluida = await crud.category.remove(asyncSectionMongo=asyncSectionMongo, id=categoryParent.id)
    categoryExcluidaAposConsulta = await crud.category.get(asyncSectionMongo=asyncSectionMongo, id=categoryParent.id)
    assert categoryExcluidaAposConsulta is None
    assert categoryExcluida is not None
    categoryExcluidaX: CategoryOrm = categoryExcluida
    assert categoryExcluidaX.owner_id == user.id

    categoryChildExcluidaAposConsulta = await crud.category.get(asyncSectionMongo=asyncSectionMongo, id=categoryChild.id)
    assert categoryChildExcluidaAposConsulta is None
