// In-memory hand-off between screens for intents that have no URL (docs/03 allows only the
// /ledger?id= and /memory?tab= deep links). Survives client-side navigation, not a reload.

let approvalsTab: "pending" | "history" | null = null;

/** An activity click on a decided/executed action opens Approvals on the History tab. */
export function requestApprovalsTab(tab: "pending" | "history") {
  approvalsTab = tab;
}

/** Read once by the Approvals screen on mount. */
export function takeApprovalsTab(): "pending" | "history" | null {
  const tab = approvalsTab;
  approvalsTab = null;
  return tab;
}
