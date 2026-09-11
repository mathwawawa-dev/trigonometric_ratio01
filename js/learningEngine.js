/**
 * learningEngine.js — 삼각비 학습 모드 엔진
 * v1.2.0_260911_0736
 */

(function(global) {
  'use strict';

  /* ─── 약분 가능한 삼각형 제거 ──────────────────────────── */
  const REDUCIBLE_IDS = new Set([
    'T004','T007','T008',
    'T013','T014','T015','T016',
    'T018',
    'T019','T020','T021',
    'T027',
  ]);

  const LABELS = ['①', '②', '③', '④'];

  /* ─── 상태 ─────────────────────────────────────────────── */
  let state = {
    pool:           [],
    session:        [],
    idx:            0,
    answered:       false,
    wrongIds:       new Set(),
    results:        [],
    isReviewMode:   false,
    multipleChoice: false,
  };

  /* ─── 줌 상태 ───────────────────────────────────────────── */
  let zoomScale = 1.0;
  const ZOOM_STEP = 0.25;
  const ZOOM_MIN  = 0.4;
  const ZOOM_MAX  = 4.0;

  function applyZoom() {
    const c = document.getElementById('learn-zoom-container');
    if (c) c.style.zoom = String(zoomScale);
  }
  function zoomIn()    { zoomScale = Math.min(zoomScale + ZOOM_STEP, ZOOM_MAX); applyZoom(); }
  function zoomOut()   { zoomScale = Math.max(zoomScale - ZOOM_STEP, ZOOM_MIN); applyZoom(); }
  function resetZoom() { zoomScale = 1.0; applyZoom(); }

  /* ─── 👍 애니메이션 ─────────────────────────────────────── */
  function showThumbsUp() {
    const el = document.getElementById('learn-thumbs-up');
    if (!el) return;
    el.textContent = '👍👍';
    el.className = 'learn-thumbs-up';
    void el.offsetWidth;
    el.classList.add('pop');
    el.addEventListener('animationend', () => {
      el.className = 'learn-thumbs-up';
    }, { once: true });
  }

  /* ─── 유틸 ─────────────────────────────────────────────── */
  function shuffle(arr) {
    const a = arr.slice();
    for (let i = a.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
  }

  /* ─── 초기화 ────────────────────────────────────────────── */
  function init() {
    const allQ = global.QUESTIONS_DATA;
    if (!allQ || !Array.isArray(allQ)) {
      alert('문항 데이터를 불러오지 못했습니다.');
      return;
    }
    state.pool = allQ.filter(q =>
      q.image_type === 1 && !REDUCIBLE_IDS.has(q.triangle_id)
    );
    state.wrongIds   = new Set();
    state.results    = [];
    state.isReviewMode = false;
    state.session = shuffle(state.pool);
    state.idx = 0;

    updateReviewBanner();
    updateWrongPill();
    showQuestion();
  }

  /* ─── 모드 전환 (외부에서 호출) ─────────────────────────── */
  function setMode(mc) {
    state.multipleChoice = mc;
    if (!state.answered) renderChoiceArea();
    updateMCToggleBtn();
  }

  /* ─── 오답 복습 시작 ─────────────────────────────────────── */
  function startReview() {
    if (state.wrongIds.size === 0) return;
    state.isReviewMode = true;
    const wrongQ = state.pool.filter(q => state.wrongIds.has(q.id));
    state.session  = shuffle(wrongQ);
    state.idx      = 0;
    state.wrongIds = new Set();
    state.results  = [];
    updateReviewBanner();
    updateWrongPill();
    hideComplete();
    showQuestion();
  }

  /* ─── 문항 렌더 ─────────────────────────────────────────── */
  function showQuestion() {
    const q = state.session[state.idx];
    if (!q) { showComplete(); return; }
    state.answered = false;

    // 카운터
    document.getElementById('learn-q-current').textContent = state.idx + 1;
    document.getElementById('learn-q-total').textContent   = state.session.length;

    // ── 수식 표시: "\sin A" 형태로 KaTeX 렌더 ──
    const trigTex = `\\${q.question_type} ${q.highlight_angle}`;
    const exprEl  = document.getElementById('learn-q-expr');
    if (global.katex) {
      try {
        global.katex.render(trigTex, exprEl, { throwOnError: false, displayMode: false });
      } catch(e) {
        exprEl.textContent = `${q.question_type} ${q.highlight_angle}`;
      }
    } else {
      exprEl.textContent = `${q.question_type} ${q.highlight_angle}`;
    }

    // 뱃지
    document.getElementById('learn-badge-trig').textContent = q.question_type;
    document.getElementById('learn-badge-cat').textContent  = q.category || '';
    document.getElementById('learn-badge-tri').textContent  = q.triangle_id || '';

    // ── 삼각형 이미지 ──
    const imgEl = document.getElementById('learn-tri-img');
    if (imgEl) {
      imgEl.src = `Tri_img_01_dash3/${q.filename}`;
      imgEl.alt = `삼각형 문제 이미지 (${q.id})`;
    }

    // 선지 영역
    renderChoiceArea();

    // 배너/해설 리셋
    const banner = document.getElementById('learn-answer-banner');
    banner.className = 'learn-answer-banner';
    banner.textContent = '';
    document.getElementById('learn-explanation').className = 'learn-explanation';

    // 버튼 리셋
    document.getElementById('learn-next-btn').style.display   = 'none';
  }

  /* ─── 선지 영역 렌더 ────────────────────────────────────── */
  function renderChoiceArea() {
    const q = state.session[state.idx];
    if (!q) return;

    const mcGrid = document.getElementById('learn-choices-grid');
    const oxGrid = document.getElementById('learn-ox-grid');

    if (state.multipleChoice) {
      mcGrid.style.display = 'grid';
      oxGrid.style.display = 'none';

      document.querySelectorAll('.learn-choice-btn').forEach((btn, i) => {
        btn.disabled  = state.answered;
        btn.className = 'learn-choice-btn';
        const label = btn.querySelector('.learn-choice-label');
        if (label) label.textContent = LABELS[i];
        const body  = btn.querySelector('.learn-choice-body');
        if (body) {
          body.innerHTML = TriRenderer.renderTexStr(q.choices[i]);
        }
      });
    } else {
      mcGrid.style.display = 'none';
      oxGrid.style.display = 'grid';
      document.querySelectorAll('.learn-ox-btn').forEach(btn => {
        btn.disabled  = state.answered;
        btn.className = 'learn-ox-btn learn-ox-btn--' + btn.dataset.result;
      });
    }
  }

  /* ─── 선지 클릭 (객관식) ────────────────────────────────── */
  function onChoiceClick(idx) {
    if (state.answered) return;
    state.answered = true;
    const q = state.session[state.idx];
    const correct = (idx === q.answer_index);

    record(q.id, correct);

    // 버튼 표시
    document.querySelectorAll('.learn-choice-btn').forEach((btn, i) => {
      btn.disabled = true;
      if (i === q.answer_index) {
        btn.classList.add(correct && i === idx ? 'learn-choice-btn--correct' : 'learn-choice-btn--reveal');
      }
      if (!correct && i === idx) btn.classList.add('learn-choice-btn--wrong');
    });

    afterAnswer(q, correct);
  }

  /* ─── O/X 교사 클릭 ─────────────────────────────────────── */
  function onOXClick(correct) {
    if (state.answered) return;
    state.answered = true;
    const q = state.session[state.idx];
    record(q.id, correct);
    document.querySelectorAll('.learn-ox-btn').forEach(btn => { btn.disabled = true; });
    afterAnswer(q, correct);
  }

  /* ─── 공통 후처리 ───────────────────────────────────────── */
  function record(id, correct) {
    if (correct) state.wrongIds.delete(id);
    else         state.wrongIds.add(id);
    state.results.push({ id, correct });
    updateWrongPill();
  }

  function afterAnswer(q, correct) {
    // 정답이면 👍👍 애니메이션
    if (correct) showThumbsUp();

    // 배너·해설 모두 숨김 (정답/오답 무관)
    const banner = document.getElementById('learn-answer-banner');
    banner.className = 'learn-answer-banner';
    banner.textContent = '';
    document.getElementById('learn-explanation').className = 'learn-explanation';

    // 다음 버튼만 표시
    const isLast = (state.idx === state.session.length - 1);
    const nextBtn = document.getElementById('learn-next-btn');
    nextBtn.textContent = isLast ? '결과 보기 →' : '다음 문제 →';
    nextBtn.className = 'btn btn--primary btn--full btn--lg';
    nextBtn.style.display = '';
  }

  /* ─── 다음 문항 ─────────────────────────────────────────── */
  function nextQuestion() {
    state.idx++;
    if (state.idx >= state.session.length) showComplete();
    else showQuestion();
  }

  /* ─── 완료 화면 ─────────────────────────────────────────── */
  function showComplete() {
    ['learn-q-area', 'learn-choices-area', 'learn-actions'].forEach(id => {
      const el = document.getElementById(id);
      if (el) el.style.display = 'none';
    });
    ['learn-answer-banner', 'learn-explanation'].forEach(id => {
      const el = document.getElementById(id);
      if (el) { el.className = el.className.replace(/\bshow\b/, ''); }
    });

    const total   = state.results.length;
    const correct = state.results.filter(r => r.correct).length;
    const wrong   = total - correct;
    const pct     = total > 0 ? Math.round(correct / total * 100) : 0;

    document.getElementById('c-total').textContent   = total;
    document.getElementById('c-correct').textContent = correct;
    document.getElementById('c-wrong').textContent   = wrong;
    document.getElementById('c-pct').textContent     = pct + '%';

    const msg = pct === 100 ? '완벽합니다! 🏆 모두 맞혔어요.'
              : pct >= 80   ? `훌륭해요! 🎉 ${wrong}문제 복습해봐요.`
              : pct >= 50   ? `조금 더 연습! 💪 ${wrong}문제 복습 추천.`
              : '포기하지 마세요! 🌱 오답 복습으로 실력을 쌓아요.';
    document.getElementById('c-comment').textContent = msg;

    const cReviewBtn = document.getElementById('c-review-btn');
    cReviewBtn.style.display = wrong > 0 ? '' : 'none';
    if (wrong > 0) cReviewBtn.textContent = `❌ 틀린 ${wrong}문제 다시 풀기`;

    document.getElementById('learn-complete').classList.add('show');
    updateWrongPill();
  }

  function hideComplete() {
    document.getElementById('learn-complete').classList.remove('show');
    ['learn-q-area', 'learn-choices-area', 'learn-actions'].forEach(id => {
      const el = document.getElementById(id);
      if (el) el.style.display = '';
    });
  }

  /* ─── UI 업데이트 ───────────────────────────────────────── */
  function updateReviewBanner() {
    const el = document.getElementById('learn-review-mode-banner');
    if (el) el.classList.toggle('show', state.isReviewMode);
  }

  function updateWrongPill() {
    const pill = document.getElementById('learn-wrong-pill');
    const cnt  = document.getElementById('wrong-count');
    if (!pill) return;
    if (state.wrongIds.size > 0) {
      pill.classList.add('show');
      if (cnt) cnt.textContent = state.wrongIds.size;
    } else {
      pill.classList.remove('show');
    }
  }

  function updateMCToggleBtn() {
    const btn = document.getElementById('learn-mc-toggle');
    if (!btn) return;
    if (state.multipleChoice) {
      btn.classList.add('mc-on');
      btn.querySelector('span').textContent = '객관식 ON';
    } else {
      btn.classList.remove('mc-on');
      btn.querySelector('span').textContent = '객관식 OFF';
    }
  }

  /* ─── 스탬프 ─────────────────────────────────────────────── */
  function showStamp(emoji) {
    const stamp = document.getElementById('learn-feedback-stamp');
    if (!stamp) return;
    stamp.textContent = emoji;
    stamp.className = 'learn-feedback-stamp';
    void stamp.offsetWidth;
    stamp.classList.add('pop');
    stamp.addEventListener('animationend', () => {
      stamp.className = 'learn-feedback-stamp';
    }, { once: true });
  }

  /* ─── 공개 API ──────────────────────────────────────────── */
  global.LearningEngine = {
    init,
    startReview,
    nextQuestion,
    onChoiceClick,
    onOXClick,
    setMode,
    updateMCToggleBtn,
    getMode: () => state.multipleChoice,
    zoomIn,
    zoomOut,
    resetZoom,
  };

})(window);
