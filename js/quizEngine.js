/**
 * quizEngine.js — 퀴즈 진행 엔진 (상태 소유자)
 * STEP 3-2 | v1.0.28_260809_1736
 *
 * 의존성: js/utils.js (TriUtils), js/renderer.js (TriRenderer)
 * 노출:   window.TriQuizEngine
 *
 * 사용법:
 *   TriQuizEngine.init({ trainer, allQuestions });
 *   TriQuizEngine.onChoiceClick(idx);
 *   TriQuizEngine.onTimeout();
 *   TriQuizEngine.resetGame(allQ, diff);
 *   const state = TriQuizEngine.getState();
 */

(function(global) {
  'use strict';

  /* ── 내부 상태 (외부 직접 접근 금지) ─────────────────── */
  let _gs = null;
  let _cfg = null;       // TriUtils.CONFIG 캐시
  let _difficulty = '';
  let _allQuestions = [];
  let _elapsedInterval = null;
  let _toggleState = { avgtime: false, elapsed: false, scorepop: true };

  /* ── 초기화 ──────────────────────────────────────────── */

  /**
   * 퀴즈 엔진 초기화. 세션을 빌드하고 첫 문항을 표시
   * @param {Object} opts
   * @param {Object} opts.trainer      - { nickname, pokemon, pokemonId, difficulty }
   * @param {Array}  opts.allQuestions - 전체 문항 배열
   * @param {Array}  opts.session      - 이미 빌드된 세션 (선택)
   */
  function init({ trainer, allQuestions, session }) {
    _cfg         = TriUtils.CONFIG;
    _difficulty  = trainer.difficulty;
    _allQuestions = allQuestions;

    _gs = {
      allQuestions,
      session:       session ?? TriUtils.buildSession(allQuestions, _difficulty),
      qIndex:        0,
      score:         0,
      combo:         0,
      maxCombo:      0,
      correctCount:  0,
      timings:       [],
      answered:      false,
      timerInterval: null,
      timerMax:      _cfg.TIMER_SEC[_difficulty] || 30,
      timerLeft:     _cfg.TIMER_SEC[_difficulty] || 30,
      qStartTime:    0,
      elapsedSec:    0,
    };

    // 토글 상태 복원 + 이벤트 연결
    _loadToggles();

    // HUD 초기화 (포켓몬 칩 제거됨 - 결과 화면 포켓몬만 세팅)
    _setEl('hud-qtotal', `/${_cfg.SESSION_LEN}`);
    _setImg('result-pokemon-img', TriUtils.pokemonArtUrl(trainer.pokemonId));
    _setEl('hud-accuracy-val', '0%');
    _setEl('hud-score', '0');
    _setEl('hud-combo', '0');

    // 경과시간 카운트업 타이머
    clearInterval(_elapsedInterval);
    _gs.elapsedSec = 0;
    _elapsedInterval = setInterval(() => {
      _gs.elapsedSec++;
      if (_toggleState.elapsed) _setEl('hud-elapsed-val', _gs.elapsedSec);
    }, 1000);

    // 진행 도트 생성
    _buildProgressDots();

    // 첫 문항 표시
    showQuestion(_gs.session[0]);
  }


  /* ── 문제 표시 ────────────────────────────────────────── */

  function showQuestion(q) {
    try {
      _gs.answered = false;

      // 메타 뱃지
      _setEl('type-badge', '유형' + ('①②③'[q.image_type - 1] || '?'));
      document.getElementById('type-badge').className = 'type-badge type-badge--' + q.image_type;
      _setEl('trig-badge', q.question_type);
      document.getElementById('trig-badge').className = 'trig-badge trig-badge--' + q.question_type;

      // 삼각형 이미지
      const imgEl = document.getElementById('tri-img');
      imgEl.classList.add('loading');
      imgEl.classList.remove('tri-img--landscape');
      imgEl.onload  = () => {
        imgEl.classList.remove('loading');
        if (imgEl.naturalWidth > imgEl.naturalHeight) {
          imgEl.classList.add('tri-img--landscape');
        }
      };
      imgEl.onerror = () => imgEl.classList.remove('loading');
      imgEl.src = _cfg.IMG_DIRS[q.image_type] + '/' + q.filename;

      // 질문 (한글+LaTeX 혼합 → renderMixedTex)
      const cleanedQuestion = q.question.replace('다음 삼각형에서 ', '').replace('의 값은?', '').trim();
      document.getElementById('question-text').innerHTML =
        TriRenderer.renderMixedTex(cleanedQuestion);

      // 선지 (순수 수식 → renderTexStr)
      document.querySelectorAll('.choice-btn').forEach((btn, idx) => {
        btn.disabled = false;
        btn.className = 'choice-btn';
        const choiceTex = q.choices[idx];
        if (TriRenderer.isSimpleChoice(choiceTex)) btn.classList.add('choice-btn--simple');
        btn.innerHTML = '<span>' + TriRenderer.renderTexStr(choiceTex) + '</span>';
        btn.setAttribute('aria-label', '선지 ' + ('①②③④'[idx] || (idx + 1)));
      });

      // 해설 배너 / 다음 버튼 숨김
      document.getElementById('answer-banner').style.display = 'none';
      document.getElementById('next-btn').style.display = 'none';

      // 진행 도트 갱신
      _updateDots();

      // HUD 문항 번호
      _setEl('hud-qnum', _gs.qIndex + 1);

      // 타이머 시작
      _startTimer();
      _gs.qStartTime = Date.now();

    } catch(e) {
      console.error('[TriQuizEngine] showQuestion 실패:', e, q);
      // fallback: 텍스트만 표시하고 타이머는 반드시 시작
      const qt = document.getElementById('question-text');
      if (qt) qt.textContent = (q && q.question) ? q.question.replace('다음 삼각형에서 ', '').replace('의 값은?', '').trim() : '문제 로드 실패';
      document.querySelectorAll('.choice-btn').forEach((btn, idx) => {
        btn.disabled = false;
        btn.textContent = (q && q.choices && q.choices[idx]) || '';
      });
      if (document.getElementById('answer-banner'))
        document.getElementById('answer-banner').style.display = 'none';
      if (document.getElementById('next-btn'))
        document.getElementById('next-btn').style.display = 'none';
      _startTimer();
      _gs.qStartTime = Date.now();
    }
  }

  /* ── 타이머 ───────────────────────────────────────────── */

  function _startTimer() {
    clearInterval(_gs.timerInterval);
    _gs.timerLeft = _gs.timerMax;
    _updateTimerUI();
    _gs.timerInterval = setInterval(() => {
      _gs.timerLeft--;
      _updateTimerUI();
      if (_gs.timerLeft <= 0) {
        clearInterval(_gs.timerInterval);
        if (!_gs.answered) onTimeout();
      }
    }, 1000);
  }

  function _updateTimerUI() {
    const pct     = (_gs.timerLeft / _gs.timerMax) * 100;
    const bar     = document.getElementById('timer-bar');
    const display = document.getElementById('timer-display');
    bar.style.width  = pct + '%';
    display.textContent = _gs.timerLeft;

    bar.className     = 'timer-bar-fill';
    display.className = 'timer-countdown';

    if (_gs.timerLeft <= 10) {
      bar.classList.add('timer-bar-fill--critical');
      display.classList.add('timer-countdown--critical');
    } else if (_gs.timerLeft <= 15) {
      bar.classList.add('timer-bar-fill--warning');
      display.classList.add('timer-countdown--warning');
    }
  }

  /* ── 답 선택 ─────────────────────────────────────────── */

  function onChoiceClick(idx) {
    if (_gs.answered) return;
    _gs.answered = true;
    clearInterval(_gs.timerInterval);

    const q       = _gs.session[_gs.qIndex];
    const elapsed = (Date.now() - _gs.qStartTime) / 1000;
    _gs.timings.push(elapsed);

    const isCorrect  = idx === q.answer_index;
    const choiceBtns = document.querySelectorAll('.choice-btn');
    choiceBtns.forEach(b => b.disabled = true);
    choiceBtns[q.answer_index].classList.add('choice-btn--correct');
    if (!isCorrect) choiceBtns[idx].classList.add('choice-btn--wrong');

    if (isCorrect) {
      _gs.combo++;
      _gs.maxCombo     = Math.max(_gs.maxCombo, _gs.combo);
      _gs.correctCount++;
      const speedBonus = Math.round((_gs.timerLeft / _gs.timerMax) * 50);
      const comboBonus = Math.min(_gs.combo - 1, 5) * 10;
      const gained     = 100 + speedBonus + comboBonus;
      _gs.score += gained;
      if (_toggleState.scorepop) _showScorePopup(gained);
      _showFeedback(true);
      _showAnswerBanner(true, q);
    } else {
      _gs.combo = 0;
      _showFeedback(false);
      _showAnswerBanner(false, q);
    }

    _updateHUD();
    _showNextBtn();
  }

  /* ── 타임아웃 ────────────────────────────────────────── */

  function onTimeout() {
    if (_gs.answered) return;
    _gs.answered = true;
    _gs.combo    = 0;
    _gs.timings.push(_gs.timerMax);

    const q = _gs.session[_gs.qIndex];
    document.querySelectorAll('.choice-btn').forEach(b => b.disabled = true);
    document.querySelectorAll('.choice-btn')[q.answer_index]
      .classList.add('choice-btn--correct');

    _showFeedback(false, true);
    _showAnswerBanner(false, q, true);
    _updateHUD();
    _showNextBtn();
  }

  /* ── 다음 문항 진행 ───────────────────────────────────── */

  function nextQuestion() {
    _gs.qIndex++;
    if (_gs.qIndex >= _gs.session.length) {
      showResult();
    } else {
      showQuestion(_gs.session[_gs.qIndex]);
    }
  }

  /* ── 결과 표시 ────────────────────────────────────────── */

  function showResult() {
    // 도트 전부 완료
    for (let i = 0; i < _cfg.SESSION_LEN; i++) {
      const d = document.getElementById(`dot-${i}`);
      if (d) d.className = 'progress-dot progress-dot--done';
    }

    const totalTime = _gs.timings.reduce((a, b) => a + b, 0);
    const avgTime   = _gs.timings.length
      ? (totalTime / _gs.timings.length).toFixed(1)
      : '-';
    const accuracy  = Math.round((_gs.correctCount / _gs.session.length) * 100);

    // 결과 오버레이 채우기
    _setEl('r-score',   _gs.score.toLocaleString());
    _setEl('r-correct', `${_gs.correctCount}/${_gs.session.length} (${accuracy}%)`);
    _setEl('r-combo',   _gs.maxCombo);
    _setEl('r-time',    `${avgTime}s`);

    const titles   = ['아직 멀었어요...', '조금 더 힘내요!', '잘하고 있어요!', '대단해요!', '완벽해요! 🎉'];
    const titleIdx = Math.min(Math.floor(accuracy / 25), 4);
    _setEl('result-title', titles[titleIdx]);

    const stars   = accuracy >= 90 ? 3 : accuracy >= 60 ? 2 : 1;
    const starsEl = document.getElementById('r-stars');
    if (starsEl) starsEl.innerHTML = [1,2,3]
      .map(i => `<span class="star${i <= stars ? ' star--filled' : ''}">★</span>`)
      .join('');

    document.getElementById('result-overlay').classList.add('show');

    // sessionStorage → result.html (TriApp 위임)
    if (global.TriApp) {
      TriApp.setResult({
        score:        _gs.score,
        correctCount: _gs.correctCount,
        totalCount:   _gs.session.length,
        maxCombo:     _gs.maxCombo,
        avgTime:      parseFloat(avgTime),
        accuracy,
      });
    } else {
      // TriApp 미로드 환경 폴백
      sessionStorage.setItem('lastResult', JSON.stringify({
        score: _gs.score, correctCount: _gs.correctCount,
        totalCount: _gs.session.length, maxCombo: _gs.maxCombo,
        avgTime: parseFloat(avgTime), accuracy,
      }));
    }
  }

  /* ── 게임 리셋 ────────────────────────────────────────── */

  function resetGame(allQ, diff) {
    if (!_gs) return;
    clearInterval(_gs.timerInterval);
    clearInterval(_elapsedInterval);
    _gs.qIndex       = 0;
    _gs.score        = 0;
    _gs.combo        = 0;
    _gs.maxCombo     = 0;
    _gs.correctCount = 0;
    _gs.timings      = [];
    _gs.answered     = false;
    _gs.elapsedSec   = 0;
    _gs.session      = TriUtils.buildSession(allQ ?? _allQuestions, diff ?? _difficulty);

    _setEl('hud-score',        '0');
    _setEl('hud-combo',        '0');
    _setEl('hud-accuracy-val', '0%');
    _setEl('hud-elapsed-val',  '0');
    _setEl('hud-avgtime-val',  '-');

    _elapsedInterval = setInterval(() => {
      _gs.elapsedSec++;
      if (_toggleState.elapsed) _setEl('hud-elapsed-val', _gs.elapsedSec);
    }, 1000);

    _updateDots();
    showQuestion(_gs.session[0]);
  }

  /* ── 내부: 피드백 스탬프 ─────────────────────────────── */

  function _showFeedback(correct, timeout = false) {
    const ov    = document.getElementById('feedback-overlay');
    const stamp = document.getElementById('feedback-stamp');
    stamp.className = 'feedback-stamp ' +
      (correct ? 'feedback-stamp--correct' : 'feedback-stamp--wrong');
    stamp.textContent = timeout ? '시간 초과!' : (correct ? '정답!' : '오답!');
    ov.classList.add('show');
    setTimeout(() => ov.classList.remove('show'), 900);
  }

  /* ── 내부: 해설 배너 ─────────────────────────────────── */

  function _showAnswerBanner(correct, q, timeout = false) {
    const banner = document.getElementById('answer-banner');
    const correctChoice = q.choices[q.answer_index];
    banner.className = `answer-banner answer-banner--${correct ? 'correct' : 'wrong'}`;
    banner.innerHTML = `
      <span class="answer-banner__icon">${correct ? '✅' : (timeout ? '⏰' : '❌')}</span>
      <div class="answer-banner__text">
        ${timeout ? '시간 초과! ' : (correct ? '정답입니다! ' : '오답! ')}정답:
        <span class="answer-banner__formula">${TriRenderer.renderTexStr(correctChoice)}</span>
      </div>
    `;
    banner.style.display = 'flex';
  }

  /* ── 내부: 다음 버튼 ─────────────────────────────────── */

  function _showNextBtn() {
    const nextBtn = document.getElementById('next-btn');
    const isLast  = _gs.qIndex >= _gs.session.length - 1;
    nextBtn.textContent = isLast ? '결과 보기 🏆' : '다음 문제 →';
    nextBtn.style.display = 'block';
  }

  /* ── 내부: HUD 업데이트 ──────────────────────────────── */

  function _updateHUD() {
    // 점수
    _setEl('hud-score', _gs.score.toLocaleString());
    // 콤보
    const comboEl = document.getElementById('hud-combo');
    if (comboEl) comboEl.textContent = _gs.combo;
    // 정답류
    const answered = _gs.qIndex + 1;
    const acc = answered > 0 ? Math.round((_gs.correctCount / answered) * 100) : 0;
    _setEl('hud-accuracy-val', acc + '%');
    // 평균 응답시간 (토글 ON일 때만)
    if (_toggleState.avgtime && _gs.timings.length > 0) {
      const avg = (_gs.timings.reduce((a, b) => a + b, 0) / _gs.timings.length).toFixed(1);
      _setEl('hud-avgtime-val', avg);
    }
  }

  /* ── 내부: 점수 팝업 ─────────────────────────────────── */

  function _showScorePopup(amount) {
    const badge = document.getElementById('hud-score-badge');
    if (!badge) return;
    badge.style.position = 'relative';
    const popup = document.createElement('span');
    popup.className = 'score-popup';
    popup.textContent = '+' + amount + '점';
    badge.appendChild(popup);
    setTimeout(() => popup.remove(), 1300);
  }

  /* ── 내부: 토글 로드/저장 ─────────────────────────────── */

  function _loadToggles() {
    try {
      const saved = JSON.parse(localStorage.getItem('triToggles') || 'null');
      if (saved) _toggleState = Object.assign(_toggleState, saved);
    } catch(e) {}
    _applyToggleUI('avgtime');
    _applyToggleUI('elapsed');
    _applyToggleUI('scorepop');
    ['avgtime', 'elapsed', 'scorepop'].forEach(key => {
      const btn = document.getElementById('toggle-' + key);
      if (!btn) return;
      btn.addEventListener('click', () => {
        _toggleState[key] = !_toggleState[key];
        _applyToggleUI(key);
        try { localStorage.setItem('triToggles', JSON.stringify(_toggleState)); } catch(e) {}
      });
    });
  }

  function _applyToggleUI(key) {
    const track = document.getElementById('track-' + key);
    if (!track) return;
    const thumb = track.querySelector('.toggle-thumb');
    if (_toggleState[key]) {
      track.classList.add('toggle-track--on');
      if (thumb) thumb.classList.add('toggle-thumb--on');
    } else {
      track.classList.remove('toggle-track--on');
      if (thumb) thumb.classList.remove('toggle-thumb--on');
    }
    if (key === 'avgtime') {
      const b = document.getElementById('hud-avgtime-badge');
      if (b) b.style.display = _toggleState.avgtime ? '' : 'none';
    } else if (key === 'elapsed') {
      const b = document.getElementById('hud-elapsed-badge');
      if (b) b.style.display = _toggleState.elapsed ? '' : 'none';
    }
  }

  /* ── 내부: 진행 도트 ─────────────────────────────────── */

  function _buildProgressDots() {
    const dotsEl = document.getElementById('progress-dots');
    if (!dotsEl) return;
    dotsEl.innerHTML = '';
    for (let i = 0; i < _cfg.SESSION_LEN; i++) {
      const d = document.createElement('div');
      d.className = 'progress-dot';
      d.id = `dot-${i}`;
      dotsEl.appendChild(d);
    }
  }

  function _updateDots() {
    for (let i = 0; i < _cfg.SESSION_LEN; i++) {
      const d = document.getElementById(`dot-${i}`);
      if (!d) continue;
      d.className = 'progress-dot' +
        (i < _gs.qIndex        ? ' progress-dot--done'    :
         i === _gs.qIndex      ? ' progress-dot--current' : '');
    }
  }

  /* ── 내부: DOM 헬퍼 ──────────────────────────────────── */

  function _setEl(id, text) {
    const el = document.getElementById(id);
    if (el) el.textContent = text;
  }
  function _setImg(id, src) {
    const el = document.getElementById(id);
    if (el) el.src = src;
  }

  // 상태를 얕은 복사하되 allQuestions는 참조 유지 (배열 복제 방지)
  function getState() {
    if (!_gs) return null;
    const { allQuestions, ...rest } = _gs;
    return { ...rest, allQuestions };
  }

  /* ── 네임스페이스 노출 ───────────────────────────────── */

  global.TriQuizEngine = {
    init,
    showQuestion,
    onChoiceClick,
    onTimeout,
    nextQuestion,
    showResult,
    resetGame,
    getState,
  };

})(window);
