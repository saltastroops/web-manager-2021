from typing import Dict, List
from aiomysql import connect

from app.models.pydantic import Semester


async def get_proposal_text(proposal_code: str, semester: Semester, db: connect) -> Dict:
    sql = """
SELECT Title, Abstract, ReadMe, NightLogSummary FROM ProposalText as pt
JOIN ProposalCode AS pc ON pt.ProposalCode_Id = pc.ProposalCode_Id
JOIN Semester AS s ON s.Semester_Id = pt.Semester_Id
WHERE Proposal_Code = %(proposal_code)s AND s.Year = %(year)s AND s.Semester = %(semester)s 
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
            rs = await cur.fetchone()
            if rs:
                return dict(
                    title=rs[0],
                    abstract=rs[0],
                    read_me=rs[0],
                    night_summary=rs[0],
                )


async def get_proposal_investigators(proposal_code: str, db: connect) -> List[Dict]:
    sql = """
SELECT pi.Investigator_Id, FirstName, Surname, Partner_Name, InstituteName_Name, Department, Url, Leader_Id, Contact_Id FROM ProposalInvestigator AS pi
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
            await cur.execute(
                sql,
                {"proposal_code": proposal_code}
            )
            rs = await cur.fetchall()
            if rs:
                return [dict(
                    pc=r[0] == r[8],
                    pi=r[0] == r[7],
                    name=f"{r[2]} {r[1]}",
                    partner=[3],
                    institute=[4],
                    department=r[5],
                    home_page=r[6]
                ) for r in rs]


async def get_proposal_allocations(proposal_code: str, semester: Semester, db: connect) -> List[Dict]:
    sql = """
SELECT Partner_Code, Partner_Name, Priority ,TimeAlloc, TacComment FROM MultiPartner AS mp
    JOIN ProposalCode AS pc ON mp.ProposalCode_Id = pc.ProposalCode_Id
    JOIN Semester AS s ON s.Semester_Id = mp.Semester_Id
    JOIN Partner AS p ON p.Partner_Id = mp.Partner_Id
    JOIN PriorityAlloc AS pa ON pa.MultiPartner_Id = mp.MultiPartner_Id
    JOIN TacProposalComment AS tc ON tc.MultiPartner_Id = mp.MultiPartner_Id
WHERE Proposal_Code = %(proposal_code)s AND s.Year = %(year)s AND s.Semester = %(semester)s 
    """
    async with db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                sql,
                {
                    "proposal_code": proposal_code,
                    "year": semester.year,
                    "semester": semester.semester
                }
            )
            rs = await cur.fetchall()
            if rs:
                _alloc = {}
                for r in rs:
                    if not (r[0] in _alloc):
                        _alloc[0] = {
                            "partner_code": r[0],
                            "partner_name": r[1],
                            "tac_comment": r[4]
                        }
                    _alloc[0] = {
                        f"priority_{r[2]}": r[3]
                    }
                return [_alloc[r] for r in _alloc]


async def get_proposal_targets(proposal_code: str, db: connect) -> List[Dict]:
    sql = """
SELECT Target_Name, RaH, RaM, RaS, DecSign, DecD, DecM, DecS, Equinox, MinMag, MaxMag, TargetType, TargetSubType, 
    Optional, NVisits, MaxLunarPhase, Ranking, NightCount, MoonProbability, CompetitionProbability, 
    ObservabilityProbability, SeeingProbability
FROM P1ProposalTarget AS pt
    JOIN ProposalCode AS pc ON pt.ProposalCode_Id = pc.ProposalCode_Id
    JOIN Target AS ta ON ta.Target_Id = pt.Target_Id
    JOIN TargetCoordinates AS tc ON ta.TargetCoordinates_Id = tc.TargetCoordinates_Id
    JOIN TargetMagnitudes AS tm ON ta.TargetMagnitudes_Id = tm.TargetMagnitudes_Id
    JOIN TargetSubType AS tst ON ta.TargetSubType_Id = tst.TargetSubType_Id
    JOIN TargetType AS tt ON tst.TargetType_Id = tt.TargetType_Id
    LEFT JOIN PiRanking AS pr ON pr.PiRanking_Id = pt.PiRanking_Id
    LEFT JOIN P1TargetProbabilities AS tp ON tp.Target_Id = ta.Target_Id
WHERE Proposal_Code = %(proposal_code)s
    """
    async with db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                sql,
                {"proposal_code": proposal_code}
            )
            rs = await cur.fetchall()
            if rs:
                return [dict(
                    name=r[0],
                    ra_h=r[1],
                    ra_M=r[2],
                    ra_S=r[3],
                    dec_sign=r[4],
                    dec_d=r[5],
                    dec_m=r[6],
                    dec_s=r[7],
                    equinox=r[8],
                    min_mag=r[9],
                    max_mag=r[10],
                    type=r[11],
                    sub_type=r[12],
                    optional=r[13],
                    nvisits=r[14],
                    max_luner_phase=r[15],
                    raking=[16],
                    night_count=[17],
                    moon_probability=r[18],
                    competition_probability=r[19],
                    observability_probability=r[20],
                    seeing_probability=r[21]

                ) for r in rs]


async def get_observed_targets(proposal_code: str, db: connect) -> List[Dict]:

    sql = """
SELECT bv.Block_Id, Block_Name, p.ObsTime, Priority, MaxLunarPhase, Target_Name, `Date`, BlockVisitStatus
RejectedReason FROM BlockVisit AS bv
JOIN `Block` AS b ON b.Block_Id = bv.Block_Id
JOIN ProposalCode AS pc ON pc.ProposalCode_Id = b.ProposalCode_Id
JOIN NightInfo AS ni ON ni.NightInfo_Id = bv.NightInfo_Id
JOIN Pointing AS p ON p.Block_Id = bv.Block_Id
JOIN Observation AS o ON o.Pointing_Id = p.Pointing_Id
JOIN Target AS t ON t.Target_Id = o.Target_Id
LEFT JOIN BlockVisitStatus AS bvs ON bvs.BlockVisitStatus_Id = bv.BlockVisitStatus_Id
LEFT JOIN BlockRejectedReason AS brr ON brr.BlockRejectedReason_Id = bv.BlockRejectedReason_Id 
WHERE Proposal_Code = %(proposal_code)s    
    """
    async with db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                sql,
                {"proposal_code": proposal_code}
            )
            rs = await cur.fetchall()
            if rs:
                return [dict(
                    block_id=r[0],
                    block_name=r[1],
                    observed_time=r[2],
                    priority=r[3],
                    max_luner_phase=r[4],
                    target_name=r[5],
                    observation_date=r[6],
                    block_visit_status=r[7],
                    block_rejection_reason=r[8]
                ) for r in rs]


async def get_proposal_requested_time(proposal_code: str, db: connect) -> List[dict]:
    requested_time_sql = """
SELECT TotalReqTime, P1MinimumUsefulTime, P1TimeComment, Year, Semester FROM Proposal as p
JOIN ProposalCode AS pc ON p.ProposalCode_Id = pc.ProposalCode_Id
JOIN P1MinTime AS pmt ON p.ProposalCode_Id = pmt.ProposalCode_Id
JOIN Semester AS s ON s.Semester_Id = pmt.Semester_Id
WHERE Proposal_Code = %(proposal_code)s AND `Current` = 1   
    """
    distribution_time_sql = """
SELECT Year, Semester, Partner_Code, Partner_Name, ReqTimePercent FROM MultiPartner AS mp
JOIN ProposalCode AS pc ON mp.ProposalCode_Id = pc.ProposalCode_Id
JOIN Semester AS s ON s.Semester_Id = mp.Semester_Id
JOIN Partner AS p ON p.Partner_Id = mp.Partner_Id
WHERE Proposal_Code = %(proposal_code)s
    """
    requested_time = dict()
    async with db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                requested_time_sql,
                {"proposal_code": proposal_code}
            )
            rrs = await cur.fetchall()
            for r in rrs:
                _sem = f"{r[3]}-{r[4]}"
                if not (_sem in requested_time):
                    requested_time[_sem] = dict(
                        total_requested_time=r[0],
                        minimum_useful_time=r[1],
                        time_comment=r[2],
                        distribution=[]
                    )
            await cur.execute(
                distribution_time_sql,
                {"proposal_code": proposal_code}
            )
            drs = await cur.fetchall()
            for r in drs:
                if not (r[2] == "OTH"):
                    _sem = f"{r[0]}-{r[1]}"
                    requested_time[_sem]["distribution"].append(
                        dict(
                            partner_code=r[2],
                            partner_name=r[3],
                            share_percentage=r[4]
                        )
                    )
            _req = []
            for r in requested_time:
                requested_time[r].update(semester=r)
                _req.append(requested_time[r])
    return _req


async def get_observed_time(proposal_code: str, semester:Semester, db:connect):
    sql = """
SELECT SUM(ObsTime), Priority FROM BlockVisit AS bv
    JOIN `Block` AS b ON bv.Block_Id = b.Block_Id
    JOIN ProposalCode AS pc ON pc.ProposalCode_Id = b.ProposalCode_Id
    JOIN Proposal AS p ON p.Proposal_Id = b.Proposal_Id
    JOIN Semester AS s ON s.Semester_Id = p.Semester_Id
    JOIN BlockVisitStatus AS bvs ON bvs.BlockVisitStatus_Id = bv.BlockVisitStatus_Id
WHERE Proposal_Code = '2020-1-MLT-005'
    AND BlockVisitStatus = 'Accepted'
    AND `Year` = %{year}s AND Semester = %(semester)s
GROUP BY Priority
    """
    async with db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                sql,
                {
                    "proposal_code": proposal_code,
                    "year": semester.year,
                    "semester": semester.semester
                }
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
