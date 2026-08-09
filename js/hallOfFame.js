/**
 * hallOfFame.js — 명예의 전당 LocalStorage 저장소
 * STEP 3-3 | v1.0.29_260809_1744
 *
 * 의존성: 없음 (순수 JS)
 * 노출:   window.TriHallOfFame
 */

(function(global) {
  'use strict';

  const STORAGE_KEY = 'tri_records';
  const MAX_RECORDS = 50;

  /* ── 읽기 ────────────────────────────────────────────── */

  /**
   * 저장된 전체 기록 반환 (점수 내림차순 정렬)
   * @returns {Array}
   */
  function loadRecords() {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
    } catch(e) {
      return [];
    }
  }

  /**
   * 난이도 필터 적용 후 반환
   * @param {'all'|'easy'|'normal'|'hard'} diff
   * @returns {Array}
   */
  function getFiltered(diff) {
    const all = loadRecords();
    return diff === 'all' ? all : all.filter(r => r.difficulty === diff);
  }

  /**
   * 특정 점수가 현재 리더보드에서 몇 위인지 계산
   * @param {number} score
   * @param {'all'|'easy'|'normal'|'hard'} [diff='all']
   * @returns {number} 1-indexed 순위 (리스트가 비었으면 1)
   */
  function getRank(score, diff = 'all') {
    const records = getFiltered(diff);
    const higherCount = records.filter(r => r.score > score).length;
    return higherCount + 1;
  }

  /* ── 쓰기 ────────────────────────────────────────────── */

  /**
   * 기록 저장. 점수 내림차순 정렬 후 MAX_RECORDS 이하로 트림.
   * @param {Object} record - { nickname, pokemon, pokemonId, difficulty, score, accuracy, maxCombo, avgTime, correctCount, totalCount, date }
   * @returns {Array} 저장 후 전체 기록 배열
   */
  function saveRecord(record) {
    try {
      const records = loadRecords();
      records.push({
        ...record,
        date: record.date || new Date().toLocaleDateString('ko-KR'),
      });
      records.sort((a, b) => b.score - a.score);
      const trimmed = records.slice(0, MAX_RECORDS);
      localStorage.setItem(STORAGE_KEY, JSON.stringify(trimmed));
      return trimmed;
    } catch(e) {
      console.warn('[TriHallOfFame] saveRecord 실패:', e);
      return [];
    }
  }

  /* ── 삭제 ────────────────────────────────────────────── */

  /**
   * 전체 기록 삭제
   */
  function clearRecords() {
    try { localStorage.removeItem(STORAGE_KEY); }
    catch(e) {}
  }

  /* ── 노출 ────────────────────────────────────────────── */

  global.TriHallOfFame = {
    STORAGE_KEY,
    MAX_RECORDS,
    loadRecords,
    getFiltered,
    getRank,
    saveRecord,
    clearRecords,
  };

})(window);
