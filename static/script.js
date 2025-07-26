document.addEventListener("DOMContentLoaded", function () {
  const reloadBtn = document.getElementById("reloadBtn");
  const plannerContainer = document.getElementById("planner-container");
  const modal = document.getElementById("modal");
  const dateSpan = document.getElementById("date");
  const addTaskBtn = document.getElementById("addTaskBtn");
  const addGoalBtn = document.getElementById("addGoalBtn");
  const addFoodBtn = document.getElementById("addFoodBtn");
  const addWaterBtn = document.getElementById("addWaterBtn");
  // Removed addExerciseBtn

  let lastData = null; // Store last loaded data for dynamic dropdowns

  function formatDate(date) {
    return date.toISOString().split("T")[0];
  }

  function showModal(html) {
    modal.innerHTML = html;
    modal.style.display = "block";
    // Add click-to-close on background
    modal.onclick = function (e) {
      if (e.target === modal) closeModal();
    };
  }
  function closeModal() {
    modal.style.display = "none";
    modal.innerHTML = "";
    modal.onclick = null;
  }
  window.closeModal = closeModal;

  function getSection(data, name) {
    // Try lowercase, then capitalized
    return (
      data.tasks &&
      (data.tasks[name] ||
        data.tasks[name.charAt(0).toUpperCase() + name.slice(1)])
    );
  }
  function getDone(data, name) {
    return (
      data.done &&
      (data.done[name] ||
        data.done[name.charAt(0).toUpperCase() + name.slice(1)])
    );
  }

  function getSectionName(data, name) {
    // Return the actual key from data.tasks matching name (case-insensitive)
    if (!data.tasks) return name;
    const keys = Object.keys(data.tasks);
    const found = keys.find((k) => k.toLowerCase() === name.toLowerCase());
    return found || name;
  }

  function renderPlanner(data) {
    lastData = data; // Save for dropdowns
    plannerContainer.innerHTML = "";
    if (!data) {
      plannerContainer.textContent = "No data available.";
      return;
    }
    const morningKey = getSectionName(data, "morning");
    if (data.tasks && data.tasks[morningKey]) {
      renderRoutineSection(
        morningKey,
        data.tasks[morningKey],
        getDone(data, "morning"),
        true,
        false
      );
    }
    const eveningKey = getSectionName(data, "evening");
    if (data.tasks && data.tasks[eveningKey]) {
      renderRoutineSection(
        eveningKey,
        data.tasks[eveningKey],
        getDone(data, "evening"),
        false,
        true
      );
    }
    // 3. [Plan]
    if (data.plan) {
      renderPlanSection(data.plan);
    }
    // 4. [Goals] focus
    if (data.goals && data.goals.focus) {
      renderGoalsSection("focus", data.goals.focus);
    }
    // 5. [Goals] todo
    if (data.goals && data.goals.todo) {
      renderGoalsSection("todo", data.goals.todo);
    }
    // 9. [Hydration]
    if (typeof data.water !== "undefined") {
      renderHydrationSection(data.water);
    }
    // 6-8. [Food] breakfast, lunch, dinner
    if (data.food) {
      ["breakfast", "lunch", "dinner"].forEach((meal) => {
        if (data.food[meal]) {
          renderFoodSection(meal, data.food[meal]);
        }
      });
    }
  }

  function renderRoutineSection(
    section,
    items,
    doneList,
    isMorning,
    isEvening
  ) {
    const box = document.createElement("div");
    box.className = "box routine-box";
    if (isMorning) box.classList.add("morning-box");
    if (isEvening) box.classList.add("evening-box");
    const title = document.createElement("div");
    title.className = "section-title";
    title.textContent = `[Routine] ${
      section.charAt(0).toUpperCase() + section.slice(1)
    }`;
    if (isMorning) title.classList.add("morning-title");
    if (isEvening) title.classList.add("evening-title");
    box.appendChild(title);
    items.forEach((item, i) => {
      const label = document.createElement("label");
      const input = document.createElement("input");
      input.type = "checkbox";
      input.checked = doneList[i];
      input.addEventListener("change", () =>
        updateTask(section, i, input.checked)
      );
      input.disabled = false;
      label.appendChild(input);
      label.append(" " + item);
      box.appendChild(label);
    });
    plannerContainer.appendChild(box);
  }

  function renderPlanSection(plan) {
    const box = document.createElement("div");
    box.className = "box";
    const title = document.createElement("div");
    title.className = "section-title";
    title.textContent = "[Plan]";
    box.appendChild(title);
    Object.entries(plan).forEach(([hour, task]) => {
      const line = document.createElement("div");
      line.textContent = `${hour}:00 - ${task}`;
      box.appendChild(line);
    });
    plannerContainer.appendChild(box);
  }

  function renderGoalsSection(cat, goals) {
    const box = document.createElement("div");
    box.className = "box";
    const title = document.createElement("div");
    title.className = "section-title";
    title.textContent = `[Goals] ${cat}`;
    box.appendChild(title);
    (goals || []).forEach((goal, i) => {
      const label = document.createElement("label");
      const input = document.createElement("input");
      input.type = "checkbox";
      input.checked = goal.done;
      input.addEventListener("change", () => updateGoal(cat, i, input.checked));
      input.disabled = false;
      label.appendChild(input);
      label.append(" " + goal.text);
      box.appendChild(label);
    });
    plannerContainer.appendChild(box);
  }

  function renderFoodSection(meal, foods) {
    const box = document.createElement("div");
    box.className = "box";
    const title = document.createElement("div");
    title.className = "section-title";
    title.textContent = `[Food] ${meal}`;
    box.appendChild(title);
    (foods || []).forEach((food) => {
      const line = document.createElement("div");
      line.textContent = `${food.name || food} (${food.weight || ""}g)`;
      box.appendChild(line);
    });
    plannerContainer.appendChild(box);
  }

  function renderHydrationSection(water) {
    const box = document.createElement("div");
    box.className = "box";
    const title = document.createElement("div");
    title.className = "section-title";
    title.textContent = "[Hydration]";
    box.appendChild(title);
    box.appendChild(document.createTextNode(`Water: ${water} ml`));
    plannerContainer.appendChild(box);
  }

  function updateTask(section, index, done) {
    const date = currentDate || formatDate(new Date());
    fetch("/update_task", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: `part=${encodeURIComponent(
        section
      )}&index=${index}&done=${done}&date=${date}`,
    }).then(() => loadToday());
  }
  function updateGoal(section, index, done) {
    const date = currentDate || formatDate(new Date());
    fetch("/update_goal", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: `section=${encodeURIComponent(
        section
      )}&index=${index}&done=${done}&date=${date}`,
    }).then(() => loadToday());
  }
  function addTaskModal() {
    // Use dropdown for section
    let sectionOptions = "";
    if (lastData && lastData.tasks) {
      Object.keys(lastData.tasks).forEach((section) => {
        sectionOptions += `<option value="${section}">${
          section.charAt(0).toUpperCase() + section.slice(1)
        }</option>`;
      });
    }
    showModal(`
        <form id="addTaskForm" onsubmit="return false;">
            <h3>Add Task</h3>
            <label>Section:
                <select name="section" required>${sectionOptions}</select>
            </label><br>
            <label>Task: <input name="text" required></label><br>
            <button type="submit">Add</button>
        </form>`);
    document.getElementById("addTaskForm").onsubmit = function () {
      const form = this;
      fetch("/add_task", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: `section=${encodeURIComponent(
          form.section.value
        )}&text=${encodeURIComponent(form.text.value)}`,
      }).then(() => {
        closeModal();
        loadToday();
      });
    };
  }
  function addGoalModal() {
    // Use dropdown for section
    let sectionOptions = "";
    if (lastData && lastData.goals) {
      Object.keys(lastData.goals).forEach((section) => {
        sectionOptions += `<option value="${section}">${
          section.charAt(0).toUpperCase() + section.slice(1)
        }</option>`;
      });
    }
    showModal(`
        <form id="addGoalForm" onsubmit="return false;">
            <h3>Add Goal</h3>
            <label>Section:
                <select name="section" required>${sectionOptions}</select>
            </label><br>
            <label>Goal: <input name="text" required></label><br>
            <button type="submit">Add</button>
        </form>`);
    document.getElementById("addGoalForm").onsubmit = function () {
      const form = this;
      fetch("/add_goal", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: `section=${encodeURIComponent(
          form.section.value
        )}&text=${encodeURIComponent(form.text.value)}`,
      }).then(() => {
        closeModal();
        loadToday();
      });
    };
  }
  function addFoodModal() {
    // Use dropdown for meal
    let mealOptions = "";
    if (lastData && lastData.food) {
      Object.keys(lastData.food).forEach((meal) => {
        mealOptions += `<option value="${meal}">${
          meal.charAt(0).toUpperCase() + meal.slice(1)
        }</option>`;
      });
    }
    showModal(`
        <form id="addFoodForm" onsubmit="return false;">
            <h3>Add Food</h3>
            <label>Meal:
                <select name="meal" required>${mealOptions}</select>
            </label><br>
            <label>Search Food: <input name="search" id="foodSearchInput" placeholder="Type to search..."></label><br>
            <div id="searchResults" style="display: none;"></div>
            <label>Name: <input name="name" required></label><br>
            <label>Weight (g): <input name="weight" type="number" min="1" required></label><br>
            <button type="submit">Add</button>
        </form>`);

    // Add search functionality
    const searchInput = document.getElementById("foodSearchInput");
    const searchResults = document.getElementById("searchResults");
    const nameInput = document.querySelector('input[name="name"]');

    let searchTimeout;
    searchInput.addEventListener("input", function () {
      clearTimeout(searchTimeout);
      const query = this.value.trim();

      if (query.length < 2) {
        searchResults.style.display = "none";
        return;
      }

      searchTimeout = setTimeout(() => {
        fetch(`/search_food?q=${encodeURIComponent(query)}`)
          .then((res) => res.json())
          .then((data) => {
            if (data.foods && data.foods.length > 0) {
              searchResults.innerHTML = data.foods
                .map(
                  (food) =>
                    `<div class="search-result-item" onclick="selectFood('${food.name}')">
                  <div style="font-weight: bold;">${food.name}</div>
                  <div style="font-size: 0.9em; color: #98c379;">
                    Protein: ${food.protein}g | Fat: ${food.fat}g | Carbs: ${food.carbon}g
                  </div>
                </div>`
                )
                .join("");
              searchResults.style.display = "block";
            } else {
              searchResults.innerHTML =
                '<div style="padding: 8px; color: #abb2bf;">No foods found</div>';
              searchResults.style.display = "block";
            }
          })
          .catch((err) => {
            console.error("Search error:", err);
            searchResults.innerHTML =
              '<div style="padding: 8px; color: #e06c75;">Search error</div>';
            searchResults.style.display = "block";
          });
      }, 300);
    });

    // Close search results when clicking outside
    document.addEventListener("click", function (e) {
      if (
        !searchInput.contains(e.target) &&
        !searchResults.contains(e.target)
      ) {
        searchResults.style.display = "none";
      }
    });

    document.getElementById("addFoodForm").onsubmit = function () {
      const form = this;
      fetch("/add_food", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: `meal=${encodeURIComponent(
          form.meal.value
        )}&name=${encodeURIComponent(
          form.name.value
        )}&weight=${encodeURIComponent(form.weight.value)}`,
      }).then(() => {
        closeModal();
        loadToday();
      });
    };
  }

  // Global function to select food from search results
  window.selectFood = function (foodName) {
    document.querySelector('input[name="name"]').value = foodName;
    document.getElementById("searchResults").style.display = "none";
    document.getElementById("foodSearchInput").value = "";
  };
  function addWaterModal() {
    showModal(`
    <form id="addWaterForm" onsubmit="return false;">
        <h3>Add Water</h3>
        <label>Amount (ml):
            <input name="amount" id="waterAmountInput" type="number" min="0" step="100" value="100" required>
        </label><br>
        <button type="submit">Add</button>
    </form>`);
    const input = document.getElementById("waterAmountInput");
    input.addEventListener("keydown", function (e) {
      let value = parseInt(input.value, 10) || 0;
      if (e.key === "ArrowUp") {
        e.preventDefault();
        input.value = value + 100;
      } else if (e.key === "ArrowDown") {
        e.preventDefault();
        input.value = Math.max(0, value - 100);
      }
    });
    document.getElementById("addWaterForm").onsubmit = function () {
      const form = this;
      const value = parseInt(form.amount.value, 10);
      if (value < 0) {
        alert("Amount cannot be negative.");
        return;
      }
      fetch("/add_water", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: `amount=${encodeURIComponent(form.amount.value)}`,
      }).then(() => {
        closeModal();
        loadToday();
      });
    };
  }
  // Removed addExerciseModal
  const datePicker = document.getElementById("datePicker");
  let currentDate = null;

  // When you set the date picker value (on load or change), also update the title:
  function setDateAndTitle(dateStr) {
    if (datePicker) datePicker.value = dateStr;
    if (dateSpan) dateSpan.textContent = dateStr;
  }

  function updateTitleToPicker() {
    if (dateSpan && datePicker) dateSpan.textContent = datePicker.value;
  }

  // Always fetch backend's today on load
  fetch("/get_today_str")
    .then((res) => res.json())
    .then((obj) => {
      const todayStr = obj.today;
      if (datePicker) datePicker.value = todayStr;
      updateTitleToPicker();
      currentDate = null;
      loadToday();
    });

  // When the user changes the date:
  if (datePicker) {
    datePicker.addEventListener("change", function () {
      updateTitleToPicker();
      const date = datePicker.value;
      if (date) {
        currentDate = date;
        fetch(`/get_day?date=${date}`)
          .then((res) => res.json())
          .then((data) => {
            renderPlanner(data);
            updateTitleToPicker();
          });
      } else {
        // If cleared, reset to today
        fetch("/get_today_str")
          .then((res) => res.json())
          .then((obj) => {
            if (datePicker) datePicker.value = obj.today;
            updateTitleToPicker();
            currentDate = null;
            loadToday();
          });
      }
    });
  }

  function loadToday() {
    if (currentDate) {
      fetch(`/get_day?date=${currentDate}`)
        .then((res) => res.json())
        .then((data) => {
          renderPlanner(data);
          updateTitleToPicker();
        })
        .catch((err) => {
          console.error("Failed to load planner:", err);
          plannerContainer.textContent = "Failed to fetch plan.";
        });
    } else {
      fetch("/get_today_str")
        .then((res) => res.json())
        .then((obj) => {
          if (datePicker) datePicker.value = obj.today;
          updateTitleToPicker(); // <-- ensures header is in sync
          renderPlanner(null); // optionally clear planner while loading
          return fetch("/reload_today");
        })
        .then((res) => res.json())
        .then((data) => renderPlanner(data))
        .catch((err) => {
          console.error("Failed to load planner:", err);
          plannerContainer.textContent = "Failed to fetch today's plan.";
        });
    }
  }
  if (reloadBtn) reloadBtn.addEventListener("click", loadToday);
  if (addTaskBtn) addTaskBtn.addEventListener("click", addTaskModal);
  if (addGoalBtn) addGoalBtn.addEventListener("click", addGoalModal);
  if (addFoodBtn) addFoodBtn.addEventListener("click", addFoodModal);
  if (addWaterBtn) addWaterBtn.addEventListener("click", addWaterModal);
  // Removed addExerciseBtn event listener
  loadToday();

  const todayBtn = document.getElementById("todayBtn");
  if (todayBtn && datePicker) {
    todayBtn.addEventListener("click", function () {
      fetch("/get_today_str")
        .then((res) => res.json())
        .then((obj) => {
          if (datePicker) datePicker.value = obj.today;
          updateTitleToPicker();
          currentDate = null;
          loadToday();
        });
    });
  }
});
