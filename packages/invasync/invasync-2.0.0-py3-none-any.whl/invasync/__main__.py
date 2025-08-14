import argparse
import asyncio
import json
from pathlib import Path

import httpx
from bs4 import BeautifulSoup

FLASH_GALLERY_ENDPOINT = "https://api.space-invaders.com/flashinvaders_v3_pas_trop_predictif/api/gallery?uid="
MAP_URL = "https://invaders.code-rhapsodie.com"
MAP_RESTORE_ENDPOINT = f"{MAP_URL}/restore"
MAP_LOGIN_ENDPOINT = f"{MAP_URL}/login"


class User:
    def __init__(
        self,
        name: str,
        flash_uid: str,
        map_email: str,
        map_password: str,
    ) -> None:
        self.name = name
        self.flash_uid = flash_uid
        self.map_email = map_email
        self.map_password = map_password
        self.map_token: str = ""

    async def run(self) -> None:
        try:
            async with httpx.AsyncClient() as client:
                await self._get_invaders(client)
                await self._login_map(client)
                await self._update_map(client)
        except IndexError as e:
            print(f"[!] [{self.name}] - Bad map token")
            print(e)

    async def _get_invaders(self, client: httpx.AsyncClient) -> None:
        print(f"[+] [{self.name}] - Fetching flashed invaders")
        response = await client.get(f"{FLASH_GALLERY_ENDPOINT}{self.flash_uid}")
        data: dict = response.json()
        self.total_invaders = len(data["invaders"])
        self.invaders_payload = (
            "[" + ",".join([f'"{invader_id}"' for invader_id in data["invaders"]]) + "]"
        ).encode()

    async def _login_map(self, client: httpx.AsyncClient) -> None:
        print(f"[+] [{self.name}] - Performing map login")
        response = await client.get(MAP_LOGIN_ENDPOINT)
        soup = BeautifulSoup(response.text, "html.parser")
        csrf_token = soup.find("input", attrs={"name": "_csrf_token"})["value"]  # type: ignore[index]
        response = await client.post(
            MAP_LOGIN_ENDPOINT,
            data={
                "_username": self.map_email,
                "_password": self.map_password,
                "_remember_me": "off",
                "_csrf_token": csrf_token,
            },
        )
        self.map_token = response.cookies.get("PHPSESSID")  # type: ignore[assignment]

    async def _update_map(self, client: httpx.AsyncClient) -> None:
        print(f"[+] [{self.name}] - Updating map")
        response = await client.get(
            MAP_RESTORE_ENDPOINT,
            cookies={"PHPSESSID": self.map_token},
        )
        soup = BeautifulSoup(response.text, "html.parser")
        self.csrf_token = soup.find(
            "input",
            attrs={"name": "restore[_token]"},
        )["value"]  # type: ignore[index]
        await client.post(
            MAP_RESTORE_ENDPOINT,
            data={
                "restore[_token]": self.csrf_token,
            },
            files={
                "restore[file]": (
                    "invaders.txt",
                    self.invaders_payload,
                    "text/plain",
                ),
            },
            cookies={"PHPSESSID": self.map_token},
        )
        print(
            f"[+] [{self.name}] - Updated user's map with {self.total_invaders} entries",
        )


def load_json(users_json: Path) -> list[User]:
    with users_json.open("r") as file:
        data = json.load(file)
        return [
            User(
                name=name,
                flash_uid=data["flash_uid"],
                map_email=data["map_email"],
                map_password=data["map_password"],
            )
            for name, data in data.items()
        ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Invaders synchronizer")
    parser.add_argument(
        "-u",
        "--users",
        type=Path,
        required=True,
        help="Path to the JSON users file",
    )
    return parser.parse_args()


async def async_main() -> None:
    args = parse_args()
    users = load_json(args.users)
    await asyncio.gather(*[user.run() for user in users])


def main() -> None:
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
