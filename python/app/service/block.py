import aiofiles
import os
from typing import List


def get_last_submission(proposal_code: str) -> List[str]:
    return sorted(
        [f.path for f in os.scandir(f"""{os.getenv("BASE_DIR")}/{proposal_code}""") if f.is_dir()]
    )[-2]


async def get_block_html(proposal_code: str, block_code: str) -> str:
    last_submission = f"""{os.getenv("BASE_DIR")}/{proposal_code}/Included/Block-{block_code}-2018-1.xml"""
    with aiofiles.open(last_submission, mode='r') as f:
        contents = await f.read()
        return f"""
<pre>
    ProposalCode: {proposal_code}    Block: {block_code}
    ____________________________________________________________
    {contents}
</pre>"""
