/**
 * utils.js — 삼각비 마스터 공통 유틸리티
 * STEP 3-1 | v1.0.27_260809_1730
 *
 * 의존성: 없음 (순수 JS)
 * 노출: window.TriUtils 네임스페이스
 */

(function(global) {
  'use strict';

  /* ── 게임 상수 ─────────────────────────────────────────── */
  const CONFIG = Object.freeze({
    SESSION_LEN:   10,
    TIMER_SEC:     30,
    TRI_COOLDOWN:  5,
    TRIG_COOLDOWN: 2,
    IMG_DIRS:  { 1: 'Tri_img_01', 2: 'Tri_img_02', 3: 'Tri_img_03' },
    DIFF_WEIGHTS: {
      easy:   [1.0, 0.0, 0.0],
      normal: [0.5, 0.4, 0.1],
      hard:   [0.3, 0.4, 0.3],
    },
    // 세션 전반 type1 강화 가중치
    WARMUP_WEIGHTS: [0.8, 0.15, 0.05],
  });

  /* ── 배열 유틸 ─────────────────────────────────────────── */

  /**
   * Fisher-Yates 셔플 (원본 배열 변경 없이 복사본 반환)
   * @param {Array} arr
   * @returns {Array}
   */
  function shuffleArray(arr) {
    const a = arr.slice();
    for (let i = a.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
  }

  /**
   * 가중 랜덤 선택
   * @param {Array} candidates - 후보 question 객체 배열
   * @param {number[]} typeWeights - [type1비율, type2비율, type3비율]
   * @returns {Object} 선택된 question
   */
  function weightedPick(candidates, typeWeights) {
    const weighted = candidates.map(q => ({
      q,
      w: typeWeights[q.image_type - 1] ?? 0.1,
    }));
    const totalW = weighted.reduce((s, x) => s + x.w, 0);
    if (totalW === 0) return candidates[Math.floor(Math.random() * candidates.length)];
    let r = Math.random() * totalW;
    for (const { q, w } of weighted) {
      r -= w;
      if (r <= 0) return q;
    }
    return weighted[weighted.length - 1].q;
  }

  /**
   * cooldown / trig 제약 기반 후보 필터링
   * @param {Array}  pool       - 전체 문항 풀
   * @param {Set}    usedIds    - 이미 사용한 question id 집합
   * @param {Array}  recentTri  - 최근 출제 triangle_id 큐
   * @param {Array}  recentTrg  - 최근 출제 question_type 큐
   * @param {number} cooldown   - triangle cooldown 크기
   * @returns {Array} 출제 가능한 문항 배열
   */
  function filterQ(pool, usedIds, recentTri, recentTrg, cooldown) {
    const { TRIG_COOLDOWN } = CONFIG;
    return pool.filter(q =>
      !usedIds.has(q.id) &&
      !recentTri.slice(-cooldown).includes(q.triangle_id) &&
      !recentTrg.slice(-TRIG_COOLDOWN).includes(q.question_type)
    );
  }

  /**
   * cooldown 기반 세션 빌드
   * @param {Array}  allQ   - 전체 문항 배열 (questions.json)
   * @param {string} diff   - 'easy' | 'normal' | 'hard'
   * @param {number} [len]  - 세션 길이 (기본: CONFIG.SESSION_LEN)
   * @returns {Array} 출제 순서가 결정된 question 배열
   */
  function buildSession(allQ, diff, len) {
    const { SESSION_LEN, TRI_COOLDOWN, TRIG_COOLDOWN, DIFF_WEIGHTS, WARMUP_WEIGHTS } = CONFIG;
    const sessionLen = len ?? SESSION_LEN;
    const weights    = DIFF_WEIGHTS[diff] || DIFF_WEIGHTS.normal;

    const session   = [];
    const usedIds   = new Set();
    const recentTri = [];
    const recentTrg = [];
    let cooldown    = TRI_COOLDOWN;

    for (let i = 0; i < sessionLen; i++) {
      // 전반: type1 워밍업, 후반: 난이도 가중치
      const tw = i < sessionLen / 2 ? WARMUP_WEIGHTS : weights;

      let eligible = filterQ(allQ, usedIds, recentTri, recentTrg, cooldown);

      // 폴백: cooldown 1단계씩 완화
      while (eligible.length === 0 && cooldown > 1) {
        cooldown--;
        eligible = filterQ(allQ, usedIds, recentTri, recentTrg, cooldown);
      }
      if (eligible.length === 0) break;

      const q = weightedPick(eligible, tw);
      session.push(q);

      usedIds.add(q.id);
      recentTri.push(q.triangle_id);
      if (recentTri.length > TRI_COOLDOWN) recentTri.shift();
      recentTrg.push(q.question_type);
      if (recentTrg.length > TRIG_COOLDOWN) recentTrg.shift();
    }

    return session;
  }

  /* ── HTML 이스케이프 ────────────────────────────────────── */
  function escHtml(str) {
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  /* ── 점수 계산 ──────────────────────────────────────────── */
  /**
   * 정답 시 점수 계산
   * @param {number} timerLeft  - 남은 타이머 초
   * @param {number} timerTotal - 전체 타이머 초
   * @param {number} combo      - 현재 콤보 수
   * @returns {number} 획득 점수
   */
  function calcScore(timerLeft, timerTotal, combo) {
    const base       = 100;
    const speedBonus = Math.round((timerLeft / timerTotal) * 50);
    const comboBonus = Math.min(combo - 1, 5) * 10;
    return base + speedBonus + comboBonus;
  }

  /* ── 포켓몬 이미지 URL ──────────────────────────────────── */
  function pokemonArtUrl(id) {
    return `https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/${id}.png`;
  }
  function pokemonSpriteUrl(id) {
    return `https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/${id}.png`;
  }

  /* ── 네임스페이스 노출 ──────────────────────────────────── */
  global.TriUtils = {
    CONFIG,
    shuffleArray,
    weightedPick,
    filterQ,
    buildSession,
    escHtml,
    calcScore,
    pokemonArtUrl,
    pokemonSpriteUrl,
  };

})(window);
