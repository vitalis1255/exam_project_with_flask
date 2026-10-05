// When document has finished loading 
document.addEventListener("DOMContentLoaded", () => {
  const appElement = document.getElementById("exam-app");
  if (!appElement) return;


  //Read JSON safely from the script tag text content
  const questionScript = document.getElementById("exam-data");
  const questions = JSON.parse(questionScript.textContent);
  let timeLeft = parseInt(appElement.getAttribute("data-duration"), 10);
  let currentIndex = 0;
  const userAnswers = {};//{question_id: selected_option}


  //Countdown Timer Engine
  const timerInterval = setInterval(() => {
    if (timeLeft <= 0) {
      clearInterval(timerInterval);
      alert("Time is up! Your exam will be submitted automatically. ");
      submitExam();
      return;
    }
    timeLeft--;
    let mins = Math.floor(timeLeft / 60);
    let secs = timeLeft % 60;
    document.getElementById("timer-display").innerText = `Time Left: ${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
  },1000);


  function renderQuestion() {
    if (questions.length === 0) return;
    const q = questions[currentIndex];
    document.getElementById("q-counter").innerText = `Question ${currentIndex + 1} of ${questions.length}`;
    document.getElementById("q-text").innerText = q.question_text;

    const optionList = document.getElementById("options-list");
    optionList.innerHTML = "";

    const opts = {
      A: q.option_a, B: q.option_b, C: q.option_c, D: q.option_d
    };
    for (const [key, val] of Object.entries(opts)) {
      const isChecked = userAnswers[q.id] === key ? "checked" : "";
      optionList.innerHTML += `
      <label style="display:flex; align-items:center; padding: 1rem; background: #0f172a; border: 1px solid #334155; border-radius: 6px; cursor: pointer;">
      <input type="radio" name="option" value="${key}" ${isChecked} onclick="window.saveAnswer(${q.id}, '${key}')" style="margin-right:1rem;"><span><strong>${key}.</strong> ${val}</span></label>
      `;
    }
    
    //Using ternary operator
    document.getElementById("prev-btn").style.display = currentIndex === 0 ? "none" : "block";
    document.getElementById("next-btn").style.display = currentIndex === questions.length - 1 ? "none" : "block";
    document.getElementById("submit-btn").style.display = currentIndex === questions.length - 1 ? "block" : "none";
  }


  //Expose helper functions globally so HTML onclick triggers work correctly
  window.saveAnswer = function(questionId, option) {
    userAnswers[questionId] = option;
  };


  window.changeQuestion = function(direction) {
    currentIndex += direction;
    if (currentIndex < 0) 
      currentIndex = 0;
    if (currentIndex >= questions.length)
      currentIndex = questions.length - 1;
    renderQuestion();
  };

  window.submitExam = function() {
    clearInterval(timerInterval);
    fetch("/exam/submit", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        answers: userAnswers
      }),
    }).then((res) => res.json()).then((data)=>{
      if (data.redirect) {
        window.location.href = data.redirect;
      }
    });
  };

  renderQuestion()
});