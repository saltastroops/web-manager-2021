from typing import Any, Dict, List, Union

from aiomysql import connect
# from astropy.coordinates import Angle
# import astropy.units as u

from app.models.proposal_model import TextContent, Investigator, Affiliation, \
    BlockVisit, Partner, Target, RequestedTime
from app.models.pydantic import Semester


async def get_text_content(
    proposal_code: str, semester: Semester, db: connect
) -> TextContent:
    sql = """
SELECT Title, Abstract, ReadMe, NightLogSummary FROM ProposalText as pt
JOIN ProposalCode AS pc ON pt.ProposalCode_Id = pc.ProposalCode_Id
JOIN Semester AS s ON s.Semester_Id = pt.Semester_Id
WHERE Proposal_Code = %(proposal_code)s
    AND s.Year = %(year)s AND s.Semester = %(semester)s
    """
    async with db.acquire() as conn:
        async with conn.dictcursor() as cur:
            await cur.execute(
                sql,
                {
                    "proposal_code": proposal_code,
                    "year": semester.year,
                    "semester": semester.semester,
                },
            )
            rs = await cur.fetchone()
            if rs:
                return TextContent(
                    title=rs[0],
                    abstract=rs[1],
                    read_me=rs[2],
                    nightlog_summary=rs[3],
                )
    raise ValueError(f"Proposal content of {proposal_code} could not be found.")


async def get_investigators(
    proposal_code: str, db: connect
) -> List[Investigator]:
    sql = """\
SELECT pi.Investigator_Id, FirstName, Surname, Partner_Name, InstituteName_Name,
        Department, Url, Leader_Id, Contact_Id, Partner_Code 
FROM ProposalInvestigator AS pi
    JOIN ProposalCode AS pc ON pi.ProposalCode_Id = pc.ProposalCode_Id
    JOIN Investigator AS inv ON inv.Investigator_Id = pi.Investigator_Id
    JOIN Institute AS ins ON ins.Institute_Id = inv.Institute_Id
    JOIN ProposalContact AS pcon ON pcon.ProposalCode_Id = pc.ProposalCode_Id
    JOIN InstituteName AS insn ON insn.InstituteName_Id = ins.InstituteName_Id
    JOIN Partner AS p ON ins.Partner_Id = p.Partner_Id
WHERE Proposal_Code = %(proposal_code)s
    """
    async with db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(sql, {"proposal_code": proposal_code})
            rs = await cur.fetchall()
            if rs:
                return [
                    Investigator(
                        is_pc=r[0] == r[8],
                        is_pi=r[0] == r[7],
                        name=f"{r[2]} {r[1]}",
                        affiliation=Affiliation(
                            partner_code=r[9],
                            partner_name=r[3],
                            institute=r[4],
                            department=r[5],
                            home_page=r[6]
                        )
                    )
                    for r in rs
                ]
    raise ValueError(f"Investigator for {proposal_code} couldn't be found.")


async def get_time_allocations(
    proposal_code: str, semester: Semester, db: connect
) -> List[Dict[str, Any]]:
    sql = """
SELECT Partner_Code, Partner_Name, Priority ,TimeAlloc, TacComment
FROM MultiPartner AS mp
    JOIN ProposalCode AS pc ON mp.ProposalCode_Id = pc.ProposalCode_Id
    JOIN Semester AS s ON s.Semester_Id = mp.Semester_Id
    JOIN Partner AS p ON p.Partner_Id = mp.Partner_Id
    JOIN PriorityAlloc AS pa ON pa.MultiPartner_Id = mp.MultiPartner_Id
    JOIN TacProposalComment AS tc ON tc.MultiPartner_Id = mp.MultiPartner_Id
WHERE Proposal_Code = %(proposal_code)s
    AND s.Year = %(year)s AND s.Semester = %(semester)s
    """
    async with db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                sql,
                {
                    "proposal_code": proposal_code,
                    "year": semester.year,
                    "semester": semester.semester,
                },
            )
            rs = await cur.fetchall()
            if rs:
                _alloc = {}
                for r in rs:
                    if not (r[0] in _alloc):
                        _alloc[r[0]] = {
                            "partner": Partner(
                                name=r[1],
                                code=r[0]
                            ),
                            "tac_comment": r[4],
                        }
                    _alloc[r[0]][f"priority_{r[2]}"] = r[3]
                return [_alloc[r] for r in _alloc]
    raise ValueError(f"Targets for proposal {proposal_code} couldn't be found")


# async def get_phase_1_targets(proposal_code: str, db: connect) -> List[Target]:
#     sql = """
# SELECT Target_Name, RaH, RaM, RaS, DecSign, DecD, DecM, DecS, Equinox, MinMag, MaxMag-10,
#     TargetType, TargetSubType, Optional, NVisits, MaxLunarPhase, Ranking, NightCount,
#     MoonProbability, CompetitionProbability, ObservabilityProbability-20, SeeingProbability,
#     Identifier, OutputInterval, RaDot, DecDot, Epoch
# FROM P1ProposalTarget AS pt
#     JOIN ProposalCode AS pc ON pt.ProposalCode_Id = pc.ProposalCode_Id
#     JOIN Target AS ta ON ta.Target_Id = pt.Target_Id
#     JOIN TargetCoordinates AS tc ON ta.TargetCoordinates_Id = tc.TargetCoordinates_Id
#     JOIN TargetMagnitudes AS tm ON ta.TargetMagnitudes_Id = tm.TargetMagnitudes_Id
#     JOIN TargetSubType AS tst ON ta.TargetSubType_Id = tst.TargetSubType_Id
#     JOIN TargetType AS tt ON tst.TargetType_Id = tt.TargetType_Id
#     LEFT JOIN PiRanking AS pr ON pr.PiRanking_Id = pt.PiRanking_Id
#     LEFT JOIN P1TargetProbabilities AS tp ON tp.Target_Id = ta.Target_Id
#     LEFT JOIN HorizonsTarget AS ht ON ht.HorizonsTarget_Id = ta.HorizonsTarget_Id
#     LEFT JOIN MovingTarget AS mt ON mt.MovingTarget_Id = ta.MovingTarget_Id
# WHERE Proposal_Code = %(proposal_code)s
#     """
#     async with db.acquire() as conn:
#         async with conn.cursor() as cur:
#             await cur.execute(sql, {"proposal_code": proposal_code})
#             rs = await cur.fetchall()
#             if rs:
#                 return [
#                     Target(
#                         name=r[0],
#                         ra=Angle(f"{r[1]}:{r[2]}:{r[3]} hours").degree * u.deg,
#                         dec=Angle(f"{r[4]}{r[5]}:{r[6]}:{r[7]} degrees").degree * u.deg,
#                         equinox=r[8],
#                         minimun_magnitude=r[9],
#                         maximun_magnitude=r[10],
#                         target_type=r[11],
#                         sub_type=r[12],
#                         is_optional=r[13] == 1,
#                         n_visits=r[14],
#                         max_luner_phase=r[15],
#                         ranking=r[16],
#                         night_count=r[17],
#                         moon_probability=r[18],
#                         competition_probability=r[19],
#                         observability_probability=r[20],
#                         seeing_probability=r[21],
#                         identifier=r[22],
#                         output_interval=r[23],
#                         ra_dot=Angle(r[24]),  # Todo units of this two please
#                         dec_dot=Angle(r[25]),  # Todo units of this two please
#                         epoch=r[26]
#                     )
#                     for r in rs
#                 ]
#     raise ValueError(f"Targets for proposal {proposal_code} couldn't be found")


async def get_block_visits(
    proposal_code: str, db: connect
) -> List[BlockVisit]:

    sql = """
SELECT bv.Block_Id, Block_Name, p.ObsTime, Priority, MaxLunarPhase, Target_Name,
    `Date`, BlockVisitStatus, RejectedReason
RejectedReason FROM BlockVisit AS bv
    JOIN `Block` AS b ON b.Block_Id = bv.Block_Id
    JOIN ProposalCode AS pc ON pc.ProposalCode_Id = b.ProposalCode_Id
    JOIN NightInfo AS ni ON ni.NightInfo_Id = bv.NightInfo_Id
    JOIN Pointing AS p ON p.Block_Id = bv.Block_Id
    JOIN Observation AS o ON o.Pointing_Id = p.Pointing_Id
    JOIN Target AS t ON t.Target_Id = o.Target_Id
    LEFT JOIN BlockVisitStatus AS bvs
        ON bvs.BlockVisitStatus_Id = bv.BlockVisitStatus_Id
    LEFT JOIN BlockRejectedReason AS brr
        ON brr.BlockRejectedReason_Id = bv.BlockRejectedReason_Id
WHERE Proposal_Code = %(proposal_code)s
    """
    async with db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(sql, {"proposal_code": proposal_code})
            rs = await cur.fetchall()
            if rs:
                return [
                    BlockVisit(
                        block_id=r[0],
                        block_name=r[1],
                        observed_time=r[2],
                        priority=r[3],
                        max_luner_phase=r[4],
                        target_name=r[5],
                        observation_date=r[6],
                        status=r[7],
                        rejection_reason=r[8],
                    )
                    for r in rs
                ]
    raise ValueError(f"Targets for proposal {proposal_code} couldn't be found")


async def get_total_requested_time(
    proposal_code: str, db: connect
) -> List[BlockVisit]:

    sql = """
SELECT SUM(p1rt.P1RequestedTime) AS total_requested_time
FROM P1RequestedTime AS p1rt
WHERE p1rt.Proposal_Id IN %(proposal_id)s
GROUP BY p1rt.Proposal_Id, p1rt.Semester_Id
    """
    async with db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(sql, {"proposal_code": proposal_code})
            rs = await cur.fetchall()
            if rs:
                return [
                    BlockVisit(
                        block_id=r[0],
                        block_name=r[1],
                        observed_time=r[2],
                        priority=r[3],
                        max_luner_phase=r[4],
                        target_name=r[5],
                        observation_date=r[6],
                        status=r[7],
                        rejection_reason=r[8],
                    )
                    for r in rs
                ]
    raise ValueError(f"Targets for proposal {proposal_code} couldn't be found")


async def get_requested_time(
    proposal_code: str, proposal_id: int, db: connect
) -> List[RequestedTime]:
    requested_time_sql = """
SELECT P1MinimumUsefulTime, P1TimeComment, Year, Semester
FROM P1MinTime AS pmt
    JOIN ProposalCode AS pc ON pmt.ProposalCode_Id = pc.ProposalCode_Id
    JOIN Semester AS s ON s.Semester_Id = pmt.Semester_Id
WHERE Proposal_Code = %(proposal_code)s 
    """
    distribution_time_sql = """
SELECT Year, Semester, Partner_Code, Partner_Name, ReqTimePercent
FROM MultiPartner AS mp
    JOIN ProposalCode AS pc ON mp.ProposalCode_Id = pc.ProposalCode_Id
    JOIN Semester AS s ON s.Semester_Id = mp.Semester_Id
    JOIN Partner AS p ON p.Partner_Id = mp.Partner_Id
WHERE Proposal_Code = %(proposal_code)s
    """
    total_requested_time_sql = """
SELECT `Year`, Semester, SUM(p1rt.P1RequestedTime) AS total_requested_time
FROM P1RequestedTime AS p1rt
    JOIN Semester AS s ON s.Semester_Id = p1rt.Semester_Id
WHERE p1rt.Proposal_Id = %(proposal_id)s
GROUP BY p1rt.Proposal_Id, p1rt.Semester_Id
    """
    requested_time = dict()
    async with db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(requested_time_sql, {"proposal_code": proposal_code})
            rrs = await cur.fetchall()
            for r in rrs:
                _sem = f"{r[2]}-{r[3]}"
                if not (_sem in requested_time):
                    requested_time[_sem] = RequestedTime(
                        total_requested_time=0,
                        minimum_useful_time=r[0],
                        time_comment=r[1],
                        semester=Semester(year=r[2], semester=r[3]),
                        distribution=[],
                    )
            await cur.execute(total_requested_time_sql, {"proposal_id": proposal_id})
            trt = await cur.fetchall()
            for r in trt:
                _sem = f"{r[0]}-{r[1]}"
                requested_time[_sem].total_requested_time = r[2]
            await cur.execute(distribution_time_sql, {"proposal_code": proposal_code})
            drs = await cur.fetchall()
            for r in drs:
                if not (r[2] == "OTH"):  # TODO: raise error if oth allocated time
                    _sem = f"{r[0]}-{r[1]}"
                    requested_time[_sem].distribution.append(
                        dict(
                            partner=Partner(code=r[2], name=r[3]), share_percentage=r[4]
                        )
                    )
    return [requested_time[r] for r in requested_time]


async def get_observed_time(
    proposal_code: str, semester: Semester, db: connect
) -> Dict[str, Any]:
    sql = """
SELECT SUM(ObsTime), Priority 
FROM BlockVisit AS bv
    JOIN `Block` AS b ON bv.Block_Id = b.Block_Id
    JOIN ProposalCode AS pc ON pc.ProposalCode_Id = b.ProposalCode_Id
    JOIN Proposal AS p ON p.Proposal_Id = b.Proposal_Id
    JOIN Semester AS s ON s.Semester_Id = p.Semester_Id
    JOIN BlockVisitStatus AS bvs ON bvs.BlockVisitStatus_Id = bv.BlockVisitStatus_Id
WHERE Proposal_Code = %(proposal_code)s
    AND BlockVisitStatus = 'Accepted'
    AND `Year` = %(year)s AND Semester = %(semester)s
GROUP BY Priority
    """
    async with db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                sql,
                {
                    "proposal_code": proposal_code,
                    "year": semester.year,
                    "semester": semester.semester,
                },
            )
            rs = await cur.fetchall()
            observed_time = dict(
                priority_0=0,
                priority_1=0,
                priority_2=0,
                priority_3=0,
                priority_4=0,
            )
            for r in rs:
                observed_time[f"priority_{r[1]}"] = r[0]
            return observed_time
