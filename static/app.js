let allTasks = [];

const priorityWeight = {
    high: 3,
    medium: 2,
    low: 1
};

function updateStats(tasks) {
    const total = tasks.length;
    const done = tasks.filter(task => task.status === "done").length;
    const todo = total - done;

    document.getElementById("todo-count").textContent = todo;
    document.getElementById("done-count").textContent = done;
    document.getElementById("total-count").textContent = total;
}

function updateNextBestAction(tasks) {
    const todoTasks = tasks
        .filter(task => task.status !== "done")
        .sort((a, b) => {
            const priorityDifference =
                priorityWeight[b.priority] - priorityWeight[a.priority];

            if (priorityDifference !== 0) {
                return priorityDifference;
            }

            return new Date(a.created_at) - new Date(b.created_at);
        });

    const title = document.getElementById("next-action-title");
    const meta = document.getElementById("next-action-meta");

    if (todoTasks.length === 0) {
        title.textContent = "Nessun task attivo";
        meta.textContent = "Crea un nuovo task per continuare.";
        return;
    }

    const nextTask = todoTasks[0];

    title.textContent = nextTask.title;
    meta.textContent =
        `${nextTask.project} · ${nextTask.priority} priority`;
}

function renderProjects(tasks) {
    const container = document.getElementById("projects");
    const projects = {};

    tasks.forEach(task => {
        if (!projects[task.project]) {
            projects[task.project] = {
                total: 0,
                done: 0
            };
        }

        projects[task.project].total += 1;

        if (task.status === "done") {
            projects[task.project].done += 1;
        }
    });

    const names = Object.keys(projects).sort();
    container.innerHTML = "";

    if (names.length === 0) {
        container.innerHTML = "<p>Nessun progetto presente.</p>";
        return;
    }

    names.forEach(name => {
        const stats = projects[name];
        const progress = Math.round(
            (stats.done / stats.total) * 100
        );

        const card = document.createElement("div");
        card.className = "project-card";

        card.innerHTML = `
            <div class="project-title">${name}</div>
            <div class="project-meta">
                ${stats.done}/${stats.total} done · ${progress}%
            </div>
            <div class="progress-track">
                <div class="progress-fill" style="width: ${progress}%"></div>
            </div>
        `;

        card.addEventListener("click", () => {
            document.getElementById("filter-project").value = name;
            applyFilters();
        });

        container.appendChild(card);
    });
}

function getFilteredTasks() {
    const status = document.getElementById("filter-status").value;
    const priority = document.getElementById("filter-priority").value;
    const project = document.getElementById("filter-project").value.trim().toLowerCase();

    return allTasks.filter(task => {
        const statusMatches = status === "all" || task.status === status;
        const priorityMatches = priority === "all" || task.priority === priority;
        const projectMatches =
            !project || task.project.toLowerCase().includes(project);

        return statusMatches && priorityMatches && projectMatches;
    });
}

function sortTasks(tasks) {
    const sortMode = document.getElementById("sort-tasks").value;
    const sorted = [...tasks];

    if (sortMode === "priority") {
        sorted.sort((a, b) => {
            const statusDifference =
                (a.status === "done") - (b.status === "done");

            if (statusDifference !== 0) {
                return statusDifference;
            }

            return priorityWeight[b.priority] - priorityWeight[a.priority];
        });
    }

    if (sortMode === "newest") {
        sorted.sort(
            (a, b) => new Date(b.created_at) - new Date(a.created_at)
        );
    }

    if (sortMode === "oldest") {
        sorted.sort(
            (a, b) => new Date(a.created_at) - new Date(b.created_at)
        );
    }

    if (sortMode === "project") {
        sorted.sort((a, b) =>
            a.project.localeCompare(b.project)
        );
    }

    return sorted;
}

function renderTasks(tasks) {
    const container = document.getElementById("tasks");
    container.innerHTML = "";

    if (tasks.length === 0) {
        container.innerHTML =
            "<p>Nessun task corrisponde ai filtri.</p>";
        return;
    }

    tasks.forEach(task => {
        const div = document.createElement("div");
        const priorityClass = `priority-${task.priority}`;
        const doneClass = task.status === "done" ? "done" : "";

        div.className = `task ${priorityClass} ${doneClass}`;

        div.innerHTML = `
            <div class="task-title">${task.title}</div>
            <div class="task-meta">
                Project: ${task.project}<br>
                Priority: <span class="priority-label">${task.priority}</span><br>
                Status: ${task.status}<br>
                Created: ${task.created_at}
            </div>
            <div class="task-actions">
                <button onclick="completeTask(${task.id})">Done</button>
                <button onclick="deleteTask(${task.id})">Delete</button>
            </div>
        `;

        container.appendChild(div);
    });
}

function renderActivity(items) {
    const container = document.getElementById("activity-log");
    container.innerHTML = "";

    if (items.length === 0) {
        container.innerHTML = "<p>Nessuna attività registrata.</p>";
        return;
    }

    items.forEach(item => {
        const div = document.createElement("div");
        div.className = "activity-item";

        div.innerHTML = `
            <span class="activity-action ${item.action}">
                ${item.action}
            </span>
            <span class="activity-main">
                ${item.task_title} · ${item.project}
            </span>
            <span class="activity-time">
                ${item.created_at}
            </span>
        `;

        container.appendChild(div);
    });
}

function applyFilters() {
    const filtered = getFilteredTasks();
    const sorted = sortTasks(filtered);
    renderTasks(sorted);
}

async function loadTasks() {
    const response = await fetch("/api/tasks");
    allTasks = await response.json();

    updateStats(allTasks);
    updateNextBestAction(allTasks);
    renderProjects(allTasks);
    applyFilters();
}

async function loadActivity() {
    const response = await fetch("/api/activity?limit=15");
    const activity = await response.json();
    renderActivity(activity);
}

async function refreshDashboard() {
    await Promise.all([
        loadTasks(),
        loadActivity()
    ]);
}

async function createTask() {
    const title = document.getElementById("task-title").value;
    const priority = document.getElementById("task-priority").value;
    const project = document.getElementById("task-project").value;

    if (!title.trim()) {
        alert("Inserisci un titolo");
        return;
    }

    const response = await fetch("/api/tasks", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title, priority, project })
    });

    if (!response.ok) {
        alert("Errore nella creazione del task");
        return;
    }

    document.getElementById("task-title").value = "";
    await refreshDashboard();
}

async function completeTask(taskId) {
    const response = await fetch(`/api/tasks/${taskId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: "done" })
    });

    if (!response.ok) {
        alert("Errore nell'aggiornamento del task");
        return;
    }

    await refreshDashboard();
}

async function deleteTask(taskId) {
    const response = await fetch(`/api/tasks/${taskId}`, {
        method: "DELETE"
    });

    if (!response.ok) {
        alert("Errore nell'eliminazione del task");
        return;
    }

    await refreshDashboard();
}

document.getElementById("create-task-button")
    .addEventListener("click", createTask);

document.getElementById("filter-status")
    .addEventListener("change", applyFilters);

document.getElementById("filter-priority")
    .addEventListener("change", applyFilters);

document.getElementById("filter-project")
    .addEventListener("input", applyFilters);

document.getElementById("sort-tasks")
    .addEventListener("change", applyFilters);

document.getElementById("clear-project-filter")
    .addEventListener("click", () => {
        document.getElementById("filter-project").value = "";
        applyFilters();
    });

refreshDashboard();
