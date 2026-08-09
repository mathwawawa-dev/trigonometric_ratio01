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
   * file:// 프로토콜 여부 감지
   * @returns {boolean}
   */
  function isFileProtocol() {
    return location.protocol === 'file:';
  }

  /**
   * questions.json 로드 + 세션 빌드를 한 번에 처리
   * 에러 시 null 반환, err 콜백 호출
   *
   * @param {Object}   opts
   * @param {string}   opts.difficulty - 'easy' | 'normal' | 'hard'
   * @param {Function} opts.onSuccess  - (allQ, session) => void
   * @param {Function} opts.onError    - (err) => void
   * @param {Function} opts.onFileProtocol - () => void (file:// 감지 시)
   */
  async function initQuestions({ difficulty, onSuccess, onError, onFileProtocol }) {
    if (isFileProtocol()) {
      onFileProtocol?.();
      return;
    }
    try {
      const allQ    = await loadQuestions();
      const session = TriUtils.buildSession(allQ, difficulty);
      onSuccess(allQ, session);
    } catch(err) {
      console.error('[TriLoader] questions.json 로드 실패:', err);
      onError?.(err);
    }
  }

  global.TriLoader = {
    loadQuestions,
    initQuestions,
    isFileProtocol,
  };

})(window);
