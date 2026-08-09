/**
 * questionLoader.js — questions.json 로더
 * STEP 3-2 | v1.0.28_260809_1736
 *
 * 의존성: js/utils.js (TriUtils)
 * 노출:   window.TriLoader
 */

(function(global) {
  'use strict';

  const DATA_URL = 'data/questions.json';

  /**
   * questions.json을 fetch하여 파싱된 배열로 반환
   * @param {string} [url] - 커스텀 경로 (기본: 'data/questions.json')
   * @returns {Promise<Array>}
   * @throws {Error} HTTP 오류 또는 JSON 파싱 실패 시
   */
  async function loadQuestions(url = DATA_URL) {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`HTTP ${res.status} — ${url}`);
    return res.json();
  }

  /**
   * 문항 데이터 로드 + 세션 빌드를 한 번에 처리.
   *
   * 우선순위:
   *   1) window.QUESTIONS_DATA (js/questionsData.js 내장 데이터) → fetch 불필요
   *   2) fetch(url) → HTTP 서버 필요
   *
   * @param {Object}   opts
   * @param {string}   opts.difficulty      - 'easy' | 'normal' | 'hard'
   * @param {Function} opts.onSuccess       - (allQ, session) => void
   * @param {Function} [opts.onError]       - (err) => void
   * @param {Function} [opts.onFileProtocol] - 더 이상 사용되지 않음 (하위호환 유지)
   */
  async function initQuestions({ difficulty, onSuccess, onError, onFileProtocol }) {
    try {
      let allQ;

      if (global.QUESTIONS_DATA && Array.isArray(global.QUESTIONS_DATA)) {
        // ① 내장 데이터 사용 (file:// 포함 어디서나 동작)
        allQ = global.QUESTIONS_DATA;
      } else {
        // ② fetch 폴백 (HTTP 서버 환경)
        allQ = await loadQuestions();
      }

      const session = TriUtils.buildSession(allQ, difficulty);
      onSuccess(allQ, session);
    } catch(err) {
      console.error('[TriLoader] 데이터 로드 실패:', err);
      onError?.(err);
    }
  }

  global.TriLoader = {
    loadQuestions,
    initQuestions,
    isFileProtocol,
  };

})(window);
