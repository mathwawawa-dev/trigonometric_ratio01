/**
 * learningEngine.js — 삼각비 학습 모드 엔진
 * v1.1.0_260911_0729
 *
 * 의존성: js/renderer.js (TriRenderer), js/questionsData.js
 */

(function(global) {
  'use strict';

  /* ─── 약분되는 삼각형 ID 제거 ─────────────────────────────
   * 아래 ID들은 세 변에 공통인수가 있어 기존 삼각형과 동일한 비를 가짐
   *   T004 (2,2√3,4)   = T001×2   T007 (2,6,2√10)  = T005×2
   *   T008 (3,9,3√10)  = T005×3   T013 (6,8,10)    = T009×2
   *   T014 (9,12,15)   = T009×3   T015 (10,24,26)  = T010×2
   *   T016 (12,16,20)  = T009×4   T018 (4,6,2√13)  = T017×2
   *   T019 (2,2,2√2)   = T002×2   T020 (3,3,3√2)   = T002×3
   *   T021 (4,4,4√2)   = T002×4   T027 (4,8,4√5)   = T026×4
   ────────────────────────────────────────────────────────── */
  const REDUCIBLE_IDS = new Set([
    'T004','T007','T008',
    'T013','T014','T015','T016',
    'T018',
    'T019','T020','T021',
    'T027',
  ]);

  const IMG_DIR = 'Tri_img_01_dash3';
  const LABELS  = ['①', '②', '③', '④'];

  /* ─── 상태 ─────────────────────────────────────────────── */
  let state = {
    pool:          [],
    session:       [],
    idx:           0,
    answered:      false,
    wrongIds:      new Set(),
    correctIds:    new Set(),
    isReviewMode:  false,
    results:       [],
    multipleChoice: true,   // true=객관식, false=O/X 교사모드
  };

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
    // image_type===1 이고, 약분 가능한 삼각형 제외
    state.pool = allQ.filter(q =>
      q.image_type === 1 && !REDUCIBLE_IDS.has(q.triangle_id)
    );

    state.wrongIds   = new Set();
    state.correctIds = new Set();
    state.results    = [];
    state.isReviewMode = false;

    state.session = shuffle(state.pool);
    state.idx = 0;

    updateReviewBanner();
    showQuestion();
  }

  /* ─── 객관식/O·X 모드 전환 ─────────────────────────────── */
  function setMode(multipleChoice) {
    state.multipleChoice = multipleChoice;
    // 토글 버튼 UI 업데이트
    const btnMC = document.getElementById('mode-mc-btn');
    const btnOX = document.getElementById('mode-ox-btn');
    if (btnMC) btnMC.classList.toggle('mode-btn--active', multipleChoice);
    if (btnOX) btnOX.classList.toggle('mode-btn--active', !multipleChoice);

    // 현재 문항 다시 렌더 (답하지 않은 상태에만)
    if (!state.answered) {
      renderChoiceArea();
    }
  }

  /* ─── 오답 복습 모드 ────────────────────────────────────── */
  function startReview() {
    if (state.wrongIds.size === 0) { showComplete(); return; }
    state.isReviewMode = true;
    const wrongQ = state.pool.filter(q => state.wrongIds.has(q.id));
    state.session = shuffle(wrongQ);
    state.idx     = 0;
    state.wrongIds   = new Set();
    state.results    = [];
    updateReviewBanner();
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

    // 질문 텍스트
    document.getElementById('learn-question-text').innerHTML =
      TriRenderer.renderMixedTex(q.question);

    // 뱃지
    document.getElementById('learn-trig-badge').textContent = q.question_type;

    // 선지 영역
    renderChoiceArea();

    // 배너 리셋
    const banner = document.getElementById('learn-answer-banner');
    banner.className = 'learn-answer-banner';
    banner.textContent = '';

    // 해설 리셋
    document.getElementById('learn-explanation').className = 'learn-explanation';

    // 버튼 리셋
    document.getElementById('learn-next-btn').style.display   = 'none';
    document.getElementById('learn-review-btn').style.display = 'none';
  }

  /* ─── 선지 영역 렌더 (모드에 따라 다름) ───────────────────── */
  function renderChoiceArea() {
    const q = state.session[state.idx];
    if (!q) return;

    if (state.multipleChoice) {
      // 객관식 4지선다
      document.getElementById('learn-choices-grid').style.display = '';
      document.getElementById('learn-ox-grid').style.display      = 'none';

      const choiceEls = document.querySelectorAll('.learn-choice-btn');
      choiceEls.forEach((btn, i) => {
        btn.disabled = state.answered;
        btn.className = 'learn-choice-btn';
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
    } else {
      // O/X 교사 모드
      document.getElementById('learn-choices-grid').style.display = 'none';
      document.getElementById('learn-ox-grid').style.display      = 'grid';

      // O/X 버튼 리셋
      document.querySelectorAll('.learn-ox-btn').forEach(btn => {
        btn.disabled = state.answered;
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

    recordResult(q.id, correct);
    renderAfterAnswer(q, correct, idx);
  }

  /* ─── O/X 교사 클릭 ─────────────────────────────────────── */
  function onOXClick(correct) {
    if (state.answered) return;
    state.answered = true;

    const q = state.session[state.idx];
    recordResult(q.id, correct);

    // O/X 버튼 비활성화
    document.querySelectorAll('.learn-ox-btn').forEach(btn => {
      btn.disabled = true;
    });

    renderAfterAnswer(q, correct, null);
  }

  /* ─── 결과 기록 및 공통 후처리 ──────────────────────────── */
  function recordResult(id, correct) {
    if (correct) {
      state.correctIds.add(id);
      state.wrongIds.delete(id);
    } else {
      state.wrongIds.add(id);
      state.correctIds.delete(id);
    }
    state.results.push({ id, correct });
  }

  function renderAfterAnswer(q, correct, chosenIdx) {
    // 객관식 버튼 색상 처리
    if (state.multipleChoice && chosenIdx !== null) {
      document.querySelectorAll('.learn-choice-btn').forEach((btn, i) => {
        btn.disabled = true;
        if (i === q.answer_index) {
          btn.classList.add(correct && i === chosenIdx
            ? 'learn-choice-btn--correct'
            : 'learn-choice-btn--reveal');
        }
        if (!correct && i === chosenIdx) {
          btn.classList.add('learn-choice-btn--wrong');
        }
      });
    }

    // 스탬프
    showStamp(correct ? '⭕' : '❌');

    // 배너
    const banner = document.getElementById('learn-answer-banner');
    if (correct) {
      banner.className = 'learn-answer-banner learn-answer-banner--correct show';
      banner.textContent = '✅ 정답!';
    } else {
      const ansHtml = TriRenderer.renderTexStr(q.choices[q.answer_index]);
      banner.className = 'learn-answer-banner learn-answer-banner--wrong show';
      banner.innerHTML = `❌ 오답! 정답: <strong>${ansHtml}</strong>`;
    }

    // 해설
    showExplanation(q);

    // 버튼
    const isLast = (state.idx === state.session.length - 1);
    const nextBtn   = document.getElementById('learn-next-btn');
    const reviewBtn = document.getElementById('learn-review-btn');
    if (!isLast) {
      nextBtn.style.display   = '';
      reviewBtn.style.display = 'none';
    } else {
      nextBtn.style.display   = 'none';
      reviewBtn.style.display = '';
      if (state.wrongIds.size > 0) {
        reviewBtn.textContent = `❌ 틀린 ${state.wrongIds.size}문제 다시 풀기`;
        reviewBtn.className = 'btn btn--primary btn--full btn--lg';
      } else {
        reviewBtn.textContent = '🎉 모두 완료! 다시 처음부터';
        reviewBtn.className = 'btn btn--ghost btn--full btn--lg';
      }
    }
  }

  /* ─── 해설 ──────────────────────────────────────────────── */
  function showExplanation(q) {
    const trig  = q.question_type;
    const angle = q.highlight_angle;
    const right = q.right_vertex;
    let hint = '';
    if (trig === 'sin')      hint = `sin ${angle} = (각 ${angle}의 대변) ÷ (빗변)`;
    else if (trig === 'cos') hint = `cos ${angle} = (각 ${angle}의 인접변) ÷ (빗변)`;
    else if (trig === 'tan') hint = `tan ${angle} = (각 ${angle}의 대변) ÷ (인접변)`;
    if (right) hint += `  |  직각: ∠${right} = 90°`;
    const expEl = document.getElementById('learn-explanation');
    expEl.textContent = hint;
    expEl.className = 'learn-explanation show';
  }

  /* ─── 다음 문항 ─────────────────────────────────────────── */
  function nextQuestion() {
    state.idx++;
    if (state.idx >= state.session.length) showComplete();
    else showQuestion();
  }

  /* ─── 완료 화면 ─────────────────────────────────────────── */
  function showComplete() {
    document.getElementById('learn-card-area').style.display    = 'none';
    document.getElementById('learn-choices-area').style.display = 'none';
    document.getElementById('learn-actions').style.display      = 'none';
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

    let msg = pct === 100 ? '완벽합니다! 🏆'
            : pct >= 80  ? `훌륭해요! 🎉 ${wrong}문제 복습해봐요.`
            : pct >= 50  ? `조금 더 연습! 💪 ${wrong}문제 복습 추천.`
            : `포기하지 마세요! 🌱 오답 복습으로 실력을 키워요.`;
    document.getElementById('c-comment').textContent = msg;

    const cReviewBtn = document.getElementById('c-review-btn');
    if (wrong > 0) {
      cReviewBtn.style.display = '';
      cReviewBtn.textContent = `❌ 틀린 ${wrong}문제 다시 풀기`;
    } else {
      cReviewBtn.style.display = 'none';
    }
    document.getElementById('learn-complete').classList.add('show');
  }

  function hideComplete() {
    document.getElementById('learn-complete').classList.remove('show');
    document.getElementById('learn-card-area').style.display    = '';
    document.getElementById('learn-choices-area').style.display = '';
    document.getElementById('learn-actions').style.display      = '';
  }

  /* ─── 오답 배너 ─────────────────────────────────────────── */
  function updateReviewBanner() {
    const el = document.getElementById('learn-review-mode-banner');
    el.classList.toggle('show', state.isReviewMode);
  }

  /* ─── 스탬프 ─────────────────────────────────────────────── */
  function showStamp(emoji) {
    const stamp = document.getElementById('learn-feedback-stamp');
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
  };

})(window);
