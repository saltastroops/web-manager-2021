"""Block service."""
import pathlib

import aiofiles
import collections
import xmltodict
import re
from aiomysql import Pool
from typing import Any, List, OrderedDict


async def get_block(
        proposal_code: str, block_code: str, proposals_base_dir: str
) -> OrderedDict[str, Any]:
    """
    Return a block as a JSON object (in form of a dictionary).

    The JSON object is constructed from the block XML file saved during the propsal
    submission. All namespaces in the XML file are ignored. The current block status
    and the observations made are included in the JSON object. If the block exists for
    multiple semesters, the block content for the given semester is returned, with the
    exception that observations are included for all the semesters.

    XML attributes are included, and their name is prefixed with an '@'.
    """
    block_json = await _block_json_from_xml_file(proposal_code, block_code, proposals_base_dir)
    return block_json


async def _block_json_from_xml_file(proposal_code: str, block_code: str, proposals_base_dir: str) -> OrderedDict[str, Any]:
    """
    Get the JSON object (as a dictionary) for a block from the XML file.

    The JSON object only contains the (cleaned) XML content; use the get_block method to
    get the block content with additional information.
    """
    block_xml = get_block_file(proposal_code, block_code, proposals_base_dir)
    async with aiofiles.open(block_xml, mode="r") as f:
        content = await f.read()
        block_dict = xmltodict.parse(content)
        block_without_namespaces = _clean_block_dict(block_dict)["Block"]
        return block_without_namespaces


def _remove_namespace_prefix(name: str) -> str:
    """
    Remove a namespace prefix from an XML attribute or tag name, if there is one.

    For example, "name" is returned "ns4:name", and "id" is returned for "id".
    """
    if ":" in name:
        ns, unqualified_name = name.split(":", 1)
        return unqualified_name
    else:
        return name


def _clean_block_dict(data: OrderedDict[str, Any]) -> OrderedDict[str, Any]:
    """
    Create a cleaned version of a dictionary.

    The following cleaning is done:

    * If a dictionary key contains a colon, the part up to the (first) colon is taken to
    be a namespace prefix, and it (and the colon following it) is ignored. So, for
    example, a key "ns:Name" will be replaced with "Name".

    * If a dictionary key starts with "http", the key-value pair is taken to be a
    namespace definition and is ignored.

    * If a dictionary contains the key "#text", it is replaced with the value for that
    key.

    * If a key is "@useWithReferenceName" or "@useWithReferenceNamespaceURI", the key-
    value pair is ignored.

    A new ordered dictionary is returned; the dictionary passed in remains unchanged.
    """
    updated = collections.OrderedDict()
    for key, value in data.items():
        # ignore namespace definitions
        if key and re.match(r"^http", str(key)):
            continue

        # ignore non-needed attributes
        if key in ("@useWithReferenceName", "@useWithReferenceNamespaceURI"):
            continue

        # ignore namespace prefixes
        new_key = _remove_namespace_prefix(key)

        # recursively apply the cleaning
        if isinstance(value, OrderedDict):
            if "#text" in value:
                new_value = value["#text"]
            else:
                new_value = _clean_block_dict(value)
        elif isinstance(value, list) or isinstance(value, tuple):
            new_value = [_clean_block_dict(item) for item in value]
        else:
            new_value = value

        updated[new_key] = new_value

    return updated


def get_block_file(proposal_code: str, block_code: str, proposals_base_dir: str) -> pathlib.Path:
    """
    Return the path of the XML file generated during submission for a block.
    """
    base_dir = pathlib.Path(proposals_base_dir)
    block_files = list(base_dir.glob(f"{proposal_code}/Included/Block-{block_code}-*"))
    if len(block_files) == 0:
        raise ValueError(f"Block not found: {block_code}")
    return block_files[0]




async def get_block_codes(proposal_code: str, db: Pool) -> List[str]:
    """
    WARNING: This is a temporary function! It will disappear soon!
    """
    sql = """
SELECT BlockCode
FROM BlockCode bc
JOIN Block b ON bc.BlockCode_Id = b.BlockCode_Id
JOIN ProposalCode pc ON b.ProposalCode_Id = pc.ProposalCode_Id
WHERE pc.Proposal_Code=%(proposal_code)s
ORDER BY b.Block_Id
"""
    async with db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(sql, {"proposal_code": proposal_code})
            rs = await cur.fetchall()
            return [r[0] for r in rs]
