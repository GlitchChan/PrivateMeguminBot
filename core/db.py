import anyio
from prisma import Prisma

DB = Prisma(auto_register=True)


async def add_trusted_user(user_id: int) -> None:
    """Function to add a user to `trusted_users`.

    Args:
        user_id (int): ID of the user to add
    """
    file = anyio.Path(__file__).parent / "trusted_users"

    if not await file.exists():
        await file.write_text("")

    data = await file.read_text()
    data += f"{user_id},"
    await file.write_text(data)
