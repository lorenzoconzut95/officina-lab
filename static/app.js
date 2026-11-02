async function loadTasks() {
    const response = await fetch("/api/tasks");
    const tasks = await response.json();

    const container = document.getElementById("tasks");

    container.innerHTML = "";

    if (tasks.length === 0) {
        container.innerHTML = "<p>Nessun task presente.</p>";
        return;
    }

    tasks.forEach(task => {
        const div = document.createElement("div");
        div.className = "task";

        div.innerHTML = `
            <div class="task-title">
                ${task.title}
            </div>

            <div class="task-meta">
                Project: ${task.project}<br>
                Priority: ${task.priority}<br>
                Status: ${task.status}<br>
                Created: ${task.created_at}
            </div>
        `;

        container.appendChild(div);
    });
}

loadTasks();
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
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            title: title,
            priority: priority,
            project: project
        })
    });

    if (!response.ok) {
        alert("Errore nella creazione del task");
        return;
    }

    document.getElementById("task-title").value = "";

    await loadTasks();
}


document
    .getElementById("create-task-button")
    .addEventListener("click", createTask);