import httpx
from django.conf import settings


class NFMerSearchService:
    @staticmethod
    async def search_composers(search_qerry=""):
        """Search composers by name asynchronously"""
        url = f"{settings.API_URL}/composers/"
        params = {"search": search_qerry} if search_qerry else {}
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                return response.json()
            except httpx.RequestError:
                return []

    @staticmethod
    async def search_compositions(search_querry=""):
        """Search compositions by name asynchronously"""
        url = f"{settings.API_URL}/compositions/"
        params = {"search": search_querry} if search_querry else {}
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                return response.json()
            except httpx.RequestError:
                return []

    @staticmethod
    async def get_composer_details(composer_id):
        """Get detailed information about a composer asynchronously"""
        url = f"{settings.API_URL}/composers/{composer_id}"
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
            except httpx.RequestError:
                return None

    @staticmethod
    async def get_composition_details(composition_id):
        """Get detailed information about a composition asynchronously"""
        url = f"{settings.API_URL}/compositions/{composition_id}"

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
            except httpx.RequestError:
                return None
