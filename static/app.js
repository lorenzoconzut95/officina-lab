let allTasks = [];
let allAgents = [];
let allRuns = [];
let allMemories = [];
let allApprovals = [];
let allToolCalls = [];
let allErrors = [];
let allIncidents = [];
let incidentFilter = "open";
let selectedRunId = null;
const activeRunExecutions = new Set();

const priorityWeight = { high: 3, medium: 2, low: 1 };

function switchDashboardView(viewName, {scrollToTop = true} = {}) {
  document.querySelectorAll(".dashboard-view").forEach(view => {
    view.classList.toggle(
      "active",
      view.dataset.view === viewName
    );
  });

  document.querySelectorAll("[data-view-target]").forEach(button => {
    button.classList.toggle(
      "active",
      button.dataset.viewTarget === viewName
    );
  });

  if (scrollToTop) {
    window.scrollTo({top: 0, behavior: "smooth"});
  }
}

function updateIncidentNavBadge(items) {
  const badge = document.getElementById("nav-incident-badge");
  if (!badge) return;

  const active = items.filter(
    item => item.status !== "resolved"
  ).length;

  badge.textContent = active;
  badge.classList.toggle("empty", active === 0);
}

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
  const resolved = approvals.filter(a => a.status !== "pending");

  document.getElementById("approval-count").textContent =
    pending.length + " pending";

  c.innerHTML = "";

  if (!approvals.length) {
    c.innerHTML =
      '<div class="approval-empty">No approvals waiting. Officina will place protected actions here.</div>';
    return;
  }

  pending.forEach(a => {
    const card = document.createElement("article");
    card.className = "approval-card approval-card-pending";

    const p = a.payload || {};
    const isIncidentProposal = a.action === "incident_builder_proposal";

    if (isIncidentProposal) {
      card.innerHTML =
        '<div class="approval-card-top">' +
          '<div>' +
            '<span class="eyebrow">Decision required</span>' +
            '<div class="approval-title">Incident #' +
              (p.incident_id ?? "—") + ' · ' +
              (p.incident_key || "Builder proposal") +
            '</div>' +
          '</div>' +
          '<span class="approval-status pending">pending</span>' +
        '</div>' +
        '<div class="approval-summary-grid">' +
          '<div><span>Action</span><strong>' + (p.action_type || "n/a") + '</strong></div>' +
          '<div><span>Risk</span><strong>' + (p.risk || "n/a") + '</strong></div>' +
          '<div><span>Agent</span><strong>' + a.agent_name + '</strong></div>' +
          '<div><span>Run</span><strong>#' + (a.run_id || "—") + '</strong></div>' +
        '</div>' +
        '<div class="approval-block"><span>Target</span><p>' +
          (p.target || "Not specified") + '</p></div>' +
        '<div class="approval-block"><span>Why</span><p>' +
          (p.rationale || "Not specified") + '</p></div>' +
        '<div class="approval-block"><span>Proposed change</span><p>' +
          (p.change || "Not specified") + '</p></div>' +
        '<div class="approval-block"><span>Verification test</span><p>' +
          (p.test || "Not specified") + '</p></div>';
    } else {
      card.innerHTML =
        '<div class="approval-card-top">' +
          '<div>' +
            '<span class="eyebrow">Decision required</span>' +
            '<div class="approval-title">' + a.action + '</div>' +
          '</div>' +
          '<span class="approval-status pending">pending</span>' +
        '</div>' +
        '<div class="approval-meta">Agent: ' + a.agent_name +
          (a.run_id ? ' · Run #' + a.run_id : '') +
          ' · ' + a.created_at + '</div>' +
        '<details class="approval-raw">' +
          '<summary>Payload</summary>' +
          '<pre>' + JSON.stringify(p, null, 2) + '</pre>' +
        '</details>';
    }

    const actions = document.createElement("div");
    actions.className = "approval-actions";

    const approveButton = document.createElement("button");
    approveButton.type = "button";
    approveButton.className = "approval-approve";
    approveButton.textContent = "Approve";
    approveButton.addEventListener("click", () => approveRequest(a.id));

    const rejectButton = document.createElement("button");
    rejectButton.type = "button";
    rejectButton.className = "approval-reject";
    rejectButton.textContent = "Reject";
    rejectButton.addEventListener("click", () => rejectRequest(a.id));

    actions.appendChild(approveButton);
    actions.appendChild(rejectButton);
    card.appendChild(actions);
    c.appendChild(card);
  });

  if (resolved.length) {
    const history = document.createElement("details");
    history.className = "approval-history";

    const summary = document.createElement("summary");
    summary.textContent = "Decision history · " + resolved.length;
    history.appendChild(summary);

    const body = document.createElement("div");
    body.className = "approval-history-list";

    resolved.slice(0, 12).forEach(a => {
      const item = document.createElement("div");
      item.className = "approval-history-item";
      item.innerHTML =
        '<div><strong>' + a.action + '</strong>' +
        '<span>' + a.agent_name +
        (a.run_id ? ' · Run #' + a.run_id : '') +
        '</span></div>' +
        '<span class="approval-status ' + a.status + '">' + a.status + '</span>';
      body.appendChild(item);
    });

    history.appendChild(body);
    c.appendChild(history);
  }
}

function getVerificationState(run, structuredResult = null) {
  if (!run) {
    return {
      key: "not_started",
      label: "Verification not started",
      ready: false
    };
  }

  if (run.status === "running") {
    return {
      key: "running",
      label: "Verification running",
      ready: false
    };
  }

  if (run.status !== "completed") {
    return {
      key: "needs_action",
      label: "Verification failed",
      ready: false
    };
  }

  let verdict = structuredResult?.verdict || null;

  if (!verdict && run.output) {
    const match = run.output.match(/^VERDICT:\s*(verified|not_verified)\b/im);
    verdict = match ? match[1].toLowerCase() : null;
  }

  if (verdict === "verified") {
    return {
      key: "ready",
      label: "Ready to resolve",
      ready: true
    };
  }

  if (verdict === "not_verified") {
    return {
      key: "needs_action",
      label: "Needs action",
      ready: false
    };
  }

  return {
    key: "unknown",
    label: "Verification format invalid",
    ready: false
  };
}

function buildIncidentTimeline(item, analysisRun, builderRun, approval, verificationRun) {
  const steps = [];

  steps.push({
    label: "Error",
    state: "done",
    meta: item.latest_run_id ? ("Run #" + item.latest_run_id) : ""
  });

  let analysisState = "pending";
  if (analysisRun) {
    analysisState =
      analysisRun.status === "completed"
        ? "done"
        : analysisRun.status === "failed"
          ? "failed"
          : "active";
  }

  steps.push({
    label: "Bug Hunter",
    state: analysisState,
    meta: analysisRun ? ("#" + analysisRun.id) : ""
  });

  let builderState = "pending";
  if (builderRun) {
    builderState =
      builderRun.status === "completed"
        ? "done"
        : builderRun.status === "failed"
          ? "failed"
          : "active";
  }

  steps.push({
    label: "Builder",
    state: builderState,
    meta: builderRun ? ("#" + builderRun.id) : ""
  });

  let approvalState = "pending";
  if (approval) {
    approvalState =
      approval.status === "approved"
        ? "done"
        : approval.status === "rejected"
          ? "failed"
          : "active";
  }

  steps.push({
    label: "Approval",
    state: approvalState,
    meta: approval ? ("#" + approval.id) : ""
  });

  let verificationState = "pending";
  if (verificationRun) {
    verificationState =
      verificationRun.status === "completed"
        ? "done"
        : verificationRun.status === "failed"
          ? "failed"
          : "active";
  }

  steps.push({
    label: "Verification",
    state: verificationState,
    meta: verificationRun ? ("#" + verificationRun.id) : ""
  });

  steps.push({
    label: "Resolved",
    state: item.status === "resolved" ? "done" : "pending",
    meta: item.resolved_at || ""
  });

  return steps;
}

function renderIncidentTimeline(steps) {
  const timeline = document.createElement("div");
  timeline.className = "incident-timeline";

  steps.forEach((step, index) => {
    const item = document.createElement("div");
    item.className = "incident-timeline-step " + step.state;

    item.innerHTML =
      '<div class="incident-timeline-marker">' +
        '<span></span>' +
      '</div>' +
      '<div class="incident-timeline-content">' +
        '<strong>' + step.label + '</strong>' +
        (step.meta
          ? '<small>' + step.meta + '</small>'
          : '') +
      '</div>';

    timeline.appendChild(item);

    if (index < steps.length - 1) {
      const connector = document.createElement("div");
      connector.className =
        "incident-timeline-connector " +
        (
          step.state === "done"
            ? "done"
            : "pending"
        );
      timeline.appendChild(connector);
    }
  });

  return timeline;
}

function renderIncidents(items) {
  const c = document.getElementById("incidents");
  const visibleItems = incidentFilter === "all"
    ? items
    : items.filter(item => item.status === incidentFilter);

  document.getElementById("incident-count").textContent =
    visibleItems.length + " " + incidentFilter + " incidents";

  c.innerHTML = "";

  if (!visibleItems.length) {
    c.innerHTML = "<p>Nessun incidente in questa vista.</p>";
    return;
  }

  visibleItems.forEach(item => {
    const card = document.createElement("article");
    card.className =
      "incident-card severity-" + item.severity +
      " status-" + item.status;

    const analysisRun = item.analysis_run_id
      ? allRuns.find(run => run.id === item.analysis_run_id)
      : null;

    const builderRun = item.builder_run_id
      ? allRuns.find(run => run.id === item.builder_run_id)
      : null;

    const messagePreview = (item.latest_error_message || "")
      .replace(/\s+/g, " ")
      .slice(0, 160);

    const top = document.createElement("div");
    top.className = "incident-card-top";
    top.innerHTML =
      '<div>' +
      '<div class="incident-title">' + item.incident_key + '</div>' +
      '<div class="incident-meta">Incident #' + item.id +
      ' · Run #' + item.latest_run_id +
      ' · ' + item.latest_agent_name +
      ' · ' + item.occurrences + ' occurrence' +
      (item.occurrences === 1 ? '' : 's') +
      '</div>' +
      '</div>' +
      '<div class="incident-badges">' +
      '<span class="incident-badge status-' + item.status + '">' + item.status + '</span>' +
      '<span class="incident-badge severity-' + item.severity + '">' + item.severity + '</span>' +
      '</div>';

    card.appendChild(top);

    const preview = document.createElement("div");
    preview.className = "incident-preview";
    preview.textContent = messagePreview || "Nessun messaggio errore.";
    card.appendChild(preview);

    const approval = item.approval_id
      ? allApprovals.find(a => a.id === item.approval_id)
      : null;

    const verificationRun = item.verification_run_id
      ? allRuns.find(run => run.id === item.verification_run_id)
      : null;

    const verificationState = getVerificationState(verificationRun);

    const recommendation = document.createElement("div");
    recommendation.className =
      "incident-recommendation " + verificationState.key;
    recommendation.innerHTML =
      '<span class="incident-recommendation-dot"></span>' +
      '<strong>' + verificationState.label + '</strong>';

    if (
      verificationRun &&
      verificationRun.status === "completed" &&
      !verificationState.ready
    ) {
      recommendation.innerHTML +=
        '<span>Review verification output before resolving.</span>';
    }

    card.appendChild(recommendation);

    let analysisStatus = analysisRun?.status || "not started";
    if (analysisStatus === "running") {
      analysisStatus = analysisRun.execution_started_at ? "executing" : "run created";
    }

    const pipeline = document.createElement("div");
    pipeline.className = "incident-pipeline";
    pipeline.innerHTML =
      '<span>Analysis: ' +
      analysisStatus +
      '</span>' +
      '<span>Build proposal: ' +
      (builderRun ? builderRun.status : 'not started') +
      '</span>' +
      '<span>Decision: ' +
      (approval ? approval.status : 'not requested') +
      '</span>' +
      '<span>Verification: ' +
      (verificationRun ? verificationRun.status : 'not started') +
      '</span>';
    card.appendChild(pipeline);

    const actions = document.createElement("div");
    actions.className = "incident-primary-actions";

    const analyzeButton = document.createElement("button");
    analyzeButton.type = "button";
    analyzeButton.textContent = analysisRun ? "Re-analyze" : "Analyze";
    const analysisHelp = document.createElement("p");
    analysisHelp.id = "incident-analysis-help-" + item.id;
    analysisHelp.className = "incident-meta";
    analysisHelp.textContent = analysisRun
      ? "Re-analyze prepara una nuova run e la collega a questo incidente."
      : "Analyze prepara una run di Bug Hunter e la collega a questo incidente.";
    if (analysisStatus === "run created") {
      analysisHelp.textContent += " La run collegata è pronta: aprila e premi Execute per avviarla.";
    }
    analyzeButton.setAttribute("aria-describedby", analysisHelp.id);
    analyzeButton.addEventListener("click", () => {
      analyzeIncidentWithBugHunter(item.id);
    });
    actions.appendChild(analyzeButton);

    if (analysisRun) {
      const openAnalysisLink = createRunLink(analysisRun.id, "Open analysis run #" + analysisRun.id);
      openAnalysisLink.className = "incident-analysis-link";
      const arrow = document.createElement("span");
      arrow.textContent = "→";
      arrow.setAttribute("aria-hidden", "true");
      openAnalysisLink.appendChild(arrow);
      actions.appendChild(openAnalysisLink);
    }

    if (analysisRun && analysisRun.status === "completed") {
      const handoffButton = document.createElement("button");
      handoffButton.type = "button";
      handoffButton.textContent = "Handoff to Builder";
      handoffButton.addEventListener("click", () => {
        handoffIncidentToBuilder(item.id);
      });
      actions.appendChild(handoffButton);
    }

    if (builderRun) {
      const openBuilderButton = document.createElement("button");
      openBuilderButton.type = "button";
      openBuilderButton.textContent = "Open Builder run";
      openBuilderButton.addEventListener("click", () => {
        openRunWorkspace(builderRun.id);
      });
      actions.appendChild(openBuilderButton);
    }

    if (
      builderRun &&
      builderRun.status === "completed" &&
      !approval
    ) {
      const approvalButton = document.createElement("button");
      approvalButton.type = "button";
      approvalButton.textContent = "Request Approval";
      approvalButton.addEventListener("click", () => {
        requestIncidentApproval(item.id);
      });
      actions.appendChild(approvalButton);
    }

    if (
      approval &&
      approval.status === "approved" &&
      (!verificationRun || verificationRun.status === "completed")
    ) {
      const verifyButton = document.createElement("button");
      verifyButton.type = "button";
      verifyButton.textContent = verificationRun
        ? "Verify Again"
        : "Start Verification";
      verifyButton.addEventListener("click", () => {
        startIncidentVerification(item.id);
      });
      actions.appendChild(verifyButton);
    }

    const reportButton = document.createElement("button");
    reportButton.type = "button";
    reportButton.textContent = "Incident Report";
    reportButton.addEventListener("click", () => {
      viewIncidentReport(item.id, card);
    });
    actions.appendChild(reportButton);

    if (item.status !== "resolved") {
      const resolveButton = document.createElement("button");
      resolveButton.type = "button";
      resolveButton.textContent = verificationState.ready
        ? "Resolve incident"
        : "Resolve";
      resolveButton.className = verificationState.ready
        ? "resolve-ready"
        : "";
      resolveButton.addEventListener("click", () => {
        if (
          !verificationState.ready &&
          verificationRun &&
          verificationRun.status === "completed"
        ) {
          const proceed = confirm(
            "Verification does not mark this incident as VERIFIED. Resolve anyway?"
          );
          if (!proceed) return;
        }

        setIncidentStatus(item.id, "resolved");
      });
      actions.appendChild(resolveButton);
    }

    card.append(actions, analysisHelp);

    const details = document.createElement("details");
    details.className = "incident-details";
    details.innerHTML =
      '<summary>More details</summary>' +
      '<div class="incident-details-body">' +
      '<div><strong>Latest task</strong><br>' + item.latest_task + '</div>' +
      '<div><strong>Latest error</strong><br>' + item.latest_error_message + '</div>' +
      '<div><strong>Updated</strong><br>' + item.updated_at + '</div>' +
      '<details class="incident-technical-context">' +
      '<summary>Technical context</summary>' +
      '<pre>' + JSON.stringify({
        analysis_run_id:item.analysis_run_id,
        builder_run_id:item.builder_run_id,
        approval_id:item.approval_id,
        verification_run_id:item.verification_run_id
      }, null, 2) + '</pre>' +
      '</details>' +
      '</div>';

    const secondary = document.createElement("div");
    secondary.className = "incident-secondary-actions";

    if (item.status !== "investigating") {
      const investigatingButton = document.createElement("button");
      investigatingButton.type = "button";
      investigatingButton.textContent = "Mark investigating";
      investigatingButton.addEventListener("click", () => {
        setIncidentStatus(item.id, "investigating");
      });
      secondary.appendChild(investigatingButton);
    }

    const caseStudyButton = document.createElement("button");
    caseStudyButton.type = "button";
    caseStudyButton.textContent = "Generate Case Study";
    caseStudyButton.addEventListener("click", () => {
      generateIncidentCaseStudy(item.id, card);
    });
    secondary.appendChild(caseStudyButton);

    details.appendChild(secondary);
    card.appendChild(details);

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

function populateRunAgentFilter() {
  const select = document.getElementById("run-filter-agent");
  if (!select) return;

  const current = select.value || "all";
  const names = [...new Set(
    allRuns.map(run => run.agent_name).filter(Boolean)
  )].sort();

  select.innerHTML = '<option value="all">All agents</option>';

  names.forEach(name => {
    const option = document.createElement("option");
    option.value = name;
    option.textContent = name;
    select.appendChild(option);
  });

  select.value = names.includes(current) ? current : "all";
}

function getVisibleRuns(runs) {
  const status = document.getElementById("run-filter-status")?.value || "all";
  const agent = document.getElementById("run-filter-agent")?.value || "all";
  const search = (document.getElementById("run-search")?.value || "")
    .trim()
    .toLowerCase();

  return runs.filter(run => {
    const statusOk = status === "all" || runDisplayState(run) === status;
    const agentOk = agent === "all" || run.agent_name === agent;
    const haystack = (
      (run.task || "") + " " +
      (run.output || "") + " " +
      (run.agent_name || "")
    ).toLowerCase();
    const searchOk = !search || haystack.includes(search);
    return statusOk && agentOk && searchOk;
  });
}

function runDisplayState(run) {
  if (run.status !== "running") return run.status;
  return run.execution_claimed_at || run.execution_started_at || activeRunExecutions.has(run.id)
    ? "executing"
    : "ready";
}

function runStatusLabel(run) {
  const state = runDisplayState(run);
  if (state === "ready") return "Pronta da avviare";
  if (state === "executing") return "In esecuzione";
  return state;
}

function refreshRunStatusLabels(runId) {
  const run = allRuns.find(item => item.id === runId);
  if (!run) return;
  document.querySelectorAll('[data-run-status="' + runId + '"]').forEach(label => {
    label.textContent = runStatusLabel(run);
  });
}

function selectRun(runId) {
  selectedRunId = runId;
  renderRuns(allRuns);
}

function createRunLink(runId, label) {
  const link = document.createElement("a");
  link.href = "#run-" + runId;
  link.textContent = label;
  link.addEventListener("click", event => {
    if (!event.metaKey && !event.ctrlKey && !event.shiftKey && !event.altKey &&
        window.location.hash === link.hash) {
      event.preventDefault();
      openRunWorkspace(runId);
    }
  });
  return link;
}

function openRunWorkspace(runId) {
  if (!allRuns.some(run => run.id === runId)) {
    return alert("Run #" + runId + " is not available in Run Workspace.");
  }

  if (!getVisibleRuns(allRuns).some(run => run.id === runId)) {
    document.getElementById("run-filter-status").value = "all";
    document.getElementById("run-filter-agent").value = "all";
    document.getElementById("run-search").value = "";
  }

  switchDashboardView("agents", {scrollToTop: false});
  selectRun(runId);

  const detail = document.getElementById("run-detail");
  detail.scrollTop = 0;
  detail.focus({preventScroll: true});
  detail.scrollIntoView({block: "start"});
}

function splitRunOutput(output) {
  const text = output || "";
  const marker = "TECHNICAL_DETAIL:";

  if (!text.includes(marker)) {
    return {
      summary: text,
      technical: ""
    };
  }

  const parts = text.split(marker);

  return {
    summary: parts[0].trim(),
    technical: parts.slice(1).join(marker).trim()
  };
}

function summarizeRunTask(task) {
  const text = (task || "").trim();
  const heading = text.split("\n", 1)[0];
  const incident = /^Incident #(\d+)$/m.exec(text.slice(0, 240));
  const subject = incident ? "l’incidente #" + incident[1] : "l’incidente";

  if (heading === "INCIDENT HANDOFF TO BUILDER") {
    return "Esamina la diagnosi per " + subject + " e proponi la modifica più piccola da verificare.";
  }
  if (heading === "VERIFY INCIDENT AFTER APPROVED BUILDER PROPOSAL") {
    return "Verifica se la modifica approvata risolve il problema per " + subject + ".";
  }
  if (heading.startsWith("HANDOFF FROM RUN #")) {
    const source = /^HANDOFF FROM RUN #(\d+)$/.exec(heading);
    return source
      ? "Riprendi il lavoro dalla run #" + source[1] + " e proponi il prossimo passo tecnico."
      : "Riprendi il lavoro precedente e proponi il prossimo passo tecnico.";
  }
  if (heading.startsWith("Analizza questo incidente reale di Officina Lab")) {
    return "Analizza l’incidente: controlla le prove, spiega la causa probabile e suggerisci una verifica.";
  }
  if (heading.startsWith("Analizza questo errore reale di Officina Lab")) {
    return "Analizza l’errore: controlla le prove, spiega la causa probabile e suggerisci una verifica.";
  }
  if (heading.startsWith("[TEST limite 512 KiB]")) {
    return "Verifica che Officina Lab blocchi una richiesta oltre il limite di 512 KiB.";
  }

  if (/^\{\s*(?:"|\})|^\[\s*(?:[\[{"\]\d-]|true\b|false\b|null\b)/.test(text)) {
    return "Questo task contiene dati strutturati. Apri il task completo per leggerli.";
  }

  const preview = text.slice(0, 500).split(/\n\s*\n/, 1)[0].replace(/\s+/g, " ").trim();
  const excerpt = preview.slice(0, 220).trimEnd();
  return text.length > 500 || excerpt.length < text.replace(/\s+/g, " ").length
    ? excerpt + "…"
    : excerpt;
}

function renderRunDetail(run) {
  const detail = document.getElementById("run-detail");
  if (!detail) return;

  if (!run) {
    detail.innerHTML =
      '<div class="run-detail-empty">Select a run to inspect task, output, metrics and actions.</div>';
    return;
  }

  const totalTokens = (run.tokens_in || 0) + (run.tokens_out || 0);
  let actions = "";

  if (run.status === "running") {
    if (runDisplayState(run) === "ready") {
      actions += '<button onclick="executeRun(' + run.id + ', this)">Execute</button>';
    }
    actions +=
      '<button onclick="finishRun(' + run.id + ',\'completed\')">Complete</button>' +
      '<button onclick="finishRun(' + run.id + ',\'failed\')">Fail</button>';
  }

  if (run.can_prepare_retry) {
    actions += '<button onclick="prepareRunRetry(' + run.id + ', this)">Prepare retry</button>';
  }

  if (
    run.status === "completed" &&
    run.output &&
    run.agent_name.toLowerCase() === "explorer"
  ) {
    actions +=
      '<button onclick="handoffToBuilder(' + run.id + ')">Handoff to Builder</button>';
  }

  let context = "";
  if (run.context_sources) {
    try {
      const parsed = JSON.parse(run.context_sources);
      context = Array.isArray(parsed) ? parsed.join(" · ") : String(parsed);
    } catch (error) {
      context = String(run.context_sources);
    }
  }

  const taskSummary = summarizeRunTask(run.task);
  const outputParts = splitRunOutput(run.output);

  detail.innerHTML =
    '<div class="run-detail-header">' +
      '<div>' +
        '<span class="eyebrow">Run #' + run.id + '</span>' +
        '<h3>' + run.agent_name + '</h3>' +
        (run.retry_of_run_id != null ? '<p class="incident-meta run-retry-source"></p>' : '') +
      '</div>' +
      '<span class="run-status ' + run.status + '" data-run-status="' + run.id + '">' + runStatusLabel(run) + '</span>' +
    '</div>' +
    '<div class="run-detail-grid">' +
      '<div><span class="run-detail-label">Started</span><strong>' + (run.started_at || "—") + '</strong></div>' +
      '<div><span class="run-detail-label">Ended</span><strong>' + (run.ended_at || "—") + '</strong></div>' +
      '<div><span class="run-detail-label">Tokens</span><strong>' + totalTokens.toLocaleString() + '</strong></div>' +
      '<div><span class="run-detail-label">Cost</span><strong>$' + Number(run.cost_usd || 0).toFixed(4) + '</strong></div>' +
    '</div>' +
    '<div class="run-detail-block">' +
      '<span class="run-detail-label">Task</span>' +
      '<div class="run-detail-text run-task-summary"></div>' +
    '</div>' +
    (run.task && taskSummary !== run.task.trim()
      ? '<details class="run-technical-context">' +
          '<summary>Task completo</summary>' +
          '<pre class="run-full-task"></pre>' +
        '</details>'
      : '') +
    '<div class="run-detail-block run-output-block">' +
      '<span class="run-detail-label">Output</span>' +
      '<pre class="run-detail-output">' + (outputParts.summary || "No output yet.") + '</pre>' +
    '</div>' +
    (outputParts.technical
      ? '<details class="run-technical-context">' +
          '<summary>Technical error details</summary>' +
          '<pre>' + outputParts.technical + '</pre>' +
        '</details>'
      : '') +
    (context
      ? '<details class="run-technical-context">' +
          '<summary>Context sources</summary>' +
          '<div class="run-detail-text">' + context + '</div>' +
        '</details>'
      : '') +
    '<div class="run-detail-actions">' + actions + '</div>' +
    (run.can_prepare_retry
      ? '<p class="incident-meta">Prepara una nuova run con lo stesso agente e lo stesso task. Premi Execute nella nuova run quando vuoi avviarla.</p>'
      : '');

  detail.querySelector(".run-task-summary").textContent = taskSummary || "—";
  const retrySource = detail.querySelector(".run-retry-source");
  if (retrySource) {
    retrySource.append("Nuovo tentativo della ", createRunLink(run.retry_of_run_id, "run #" + run.retry_of_run_id));
  }
  const fullTask = detail.querySelector(".run-full-task");
  if (fullTask) fullTask.textContent = run.task;
}

function renderRuns(runs) {
  const count = document.getElementById("run-count");
  if (count) count.textContent = runs.length + " runs";

  populateRunAgentFilter();

  const visible = getVisibleRuns(runs);
  const list = document.getElementById("run-list");

  if (!list) return;

  list.innerHTML = "";

  if (!visible.length) {
    list.innerHTML = '<div class="run-list-empty">No runs match these filters.</div>';
    renderRunDetail(null);
    return;
  }

  if (
    selectedRunId === null ||
    !visible.some(run => run.id === selectedRunId)
  ) {
    selectedRunId = visible[0].id;
  }

  visible.forEach(run => {
    const item = document.createElement("button");
    item.type = "button";
    item.className =
      "run-list-item" +
      (run.id === selectedRunId ? " active" : "");
    item.addEventListener("click", () => selectRun(run.id));

    const preview = summarizeRunTask(run.task);

    item.innerHTML =
      '<div class="run-list-top">' +
        '<strong>' + run.agent_name + '</strong>' +
        '<span class="run-status ' + run.status + '" data-run-status="' + run.id + '">' + runStatusLabel(run) + '</span>' +
      '</div>' +
      '<div class="run-list-task"></div>' +
      '<div class="run-list-meta">#' + run.id + ' · ' + (run.started_at || "") + '</div>';

    item.querySelector(".run-list-task").textContent = preview || "—";
    list.appendChild(item);
  });

  renderRunDetail(
    runs.find(run => run.id === selectedRunId)
  );
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
  updateIncidentNavBadge(allIncidents);
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

async function prepareRunRetry(runId, button) {
  button.disabled = true;
  try {
    const response = await fetch("/api/runs/" + runId + "/retry", {method: "POST"});
    const run = await response.json();
    if (!response.ok) return alert(run.detail || "Impossibile preparare il nuovo tentativo.");

    await Promise.all([loadRuns(), loadAgents()]);
    openRunWorkspace(run.id);
    await loadIncidents();
  } catch (error) {
    alert("Impossibile aprire il nuovo tentativo: " + error.message);
  } finally {
    button.disabled = false;
  }
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

function estimateRunDurationSeconds(runId) {
  const run = allRuns.find(item => item.id === runId);
  if (!run) return null;

  const samples = allRuns
    .filter(item =>
      item.agent_name === run.agent_name &&
      item.status === "completed" &&
      Number.isFinite(item.duration_seconds) &&
      item.duration_seconds > 0
    )
    .map(item => item.duration_seconds)
    .sort((a, b) => a - b);

  if (!samples.length) return null;

  const middle = Math.floor(samples.length / 2);

  return samples.length % 2
    ? samples[middle]
    : Math.round((samples[middle - 1] + samples[middle]) / 2);
}

async function executeRun(id, button = null) {
  const originalLabel = button ? button.textContent : null;
  const estimatedSeconds = estimateRunDurationSeconds(id);
  const startedAt = Date.now();
  let timerId = null;

  activeRunExecutions.add(id);
  refreshRunStatusLabels(id);

  const updateButtonTimer = () => {
    if (!button) return;

    const elapsed = Math.max(
      0,
      Math.floor((Date.now() - startedAt) / 1000)
    );

    button.textContent =
      "Executing… " + elapsed + "s" +
      (
        estimatedSeconds
          ? " · stima ~" + estimatedSeconds + "s"
          : " · stima n/d"
      );
  };

  if (button) {
    button.disabled = true;
    updateButtonTimer();
    timerId = setInterval(updateButtonTimer, 1000);
  }

  try {
    const r = await fetch(
      "/api/runs/" + id + "/execute",
      { method:"POST" }
    );

    let payload = null;

    try {
      payload = await r.json();
    } catch (error) {
      payload = null;
    }

    if (!r.ok) {
      const detail =
        payload?.detail ||
        payload?.error ||
        ("HTTP " + r.status);

      alert("Run #" + id + " execution failed: " + detail);
      return;
    }

    selectedRunId = id;

    await Promise.all([
      loadRuns(),
      loadAgents(),
      loadIncidents(),
      loadErrors()
    ]);

    const refreshedRun = allRuns.find(run => run.id === id);

    if (refreshedRun) {
      renderRunDetail(refreshedRun);
    }
  } catch (error) {
    alert(
      "Impossibile raggiungere il backend per il run #" +
      id + ": " + error.message
    );
  } finally {
    activeRunExecutions.delete(id);
    refreshRunStatusLabels(id);

    if (timerId) {
      clearInterval(timerId);
    }

    if (button) {
      button.disabled = false;
      button.textContent = originalLabel || "Execute";
    }
  }
}

async function handoffIncidentToBuilder(incidentId) {
  const r = await fetch(
    "/api/incidents/" + incidentId + "/handoff-builder",
    { method:"POST" }
  );

  if (!r.ok) {
    const error = await r.json();
    return alert(
      "Errore nell'handoff a Builder: " +
      (error.detail || "errore sconosciuto")
    );
  }

  await Promise.all([
    loadRuns(),
    loadAgents()
  ]);
}

async function requestIncidentApproval(incidentId) {
  const r = await fetch(
    "/api/incidents/" + incidentId + "/proposal-approval",
    { method:"POST" }
  );

  if (!r.ok) {
    const error = await r.json();
    return alert(
      "Errore approval: " +
      (error.detail || "errore sconosciuto")
    );
  }

  await Promise.all([
    loadApprovals(),
    loadIncidents()
  ]);
}

async function startIncidentVerification(incidentId) {
  const r = await fetch(
    "/api/incidents/" + incidentId + "/verify",
    { method:"POST" }
  );

  if (!r.ok) {
    const error = await r.json();
    return alert(
      "Errore verification: " +
      (error.detail || "errore sconosciuto")
    );
  }

  await Promise.all([
    loadRuns(),
    loadIncidents(),
    loadAgents()
  ]);
}

async function generateIncidentCaseStudy(incidentId, card) {
  const existing = card.querySelector(".incident-case-study");

  if (existing) {
    existing.remove();
    return;
  }

  const r = await fetch(
    "/api/incidents/" + incidentId + "/case-study"
  );

  if (!r.ok) {
    return alert("Errore nella generazione del case study");
  }

  const result = await r.json();

  const box = document.createElement("div");
  box.className = "incident-case-study";

  const title = document.createElement("div");
  title.className = "incident-case-study-title";
  title.textContent = result.filename;

  const pre = document.createElement("pre");
  pre.textContent = result.markdown;

  const downloadButton = document.createElement("button");
  downloadButton.type = "button";
  downloadButton.textContent = "Download Markdown";
  downloadButton.addEventListener("click", () => {
    const blob = new Blob(
      [result.markdown],
      { type:"text/markdown;charset=utf-8" }
    );
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = result.filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  });

  const copyButton = document.createElement("button");
  copyButton.type = "button";
  copyButton.textContent = "Copy Markdown";
  copyButton.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(
        result.markdown
      );
      copyButton.textContent = "Copied";
    } catch (error) {
      alert("Copia automatica non disponibile");
    }
  });

  box.appendChild(title);
  box.appendChild(downloadButton);
  box.appendChild(copyButton);
  box.appendChild(pre);
  card.appendChild(box);
}

async function viewIncidentReport(incidentId, card) {
  const existing = card.querySelector(".incident-report");

  if (existing) {
    existing.remove();
    return;
  }

  const r = await fetch(
    "/api/incidents/" + incidentId + "/report"
  );

  if (!r.ok) {
    return alert("Errore nel caricamento dell'Incident Report");
  }

  const report = await r.json();
  const analysis = report.analysis;

  const box = document.createElement("div");
  box.className = "incident-report";

  let text =
    "INCIDENT REPORT #" + report.incident_id + "\n\n" +
    "Key: " + report.incident_key + "\n" +
    "Status: " + report.status + "\n" +
    "Severity: " + report.severity + "\n" +
    "Occurrences: " + report.occurrences + "\n" +
    "Created: " + report.created_at + "\n" +
    "Updated: " + report.updated_at + "\n";

  if (report.resolved_at) {
    text += "Resolved: " + report.resolved_at + "\n";
  }

  const latestTask = report.latest_error.task || "";
  const taskPreview = latestTask.slice(0, 4000);
  const taskPreviewNote = latestTask.length > taskPreview.length
    ? "\n[Task shortened. See Run Workspace for the full task.]"
    : "";

  text +=
    "\nLATEST ERROR\n" +
    "Run: #" + report.latest_error.run_id + "\n" +
    "Agent: " + report.latest_error.agent_name + "\n" +
    "Task: " + taskPreview + taskPreviewNote + "\n" +
    "Message:\n" + report.latest_error.message + "\n";

  const structured = report.structured_analysis || {};

  text +=
    "\nSTRUCTURED ANALYSIS\n" +
    "Symptom: " + (structured.symptom || "n/a") + "\n" +
    "Evidence: " + (structured.evidence || "n/a") + "\n" +
    "Root cause: " + (structured.root_cause || "n/a") + "\n" +
    "Confidence: " + (structured.confidence || "n/a") + "\n" +
    "Minimal test: " + (structured.minimal_test || "n/a") + "\n" +
    "Smallest fix: " + (structured.smallest_fix || "n/a") + "\n";

  const builderProposal = report.builder_proposal || {};
  const builderRun = report.builder_run;

  text +=
    "\nBUILDER PROPOSAL\n" +
    "Action type: " + (builderProposal.action_type || "n/a") + "\n" +
    "Target: " + (builderProposal.target || "n/a") + "\n" +
    "Rationale: " + (builderProposal.rationale || "n/a") + "\n" +
    "Change: " + (builderProposal.change || "n/a") + "\n" +
    "Test: " + (builderProposal.test || "n/a") + "\n" +
    "Risk: " + (builderProposal.risk || "n/a") + "\n" +
    "Approval needed: " + (builderProposal.approval_needed || "n/a") + "\n";

  if (builderRun) {
    text +=
      "Builder run: #" + builderRun.run_id +
      " · " + builderRun.status + "\n";
  }

  const approval = report.approval;
  const verificationRun = report.verification_run;

  text +=
    "\nAPPROVAL\n" +
    (approval
      ? "Approval #" + approval.id + " · " + approval.status + "\n"
      : "Not requested\n");

  const verificationResult = report.verification_result || {};
  const verificationState = getVerificationState(
    verificationRun,
    verificationResult
  );

  text +=
    "\nVERIFICATION\n" +
    (verificationRun
      ? "Run #" + verificationRun.run_id + " · " + verificationRun.status + "\n" +
        "Verification recommendation: " + verificationState.label + "\n" +
        (verificationRun.output || "No output yet.") + "\n"
      : "Not started\n");

  if (analysis) {
    text +=
      "\nBUG HUNTER ANALYSIS\n" +
      "Run: #" + analysis.run_id +
      " · " + analysis.status + "\n" +
      "Agent: " + analysis.agent_name + "\n" +
      "Model: " + (analysis.model || "n/a") + "\n" +
      "Tokens: " +
      ((analysis.tokens_in || 0) + (analysis.tokens_out || 0)) +
      "\nCost: $" + Number(analysis.cost_usd || 0).toFixed(4) +
      "\nStarted: " + analysis.started_at + "\n" +
      "Ended: " + (analysis.ended_at || "running") + "\n\n" +
      (analysis.output || "Nessun output disponibile.");
  } else {
    text += "\nBUG HUNTER ANALYSIS\nNessuna analisi collegata.";
  }

  const sourceRunId = report.latest_error.run_id;
  if (sourceRunId != null) {
    const openSourceButton = document.createElement("button");
    openSourceButton.type = "button";
    openSourceButton.textContent = "Open source run #" + sourceRunId;
    openSourceButton.addEventListener("click", () => openRunWorkspace(sourceRunId));
    box.append(openSourceButton, "\n\n" + text);
  } else {
    box.textContent = text;
  }
  card.appendChild(box);
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

  if (incident.status !== "investigating") {
    const statusResponse = await fetch(
      "/api/incidents/" + incidentId +
      "/status?status=investigating",
      { method:"PATCH" }
    );

    if (!statusResponse.ok) {
      return alert("Errore nel passaggio dell'incidente a investigating");
    }

    incident.status = "investigating";
  }

  const task =
    "Analizza questo incidente reale di Officina Lab.\n\n" +
    "Incident key: " + incident.incident_key + "\n" +
    "Status: " + incident.status + "\n" +
    "Severity: " + incident.severity + "\n" +
    "Occurrences: " + incident.occurrences + "\n" +
    "Latest run: #" + incident.latest_run_id + "\n" +
    "Latest agent: " + incident.latest_agent_name + "\n" +
    "Latest task: " + (incident.latest_task || "").slice(0, 4000) + "\n" +
    "Latest error:\n" + (incident.latest_error_message || "").slice(0, 4000) + "\n\n" +
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

  const createdRun = await r.json();

  const linkResponse = await fetch(
    "/api/incidents/" + incidentId +
    "/analysis-run?run_id=" + encodeURIComponent(createdRun.id),
    { method:"PATCH" }
  );

  if (!linkResponse.ok) {
    return alert("Run creato, ma collegamento all'incidente fallito");
  }

  if (incidentFilter !== "all") {
    incidentFilter = "investigating";
  }
  await Promise.all([loadRuns(), loadAgents()]);
  await loadIncidents();
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

document.querySelectorAll("[data-view-target]").forEach(button => {
  button.addEventListener("click", () => {
    const viewName = button.getAttribute("data-view-target");
    switchDashboardView(viewName);
    if (viewName === "incidents") {
      loadRuns().then(() => renderIncidents(allIncidents)).catch(error => {
        console.error("Could not refresh incident run states", error);
      });
    }
  });
});

document.querySelectorAll("[data-incident-filter]").forEach(button => {
  button.addEventListener("click", () => {
    incidentFilter = button.dataset.incidentFilter;
    renderIncidents(allIncidents);
  });
});

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

function openRunFromLink() {
  const match = /^#run-(\d+)$/.exec(window.location.hash);
  if (match) openRunWorkspace(Number(match[1]));
}

const dashboardReady = refreshDashboard();
dashboardReady.then(openRunFromLink);
window.addEventListener("hashchange", () => dashboardReady.then(openRunFromLink));
