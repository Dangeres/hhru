import asyncio

from src.service.main import HHruService


async def main():
    service = HHruService()
    await service.login()
    await service.bump_resume()


if __name__ == "__main__":
    loop = asyncio.get_event_loop_policy().get_event_loop()
    loop.run_until_complete(main())
