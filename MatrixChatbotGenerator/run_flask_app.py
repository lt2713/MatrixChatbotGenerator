import asyncio
from store.flask_app import main


def run_main():
    asyncio.run(main())


if __name__ == '__main__':
    run_main()
