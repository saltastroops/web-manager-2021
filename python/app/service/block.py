import os
import zipfile
from typing import List


def get_last_submission(proposal_code: str) -> List[str]:
    return sorted(
        [f.path for f in os.scandir(f"""{os.getenv("BASE_DIR")}/{proposal_code}""") if f.is_dir()]
    )[-2]


def get_block_html(proposal_code: str, block_code: str) -> str:
    last_submission = get_last_submission(proposal_code)
    archive = zipfile.ZipFile(f"{last_submission}/{proposal_code}.zip", 'r')
    proposal_xml = archive.open('Proposal.xml')
    return f"""
<pre>
    ProposalCode: {proposal_code}    Block: {block_code}
    ____________________________________________________________
    
    {proposal_xml.read()}
    
</pre>
"""
