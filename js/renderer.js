/**
 * renderer.js — KaTeX 수식 렌더링 헬퍼
 * STEP 3-1 | v1.0.27_260809_1730
 *
 * 의존성: KaTeX (CDN으로 로드된 window.katex)
 * 노출: window.TriRenderer 네임스페이스
 */

(function(global) {
  'use strict';

  /* ── KaTeX 옵션 기본값 ──────────────────────────────────── */
  const KATEX_OPTS = {
    throwOnError: false,
    displayMode:  false,
    strict:       false,
    trust:        false,
  };

  /**
   * $...$ 또는 \frac{}{} 등 LaTeX 문자열에서 $ 래퍼를 제거하고 raw 수식 반환
   * @param {string} tex
   * @returns {string}
   */
  function stripDollar(tex) {
    return String(tex).replace(/^\$+|\$+$/g, '').trim();
  }

  /**
   * DOM 엘리먼트에 KaTeX 수식을 직접 렌더링
   * @param {HTMLElement} el  - 렌더링 대상 요소
   * @param {string}      tex - LaTeX 수식 문자열 ($ 포함 가능)
   */
  function renderTex(el, tex) {
    if (!global.katex) { el.textContent = tex; return; }
    try {
      global.katex.render(stripDollar(tex), el, KATEX_OPTS);
    } catch(e) {
      el.textContent = tex;
    }
  }

  /**
   * KaTeX 수식을 HTML 문자열로 반환 (innerHTML 삽입용)
   * @param {string} tex - LaTeX 수식 문자열 ($ 포함 가능)
   * @returns {string}   - 렌더링된 HTML 문자열
   */
  function renderTexStr(tex) {
    if (!global.katex) return escapeHtml(tex);
    const stripped = stripDollar(tex);
    const span = document.createElement('span');
    try {
      global.katex.render(stripped, span, KATEX_OPTS);
    } catch(e) {
      span.textContent = tex;
    }
    return span.innerHTML;
  }

  /**
   * 선지가 "단순" 꼴인지 판별 (정수 | \sqrt{정수} | 정수\sqrt{정수} 등)
   * → true이면 choice-btn--simple 클래스를 부여해 KaTeX 크기를 줄임
   * @param {string} tex
   * @returns {boolean}
   */
  function isSimpleChoice(tex) {
    const s = stripDollar(tex).replace(/\s/g, '');
    // 순수 정수 (음수 포함)
    if (/^-?\d+$/.test(s)) return true;
    // \sqrt{n} 꼴
    if (/^-?\\sqrt\{\d+\}$/.test(s)) return true;
    // n\sqrt{m} 꼴
    if (/^-?\d+\\sqrt\{\d+\}$/.test(s)) return true;
    return false;
  }

  /**
   * 질문 문자열 내 $...$ 패턴을 모두 KaTeX HTML로 치환
   * (혼합 텍스트 처리: "다음 삼각형에서 $\\sin A$의 값은?" 형태)
   * @param {string} text
   * @returns {string} HTML 문자열
   */
  function renderMixedTex(text) {
    if (!global.katex) return escapeHtml(text);
    // $...$ 패턴을 찾아 KaTeX로 치환, 나머지는 escapeHtml
    return String(text).replace(/\$([^$]+)\$/g, (_, raw) => {
      const span = document.createElement('span');
      try { global.katex.render(raw.trim(), span, KATEX_OPTS); }
      catch(e) { span.textContent = '$' + raw + '$'; }
      return span.outerHTML;
    }).replace(/(?<!\$)[^<>]*(?![^<]*>)/g, seg =>
      // $ 없는 일반 텍스트는 그대로 (이미 치환된 HTML 밖의 텍스트만)
      seg
    );
  }

  /**
   * 선지 4개 배열을 KaTeX HTML 배열로 변환
   * @param {string[]} choices
   * @returns {string[]}
   */
  function renderChoices(choices) {
    return choices.map(c => renderTexStr(c));
  }

  /**
   * 분수 분모가 1인 경우 정수로 단순화된 표현 반환
   * (예: \frac{3}{1} → "3")
   * @param {string} tex
   * @returns {string}
   */
  function simplifyFrac(tex) {
    return String(tex).replace(/\\frac\{([^}]+)\}\{1\}/g, '$1');
  }

  /* ── 내부 헬퍼 ──────────────────────────────────────────── */
  function escapeHtml(str) {
    return String(str)
      .replace(/&/g,'&amp;').replace(/</g,'&lt;')
      .replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }

  /* ── 네임스페이스 노출 ──────────────────────────────────── */
  global.TriRenderer = {
    renderTex,
    renderTexStr,
    renderMixedTex,
    renderChoices,
    simplifyFrac,
    isSimpleChoice,
  };

})(window);
