import aiofiles
import os
from glob import glob


def get_block_file(proposal_code: str, block_code:str) -> str:
    block = glob(f"""{os.getenv("PROPOSALS_BASE_DIR")}/{proposal_code}/Included/Block-{block_code}-*""")
    if len(block) < 1:
        raise ValueError(f"Block: {block_code } not found")
    return block[0]


async def get_block_html(proposal_code: str, block_code: str) -> str:
    block_xml = get_block_file(proposal_code, block_code)
    async with aiofiles.open(block_xml, mode='r') as f:
        contents = await f.read()
        return f"""
<pre>
    ProposalCode: {proposal_code}    Block: {block_code}
    ____________________________________________________________
    {contents}
</pre>"""
