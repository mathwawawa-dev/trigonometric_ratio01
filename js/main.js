/**
 * main.js — 앱 통합 레이어 & sessionStorage 관리
 * STEP 3-3 | v1.0.29_260809_1744
 *
 * 의존성: 없음 (순수 JS)
 * 노출:   window.TriApp
 */

(function(global) {
  'use strict';

  /* ── 버전 & 앱 정보 ──────────────────────────────────── */
  const VERSION = 'v1.0.29_260809_1744_step3_3';

  const KEYS = Object.freeze({
    TRAINER: 'trainer',
    RESULT:  'lastResult',
  });

  /* ── sessionStorage: 트레이너 ────────────────────────── */

  /**
   * 트레이너 정보를 sessionStorage에 저장
   * @param {Object} trainer - { nickname, pokemon, pokemonId, difficulty }
   */
  function setTrainer(trainer) {
    try {
      sessionStorage.setItem(KEYS.TRAINER, JSON.stringify(trainer));
    } catch(e) {
      console.warn('[TriApp] setTrainer 실패:', e);
    }
  }

  /**
   * sessionStorage에서 트레이너 정보 로드
   * @returns {Object|null}
   */
  function getTrainer() {
    try {
      return JSON.parse(sessionStorage.getItem(KEYS.TRAINER) || 'null');
    } catch(e) {
      return null;
    }
  }

  /**
   * 트레이너 정보가 없으면 지정 URL로 리다이렉트
   * @param {string} [redirectUrl='index.html']
   * @returns {Object|null} 트레이너 정보 또는 null (리다이렉트됨)
   */
  function requireTrainer(redirectUrl = 'index.html') {
    const trainer = getTrainer();
    if (!trainer) {
      window.location.href = redirectUrl;
      return null;
    }
    return trainer;
  }

  /**
   * 트레이너 정보 삭제
   */
  function clearTrainer() {
    try { sessionStorage.removeItem(KEYS.TRAINER); } catch(e) {}
  }

  /* ── sessionStorage: 결과 ────────────────────────────── */

  /**
   * 게임 결과를 sessionStorage에 저장
   * @param {Object} result - { score, correctCount, totalCount, maxCombo, avgTime, accuracy }
   */
  function setResult(result) {
    try {
      sessionStorage.setItem(KEYS.RESULT, JSON.stringify(result));
    } catch(e) {
      console.warn('[TriApp] setResult 실패:', e);
    }
  }

  /**
   * sessionStorage에서 마지막 게임 결과 로드
   * @returns {Object|null}
   */
  function getResult() {
    try {
      return JSON.parse(sessionStorage.getItem(KEYS.RESULT) || 'null');
    } catch(e) {
      return null;
    }
  }

  /**
   * 결과 데이터 삭제
   */
  function clearResult() {
    try { sessionStorage.removeItem(KEYS.RESULT); } catch(e) {}
  }

  /* ── 난이도 표시 헬퍼 ────────────────────────────────── */
  const DIFF_KO = Object.freeze({
    easy:   '쉬움',
    normal: '보통',
    hard:   '어려움',
  });

  function diffLabel(diff) {
    return DIFF_KO[diff] || diff;
  }

  /* ── 결과 등급 계산 ──────────────────────────────────── */

  /**
   * 정확도 기반 별점(1~3) 반환
   * @param {number} accuracy - 0~100
   * @returns {1|2|3}
   */
  function calcStars(accuracy) {
    if (accuracy >= 90) return 3;
    if (accuracy >= 60) return 2;
    return 1;
  }

  /**
   * 정확도 기반 결과 제목 반환
   * @param {number} accuracy - 0~100
   * @returns {string}
   */
  function resultTitle(accuracy) {
    const titles = [
      '아직 멀었어요...',
      '조금 더 힘내요!',
      '잘하고 있어요!',
      '대단해요!',
      '완벽해요! 🎉',
    ];
    return titles[Math.min(Math.floor(accuracy / 25), 4)];
  }

  /* ── 페이지 진입 애니메이션 트리거 ──────────────────── */

  /**
   * DOMContentLoaded 시 .page-enter 클래스 활성화
   * (css/layout.css의 page-enter 애니메이션 적용)
   */
  function initPageEnter() {
    document.addEventListener('DOMContentLoaded', () => {
      document.querySelectorAll('.page-enter').forEach(el => {
        el.style.opacity = '1';
        el.style.transform = 'none';
      });
    });
  }

  /* ── 노출 ────────────────────────────────────────────── */
  global.TriApp = {
    VERSION,
    KEYS,
    DIFF_KO,
    setTrainer,
    getTrainer,
    requireTrainer,
    clearTrainer,
    setResult,
    getResult,
    clearResult,
    diffLabel,
    calcStars,
    resultTitle,
    initPageEnter,
  };

})(window);
