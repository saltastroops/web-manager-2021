import json
import os

import collections
import xmltodict
import re
from zipfile import ZipFile
from typing import Any, Dict, OrderedDict, List


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


def get_latest_submission(proposal_code: str, proposals_base_dir: str) -> ZipFile:
    last_submission = sorted(
        [f.path for f in os.scandir(f"""{proposals_base_dir}/{proposal_code}""") if f.is_dir()]
    )[-2]
    return ZipFile(f"{last_submission}/{proposal_code}.zip", 'r')


def _block_codes(blocks: OrderedDict) -> List:
    """
    Converts the dictionary from the proposal `Blocks` and makes a list
    block codes.
    Parameters
    ----------
    blocks
        Blocks

    Returns
    -------
        An Array of the block codes
    """
    block_codes = []
    for block in blocks["Block"]:
        block_codes.append(block["BlockCode"])
    return block_codes


def clean_proposal(proposal: Dict) -> Dict:
    """
    Removes the unwanted data from the proposal and converts the blocks to and array of block codes

    Parameters
    ----------
    proposal
        A dictionary of a proposals

    Returns
    -------
        The cleaned proposal

    """
    data_to_remove = [
        "Targets", "Pools", "SubBlocks", "SubSubBlocks", "BlockObservations",
        "Pointings", "Observations", "Acquisitions", "TelescopeConfigurations",
        "PayloadConfigurations", "InstrumentConfigurations"
    ]
    for key in data_to_remove:
        try:
            proposal.pop(key)
        except KeyError:
            pass

    proposal["Blocks"] = _block_codes(proposal["Blocks"])
    return proposal


def get_proposal_html(
    proposal_code: str, proposals_base_dir: str
) -> str:
    """
    Return a proposal as a JSON object (in form of a dictionary).

    The JSON object is constructed from the proposal XML file of the latest submission.
    submission. All namespaces in the XML file are ignored.
    """
    proposal_xml = get_latest_submission(proposal_code, proposals_base_dir).read("Proposal.xml")
    proposal_dict = xmltodict.parse(proposal_xml)
    proposal_without_namespaces = remove_namespaces(proposal_dict)["Proposal"]

    proposal_json = json.dumps(clean_proposal(proposal_without_namespaces), indent=2)
    return f"""
<pre>
    {proposal_json}
</pre>"""
