/**
 * learningEngine.js — 삼각비 학습 모드 엔진
 * v1.0.0_260911_0713
 *
 * 의존성: js/utils.js (TriUtils), js/renderer.js (TriRenderer), js/questionsData.js
 * 기능: image_type===1 문항 풀링, 오답 모아보기 복습 모드
 */

(function(global) {
  'use strict';

  /* ─────────────── 상수 ─────────────────────────────────── */
  const IMG_DIR = 'Tri_img_01_dash3';    // 세 변 모두 표시 이미지
  const LABELS  = ['①', '②', '③', '④'];

  /* ─────────────── 상태 ─────────────────────────────────── */
  let state = {
    pool:        [],   // 전체 출제 풀 (image_type===1)
    session:     [],   // 현재 세션 문항 배열
    idx:         0,    // 현재 문항 인덱스
    answered:    false,
    wrongIds:    new Set(),   // 오답 id 집합
    correctIds:  new Set(),   // 정답 id 집합
    isReviewMode: false,      // 오답 복습 모드
    results:     [],   // { id, correct } 기록
  };

  /* ─────────────── 유틸 ─────────────────────────────────── */
  function shuffle(arr) {
    const a = arr.slice();
    for (let i = a.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
  }

  function imgSrc(filename) {
    return `${IMG_DIR}/${filename}`;
  }

  /* ─────────────── 초기화 ──────────────────────────────── */
  function init() {
    const allQ = global.QUESTIONS_DATA;
    if (!allQ || !Array.isArray(allQ)) {
      alert('문항 데이터를 불러오지 못했습니다.');
      return;
    }
    // image_type===1 만 → Tri_img_01_dash3 폴더 이미지
    state.pool = allQ.filter(q => q.image_type === 1);
    state.wrongIds   = new Set();
    state.correctIds = new Set();
    state.results    = [];
    state.isReviewMode = false;

    state.session = shuffle(state.pool);
    state.idx = 0;

    updateReviewBanner();
    showQuestion();
  }

  /* ─────────────── 오답 복습 모드 시작 ──────────────────── */
  function startReview() {
    if (state.wrongIds.size === 0) {
      showComplete();
      return;
    }
    state.isReviewMode = true;
    const wrongQuestions = state.pool.filter(q => state.wrongIds.has(q.id));
    state.session = shuffle(wrongQuestions);
    state.idx = 0;
    state.wrongIds   = new Set();
    state.results    = [];

    updateReviewBanner();
    hideComplete();
    showQuestion();
  }

  /* ─────────────── 현재 문항 렌더 ──────────────────────── */
  function showQuestion() {
    const q = state.session[state.idx];
    if (!q) { showComplete(); return; }

    state.answered = false;

    // 진행 카운터
    const el = id => document.getElementById(id);
    el('learn-q-current').textContent = state.idx + 1;
    el('learn-q-total').textContent   = state.session.length;

    // 진행 도트
    renderDots();

    // 질문 텍스트
    const qEl = el('learn-question-text');
    qEl.innerHTML = TriRenderer.renderMixedTex(q.question);

    // 이미지
    const imgEl = el('learn-tri-img');
    imgEl.src = imgSrc(q.filename);
    imgEl.alt = `삼각형 문제 이미지 (${q.id})`;

    // 뱃지
    el('learn-trig-badge').textContent = q.question_type;
    el('learn-type-badge').textContent = `유형 ${q.image_type}`;

    // 선지 렌더
    const choiceEls = document.querySelectorAll('.learn-choice-btn');
    choiceEls.forEach((btn, i) => {
      btn.disabled = false;
      btn.className = 'learn-choice-btn';
      btn.dataset.idx = i;
      const label = btn.querySelector('.learn-choice-label');
      if (label) label.textContent = LABELS[i];
      const body  = btn.querySelector('.learn-choice-body');
      if (body) {
        if (TriRenderer.isSimpleChoice(q.choices[i])) {
          btn.classList.add('learn-choice-btn--simple');
        }
        body.innerHTML = TriRenderer.renderTexStr(q.choices[i]);
      }
    });

    // 배너 숨기기
    const banner = el('learn-answer-banner');
    banner.className = 'learn-answer-banner';
    banner.textContent = '';

    // 해설 숨기기
    const expEl = el('learn-explanation');
    expEl.className = 'learn-explanation';

    // 다음 버튼 숨기기
    el('learn-next-btn').style.display = 'none';
    el('learn-review-btn').style.display = 'none';
  }

  /* ─────────────── 선지 클릭 ──────────────────────────── */
  function onChoiceClick(idx) {
    if (state.answered) return;
    state.answered = true;

    const q       = state.session[state.idx];
    const correct = (idx === q.answer_index);

    // 정답/오답 기록
    if (correct) {
      state.correctIds.add(q.id);
    } else {
      state.wrongIds.add(q.id);
    }
    state.results.push({ id: q.id, correct });

    // 버튼 상태 업데이트
    const choiceEls = document.querySelectorAll('.learn-choice-btn');
    choiceEls.forEach((btn, i) => {
      btn.disabled = true;
      if (i === q.answer_index) {
        btn.classList.add(correct && i === idx ? 'learn-choice-btn--correct' : 'learn-choice-btn--reveal');
      }
      if (!correct && i === idx) {
        btn.classList.add('learn-choice-btn--wrong');
      }
    });

    // 피드백 스탬프
    showStamp(correct ? '⭕' : '❌');

    // 배너
    const banner = document.getElementById('learn-answer-banner');
    if (correct) {
      banner.className = 'learn-answer-banner learn-answer-banner--correct show';
      banner.textContent = '✅ 정답입니다!';
    } else {
      const ansHtml = TriRenderer.renderTexStr(q.choices[q.answer_index]);
      banner.className = 'learn-answer-banner learn-answer-banner--wrong show';
      banner.innerHTML = `❌ 오답! 정답은 <strong>${ansHtml}</strong> 입니다.`;
    }

    // 해설 표시
    showExplanation(q, correct);

    // 도트 업데이트
    renderDots();

    // 버튼 표시
    const nextBtn   = document.getElementById('learn-next-btn');
    const reviewBtn = document.getElementById('learn-review-btn');
    const isLast = (state.idx === state.session.length - 1);

    if (!isLast) {
      nextBtn.style.display   = '';
      reviewBtn.style.display = 'none';
    } else {
      nextBtn.style.display   = 'none';
      reviewBtn.style.display = '';
      // 완료 시 버튼 텍스트 결정
      if (state.wrongIds.size > 0) {
        reviewBtn.textContent = `❌ 틀린 ${state.wrongIds.size}문제 다시 풀기`;
        reviewBtn.classList.remove('btn--ghost');
        reviewBtn.classList.add('btn--primary');
      } else {
        reviewBtn.textContent = '🎉 모두 완료! 다시 처음부터';
        reviewBtn.classList.remove('btn--primary');
        reviewBtn.classList.add('btn--ghost');
      }
    }
  }

  /* ─────────────── 해설 ──────────────────────────────── */
  function showExplanation(q, correct) {
    const expEl = document.getElementById('learn-explanation');
    const trig  = q.question_type;
    const angle = q.highlight_angle;
    const right = q.right_vertex;

    // 삼각비 정의 힌트 텍스트
    let hint = '';
    if (trig === 'sin') {
      hint = `sin ${angle} = (각 ${angle}의 대변) ÷ (빗변)`;
    } else if (trig === 'cos') {
      hint = `cos ${angle} = (각 ${angle}의 인접변) ÷ (빗변)`;
    } else if (trig === 'tan') {
      hint = `tan ${angle} = (각 ${angle}의 대변) ÷ (각 ${angle}의 인접변)`;
    }
    if (right) {
      hint += `\n직각: ∠${right} = 90°`;
    }

    expEl.textContent = hint;
    expEl.className = 'learn-explanation show';
  }

  /* ─────────────── 다음 문항 ──────────────────────────── */
  function nextQuestion() {
    state.idx++;
    if (state.idx >= state.session.length) {
      showComplete();
    } else {
      showQuestion();
    }
  }

  /* ─────────────── 완료 화면 ──────────────────────────── */
  function showComplete() {
    document.getElementById('learn-card-area').style.display   = 'none';
    document.getElementById('learn-choices-area').style.display = 'none';
    document.getElementById('learn-actions').style.display     = 'none';
    document.getElementById('learn-answer-banner').classList.remove('show');
    document.getElementById('learn-explanation').classList.remove('show');

    const total   = state.results.length;
    const correct = state.results.filter(r => r.correct).length;
    const wrong   = total - correct;
    const pct     = total > 0 ? Math.round(correct / total * 100) : 0;

    document.getElementById('c-total').textContent   = total;
    document.getElementById('c-correct').textContent = correct;
    document.getElementById('c-wrong').textContent   = wrong;
    document.getElementById('c-pct').textContent     = pct + '%';

    // 코멘트
    let msg = '';
    if (pct === 100) msg = '완벽합니다! 🏆 모든 문제를 맞혔어요.';
    else if (pct >= 80) msg = `훌륭해요! 🎉 ${wrong}문제만 다시 확인해봐요.`;
    else if (pct >= 50) msg = `조금 더 연습해봐요! 💪 ${wrong}문제 복습 추천.`;
    else msg = `포기하지 마세요! 🌱 오답 복습으로 실력을 쌓아요.`;

    document.getElementById('c-comment').textContent = msg;

    // 오답 복습 버튼
    const cReviewBtn = document.getElementById('c-review-btn');
    const cRestartBtn = document.getElementById('c-restart-btn');
    if (wrong > 0) {
      cReviewBtn.style.display = '';
      cReviewBtn.textContent = `❌ 틀린 ${wrong}문제 다시 풀기`;
    } else {
      cReviewBtn.style.display = 'none';
    }

    const completeEl = document.getElementById('learn-complete');
    completeEl.classList.add('show');
  }

  function hideComplete() {
    document.getElementById('learn-complete').classList.remove('show');
    document.getElementById('learn-card-area').style.display   = '';
    document.getElementById('learn-choices-area').style.display = '';
    document.getElementById('learn-actions').style.display     = '';
  }

  /* ─────────────── 도트 렌더 ──────────────────────────── */
  function renderDots() {
    const container = document.getElementById('learn-progress-dots');
    const n = state.session.length;
    container.innerHTML = '';
    for (let i = 0; i < n; i++) {
      const dot = document.createElement('div');
      dot.className = 'lpb-dot';
      const r = state.results[i];
      if (r) {
        dot.classList.add(r.correct ? 'lpb-dot--correct' : 'lpb-dot--wrong');
      } else if (i === state.idx) {
        dot.classList.add('lpb-dot--current');
      }
      container.appendChild(dot);
    }
  }

  /* ─────────────── 스탬프 피드백 ──────────────────────── */
  function showStamp(emoji) {
    const stamp = document.getElementById('learn-feedback-stamp');
    stamp.textContent = emoji;
    stamp.className = 'learn-feedback-stamp';
    // reflow
    void stamp.offsetWidth;
    stamp.classList.add('pop');
    stamp.addEventListener('animationend', () => {
      stamp.className = 'learn-feedback-stamp';
    }, { once: true });
  }

  /* ─────────────── 오답 복습 배너 ─────────────────────── */
  function updateReviewBanner() {
    const el = document.getElementById('learn-review-mode-banner');
    if (state.isReviewMode) {
      el.classList.add('show');
    } else {
      el.classList.remove('show');
    }
  }

  /* ─────────────── 공개 API ──────────────────────────── */
  global.LearningEngine = {
    init,
    startReview,
    nextQuestion,
    onChoiceClick,
  };

})(window);
