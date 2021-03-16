from glob import glob
from typing import List

import aiofiles
from aiomysql import Pool


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
        contents = await f.read()
        return f"""
<pre>
    {contents}
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
