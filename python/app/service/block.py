import json

import aiofiles
import collections
import xmltodict
import re
from aiomysql import Pool
from glob import glob
from typing import Any, List, Dict, OrderedDict


def updated_key(key: str) -> str:
    if ":" in key:
        ns, tag = key.split(":", 1)
        return tag
    else:
        return key


def updated_value(value: Any) -> Any:
    if isinstance(value, dict):
        return remove_namespaces(value)
    elif isinstance(value, list) or isinstance(value, tuple):
        return [updated_value(item) for item in value]
    else:
        if not value:
            return value
        if re.match(r"^http", str(value)):
            return "Pass this value."
        return value


def remove_namespaces(data: Dict[str, Any]) -> OrderedDict[str, Any]:
    updated = collections.OrderedDict()
    for key, value in data.items():
        new_key = updated_key(key)
        new_value = updated_value(value)

        if re.match(r"^\@", str(new_key)):
            new_key = new_key[1:]
        if not (new_value == "Pass this value."):
            updated[new_key] = new_value
    return updated


def get_block_file(proposal_code: str, block_code: str, proposals_base_dir: str) -> str:
    print(f"{proposals_base_dir}/{proposal_code}")
    block = glob(f"{proposals_base_dir}/{proposal_code}/Included/Block-{block_code}-*")
    if len(block) < 1:
        raise ValueError(f"Block: {block_code } not found")
    return block[0]


async def get_block_html(
    proposal_code: str, block_code: str, proposals_base_dir: str
) -> str:
    block_xml = get_block_file(proposal_code, block_code, proposals_base_dir)
    async with aiofiles.open(block_xml, mode="r") as f:
        content = await f.read()
        block_dict = xmltodict.parse(content)
        block_without_namespaces = remove_namespaces(block_dict)["Block"]
        block_json = json.dumps(block_without_namespaces, indent=2)
        return f"""
<pre>
    {block_json}
</pre>"""


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
