from __future__ import annotations

import json
import math
import re
import zipfile
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd


REQUIRED_EVENT_COLUMNS = [
    "source_dataset_id",
    "source_record_id",
    "source_year",
    "industry_major",
    "industry_minor",
    "job_title_raw",
    "job_group_standard",
    "process_group_standard",
    "accident_type_raw",
    "accident_type_standard",
    "injury_or_disease_type",
    "hazard_factor_standard",
    "severity_band",
    "worker_type",
    "employment_type",
    "company_size_band",
    "region",
    "weather_linkable",
    "chemical_related",
    "narrative_text",
    "countermeasure_text",
]

ACCIDENT_CATEGORIES = [
    "추락",
    "끼임",
    "충돌",
    "낙하",
    "붕괴",
    "전도",
    "화재폭발",
    "화학물질노출",
    "감전",
    "질식",
    "무리한동작",
    "교통/이동",
    "기타",
]

PROCESS_CATEGORIES = [
    "운반/인양",
    "설치/해체",
    "정비/보전",
    "절단/가공",
    "청소/정리",
    "점검/검사",
    "화학물질취급",
    "상하차/물류",
    "굴착/토공",
    "배관/용접",
    "전기작업",
    "도장/마감",
    "보행/이동",
    "기타",
]

INDUSTRY_PATTERNS = [
    ("건설업", [r"건설", r"토공", r"건축", r"철골", r"비계", r"전기공사", r"플랜트"]),
    ("제조업", [r"제조", r"가공", r"공업", r"인쇄", r"금속", r"화학", r"고무", r"식품", r"전자", r"기계", r"자동차"]),
    ("운수·창고업", [r"운수", r"운송", r"택배", r"배송", r"창고", r"물류", r"하역"]),
    ("농림어업", [r"농업", r"축산", r"임업", r"어업"]),
    ("광업", [r"광업", r"광산"]),
    ("전기·가스·환경", [r"전기", r"가스", r"수도", r"환경", r"폐기물"]),
    ("서비스업", [r"서비스", r"도매", r"소매", r"숙박", r"음식", r"시설", r"보건", r"사회복지", r"교육", r"사업지원", r"기타의사업"]),
]

JOB_PATTERNS = [
    ("물류·배송", [r"택배", r"배송", r"배달", r"상하차"]),
    ("운송·장비운전", [r"지게차", r"굴착기", r"백호", r"크레인", r"운전", r"기사"]),
    ("설비정비", [r"정비", r"보전", r"점검", r"설비"]),
    ("건설현장작업", [r"철골", r"형틀", r"비계", r"건설", r"토공", r"배근", r"미장"]),
    ("제조현장작업", [r"조작원", r"생산", r"제조", r"인쇄", r"가공", r"검사원"]),
    ("배관·용접", [r"배관", r"용접", r"절단"]),
    ("시설관리", [r"청소", r"시설", r"경비", r"관리"]),
    ("화학공정", [r"화학", r"혼합", r"반응", r"도금"]),
]

PROCESS_PATTERNS = [
    ("상하차/물류", [r"상하차", r"물류", r"하역", r"배송", r"택배"]),
    ("운반/인양", [r"인양", r"운반", r"리프트", r"승강기", r"이송", r"크레인"]),
    ("설치/해체", [r"설치", r"해체", r"조립", r"거푸집", r"비계"]),
    ("정비/보전", [r"정비", r"보수", r"수리", r"교체", r"윤활"]),
    ("점검/검사", [r"점검", r"검사", r"확인", r"비정형 작업\(점검\)"]),
    ("청소/정리", [r"청소", r"정리", r"폐기물"]),
    ("절단/가공", [r"절단", r"가공", r"연삭", r"프레스", r"절곡", r"절단기"]),
    ("화학물질취급", [r"화학", r"혼합", r"도금", r"세척", r"용제", r"윤활유"]),
    ("굴착/토공", [r"굴착", r"토공", r"흙막이", r"되메우기"]),
    ("배관/용접", [r"배관", r"용접", r"가스절단"]),
    ("전기작업", [r"전기", r"배선", r"활선", r"분전"]),
    ("도장/마감", [r"도장", r"방수", r"도포", r"마감"]),
    ("보행/이동", [r"출퇴근", r"이동", r"보행", r"통행"]),
]

ACCIDENT_PATTERNS = [
    ("추락", [r"추락", r"떨어져", r"떨어짐", r"개구부", r"아래로 떨어"]),
    ("끼임", [r"끼", r"말려", r"협착", r"압착", r"깔려", r"으깸", r"절단"]),
    ("충돌", [r"충돌", r"부딪", r"접촉"]),
    ("낙하", [r"낙하", r"비래", r"적재물", r"중량물", r"자재.*떨어"]),
    ("붕괴", [r"붕괴", r"무너", r"도괴", r"매몰"]),
    ("전도", [r"전도", r"전복", r"넘어지"]),
    ("화재폭발", [r"화재", r"폭발", r"연소", r"화상"]),
    ("화학물질노출", [r"화학", r"유해", r"중독", r"노출", r"가스.*흡입", r"용제"]),
    ("감전", [r"감전", r"전기", r"활선"]),
    ("질식", [r"질식", r"산소결핍", r"밀폐", r"맨홀", r"탱크"]),
    ("무리한동작", [r"염좌", r"긴장", r"근골격", r"요추", r"허리", r"무리"]),
    ("교통/이동", [r"출퇴근", r"교통", r"차량", r"자동차", r"오토바이", r"도로"]),
]

HAZARD_PATTERNS = [
    ("고소/개구부", [r"고소", r"개구부", r"지붕", r"비계", r"사다리"]),
    ("기계설비", [r"컨베이어", r"혼합기", r"프레스", r"기계", r"설비", r"벨트", r"풀리"]),
    ("중장비/차량", [r"굴착기", r"지게차", r"크레인", r"차량", r"화물자동차", r"백호"]),
    ("화학물질", [r"화학", r"산", r"용제", r"가스", r"윤활유", r"도금"]),
    ("전기", [r"전기", r"감전", r"활선", r"배선"]),
    ("화재·폭발원", [r"폭발", r"화재", r"불꽃", r"화기", r"용접"]),
    ("미끄럼/보행", [r"미끄", r"바닥", r"통로", r"보행"]),
    ("밀폐공간", [r"밀폐", r"맨홀", r"탱크", r"질식"]),
    ("붕괴위험", [r"붕괴", r"도괴", r"흙막이", r"거푸집"]),
    ("인양/하역", [r"인양", r"하역", r"상하차", r"중량물"]),
]

ACCIDENT_PATTERNS_SUPPLEMENTAL = [
    ("무리한동작", [r"염좌", r"회전근개", r"관절증", r"반달연골", r"전십자인대", r"인대의 파열", r"충격증후군", r"신경뿌리병증", r"손목터널", r"상과염"]),
    ("충돌", [r"골절", r"타박상", r"열린 상처", r"열상", r"진탕", r"두피의 열린 상처", r"찢김", r"좌상", r"타박"]),
    ("끼임", [r"절단", r"압궤", r"으깸", r"절상", r"수지신경의 손상"]),
    ("화재폭발", [r"화상"]),
    ("화학물질노출", [r"중독", r"유해물질", r"유기용제", r"질식성 가스"]),
]

PROCESS_PATTERNS_SUPPLEMENTAL = [
    ("상하차/물류", [r"택배", r"배달", r"퀵서비스", r"화물차", r"운송", r"배송", r"창고", r"지게차", r"물류", r"상하차"]),
    ("설치/해체", [r"건설관련 기능", r"건설구조관련", r"비계", r"형틀", r"철근", r"조적", r"해체", r"설치"]),
    ("굴착/토공", [r"토목", r"채굴", r"굴착", r"굴삭기", r"천공", r"발파"]),
    ("절단/가공", [r"기계조작원", r"금속공작", r"제관", r"판금", r"목재", r"가구", r"인쇄", r"금형", r"주조", r"단조", r"생산기 조작", r"제조관련"]),
    ("청소/정리", [r"조리사", r"주방", r"음식서비스", r"음식관련", r"위생"]),
    ("점검/검사", [r"검침", r"시험원", r"검사원"]),
    ("보행/이동", [r"경비", r"검표", r"순찰", r"주차"]),
]


@dataclass
class Paths:
    root: Path
    data_sources: Path
    raw: Path
    processed: Path
    intermediate: Path
    reports: Path


def normalize_space(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and math.isnan(value):
        return ""
    text = str(value).replace("\r", " ").replace("\n", " ")
    return re.sub(r"\s+", " ", text).strip()


def extract_year(text: str) -> str:
    match = re.search(r"(20\d{2})", text)
    return match.group(1) if match else ""


def first_match_category(text: str, patterns: list[tuple[str, list[str]]], default: str) -> tuple[str, str]:
    normalized = normalize_space(text)
    if not normalized:
        return default, "empty"
    for category, regexes in patterns:
        for regex in regexes:
            if re.search(regex, normalized):
                return category, f"keyword:{regex}"
    return default, "fallback"


def standardize_industry(text: str) -> tuple[str, str]:
    normalized = normalize_space(text)
    if not normalized:
        return "기타", "empty"
    for category, regexes in INDUSTRY_PATTERNS:
        for regex in regexes:
            if re.search(regex, normalized):
                return category, f"keyword:{regex}"
    return "기타", "fallback"


def standardize_job(text: str) -> tuple[str, str]:
    normalized = normalize_space(text)
    if not normalized:
        return "unknown", "empty"
    for category, regexes in JOB_PATTERNS:
        for regex in regexes:
            if re.search(regex, normalized):
                return category, f"keyword:{regex}"
    return normalized, "identity"


def standardize_process(text: str) -> tuple[str, str]:
    return first_match_category(text, PROCESS_PATTERNS + PROCESS_PATTERNS_SUPPLEMENTAL, "기타")


def standardize_accident(text: str) -> tuple[str, str]:
    return first_match_category(text, ACCIDENT_PATTERNS + ACCIDENT_PATTERNS_SUPPLEMENTAL, "기타")


def standardize_hazard(text: str) -> tuple[str, str]:
    return first_match_category(text, HAZARD_PATTERNS, "기타")


def company_size_from_numeric(value: object) -> str:
    try:
        count = int(float(str(value).strip()))
    except Exception:
        return "unknown"
    if count < 5:
        return "0-4"
    if count < 30:
        return "5-29"
    if count < 100:
        return "30-99"
    if count < 300:
        return "100-299"
    if count < 1000:
        return "300-999"
    return "1000+"


def company_size_from_text(text: str) -> str:
    normalized = normalize_space(text)
    if not normalized:
        return "unknown"
    if "5인 미만" in normalized:
        return "0-4"
    if "5~30" in normalized or "5~29" in normalized:
        return "5-29"
    if "30~50" in normalized or "30~99" in normalized:
        return "30-99"
    if "50~99" in normalized:
        return "50-99"
    if "100~299" in normalized:
        return "100-299"
    if "300~999" in normalized:
        return "300-999"
    if "1000인 이상" in normalized:
        return "1000+"
    match = re.search(r"(\d+)", normalized)
    if match:
        return company_size_from_numeric(match.group(1))
    return "unknown"


def region_from_text(text: str) -> str:
    normalized = normalize_space(text)
    if not normalized:
        return "unknown"
    parts = normalized.split()
    return " ".join(parts[:2]) if len(parts) >= 2 else parts[0]


def truthy_keyword(text: str, patterns: Iterable[str]) -> bool:
    normalized = normalize_space(text)
    return any(re.search(pattern, normalized) for pattern in patterns)


def coalesce(*values: object) -> str:
    for value in values:
        text = normalize_space(value)
        if text:
            return text
    return ""


def ensure_dirs(paths: Paths) -> None:
    paths.processed.mkdir(parents=True, exist_ok=True)
    paths.intermediate.mkdir(parents=True, exist_ok=True)
    paths.reports.mkdir(parents=True, exist_ok=True)


def load_sif_events(paths: Paths) -> pd.DataFrame:
    workbook = paths.raw / "15140383_sif_archive.xlsx"

    manufacturing = pd.read_excel(workbook, sheet_name=1, skiprows=2)
    manufacturing = manufacturing.dropna(axis=1, how="all")
    manufacturing = manufacturing.rename(columns=lambda c: normalize_space(c).replace("\n", " "))
    manufacturing = manufacturing.rename(
        columns={
            "산재업종 (대분류)": "산재업종_대분류",
            "산재업종 (중분류)": "산재업종_중분류",
            "산재업종 (소분류)": "산재업종_소분류",
        }
    )
    if "산재업종 (대분류)" in manufacturing.columns:
        manufacturing = manufacturing.rename(
            columns={
                "산재업종 (대분류)": "산재업종_대분류",
                "산재업종 (중분류)": "산재업종_중분류",
                "산재업종 (소분류)": "산재업종_소분류",
            }
        )
    manufacturing["dataset_subtype"] = "sif_manufacturing"
    manufacturing["process_raw"] = manufacturing["고위험작업·상황"].astype(str)
    manufacturing["accident_type_raw"] = manufacturing["재해유발요인"].astype(str)
    manufacturing["industry_major_raw"] = manufacturing["산재업종_대분류"].astype(str)
    manufacturing["industry_minor_raw"] = manufacturing["산재업종_중분류"].astype(str)
    manufacturing["industry_detail_raw"] = manufacturing["산재업종_소분류"].astype(str)

    construction = pd.read_excel(workbook, sheet_name=2, header=None, skiprows=4)
    construction = construction.iloc[:, 1:10]
    construction.columns = [
        "연번",
        "공종",
        "작업명",
        "단위작업명",
        "재해종류",
        "재해개요",
        "기인물",
        "재해유발요인",
        "위험성 감소대책(예시)",
    ]
    construction["dataset_subtype"] = "sif_construction"
    construction["process_raw"] = (
        construction["공종"].astype(str)
        + " / "
        + construction["작업명"].astype(str)
        + " / "
        + construction["단위작업명"].astype(str)
    )
    construction["accident_type_raw"] = construction["재해종류"].astype(str)
    construction["industry_major_raw"] = "건설업"
    construction["industry_minor_raw"] = construction["공종"].astype(str)
    construction["industry_detail_raw"] = construction["단위작업명"].astype(str)

    common = []
    for df in (manufacturing, construction):
        standardized = pd.DataFrame(index=df.index)
        standardized["source_dataset_id"] = "15140383"
        standardized["source_record_id"] = df["dataset_subtype"].astype(str) + "-" + df["연번"].astype(str)
        standardized["source_year"] = df["재해개요"].map(extract_year)
        standardized["industry_raw"] = df["industry_detail_raw"].fillna(df["industry_minor_raw"]).fillna(df["industry_major_raw"])
        standardized["industry_major_raw"] = df["industry_major_raw"]
        standardized["industry_minor_raw"] = df["industry_minor_raw"]
        standardized["job_title_raw"] = ""
        standardized["process_raw"] = df["process_raw"]
        standardized["accident_type_raw"] = df["accident_type_raw"]
        standardized["injury_or_disease_type"] = df.get("재해종류", "").astype(str) if "재해종류" in df.columns else ""
        standardized["hazard_factor_raw"] = df["재해유발요인"].astype(str) + " " + df["기인물"].astype(str)
        standardized["severity_band"] = "fatal_or_sif"
        standardized["worker_type"] = "employee"
        standardized["employment_type"] = "employee"
        standardized["company_size_band"] = "unknown"
        standardized["region"] = "unknown"
        standardized["weather_linkable"] = False
        standardized["chemical_related"] = (
            df["재해개요"].astype(str).map(lambda v: truthy_keyword(v, [r"화학", r"용제", r"산", r"가스"]))
            | df["재해유발요인"].astype(str).map(lambda v: truthy_keyword(v, [r"화학", r"용제", r"산", r"가스"]))
        )
        standardized["narrative_text"] = df["재해개요"].astype(str)
        standardized["countermeasure_text"] = df["위험성 감소대책(예시)"].astype(str)
        common.append(standardized)

    return pd.concat(common, ignore_index=True)


def load_approval_events(paths: Paths) -> pd.DataFrame:
    df = pd.read_csv(paths.raw / "3082968_first_medical_approval.csv", encoding="utf-8-sig", dtype=str)
    out = pd.DataFrame(index=df.index)
    out["source_dataset_id"] = "3082968"
    out["source_record_id"] = "3082968-" + df["연번"].astype(str)
    out["source_year"] = df["재해일자"].fillna("").astype(str).str.slice(0, 4)
    out["industry_raw"] = df["업종명"]
    out["industry_major_raw"] = df["업종명"]
    out["industry_minor_raw"] = df["업종명"]
    out["job_title_raw"] = df["직종명"].fillna("")
    out["process_raw"] = df["직종명"].fillna("")
    out["accident_type_raw"] = df["재해발생형태"].fillna("") + " " + df["세부상병명"].fillna("")
    out["injury_or_disease_type"] = coalesce_series(df.get("직업병명(대)"), df.get("세부상병명"))
    out["hazard_factor_raw"] = df["세부상병명"].fillna("")
    out["severity_band"] = df["유족급여청구"].map(lambda v: "serious" if normalize_space(v) else "general")
    out["worker_type"] = df["직종명"].fillna("").map(
        lambda v: "special_worker" if "(노무제공)" in normalize_space(v) else "employee"
    )
    out["employment_type"] = df["직종명"].fillna("").map(
        lambda v: "platform_or_contract" if "(노무제공)" in normalize_space(v) else "employee"
    )
    out["company_size_band"] = "unknown"
    out["region"] = df["사업장(현장) 소재지"].fillna("").map(region_from_text)
    out["weather_linkable"] = True
    out["chemical_related"] = (
        df["업종명"].fillna("").map(lambda v: truthy_keyword(v, [r"화학", r"고무", r"도금"]))
        | df["세부상병명"].fillna("").map(lambda v: truthy_keyword(v, [r"중독", r"화상", r"노출"]))
    )
    out["narrative_text"] = ""
    out["countermeasure_text"] = ""
    return out


def load_foreign_worker_events(paths: Paths) -> pd.DataFrame:
    df = pd.read_csv(paths.raw / "15121557_foreign_worker_accident_detail.csv", encoding="cp949", dtype=str)
    out = pd.DataFrame(index=df.index)
    out["source_dataset_id"] = "15121557"
    out["source_record_id"] = "15121557-" + df["연번"].astype(str)
    out["source_year"] = "2023"
    out["industry_raw"] = df["산재업종(대분류)"]
    out["industry_major_raw"] = df["산재업종(대분류)"]
    out["industry_minor_raw"] = df["산재업종(대분류)"]
    out["job_title_raw"] = "외국인근로자"
    out["process_raw"] = ""
    out["accident_type_raw"] = df["재해발생형태"]
    out["injury_or_disease_type"] = df["재해발생형태"]
    out["hazard_factor_raw"] = df["재해발생형태"] + " " + df["산재업종(대분류)"]
    out["severity_band"] = "general"
    out["worker_type"] = "foreign_worker"
    out["employment_type"] = "foreign_worker"
    out["company_size_band"] = df["사업장규모"].map(company_size_from_text)
    out["region"] = df["지역본부"].fillna("")
    out["weather_linkable"] = False
    out["chemical_related"] = df["산재업종(대분류)"].fillna("").map(lambda v: truthy_keyword(v, [r"화학", r"고무"]))
    out["narrative_text"] = ""
    out["countermeasure_text"] = ""
    return out


def coalesce_series(series_a: pd.Series | None, series_b: pd.Series | None) -> pd.Series:
    a = series_a.fillna("").astype(str) if series_a is not None else pd.Series(dtype=str)
    b = series_b.fillna("").astype(str) if series_b is not None else pd.Series(dtype=str)
    if len(a) == 0:
        return b
    if len(b) == 0:
        return a
    return a.where(a.str.strip() != "", b)


def normalize_event_frame(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Counter]]:
    stats = {
        "industry": Counter(),
        "job": Counter(),
        "process": Counter(),
        "accident": Counter(),
        "hazard": Counter(),
    }

    records: list[dict[str, object]] = []
    taxonomy_rows: list[dict[str, str]] = []

    for row in df.to_dict(orient="records"):
        industry_major, industry_match = standardize_industry(coalesce(row.get("industry_minor_raw"), row.get("industry_major_raw"), row.get("industry_raw")))
        job_standard, job_match = standardize_job(row.get("job_title_raw", ""))
        process_standard, process_match = standardize_process(coalesce(row.get("process_raw"), row.get("job_title_raw")))
        accident_standard, accident_match = standardize_accident(
            coalesce(
                row.get("accident_type_raw"),
                row.get("injury_or_disease_type"),
                row.get("narrative_text"),
                row.get("hazard_factor_raw"),
            )
        )
        hazard_standard, hazard_match = standardize_hazard(coalesce(row.get("hazard_factor_raw"), row.get("narrative_text"), row.get("process_raw")))

        stats["industry"][industry_match] += 1
        stats["job"][job_match] += 1
        stats["process"][process_match] += 1
        stats["accident"][accident_match] += 1
        stats["hazard"][hazard_match] += 1

        record = {
            "source_dataset_id": normalize_space(row.get("source_dataset_id")),
            "source_record_id": normalize_space(row.get("source_record_id")),
            "source_year": normalize_space(row.get("source_year")),
            "industry_major": industry_major,
            "industry_minor": coalesce(row.get("industry_minor_raw"), row.get("industry_raw")),
            "job_title_raw": normalize_space(row.get("job_title_raw")),
            "job_group_standard": job_standard,
            "process_group_standard": process_standard,
            "accident_type_raw": normalize_space(row.get("accident_type_raw")),
            "accident_type_standard": accident_standard,
            "injury_or_disease_type": normalize_space(row.get("injury_or_disease_type")),
            "hazard_factor_standard": hazard_standard,
            "severity_band": normalize_space(row.get("severity_band")) or "unknown",
            "worker_type": normalize_space(row.get("worker_type")) or "unknown",
            "employment_type": normalize_space(row.get("employment_type")) or "unknown",
            "company_size_band": normalize_space(row.get("company_size_band")) or "unknown",
            "region": normalize_space(row.get("region")) or "unknown",
            "weather_linkable": bool(row.get("weather_linkable")),
            "chemical_related": bool(row.get("chemical_related")),
            "narrative_text": normalize_space(row.get("narrative_text")),
            "countermeasure_text": normalize_space(row.get("countermeasure_text")),
            "_industry_match": industry_match,
            "_job_match": job_match,
            "_process_match": process_match,
            "_accident_match": accident_match,
            "_hazard_match": hazard_match,
            "_process_raw": normalize_space(row.get("process_raw")),
            "_hazard_raw": normalize_space(row.get("hazard_factor_raw")),
            "_industry_raw": normalize_space(row.get("industry_raw")),
        }
        records.append(record)

        taxonomy_rows.extend(
            [
                taxonomy_entry("industry", record["_industry_raw"], industry_major, record["industry_minor"], record["source_dataset_id"], industry_match),
                taxonomy_entry("job", record["job_title_raw"], job_standard, job_standard, record["source_dataset_id"], job_match),
                taxonomy_entry("process", record["_process_raw"], process_standard, process_standard, record["source_dataset_id"], process_match),
                taxonomy_entry("accident", record["accident_type_raw"], accident_standard, accident_standard, record["source_dataset_id"], accident_match),
                taxonomy_entry("hazard", record["_hazard_raw"], hazard_standard, hazard_standard, record["source_dataset_id"], hazard_match),
            ]
        )

    normalized = pd.DataFrame.from_records(records)
    taxonomy = pd.DataFrame.from_records(taxonomy_rows).drop_duplicates()
    return normalized, stats | {"taxonomy": taxonomy}


def taxonomy_entry(taxonomy_type: str, raw_value: str, standard_group: str, standard_detail: str, source_dataset_id: str, match_strategy: str) -> dict[str, str]:
    return {
        "taxonomy_type": taxonomy_type,
        "raw_value": normalize_space(raw_value) or "(empty)",
        "standard_group": standard_group,
        "standard_detail": standard_detail,
        "source_dataset_id": source_dataset_id,
        "match_strategy": match_strategy,
    }


def read_zip_csv_chunks(handle, chunksize: int = 100000) -> Iterable[pd.DataFrame]:
    sample = handle.read(4096)
    handle.seek(0)
    delimiter = "\t" if b"\t" in sample and sample.count(b"\t") > sample.count(b",") else ","
    yield from pd.read_csv(handle, encoding="cp949", encoding_errors="ignore", dtype=str, sep=delimiter, chunksize=chunksize)


def choose_existing_column(columns: Iterable[str], candidates: list[str]) -> str | None:
    normalized_map = {normalize_space(column): column for column in columns}
    for candidate in candidates:
        exact = normalized_map.get(normalize_space(candidate))
        if exact:
            return exact
    for column in columns:
        normalized = normalize_space(column)
        if any(normalize_space(candidate) in normalized for candidate in candidates):
            return column
    return None


def build_company_context_priors(paths: Paths) -> pd.DataFrame:
    zip_path = paths.raw / "15002150_employment_workers_comp_insurance_sites.zip"
    aggregate: defaultdict[tuple[str, str, str, str], dict[str, float]] = defaultdict(lambda: {"site_count": 0, "worker_sum": 0.0, "worker_max": 0.0})

    with zipfile.ZipFile(zip_path) as zf:
        csv_members = [name for name in zf.namelist() if name.lower().endswith(".csv")]
        for member in csv_members:
            year = extract_year(member)
            with zf.open(member) as handle:
                for chunk in read_zip_csv_chunks(handle):
                    industry_col = choose_existing_column(chunk.columns, ["고용보험 업종명", "업종명"])
                    address_col = choose_existing_column(chunk.columns, ["사업장 주소", "주소"])
                    workers_col = choose_existing_column(chunk.columns, ["고용보험 상시근로자수", "상시근로자수"])

                    if not (industry_col and address_col and workers_col):
                        continue

                    industry_series = chunk[industry_col].fillna("")
                    major_series = industry_series.map(lambda v: standardize_industry(v)[0])
                    address_series = chunk[address_col].fillna("").map(region_from_text)
                    workers_series = pd.to_numeric(chunk[workers_col], errors="coerce").fillna(0)
                    size_series = workers_series.map(company_size_from_numeric)
                    grouped = pd.DataFrame(
                        {
                            "source_year": year,
                            "industry_major": major_series,
                            "company_size_band": size_series,
                            "region": address_series,
                            "worker_count": workers_series,
                        }
                    ).groupby(["source_year", "industry_major", "company_size_band", "region"], dropna=False)

                    summary = grouped["worker_count"].agg(["count", "sum", "max"]).reset_index()
                    for row in summary.to_dict(orient="records"):
                        key = (
                            normalize_space(row["source_year"]),
                            normalize_space(row["industry_major"]),
                            normalize_space(row["company_size_band"]),
                            normalize_space(row["region"]),
                        )
                        aggregate[key]["site_count"] += float(row["count"])
                        aggregate[key]["worker_sum"] += float(row["sum"])
                        aggregate[key]["worker_max"] = max(aggregate[key]["worker_max"], float(row["max"]))

    rows = []
    for key, value in aggregate.items():
        year, industry_major, company_size_band, region = key
        avg_workers = value["worker_sum"] / value["site_count"] if value["site_count"] else 0
        rows.append(
            {
                "source_dataset_id": "15002150",
                "source_year": year,
                "industry_major": industry_major,
                "company_size_band": company_size_band,
                "region": region,
                "site_count": int(value["site_count"]),
                "avg_workers": round(avg_workers, 2),
                "max_workers": int(value["worker_max"]),
            }
        )
    return pd.DataFrame(rows).sort_values(["source_year", "industry_major", "company_size_band", "region"]).reset_index(drop=True)


def build_worker_segment_priors(foreign_events: pd.DataFrame, special_path: Path) -> pd.DataFrame:
    foreign_summary = (
        foreign_events.groupby(["source_dataset_id", "source_year", "worker_type", "industry_major", "accident_type_standard", "company_size_band", "region"], dropna=False)
        .size()
        .reset_index(name="metric_value")
    )
    foreign_summary["metric_name"] = "record_count"
    foreign_summary["job_group_standard"] = ""

    special = pd.read_csv(special_path, encoding="cp949", dtype=str)
    special = special.rename(columns={"구분1": "job_group_standard", "구분2": "metric_name"})
    year_cols = [col for col in special.columns if re.fullmatch(r"20\d{2}", str(col))]
    melted = special.melt(id_vars=["job_group_standard", "metric_name"], value_vars=year_cols, var_name="source_year", value_name="metric_value")
    melted["source_dataset_id"] = "15104692"
    melted["worker_type"] = "special_worker"
    melted["industry_major"] = ""
    melted["accident_type_standard"] = ""
    melted["company_size_band"] = ""
    melted["region"] = ""
    melted["metric_value"] = pd.to_numeric(melted["metric_value"], errors="coerce").fillna(0).astype(int)

    columns = [
        "source_dataset_id",
        "source_year",
        "worker_type",
        "job_group_standard",
        "industry_major",
        "accident_type_standard",
        "company_size_band",
        "region",
        "metric_name",
        "metric_value",
    ]
    foreign_summary = foreign_summary[columns]
    melted = melted[columns]
    return pd.concat([foreign_summary, melted], ignore_index=True)


def write_jsonl(path: Path, df: pd.DataFrame) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for record in df.to_dict(orient="records"):
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def write_schema_summary(path: Path) -> None:
    source_mapping_rows = [
        ("15140383", "SIF 아카이브", "산재업종/재해개요/재해유발요인/감소대책", "fatal_or_sif 고정, 제조업/건설업 시트 분리 처리"),
        ("3082968", "최초요양 승인 정보", "업종명/재해발생형태/세부상병명/재해일자/직종명/성별/연령대", "승인 통계 기반, narrative 비어 있음"),
        ("15121557", "외국인근로자 산재처리 상세현황", "재해발생형태/산재업종/사업장규모/지역본부", "foreign_worker 고정"),
        ("15104692", "특수형태근로종사자 산재처리현황", "직종별 연도 집계", "이벤트가 아닌 priors 테이블용"),
        ("15002150", "고용 산재보험 가입 현황", "업종명/사업장 주소/상시근로자수", "ZIP 내부 연도별 CSV 전량 집계"),
    ]

    lines = ["# Schema Summary", "", "## Common Event Schema", "", "| Column | Description |", "| --- | --- |"]
    descriptions = {
        "source_dataset_id": "원본 데이터셋 ID",
        "source_record_id": "원본 레코드를 재현할 수 있는 내부 키",
        "source_year": "사고 또는 통계 기준 연도",
        "industry_major": "표준화된 상위 업종",
        "industry_minor": "원본 업종명 또는 세부 업종",
        "job_title_raw": "원본 직종/직무명",
        "job_group_standard": "표준화된 직무 그룹",
        "process_group_standard": "표준화된 작업공정 그룹",
        "accident_type_raw": "원본 사고유형 관련 텍스트",
        "accident_type_standard": "표준화된 사고유형",
        "injury_or_disease_type": "원본 상병/재해종류 요약",
        "hazard_factor_standard": "표준화된 위험요인 그룹",
        "severity_band": "fatal_or_sif/serious/general/unknown",
        "worker_type": "employee/foreign_worker/special_worker/unknown",
        "employment_type": "고용형태 또는 노무제공 구분",
        "company_size_band": "통합 사업장 규모 구간",
        "region": "지역 텍스트",
        "weather_linkable": "기상 데이터 결합 가능 여부",
        "chemical_related": "화학물질 관련 여부",
        "narrative_text": "사례 본문 또는 요약",
        "countermeasure_text": "감소대책 또는 대응 문장",
    }
    for column in REQUIRED_EVENT_COLUMNS:
        lines.append(f"| `{column}` | {descriptions[column]} |")

    lines.extend(["", "## Source Mapping", "", "| Dataset | Source | Key fields used | Notes |", "| --- | --- | --- | --- |"])
    for dataset_id, source_name, fields, notes in source_mapping_rows:
        lines.append(f"| `{dataset_id}` | {source_name} | {fields} | {notes} |")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_data_quality_report(
    path: Path,
    master_events: pd.DataFrame,
    taxonomy: pd.DataFrame,
    company_priors: pd.DataFrame,
    worker_priors: pd.DataFrame,
    stats: dict[str, Counter],
) -> None:
    duplicate_count = int(master_events.duplicated(subset=["source_dataset_id", "source_record_id"]).sum())
    total_rows = len(master_events)
    accident_coverage = matched_ratio(master_events["_accident_match"])
    industry_coverage = matched_ratio(master_events["_industry_match"])
    process_coverage = matched_ratio(master_events["_process_match"])
    narrative_blank_ratio = blank_ratio(master_events["narrative_text"])
    countermeasure_blank_ratio = blank_ratio(master_events["countermeasure_text"])

    null_lines = []
    for column in REQUIRED_EVENT_COLUMNS:
        if column in {"weather_linkable", "chemical_related"}:
            continue
        null_lines.append(f"| `{column}` | {blank_ratio(master_events[column]):.2%} |")

    process_unmapped = (
        master_events.loc[master_events["_process_match"] == "fallback", ["source_dataset_id", "source_record_id", "_process_raw"]]
        .head(20)
        .rename(columns={"_process_raw": "sample_process_raw"})
    )

    lines = [
        "# Data Quality Report",
        "",
        "## Snapshot",
        "",
        f"- master incident rows: `{total_rows}`",
        f"- taxonomy rows: `{len(taxonomy)}`",
        f"- company context prior rows: `{len(company_priors)}`",
        f"- worker segment prior rows: `{len(worker_priors)}`",
        f"- duplicate source records: `{duplicate_count}`",
        "",
        "## Coverage",
        "",
        f"- accident taxonomy coverage: `{accident_coverage:.2%}`",
        f"- industry taxonomy coverage: `{industry_coverage:.2%}`",
        f"- process taxonomy explicit coverage: `{process_coverage:.2%}`",
        "",
        "## Blank Rates",
        "",
        "| Column | Blank ratio |",
        "| --- | --- |",
        *null_lines,
        "",
        f"- `narrative_text` blank ratio: `{narrative_blank_ratio:.2%}`",
        f"- `countermeasure_text` blank ratio: `{countermeasure_blank_ratio:.2%}`",
        "",
        "## Match Strategy Counts",
        "",
    ]

    for key in ["industry", "job", "process", "accident", "hazard"]:
        lines.append(f"### {key}")
        lines.append("")
        lines.append("| Strategy | Count |")
        lines.append("| --- | ---: |")
        for strategy, count in sorted(stats[key].items()):
            lines.append(f"| `{strategy}` | {count} |")
        lines.append("")

    lines.append("## Process Unmapped Samples")
    lines.append("")
    if process_unmapped.empty:
        lines.append("No fallback-only process samples.")
    else:
        lines.append("| source_dataset_id | source_record_id | sample_process_raw |")
        lines.append("| --- | --- | --- |")
        for row in process_unmapped.to_dict(orient="records"):
            lines.append(
                f"| `{row['source_dataset_id']}` | `{row['source_record_id']}` | {normalize_space(row['sample_process_raw']) or '(empty)'} |"
            )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def matched_ratio(series: pd.Series) -> float:
    total = len(series)
    if total == 0:
        return 0.0
    matched = (~series.isin(["fallback", "empty"])).sum()
    return matched / total


def blank_ratio(series: pd.Series) -> float:
    total = len(series)
    if total == 0:
        return 0.0
    blank = series.fillna("").astype(str).str.strip().eq("").sum()
    return blank / total


def export_intermediate(paths: Paths, name: str, df: pd.DataFrame) -> None:
    df.to_csv(paths.intermediate / f"{name}.csv", index=False, encoding="utf-8-sig")


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    paths = Paths(
        root=root,
        data_sources=root / "data_sources",
        raw=root / "data_sources" / "raw",
        processed=root / "data_sources" / "processed",
        intermediate=root / "data_sources" / "intermediate",
        reports=root / "data_sources" / "reports",
    )
    ensure_dirs(paths)

    sif_raw = load_sif_events(paths)
    approval_raw = load_approval_events(paths)
    foreign_raw = load_foreign_worker_events(paths)

    export_intermediate(paths, "15140383_sif_raw_events", sif_raw)
    export_intermediate(paths, "3082968_approval_raw_events", approval_raw)
    export_intermediate(paths, "15121557_foreign_raw_events", foreign_raw)

    combined_raw = pd.concat([sif_raw, approval_raw, foreign_raw], ignore_index=True)
    normalized_events, stats = normalize_event_frame(combined_raw)
    taxonomy = stats.pop("taxonomy")

    helper_cols = [col for col in normalized_events.columns if col.startswith("_")]
    master_events = normalized_events.drop(columns=helper_cols)
    master_events = master_events[REQUIRED_EVENT_COLUMNS]

    company_priors = build_company_context_priors(paths)
    worker_priors = build_worker_segment_priors(normalized_events[normalized_events["source_dataset_id"] == "15121557"], paths.raw / "15104692_special_worker_accident_status.csv")

    master_events.to_csv(paths.processed / "master_incident_events.csv", index=False, encoding="utf-8-sig")
    write_jsonl(paths.processed / "master_incident_events.jsonl", master_events)
    taxonomy.to_csv(paths.processed / "industry_job_process_taxonomy.csv", index=False, encoding="utf-8-sig")
    company_priors.to_csv(paths.processed / "company_context_priors.csv", index=False, encoding="utf-8-sig")
    worker_priors.to_csv(paths.processed / "worker_segment_priors.csv", index=False, encoding="utf-8-sig")

    write_schema_summary(paths.reports / "schema_summary.md")
    write_data_quality_report(paths.reports / "data_quality_report.md", normalized_events, taxonomy, company_priors, worker_priors, stats)

    print("Preprocessing complete.")
    print(f"master events: {len(master_events)}")
    print(f"taxonomy rows: {len(taxonomy)}")
    print(f"company priors: {len(company_priors)}")
    print(f"worker priors: {len(worker_priors)}")


if __name__ == "__main__":
    main()
