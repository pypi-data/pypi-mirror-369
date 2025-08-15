import asyncio
import os
import aiohttp
import logging
import sys

from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
from pydantic import AnyUrl
import mcp.server.stdio
from logging.handlers import RotatingFileHandler

# Store notes as a simple key-value dict to demonstrate state management
notes: dict[str, str] = {}

api_url = os.getenv("API_URL", "https://dashboard.greenpulse.com/publicapi/v1")
api_key = os.getenv("API_KEY", "123456789")
headers = {"Authorization": f"{api_key}"}

logging.basicConfig(
    level=logging.DEBUG,  # Or use logging.INFO for less detail
    format='%(asctime)s %(levelname)s %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger("greenpulse-mcp")

log_file = '/tmp/greenpulse_mcp.log'

# File handler for DEBUG+ logs with rotation (max 5MB/file, keep 3 old logs)
file_handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=3)
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
file_handler.setFormatter(formatter)

# Stream handler for terminal (stderr), INFO+ only
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(formatter)

# Set up the logger
logger = logging.getLogger('greenpulse-mcp')
logger.setLevel(logging.DEBUG)  # Catch all logs at DEBUG or above
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

# --- Lookup Maps ---
country_map = {}
region_map = {}
clipping_type_map = {}
media_type_map = {}
language_map = {}
product_map = {}
product_series_map = {}
clipping_information_map = {}
taxonomy_map = {}
media_map = {}

# Mapping for sentiment strings to integer codes
sentiment_map = {
    "negative": 0,
    "neutral": 1,
    "positive": 2
}
valid_sentiments = {0, 1, 2}

server = Server("greenpulse-mcp")

# --- Generic Loader ---
async def load_map(endpoint: str, map_obj: dict, map_name: str, name_field='name', id_field='uuid'):
    url = f"{api_url}{endpoint}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            resp.raise_for_status()
            data = await resp.json()
            items = data["results"] if isinstance(data, dict) and "results" in data else data
            for item in items:
                if isinstance(item, dict):
                    key = item.get(name_field, None)
                    val = item.get(id_field, None)
                elif isinstance(item, str):
                    key = item
                    val = item
                else:
                    continue
                if key and val:
                    map_obj[key.lower()] = val
    logger.info(f"Loaded {len(map_obj)} {map_name}.")

# --- Specific Loader Functions ---
async def load_country_map():
    global country_map
    await load_map("/options/countries/", country_map, "countries")

async def load_region_map():
    global region_map
    await load_map("/options/regions/", region_map, "regions")

async def load_clipping_type_map():
    global clipping_type_map
    await load_map("/options/clippingtypes/", clipping_type_map, "clipping types")

async def load_media_type_map():
    global media_type_map
    await load_map("/media/types/", media_type_map, "media types")

async def load_language_map():
    global language_map
    await load_map("/options/languages/", language_map, "languages")

async def load_product_map():
    global product_map
    await load_map("/options/products/", product_map, "products")

async def load_product_series_map():
    global product_series_map
    await load_map("/options/productgroups/", product_series_map, "product series")

async def load_clipping_information_map():
    global clipping_information_map
    await load_map("/options/choices/", clipping_information_map, "clipping information")

async def load_taxonomy_map():
    global taxonomy_map
    await load_map("/options/taxonomy/", taxonomy_map, "taxonomy")

async def load_media_map():
    global media_map
    await load_map("/media/all/", media_map, "media")

# --- Initialize All Maps At Once (call this at startup) ---
async def initialize_all_maps():
    await asyncio.gather(
        load_country_map(),
        load_region_map(),
        load_clipping_type_map(),
        load_media_type_map(),
        load_language_map(),
        load_product_map(),
        load_product_series_map(),
        load_clipping_information_map(),
        load_taxonomy_map(),
        load_media_map()
    )

# --- Normalization Helpers ---
def _is_uuid(val: str) -> bool:
    return isinstance(val, str) and len(val) == 36 and val.count('-') == 4

def normalize_country(name_or_uuid: str) -> str:
    if _is_uuid(name_or_uuid):
        return name_or_uuid
    return country_map.get(name_or_uuid.lower(), name_or_uuid)

def normalize_region(name_or_uuid: str) -> str:
    if _is_uuid(name_or_uuid):
        return name_or_uuid
    return region_map.get(name_or_uuid.lower(), name_or_uuid)

def normalize_clipping_type(name_or_uuid: str) -> str:
    if _is_uuid(name_or_uuid):
        return name_or_uuid
    return clipping_type_map.get(name_or_uuid.lower(), name_or_uuid)

def normalize_media_type(name_or_uuid: str) -> str:
    if _is_uuid(name_or_uuid):
        return name_or_uuid
    return media_type_map.get(name_or_uuid.lower(), name_or_uuid)

def normalize_language(name_or_uuid: str) -> str:
    if _is_uuid(name_or_uuid):
        return name_or_uuid
    return language_map.get(name_or_uuid.lower(), name_or_uuid)

def normalize_product(name_or_uuid: str) -> str:
    if _is_uuid(name_or_uuid):
        return name_or_uuid
    return product_map.get(name_or_uuid.lower(), name_or_uuid)

def normalize_product_series(name_or_uuid: str) -> str:
    if _is_uuid(name_or_uuid):
        return name_or_uuid
    return product_series_map.get(name_or_uuid.lower(), name_or_uuid)

def normalize_clipping_information(name_or_uuid: str) -> str:
    if _is_uuid(name_or_uuid):
        return name_or_uuid
    return clipping_information_map.get(name_or_uuid.lower(), name_or_uuid)

def normalize_taxonomy(name_or_uuid: str) -> str:
    if _is_uuid(name_or_uuid):
        return name_or_uuid
    return taxonomy_map.get(name_or_uuid.lower(), name_or_uuid)

def normalize_media(name_or_uuid: str) -> str:
    if _is_uuid(name_or_uuid):
        return name_or_uuid
    return media_map.get(name_or_uuid.lower(), name_or_uuid)

def normalize_sentiment(value):
    """
    Normalize sentiment input to integer codes expected by API:
      - If given as an integer (0, 1, 2), returns it.
      - If given as 'negative', 'neutral', or 'positive' (case-insensitive), returns code.
      - Ignores unknown values (returns None).
    """
    if value is None:
        return None
    if isinstance(value, int):
        if value == -1:
            return 0
        if value in valid_sentiments:
            return value
        return None
    if isinstance(value, str):
        return sentiment_map.get(value.lower(), None)
    return None
    
@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="get-user",
            description="Fetches user info from greenpulse.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        types.Tool(
            name="get-languages",
            description="Fetches available languages from greenpulse.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        types.Tool(
            name="get-countries",
            description="Fetches available countries from greenpulse.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        types.Tool(
            name="get-regions",
            description="Fetches available regions from greenpulse.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        types.Tool(
            name="get-products",
            description="Fetches available products from greenpulse.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        types.Tool(
            name="get-product-series",
            description="Fetches available product series from greenpulse.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        types.Tool(
            name="get-clipping-types",
            description="Fetches available clipping types from greenpulse.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        types.Tool(
            name="get-clipping-information",
            description="Fetches available clipping information from greenpulse.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        types.Tool(
            name="get-taxonomy",
            description="Fetches available clipping taxonomy from greenpulse.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        types.Tool(
            name="get-media-types",
            description="Fetches available media types from greenpulse.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        types.Tool(
            name="get-media",
            description="Fetches available media from greenpulse.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        types.Tool(
            name="get-clippings",
            description="Fetches available clippings from greenpulse.",
            inputSchema={
                "type": "object",
                "properties": {
                    "search": {
                        "type": "object",
                        "properties": {
                            "products": {"type": "array", "items": {"type": "string"}, "description": "Specific product or products"},
                            "media": {"type": "array", "items": {"type": "string"}, "description": "Specific media sources or channels"},
                            "types": {"type": "array", "items": {"type": "string"}, "description": "Media type or category, e.g. 'YouTube', 'Instagram', 'online', 'print', 'TikTok'"},
                            "regions": {"type": "array", "items": {"type": "string"}, "description": "Geographical regions, consisting of countries"},
                            "countries": {"type": "array", "items": {"type": "string"}, "description": "Geographical countries"},
                            "sentiments": {"type": "array", "items": {"type": "integer"}, "description": "Clipping or article sentiment (negative=0, neutral=1, positive=2)"},
                            "languages": {"type": "array", "items": {"type": "string"}, "description": "Language or languages"},
                            "productgroups": {"type": "array", "items": {"type": "string"}, "description": "Specific product series, consisting of different products"},
                            "publish_date_from": {"type": "string"},
                            "publish_date_to": {"type": "string"},
                            "awards": {"type": "boolean", "description": "Is there an award assigned to this clipping"},
                            "sponsored": {"type": "boolean", "description": "Is this clipping or article sponsored, was there money paid for it"},
                            "clippingtypes": {"type": "array", "items": {"type": "string"}, "description": "Clipping type or type of content, e.g. 'Interview', 'Review', 'Round-up', 'Byline', 'Product placement', 'Builds'"}
                        },
                        "required": []
                    }
                },
                "required": []
            }
        ),
        types.Tool(
            name="get-clippings-by-language",
            description="Fetches available clippings by language from greenpulse.",
            inputSchema={
                "type": "object",
                "properties": {
                    "languageID": {
                        "type": "string",
                        "description": "Language ID (required)."
                    },
                    "search": {
                        "type": "object",
                        "properties": {
                            "products": {"type": "array", "items": {"type": "string"}, "description": "Specific product or products"},
                            "media": {"type": "array", "items": {"type": "string"}, "description": "Specific media sources or channels"},
                            "types": {"type": "array", "items": {"type": "string"}, "description": "Media type or category, e.g. 'YouTube', 'Instagram', 'online', 'print', 'TikTok'"},
                            "regions": {"type": "array", "items": {"type": "string"}, "description": "Geographical regions, consisting of countries"},
                            "countries": {"type": "array", "items": {"type": "string"}, "description": "Geographical countries"},
                            "sentiments": {"type": "array", "items": {"type": "integer"}, "description": "Clipping or article sentiment (negative=0, neutral=1, positive=2)"},
                            "productgroups": {"type": "array", "items": {"type": "string"}, "description": "Specific product series, consisting of different products"},
                            "publish_date_from": {"type": "string"},
                            "publish_date_to": {"type": "string"},
                            "awards": {"type": "boolean", "description": "Is there an award assigned to this clipping"},
                            "sponsored": {"type": "boolean", "description": "Is this clipping or article sponsored, was there money paid for it"},
                            "clippingtypes": {"type": "array", "items": {"type": "string"}, "description": "Clipping type or type of content, e.g. 'Interview', 'Review', 'Round-up', 'Byline', 'Product placement', 'Builds'"}
                        },
                        "required": []
                    }
                },
                "required": ["languageID"]
            }
        ),
        types.Tool(
            name="get-news",
            description="Fetches available news from greenpulse.",
            inputSchema={
                "type": "object",
                "properties": {
                    "search": {
                        "type": "object",
                        "properties": {
                            "products": {"type": "array", "items": {"type": "string"}, "description": "Specific product or products"},
                            "media": {"type": "array", "items": {"type": "string"}, "description": "Specific media sources or channels"},
                            "types": {"type": "array", "items": {"type": "string"}, "description": "Media type or category, e.g. 'YouTube', 'Instagram', 'online', 'print', 'TikTok'"},
                            "regions": {"type": "array", "items": {"type": "string"}, "description": "Geographical regions, consisting of countries"},
                            "countries": {"type": "array", "items": {"type": "string"}, "description": "Geographical countries"},
                            "sentiments": {"type": "array", "items": {"type": "integer"}, "description": "Clipping or article sentiment (negative=0, neutral=1, positive=2)"},
                            "languages": {"type": "array", "items": {"type": "string"}, "description": "Language or languages"},
                            "productgroups": {"type": "array", "items": {"type": "string"}, "description": "Specific product series, consisting of different products"},
                            "publish_date_from": {"type": "string"},
                            "publish_date_to": {"type": "string"},
                        },
                        "required": []
                    }
                },
                "required": []
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None):

    logger.debug(f"MCP arguments: {arguments}")
    payload = {}

    if name == "get-user":
        async with aiohttp.ClientSession() as s:
            async with s.get(f"{api_url}/whoami/", headers=headers) as resp:
                result = await resp.json()
        return [types.TextContent(type="text", text=str(result))]

    elif name == "get-languages":
        async with aiohttp.ClientSession() as s:
            async with s.get(f"{api_url}/options/languages/", headers=headers) as resp:
                result = await resp.json()
        return [types.TextContent(type="text", text=str(result))]

    elif name == "get-countries":
        async with aiohttp.ClientSession() as s:
            async with s.get(f"{api_url}/options/countries/", headers=headers) as resp:
                result = await resp.json()
        return [types.TextContent(type="text", text=str(result))]

    elif name == "get-regions":
        async with aiohttp.ClientSession() as s:
            async with s.get(f"{api_url}/options/regions/", headers=headers) as resp:
                result = await resp.json()
        return [types.TextContent(type="text", text=str(result))]

    elif name == "get-products":
        async with aiohttp.ClientSession() as s:
            async with s.get(f"{api_url}/options/products/", headers=headers) as resp:
                result = await resp.json()
        return [types.TextContent(type="text", text=str(result))]

    elif name == "get-product-series":
        async with aiohttp.ClientSession() as s:
            async with s.get(f"{api_url}/options/productgroups/", headers=headers) as resp:
                result = await resp.json()
        return [types.TextContent(type="text", text=str(result))]

    elif name == "get-clipping-types":
        async with aiohttp.ClientSession() as s:
            async with s.get(f"{api_url}/options/clippingtypes/", headers=headers) as resp:
                result = await resp.json()
        return [types.TextContent(type="text", text=str(result))]
            
    elif name == "get-clipping-information":
        async with aiohttp.ClientSession() as s:
            async with s.get(f"{api_url}/options/choices/", headers=headers) as resp:
                result = await resp.json()
        return [types.TextContent(type="text", text=str(result))]

    elif name == "get-taxonomy":
        async with aiohttp.ClientSession() as s:
            async with s.get(f"{api_url}/options/taxonomy/", headers=headers) as resp:
                result = await resp.json()
        return [types.TextContent(type="text", text=str(result))]

    elif name == "get-media-types":
        async with aiohttp.ClientSession() as s:
            async with s.get(f"{api_url}/media/types/", headers=headers) as resp:
                result = await resp.json()
        return [types.TextContent(type="text", text=str(result))]

    elif name == "get-media":
        async with aiohttp.ClientSession() as s:
            async with s.get(f"{api_url}/media/all/", headers=headers) as resp:
                result = await resp.json()
        return [types.TextContent(type="text", text=str(result))]

    elif name == "get-clippings":
        if arguments is not None:
            search = arguments.get("search", arguments)
            if "products" in search:
                search["products"] = [normalize_product(x) for x in search["products"]]
            if "productgroups" in search:
                search["productgroups"] = [normalize_product_series(x) for x in search["productgroups"]]
            if "countries" in search:
                search["countries"] = [normalize_country(x) for x in search["countries"]]
            if "languages" in search:
                search["languages"] = [normalize_language(x) for x in search["languages"]]
            if "media" in search:
                search["media"] = [normalize_media(x) for x in search["media"]]
            if "regions" in search:
                search["regions"] = [normalize_region(x) for x in search["regions"]]
            if "clippingtypes" in search:
                search["clippingtypes"] = [normalize_clipping_type(x) for x in search["clippingtypes"]]
            if "types" in search:
                search["types"] = [normalize_media_type(x) for x in search["types"]]
            if "sentiments" in search:
                normalized = [normalize_sentiment(s) for s in search["sentiments"]]
                search["sentiments"] = [s for s in normalized if s is not None]
            payload = search

        logger.debug(f"Normalized payload to send: {payload}")
        
        async with aiohttp.ClientSession() as s:
            async with s.post(f"{api_url}/clippings/", headers=headers, json=payload) as resp:
                result = await resp.json()
        return [types.TextContent(type="text", text=str(result))]

    elif name == "get-clippings-by-language":
        language_id = arguments["languageID"]
        if arguments is not None:
            search = arguments.get("search", arguments)
            if "products" in search:
                search["products"] = [normalize_product(x) for x in search["products"]]
            if "productgroups" in search:
                search["productgroups"] = [normalize_product_series(x) for x in search["productgroups"]]
            if "countries" in search:
                search["countries"] = [normalize_country(x) for x in search["countries"]]
            if "media" in search:
                search["media"] = [normalize_media(x) for x in search["media"]]
            if "regions" in search:
                search["regions"] = [normalize_region(x) for x in search["regions"]]
            if "clippingtypes" in search:
                search["clippingtypes"] = [normalize_clipping_type(x) for x in search["clippingtypes"]]
            if "types" in search:
                search["types"] = [normalize_media_type(x) for x in search["types"]]
            if "sentiments" in search:
                normalized = [normalize_sentiment(s) for s in search["sentiments"]]
                search["sentiments"] = [s for s in normalized if s is not None]
            payload = search

        logger.debug(f"Normalized payload to send: {payload}")

        url = f"{api_url}/clippings_by_language/{language_id}/"

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as resp:
                resp.raise_for_status()
                result = await resp.json()

        return [types.TextContent(type="text", text=str(result))]

    elif name == "get-news":
        if arguments is not None:
            search = arguments.get("search", arguments)
            if "products" in search:
                search["products"] = [normalize_product(x) for x in search["products"]]
            if "productgroups" in search:
                search["productgroups"] = [normalize_product_series(x) for x in search["productgroups"]]
            if "countries" in search:
                search["countries"] = [normalize_country(x) for x in search["countries"]]
            if "languages" in search:
                search["languages"] = [normalize_language(x) for x in search["languages"]]
            if "media" in search:
                search["media"] = [normalize_media(x) for x in search["media"]]
            if "regions" in search:
                search["regions"] = [normalize_region(x) for x in search["regions"]]
            if "types" in search:
                search["types"] = [normalize_media_type(x) for x in search["types"]]
            if "sentiments" in search:
                normalized = [normalize_sentiment(s) for s in search["sentiments"]]
                search["sentiments"] = [s for s in normalized if s is not None]
            payload = search

        logger.debug(f"Normalized payload to send: {payload}")

        async with aiohttp.ClientSession() as s:
            async with s.post(f"{api_url}/news/", headers=headers, json=payload) as resp:
                result = await resp.json()
        return [types.TextContent(type="text", text=str(result))]

    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    # Run the server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        asyncio.create_task(initialize_all_maps())
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="greenpulse-mcp",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )