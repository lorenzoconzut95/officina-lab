let allTasks = [];
let allAgents = [];
let allRuns = [];
let allMemories = [];
let allApprovals = [];
let allToolCalls = [];
let allErrors = [];
let allIncidents = [];

const priorityWeight = { high: 3, medium: 2, low: 1 };

function updateStats(tasks) {
  const total = tasks.length;
  const done = tasks.filter(t => t.status === "done").length;
  document.getElementById("todo-count").textContent = total - done;
  document.getElementById("done-count").textContent = done;
  document.getElementById("total-count").textContent = total;
}

function updateRunStats(runs) {
  const running = runs.filter(r => r.status === "running").length;
  const completed = runs.filter(r => r.status === "completed").length;
  const tokens = runs.reduce((sum,r) => sum + (r.tokens_in || 0) + (r.tokens_out || 0), 0);
  const cost = runs.reduce((sum,r) => sum + Number(r.cost_usd || 0), 0);

  document.getElementById("running-count").textContent = running;
  document.getElementById("completed-count").textContent = completed;
  document.getElementById("token-count").textContent = tokens.toLocaleString();
  document.getElementById("cost-total").textContent = "$" + cost.toFixed(4);
}

function updateNextBestAction(tasks) {
  const todo = [...tasks]
    .filter(t => t.status !== "done")
    .sort((a,b) => priorityWeight[b.priority] - priorityWeight[a.priority] || new Date(a.created_at) - new Date(b.created_at));

  const title = document.getElementById("next-action-title");
  const meta = document.getElementById("next-action-meta");

  if (!todo.length) {
    title.textContent = "Nessun task attivo";
    meta.textContent = "Crea un nuovo task per continuare.";
    return;
  }

  title.textContent = todo[0].title;
  meta.textContent = todo[0].project + " · " + todo[0].priority + " priority";
}

function renderProjects(tasks) {
  const c = document.getElementById("projects");
  const projects = {};

  tasks.forEach(t => {
    if (!projects[t.project]) projects[t.project] = { total: 0, done: 0 };
    projects[t.project].total += 1;
    if (t.status === "done") projects[t.project].done += 1;
  });

  c.innerHTML = "";

  Object.keys(projects).sort().forEach(name => {
    const s = projects[name];
    const progress = Math.round((s.done / s.total) * 100);
    const card = document.createElement("div");
    card.className = "project-card";
    card.innerHTML =
      '<div class="project-title">' + name + '</div>' +
      '<div class="project-meta">' + s.done + '/' + s.total + ' done · ' + progress + '%</div>' +
      '<div class="progress-track"><div class="progress-fill" style="width:' + progress + '%"></div></div>';

    card.onclick = () => {
      document.getElementById("filter-project").value = name;
      applyFilters();
    };

    c.appendChild(card);
  });
}

function renderAgents(agents) {
  const c = document.getElementById("agents");
  document.getElementById("agent-count").textContent = agents.length + " agents";
  c.innerHTML = "";

  if (!agents.length) {
    c.innerHTML = "<p>Nessun agente creato.</p>";
    return;
  }

  agents.forEach(a => {
    const card = document.createElement("div");
    card.className = "agent-card";
    card.innerHTML =
      '<div class="agent-name">' + a.name + '</div>' +
      '<div class="agent-meta">' + a.role +
      '<br>Goal: ' + (a.goal || 'No goal set') +
      '<br>' + a.project + '</div>' +
      '<span class="agent-status">' + a.status + '</span>' +
      '<div class="agent-actions">' +
      '<button onclick="editAgent(' + a.id + ')">Edit Agent</button>' +
      '<button onclick="setAgentStatus(' + a.id + ',\'working\')">Working</button>' +
      '<button onclick="setAgentStatus(' + a.id + ',\'idle\')">Idle</button>' +
      '</div>';
    c.appendChild(card);
  });
}

function fillRunAgentSelect() {
  const select = document.getElementById("run-agent");
  select.innerHTML = "";

  allAgents.forEach(a => {
    const option = document.createElement("option");
    option.value = a.id;
    option.textContent =
      "#" + a.id + " · " +
      a.name + " · " +
      a.role + " · " +
      (a.goal ? "goal ✓" : "goal —");
    select.appendChild(option);
  });
}

function renderMemories(memories) {
  const c = document.getElementById("memories");
  document.getElementById("memory-count").textContent = memories.length + " memories";
  c.innerHTML = "";

  if (!memories.length) {
    c.innerHTML = "<p>Nessuna memoria salvata.</p>";
    return;
  }

  memories.forEach(m => {
    const card = document.createElement("div");
    card.className = "memory-card";
    card.innerHTML =
      '<div class="memory-type">' + m.memory_type + '</div>' +
      '<div class="memory-content">' + m.content + '</div>' +
      '<div class="memory-meta">' + m.project + ' · ' + m.created_at + '</div>';
    c.appendChild(card);
  });
}

function renderApprovals(approvals) {
  const c = document.getElementById("approvals");
  const pending = approvals.filter(a => a.status === "pending");

  document.getElementById("approval-count").textContent =
    pending.length + " pending";

  c.innerHTML = "";

  if (!approvals.length) {
    c.innerHTML = "<p>Nessuna approval richiesta.</p>";
    return;
  }

  approvals.forEach(a => {
    const card = document.createElement("div");
    card.className = "approval-card";

    const payload = JSON.stringify(
      a.payload,
      null,
      2
    );

    let actions = "";

    if (a.status === "pending") {
      actions =
        '<div class="approval-actions">' +
        '<button onclick="approveRequest(' + a.id + ')">Approve</button>' +
        '<button onclick="rejectRequest(' + a.id + ')">Reject</button>' +
        '</div>';
    }

    card.innerHTML =
      '<div class="approval-title">' + a.action + '</div>' +
      '<div class="approval-meta">Agent: ' + a.agent_name +
      (a.run_id ? ' · Run: ' + a.run_id : '') +
      '<br>Created: ' + a.created_at + '</div>' +
      '<div class="approval-payload">' + payload + '</div>' +
      '<span class="approval-status ' + a.status + '">' + a.status + '</span>' +
      actions;

    c.appendChild(card);
  });
}

function renderIncidents(items) {
  const c = document.getElementById("incidents");
  document.getElementById("incident-count").textContent =
    items.length + " incidents";

  c.innerHTML = "";

  if (!items.length) {
    c.innerHTML = "<p>Nessun incidente raggruppato.</p>";
    return;
  }

  items.forEach(item => {
    const card = document.createElement("div");
    card.className =
      "incident-card severity-" + item.severity;

    card.innerHTML =
      '<div class="incident-title">' + item.incident_key + '</div>' +
      '<div class="incident-meta">' +
      'Status: ' + item.status +
      ' · Severity: ' + item.severity +
      ' · Occurrences: ' + item.occurrences +
      '<br>Latest run: #' + item.latest_run_id +
      ' · Agent: ' + item.latest_agent_name +
      '<br>' + item.latest_created_at +
      '</div>' +
      '<div class="incident-message">' +
      item.latest_error_message +
      '</div>';

    const actions = document.createElement("div");
    actions.className = "run-actions";

    const button = document.createElement("button");
    button.type = "button";
    button.textContent = "Analyze with Bug Hunter";
    button.addEventListener("click", () => {
      analyzeIncidentWithBugHunter(item.id);
    });

    actions.appendChild(button);

    if (item.status !== "investigating") {
      const investigatingButton = document.createElement("button");
      investigatingButton.type = "button";
      investigatingButton.textContent = "Investigating";
      investigatingButton.addEventListener("click", () => {
        setIncidentStatus(item.id, "investigating");
      });
      actions.appendChild(investigatingButton);
    }

    if (item.status !== "resolved") {
      const resolveButton = document.createElement("button");
      resolveButton.type = "button";
      resolveButton.textContent = "Resolve";
      resolveButton.addEventListener("click", () => {
        setIncidentStatus(item.id, "resolved");
      });
      actions.appendChild(resolveButton);
    }

    card.appendChild(actions);
    c.appendChild(card);
  });
}

function renderErrors(items) {
  const c = document.getElementById("error-log");
  document.getElementById("error-count").textContent =
    items.length + " errors";

  c.innerHTML = "";

  if (!items.length) {
    c.innerHTML = "<p>Nessun errore registrato.</p>";
    return;
  }

  items.forEach(item => {
    const card = document.createElement("div");
    card.className = "error-card";

    card.innerHTML =
      '<div class="error-title">Run #' + item.run_id + ' failed</div>' +
      '<div class="error-meta">Agent: ' + item.agent_name +
      '<br>Task: ' + item.task +
      '<br>' + item.created_at + '</div>' +
      '<div class="error-message">' + item.error_message + '</div>';

    const actions = document.createElement("div");
    actions.className = "run-actions";

    const button = document.createElement("button");
    button.type = "button";
    button.textContent = "Analyze with Bug Hunter";
    button.addEventListener("click", () => {
      analyzeErrorWithBugHunter(item);
    });

    actions.appendChild(button);
    card.appendChild(actions);
    c.appendChild(card);
  });
}

function renderToolCalls(items) {
  const c = document.getElementById("tool-calls");
  document.getElementById("tool-call-count").textContent =
    items.length + " calls";

  c.innerHTML = "";

  if (!items.length) {
    c.innerHTML = "<p>Nessuna tool call registrata.</p>";
    return;
  }

  items.forEach(item => {
    const card = document.createElement("div");
    card.className = "tool-call-card";

    card.innerHTML =
      '<div class="tool-call-name">' + item.tool_name + '</div>' +
      '<div class="tool-call-meta">Agent: ' + item.agent_name +
      (item.run_id ? ' · Run: ' + item.run_id : '') +
      '<br>' + item.created_at + '</div>' +
      '<div class="tool-call-json">Args:\n' +
      JSON.stringify(item.arguments, null, 2) +
      '\n\nResult:\n' +
      JSON.stringify(item.result, null, 2) +
      '</div>';

    c.appendChild(card);
  });
}

function renderRuns(runs) {
  const c = document.getElementById("runs");
  document.getElementById("run-count").textContent = runs.length + " runs";
  c.innerHTML = "";

  if (!runs.length) {
    c.innerHTML = "<p>Nessuna esecuzione registrata.</p>";
    return;
  }

  runs.forEach(r => {
    const card = document.createElement("div");
    card.className = "run-card";

    let html =
      '<div class="run-title">' + r.agent_name + '</div>' +
      '<div class="run-meta">' + r.task + '<br>Started: ' + r.started_at;

    if (r.ended_at) html += '<br>Ended: ' + r.ended_at;

    html += '</div><span class="run-status ' + r.status + '">' + r.status + '</span>';

    const totalTokens = (r.tokens_in || 0) + (r.tokens_out || 0);

    html +=
      '<div class="run-metrics">' +
      'Tokens: ' + totalTokens.toLocaleString() +
      ' · Cost: $' + Number(r.cost_usd || 0).toFixed(4) +
      (r.duration_seconds != null ? ' · Duration: ' + r.duration_seconds + 's' : '') +
      (r.model ? ' · Model: ' + r.model : '') +
      '</div>';

    if (r.context_sources) {
      let sources = [];
      try {
        sources = JSON.parse(r.context_sources);
      } catch (error) {
        sources = [r.context_sources];
      }

      html += '<div class="run-metrics">Context: ' + sources.join(' · ') + '</div>';
    }

    if (r.output) html += '<div class="run-output">' + r.output + '</div>';

    if (r.status === "running") {
      html +=
        '<div class="run-actions">' +
        '<button onclick="executeRun(' + r.id + ')">Execute</button>' +
        '<button onclick="finishRun(' + r.id + ',\'completed\')">Complete</button>' +
        '<button onclick="finishRun(' + r.id + ',\'failed\')">Fail</button>' +
        '</div>';
    }

    if (
      r.status === "completed" &&
      r.output &&
      r.agent_name.toLowerCase() === "explorer"
    ) {
      html +=
        '<div class="run-actions">' +
        '<button onclick="handoffToBuilder(' + r.id + ')">Handoff to Builder</button>' +
        '</div>';
    }

    card.innerHTML = html;
    c.appendChild(card);
  });
}

function getFilteredTasks() {
  const status = document.getElementById("filter-status").value;
  const priority = document.getElementById("filter-priority").value;
  const project = document.getElementById("filter-project").value.trim().toLowerCase();

  return allTasks.filter(t =>
    (status === "all" || t.status === status) &&
    (priority === "all" || t.priority === priority) &&
    (!project || t.project.toLowerCase().includes(project))
  );
}

function sortTasks(tasks) {
  const mode = document.getElementById("sort-tasks").value;
  const s = [...tasks];

  if (mode === "priority") {
    s.sort((a,b) => (a.status === "done") - (b.status === "done") || priorityWeight[b.priority] - priorityWeight[a.priority]);
  }
  if (mode === "newest") s.sort((a,b) => new Date(b.created_at) - new Date(a.created_at));
  if (mode === "oldest") s.sort((a,b) => new Date(a.created_at) - new Date(b.created_at));
  if (mode === "project") s.sort((a,b) => a.project.localeCompare(b.project));

  return s;
}

function renderTasks(tasks) {
  const c = document.getElementById("tasks");
  c.innerHTML = "";

  if (!tasks.length) {
    c.innerHTML = "<p>Nessun task corrisponde ai filtri.</p>";
    return;
  }

  tasks.forEach(t => {
    const d = document.createElement("div");
    d.className = "task priority-" + t.priority + " " + (t.status === "done" ? "done" : "");
    d.innerHTML =
      '<div class="task-title">' + t.title + '</div>' +
      '<div class="task-meta">Project: ' + t.project +
      '<br>Priority: <span class="priority-label">' + t.priority + '</span>' +
      '<br>Status: ' + t.status +
      '<br>Created: ' + t.created_at + '</div>' +
      '<div class="task-actions">' +
      '<button onclick="completeTask(' + t.id + ')">Done</button>' +
      '<button onclick="deleteTask(' + t.id + ')">Delete</button>' +
      '</div>';
    c.appendChild(d);
  });
}

function renderActivity(items) {
  const c = document.getElementById("activity-log");
  c.innerHTML = "";

  if (!items.length) {
    c.innerHTML = "<p>Nessuna attività registrata.</p>";
    return;
  }

  items.forEach(i => {
    const d = document.createElement("div");
    d.className = "activity-item";
    d.innerHTML =
      '<span class="activity-action ' + i.action + '">' + i.action + '</span>' +
      '<span class="activity-main">' + i.task_title + ' · ' + i.project + '</span>' +
      '<span class="activity-time">' + i.created_at + '</span>';
    c.appendChild(d);
  });
}

function applyFilters() {
  renderTasks(sortTasks(getFilteredTasks()));
}

async function loadTasks() {
  const r = await fetch("/api/tasks");
  allTasks = await r.json();
  updateStats(allTasks);
  updateNextBestAction(allTasks);
  renderProjects(allTasks);
  applyFilters();
}

async function loadAgents() {
  const r = await fetch("/api/agents");
  allAgents = await r.json();
  renderAgents(allAgents);
  fillRunAgentSelect();
}

async function loadRuns() {
  const r = await fetch("/api/runs");
  allRuns = await r.json();
  updateRunStats(allRuns);
  renderRuns(allRuns);
}

async function loadMemories() {
  const r = await fetch("/api/memories?limit=20");
  allMemories = await r.json();
  renderMemories(allMemories);
}

async function loadApprovals() {
  const r = await fetch("/api/approvals");
  allApprovals = await r.json();
  renderApprovals(allApprovals);
}

async function loadIncidents() {
  const r = await fetch("/api/incidents?limit=50");
  allIncidents = await r.json();
  renderIncidents(allIncidents);
}

async function loadErrors() {
  const r = await fetch("/api/errors?limit=30");
  allErrors = await r.json();
  renderErrors(allErrors);
}

async function loadToolCalls() {
  const r = await fetch("/api/tool-calls?limit=30");
  allToolCalls = await r.json();
  renderToolCalls(allToolCalls);
}

async function loadActivity() {
  const r = await fetch("/api/activity?limit=15");
  renderActivity(await r.json());
}

async function refreshDashboard() {
  await Promise.all([
    loadTasks(),
    loadAgents(),
    loadRuns(),
    loadMemories(),
    loadApprovals(),
    loadIncidents(),
    loadErrors(),
    loadToolCalls(),
    loadActivity()
  ]);
}

async function createTask() {
  const title = document.getElementById("task-title").value;
  const priority = document.getElementById("task-priority").value;
  const project = document.getElementById("task-project").value;

  if (!title.trim()) return alert("Inserisci un titolo");

  const r = await fetch("/api/tasks", {
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify({title,priority,project})
  });

  if (!r.ok) return alert("Errore nella creazione del task");
  document.getElementById("task-title").value = "";
  await refreshDashboard();
}

async function completeTask(id) {
  const r = await fetch("/api/tasks/" + id, {
    method:"PATCH",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify({status:"done"})
  });

  if (!r.ok) return alert("Errore nell'aggiornamento del task");
  await refreshDashboard();
}

async function deleteTask(id) {
  const r = await fetch("/api/tasks/" + id, {method:"DELETE"});
  if (!r.ok) return alert("Errore nell'eliminazione del task");
  await refreshDashboard();
}

async function createAgent() {
  const name = document.getElementById("agent-name").value;
  const role = document.getElementById("agent-role").value;
  const goal = document.getElementById("agent-goal").value;
  const project = document.getElementById("agent-project").value;

  if (!name.trim() || !role.trim()) return alert("Inserisci nome e ruolo dell'agente");

  const r = await fetch("/api/agents", {
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify({name,role,goal,project})
  });

  if (!r.ok) return alert("Errore nella creazione dell'agente");
  document.getElementById("agent-name").value = "";
  document.getElementById("agent-role").value = "";
  document.getElementById("agent-goal").value = "";
  await loadAgents();
}

async function editAgent(id) {
  const agent = allAgents.find(a => a.id === id);
  if (!agent) return;

  const name = prompt("Agent name:", agent.name);
  if (name === null) return;

  const role = prompt("Role:", agent.role);
  if (role === null) return;

  const goal = prompt("Goal:", agent.goal || "");
  if (goal === null) return;

  const project = prompt("Project:", agent.project);
  if (project === null) return;

  const r = await fetch("/api/agents/" + id, {
    method:"PATCH",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify({name,role,goal,project})
  });

  if (!r.ok) return alert("Errore nell'aggiornamento dell'agente");

  await loadAgents();
}

async function setAgentStatus(id,status) {
  const r = await fetch("/api/agents/" + id + "/status", {
    method:"PATCH",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify({status})
  });

  if (!r.ok) return alert("Errore nell'aggiornamento dell'agente");
  await loadAgents();
}

async function createMemory() {
  const content = document.getElementById("memory-content").value;
  const project = document.getElementById("memory-project").value;
  const memoryType = document.getElementById("memory-type").value;

  if (!content.trim()) return alert("Scrivi qualcosa da ricordare");

  const r = await fetch("/api/memories", {
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify({
      content,
      project,
      memory_type:memoryType
    })
  });

  if (!r.ok) return alert("Errore nel salvataggio della memoria");
  document.getElementById("memory-content").value = "";
  await loadMemories();
}

async function approveRequest(id) {
  const r = await fetch(
    "/api/approvals/" + id + "/approve",
    { method: "POST" }
  );

  if (!r.ok) return alert("Errore nell'approvazione");

  await Promise.all([
    loadApprovals(),
    loadTasks(),
    loadMemories(),
    loadToolCalls(),
    loadActivity()
  ]);
}

async function rejectRequest(id) {
  const r = await fetch(
    "/api/approvals/" + id + "/reject",
    { method: "POST" }
  );

  if (!r.ok) return alert("Errore nel rifiuto");

  await loadApprovals();
}

async function startRun() {
  if (!allAgents.length) return alert("Crea prima un agente");

  const agentId = Number(document.getElementById("run-agent").value);
  const task = document.getElementById("run-task").value;

  if (!task.trim()) return alert("Inserisci il task del run");

  const r = await fetch("/api/runs", {
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify({agent_id:agentId,task})
  });

  if (!r.ok) return alert("Errore nell'avvio del run");
  document.getElementById("run-task").value = "";
  await Promise.all([
    loadRuns(),
    loadAgents(),
    loadApprovals(),
    loadToolCalls()
  ]);
}

async function executeRun(id) {
  const r = await fetch("/api/runs/" + id + "/execute", {method:"POST"});
  if (!r.ok) return alert("Errore nell'esecuzione dell'agente");
  await Promise.all([
    loadRuns(),
    loadAgents(),
    loadIncidents(),
    loadErrors()
  ]);
}

async function setIncidentStatus(incidentId, status) {
  const r = await fetch(
    "/api/incidents/" + incidentId + "/status?status=" + encodeURIComponent(status),
    { method:"PATCH" }
  );

  if (!r.ok) {
    return alert("Errore nell'aggiornamento dell'incidente");
  }

  await loadIncidents();
}

async function analyzeErrorWithBugHunter(errorItem) {
  const bugHunter = allAgents.find(agent =>
    agent.name.toLowerCase().replace(/\s+/g, " ").includes("bug hunter") ||
    agent.role.toLowerCase().includes("debug")
  );

  if (!bugHunter) {
    return alert("Crea prima l'agente Bug Hunter");
  }

  const task =
    "Analizza questo errore reale di Officina Lab.\n\n" +
    "Run: #" + errorItem.run_id + "\n" +
    "Agent: " + errorItem.agent_name + "\n" +
    "Task: " + errorItem.task + "\n" +
    "Created at: " + errorItem.created_at + "\n" +
    "Error:\n" + errorItem.error_message + "\n\n" +
    "Usa list_recent_errors e, se serve, list_project_files e " +
    "read_project_file. Separa evidenze da ipotesi. Restituisci: " +
    "sintomo, evidenza, causa probabile, confidenza, test minimo e " +
    "fix più piccolo. Non modificare nulla senza approval.";

  const r = await fetch("/api/runs", {
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify({
      agent_id:bugHunter.id,
      task:task
    })
  });

  if (!r.ok) {
    return alert("Errore nella creazione del run Bug Hunter");
  }

  await Promise.all([
    loadRuns(),
    loadAgents()
  ]);
}

async function analyzeIncidentWithBugHunter(incidentId) {
  const incident = allIncidents.find(
    item => item.id === incidentId
  );

  if (!incident) {
    return alert("Incidente non trovato");
  }

  const bugHunter = allAgents.find(agent =>
    agent.name.toLowerCase().replace(/\s+/g, " ").includes("bug hunter") ||
    agent.role.toLowerCase().includes("debug")
  );

  if (!bugHunter) {
    return alert("Crea prima l'agente Bug Hunter");
  }

  const task =
    "Analizza questo incidente reale di Officina Lab.\n\n" +
    "Incident key: " + incident.incident_key + "\n" +
    "Status: " + incident.status + "\n" +
    "Severity: " + incident.severity + "\n" +
    "Occurrences: " + incident.occurrences + "\n" +
    "Latest run: #" + incident.latest_run_id + "\n" +
    "Latest agent: " + incident.latest_agent_name + "\n" +
    "Latest task: " + incident.latest_task + "\n" +
    "Latest error:\n" + incident.latest_error_message + "\n\n" +
    "Usa list_recent_errors e, se serve, list_project_files e " +
    "read_project_file. Separa evidenze da ipotesi. Restituisci: " +
    "sintomo, evidenza, causa probabile, confidenza, test minimo e " +
    "fix più piccolo. Non modificare nulla senza approval.";

  const r = await fetch("/api/runs", {
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify({
      agent_id:bugHunter.id,
      task:task
    })
  });

  if (!r.ok) {
    return alert("Errore nella creazione del run Bug Hunter");
  }

  await Promise.all([
    loadRuns(),
    loadAgents()
  ]);
}

async function handoffToBuilder(runId) {
  const r = await fetch(
    "/api/runs/" + runId + "/handoff-builder",
    { method:"POST" }
  );

  if (!r.ok) {
    const error = await r.json();
    return alert(
      "Errore nell'handoff: " +
      (error.detail || "errore sconosciuto")
    );
  }

  await Promise.all([
    loadRuns(),
    loadAgents()
  ]);
}

async function finishRun(id,status) {
  const output = prompt("Output del run:","Run completato.");
  if (output === null) return;

  const tokensIn = Number(prompt("Token input:", "0") || 0);
  const tokensOut = Number(prompt("Token output:", "0") || 0);
  const costUsd = Number(prompt("Costo USD:", "0") || 0);

  const r = await fetch("/api/runs/" + id + "/finish", {
    method:"PATCH",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify({
      status,
      output,
      tokens_in:tokensIn,
      tokens_out:tokensOut,
      cost_usd:costUsd
    })
  });

  if (!r.ok) return alert("Errore nella chiusura del run");
  await Promise.all([loadRuns(),loadAgents()]);
}

document.getElementById("create-task-button").onclick = createTask;
document.getElementById("create-agent-button").onclick = createAgent;
document.getElementById("create-memory-button").onclick = createMemory;
document.getElementById("start-run-button").onclick = startRun;
document.getElementById("filter-status").onchange = applyFilters;
document.getElementById("filter-priority").onchange = applyFilters;
document.getElementById("filter-project").oninput = applyFilters;
document.getElementById("sort-tasks").onchange = applyFilters;
document.getElementById("clear-project-filter").onclick = () => {
  document.getElementById("filter-project").value = "";
  applyFilters();
};

refreshDashboard();
