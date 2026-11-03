let allTasks = [];

function updateStats(tasks) {
    const total = tasks.length;
    const done = tasks.filter(task => task.status === "done").length;
    const todo = total - done;

    document.getElementById("todo-count").textContent = todo;
    document.getElementById("done-count").textContent = done;
    document.getElementById("total-count").textContent = total;
}

function getFilteredTasks() {
    const status = document.getElementById("filter-status").value;
    const priority = document.getElementById("filter-priority").value;
    const project = document.getElementById("filter-project").value.trim().toLowerCase();

    return allTasks.filter(task => {
        const statusMatches = status === "all" || task.status === status;
        const priorityMatches = priority === "all" || task.priority === priority;
        const projectMatches = !project || task.project.toLowerCase().includes(project);

        return statusMatches && priorityMatches && projectMatches;
    });
}

function renderTasks(tasks) {
    const container = document.getElementById("tasks");
    container.innerHTML = "";

    if (tasks.length === 0) {
        container.innerHTML = "<p>Nessun task corrisponde ai filtri.</p>";
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

function applyFilters() {
    renderTasks(getFilteredTasks());
}

async function loadTasks() {
    const response = await fetch("/api/tasks");
    allTasks = await response.json();

    updateStats(allTasks);
    applyFilters();
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
    await loadTasks();
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

    await loadTasks();
}

async function deleteTask(taskId) {
    const response = await fetch(`/api/tasks/${taskId}`, {
        method: "DELETE"
    });

    if (!response.ok) {
        alert("Errore nell'eliminazione del task");
        return;
    }

    await loadTasks();
}

document.getElementById("create-task-button").addEventListener("click", createTask);
document.getElementById("filter-status").addEventListener("change", applyFilters);
document.getElementById("filter-priority").addEventListener("change", applyFilters);
document.getElementById("filter-project").addEventListener("input", applyFilters);

loadTasks();
