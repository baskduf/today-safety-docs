from __future__ import annotations

from collections import Counter
from pathlib import Path

import pandas as pd

from preprocess_today_safety import (
    Paths,
    ensure_dirs,
    load_approval_events,
    load_foreign_worker_events,
    load_sif_events,
    normalize_event_frame,
    normalize_space,
)


REVIEW_DIRNAME = "review"
TEXT_PREVIEW_LIMIT = 180


def clip_text(value: object, limit: int = TEXT_PREVIEW_LIMIT) -> str:
    text = normalize_space(value)
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "…"


def most_common_text(series: pd.Series, top_k: int = 3) -> str:
    values = [normalize_space(v) for v in series.fillna("").astype(str) if normalize_space(v)]
    if not values:
        return ""
    common = [text for text, _ in Counter(values).most_common(top_k)]
    return " | ".join(common)


def build_paths(root: Path) -> Paths:
    data_sources = root / "data_sources"
    return Paths(
        root=root,
        data_sources=data_sources,
        raw=data_sources / "raw",
        processed=data_sources / "processed",
        intermediate=data_sources / "intermediate",
        reports=data_sources / "reports",
    )


def load_normalized_events(root: Path) -> pd.DataFrame:
    paths = build_paths(root)
    ensure_dirs(paths)
    combined = pd.concat(
        [
            load_sif_events(paths),
            load_approval_events(paths),
            load_foreign_worker_events(paths),
        ],
        ignore_index=True,
    )
    normalized, _ = normalize_event_frame(combined)
    return normalized


def aggregate_review_candidates(
    df: pd.DataFrame,
    *,
    category_col: str,
    match_col: str,
    raw_value_col: str,
    output_type: str,
) -> pd.DataFrame:
    unresolved = df[df[category_col].astype(str).eq("기타")].copy()
    unresolved["review_raw_value"] = unresolved[raw_value_col].fillna("").astype(str).map(normalize_space)
    unresolved = unresolved[unresolved["review_raw_value"] != ""].copy()

    rows: list[dict[str, object]] = []
    grouped = unresolved.groupby("review_raw_value", dropna=False)
    for raw_value, group in grouped:
        sample = group.iloc[0]
        rows.append(
            {
                "taxonomy_type": output_type,
                "review_raw_value": raw_value,
                "occurrence_count": int(len(group)),
                "current_standard_group": sample[category_col],
                "match_strategy": most_common_text(group[match_col], top_k=2),
                "top_industries": most_common_text(group["industry_major"]),
                "top_jobs": most_common_text(group["job_title_raw"]),
                "source_datasets": most_common_text(group["source_dataset_id"]),
                "sample_record_id": sample["source_record_id"],
                "sample_year": sample["source_year"],
                "sample_industry_major": sample["industry_major"],
                "sample_industry_minor": sample["industry_minor"],
                "sample_job_title": sample["job_title_raw"],
                "sample_accident_type_raw": sample["accident_type_raw"],
                "sample_process_raw": sample["_process_raw"],
                "sample_hazard_raw": sample["_hazard_raw"],
                "sample_narrative_text": clip_text(sample["narrative_text"]),
                "sample_countermeasure_text": clip_text(sample["countermeasure_text"]),
                "proposed_standard_group": "",
                "review_status": "",
                "review_note": "",
            }
        )

    result = pd.DataFrame(rows)
    if result.empty:
        return result
    return result.sort_values(["occurrence_count", "review_raw_value"], ascending=[False, True]).reset_index(drop=True)


def export_review_files(root: Path) -> list[Path]:
    paths = build_paths(root)
    review_dir = paths.data_sources / REVIEW_DIRNAME
    review_dir.mkdir(parents=True, exist_ok=True)

    normalized = load_normalized_events(root)
    normalized["accident_review_raw"] = (
        normalized["accident_type_raw"].fillna("").astype(str).map(normalize_space)
    )
    normalized.loc[normalized["accident_review_raw"] == "", "accident_review_raw"] = (
        normalized.loc[normalized["accident_review_raw"] == "", "injury_or_disease_type"].fillna("").astype(str).map(normalize_space)
    )

    accident_review = aggregate_review_candidates(
        normalized,
        category_col="accident_type_standard",
        match_col="_accident_match",
        raw_value_col="accident_review_raw",
        output_type="accident",
    )
    process_review = aggregate_review_candidates(
        normalized,
        category_col="process_group_standard",
        match_col="_process_match",
        raw_value_col="_process_raw",
        output_type="process",
    )

    accident_path = review_dir / "accident_taxonomy_review.csv"
    process_path = review_dir / "process_taxonomy_review.csv"
    accident_json_path = review_dir / "accident_taxonomy_review.json"
    process_json_path = review_dir / "process_taxonomy_review.json"
    guide_path = review_dir / "README.md"

    accident_review.to_csv(accident_path, index=False, encoding="utf-8-sig")
    process_review.to_csv(process_path, index=False, encoding="utf-8-sig")
    accident_json_path.write_text(accident_review.to_json(orient="records", force_ascii=False, indent=2), encoding="utf-8")
    process_json_path.write_text(process_review.to_json(orient="records", force_ascii=False, indent=2), encoding="utf-8")

    guide_text = """# Taxonomy Review Guide

이 폴더는 사람이 `기타` 분류를 빠르게 검수할 수 있도록 만든 검수 전용 파일입니다.

## 파일

- `accident_taxonomy_review.csv`
  - 사고유형이 아직 `기타`로 남은 원문 표현 목록
- `process_taxonomy_review.csv`
  - 작업공정이 아직 `기타`로 남은 원문 표현 목록

## 검수 방법

1. `occurrence_count`가 큰 행부터 본다.
2. `review_raw_value`와 `sample_*` 컬럼을 같이 본다.
3. 분류가 가능하면 `proposed_standard_group`에 표준 taxonomy를 적는다.
4. 검수가 끝난 행은 `review_status`에 `approved` 또는 `skip`을 적는다.
5. 애매한 이유는 `review_note`에 남긴다.

## 추천 우선순위

- 사고유형: 상위 100개 표현부터 검수
- 공정: 상위 150개 표현부터 검수

## 표준값 예시

- 사고유형: `추락`, `끼임`, `충돌`, `낙하`, `붕괴`, `전도`, `화재폭발`, `화학물질노출`, `감전`, `질식`, `무리한동작`, `교통/이동`, `기타`
- 공정: `운반/인양`, `설치/해체`, `정비/보전`, `절단/가공`, `청소/정리`, `점검/검사`, `화학물질취급`, `상하차/물류`, `굴착/토공`, `배관/용접`, `전기작업`, `도장/마감`, `보행/이동`, `기타`
"""
    guide_path.write_text(guide_text, encoding="utf-8")

    return [accident_path, process_path, accident_json_path, process_json_path, guide_path]


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    outputs = export_review_files(root)
    for output in outputs:
        print(output)


if __name__ == "__main__":
    main()
