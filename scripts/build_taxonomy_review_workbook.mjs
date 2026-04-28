import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.resolve(__dirname, "..");
const reviewDir = path.join(rootDir, "data_sources", "review");

const outputPath = path.join(reviewDir, "taxonomy_review_workbook_minimal.xlsx");

const visibleColumnsBySheet = {
  "Accident Review": [
    "review_raw_value",
    "occurrence_count",
    "top_industries",
    "top_jobs",
    "sample_accident_type_raw",
    "sample_narrative_text",
    "proposed_standard_group",
    "review_status",
    "review_note",
  ],
  "Process Review": [
    "review_raw_value",
    "occurrence_count",
    "top_industries",
    "top_jobs",
    "sample_process_raw",
    "sample_narrative_text",
    "proposed_standard_group",
    "review_status",
    "review_note",
  ],
};

const accidentCategories = [
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
];

const processCategories = [
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
];

function colLetter(index) {
  let dividend = index + 1;
  let label = "";
  while (dividend > 0) {
    const modulo = (dividend - 1) % 26;
    label = String.fromCharCode(65 + modulo) + label;
    dividend = Math.floor((dividend - modulo) / 26);
  }
  return label;
}

function toMatrix(rows, headers) {
  const body = rows.map((row) =>
    headers.map((header) => {
      const value = row[header];
      if (value === null || value === undefined) return "";
      if (typeof value === "number" || typeof value === "boolean") return value;
      return String(value);
    }),
  );
  return [headers, ...body];
}

function pickVisibleHeaders(sheetName, rows) {
  const preferred = visibleColumnsBySheet[sheetName] ?? [];
  const sourceHeaders = rows.length > 0 ? Object.keys(rows[0]) : [];
  return preferred.filter((header) => sourceHeaders.includes(header));
}

function formatWorksheet(sheet, headers, rowCount) {
  const fullRange = `A1:${colLetter(headers.length - 1)}${rowCount + 1}`;
  const headerRange = `A1:${colLetter(headers.length - 1)}1`;
  const dataRange = rowCount > 0 ? `A2:${colLetter(headers.length - 1)}${rowCount + 1}` : null;

  sheet.getRange(fullRange).format.font = { name: "Calibri", size: 10, color: "tx1" };
  sheet.getRange(fullRange).format.verticalAlignment = "center";
  sheet.getRange(fullRange).format.wrapText = true;
  sheet.getRange(headerRange).format = {
    fill: { type: "solid", color: { type: "theme", value: "accent1", transform: { darken: 5 } } },
    font: { name: "Calibri", size: 10, color: "#FFFFFF", bold: true },
    horizontalAlignment: "center",
    verticalAlignment: "center",
    wrapText: true,
    borders: { preset: "outside", style: "thin", color: "#CBD5E1" },
  };
  if (dataRange) {
    sheet.getRange(dataRange).format.borders = { preset: "outside", style: "thin", color: "#E5E7EB" };
  }
  sheet.freezePanes.freezeRows(1);
  sheet.getRange(fullRange).format.autofitColumns();
  sheet.getRange(fullRange).format.autofitRows();
  const editableColumns = ["proposed_standard_group", "review_status", "review_note"]
    .map((name) => headers.indexOf(name))
    .filter((index) => index >= 0);
  for (const index of editableColumns) {
    const col = colLetter(index);
    sheet.getRange(`${col}1:${col}${rowCount + 1}`).format = {
      fill: { type: "solid", color: "#FFF2CC" },
      font: { name: "Calibri", size: 10, color: "tx1", bold: true },
      borders: { preset: "outside", style: "thin", color: "#D6B656" },
      wrapText: true,
      verticalAlignment: "center",
    };
    sheet.getRange(`${col}1:${col}${rowCount + 1}`).format.columnWidthPx = index === editableColumns[0] ? 180 : 130;
  }
}

function addOverviewSheet(workbook, accidentRows, processRows) {
  const sheet = workbook.worksheets.add("How To Review");
  const overviewRows = [
    ["Today Safety Taxonomy Review Workbook", "", "", ""],
    ["Purpose", "기타로 남은 사고유형/공정 표현을 빠르게 검수하기 위한 워크북", "", ""],
    ["Accident candidates", accidentRows.length, "", ""],
    ["Process candidates", processRows.length, "", ""],
    ["How to use", "1. occurrence_count가 큰 행부터 검수", "", ""],
    ["", "2. review_raw_value와 sample_* 컬럼을 같이 확인", "", ""],
    ["", "3. proposed_standard_group에 표준 분류를 입력", "", ""],
    ["", "4. review_status에 approved 또는 skip 입력", "", ""],
    ["", "5. 애매한 점은 review_note에 기록", "", ""],
    ["", "", "", ""],
    ["Accident taxonomy", accidentCategories.join(" | "), "", ""],
    ["Process taxonomy", processCategories.join(" | "), "", ""],
  ];

  const range = `A1:D${overviewRows.length}`;
  sheet.getRange(range).values = overviewRows;
  sheet.getRange("A1:D1").format = {
    fill: { type: "solid", color: { type: "theme", value: "accent1" } },
    font: { name: "Calibri", size: 14, color: "#FFFFFF", bold: true },
    horizontalAlignment: "left",
    verticalAlignment: "center",
  };
  sheet.getRange(range).format.font = { name: "Calibri", size: 10, color: "tx1" };
  sheet.getRange(range).format.wrapText = true;
  sheet.getRange("A2:B12").format.borders = { preset: "outside", style: "thin", color: "#CBD5E1" };
  sheet.getRange(range).format.autofitColumns();
  sheet.getRange(range).format.autofitRows();
}

async function main() {
  const accidentRows = JSON.parse(await fs.readFile(path.join(reviewDir, "accident_taxonomy_review.json"), "utf8"));
  const processRows = JSON.parse(await fs.readFile(path.join(reviewDir, "process_taxonomy_review.json"), "utf8"));

  const workbook = Workbook.create();
  addOverviewSheet(workbook, accidentRows, processRows);

  for (const [sheetName, rows] of [
    ["Accident Review", accidentRows],
    ["Process Review", processRows],
  ]) {
    const sheet = workbook.worksheets.add(sheetName);
    const headers = pickVisibleHeaders(sheetName, rows);
    const matrix = toMatrix(rows, headers);
    const range = `A1:${colLetter(headers.length - 1)}${matrix.length}`;
    sheet.getRange(range).values = matrix;
    formatWorksheet(sheet, headers, rows.length);
  }

  const output = await SpreadsheetFile.exportXlsx(workbook);
  await output.save(outputPath);
  console.log(outputPath);
}

await main();
